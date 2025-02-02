"""
Class OWTextableSelect
Copyright 2012-2025 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable package.

Orange3-Textable is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3-Textable is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange3-Textable. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

__version__ = '0.14.8'

import re, math

import LTTL.SegmenterThread as Segmenter
from LTTL.Segmentation import Segmentation
from LTTL.Utils import iround

from .TextableUtils import (
    OWTextableBaseWidget, SegmentationContextHandler, ProgressBar,
    InfoBox, SendButton, AdvancedSettings, pluralize,
    Task
)

from Orange.widgets import widget, gui, settings

# Threading
from AnyQt.QtCore import QThread, QTimer, pyqtSlot, pyqtSignal
import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableSelect(OWTextableBaseWidget):
    """Orange widget for segment in-/exclusion based on intrinsic properties"""

    name = "Select"
    description = "Select a subset of segments in a segmentation"
    icon = "icons/Select.png"
    priority = 4003

    # Input and output channels...
    inputs = [('Segmentation', Segmentation, "inputData",)]
    outputs = [
        ('Selected data', Segmentation, widget.Default),
        ('Discarded data', Segmentation)
    ]

    settingsHandler = SegmentationContextHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    method = settings.Setting(u'Regex')
    copyAnnotations = settings.Setting(True)
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    regex = settings.Setting(r'')
    regexMode = settings.Setting(u'Include')
    ignoreCase = settings.Setting(False)
    unicodeDependent = settings.Setting(True)
    multiline = settings.Setting(False)
    dotAll = settings.Setting(False)
    sampleSizeMode = settings.Setting(u'Count')
    sampleSize = settings.ContextSetting(1)
    samplingRate = settings.Setting(1)
    thresholdMode = settings.Setting(u'Count')
    applyMinThreshold = settings.Setting(True)
    applyMaxThreshold = settings.Setting(True)
    minCount = settings.ContextSetting(1)
    maxCount = settings.ContextSetting(1)
    minProportion = settings.Setting(1)
    maxProportion = settings.Setting(100)
    displayAdvancedSettings = settings.Setting(False)

    regexAnnotationKey = settings.ContextSetting(u'(none)')
    thresholdAnnotationKey = settings.ContextSetting(u'(none)')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.segmentation = None

        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = self.create_advancedSettings()

        # GUI...

        self.advancedSettings.draw()

        # Select box
        self.selectBox = self.create_widgetbox(
            box=u'Select',
            orientation='vertical',
            addSpace=False,
            )

        self.methodCombo = gui.comboBox(
            widget=self.selectBox,
            master=self,
            value='method',
            sendSelectedValue=True,
            items=[u'Regex', u'Sample', u'Threshold'],
            orientation='horizontal',
            label=u'Method:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Selection mode.\n\n"
                u"'Regex': segments are selected based on content\n"
                u"or annotation pattern matching.\n\n"
                u"'Sample': segments are selected based on random\n"
                u"or systematic sampling.\n\n"
                u"'Threshold': segments are selected based on the\n"
                u"frequency of the corresponding type (content or\n"
                u"annotation value)."
            ),
        )
        self.methodCombo.setMinimumWidth(120)
        gui.separator(widget=self.selectBox, height=3)
        # Regex box...
        self.regexBox = gui.widgetBox(
            widget=self.selectBox,
            orientation='vertical',
        )
        self.regexModeCombo = gui.comboBox(
            widget=self.regexBox,
            master=self,
            value='regexMode',
            sendSelectedValue=True,
            items=[u'Include', u'Exclude'],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether input segments matching the regex\n"
                u"pattern should be included in or excluded from\n"
                u"the output segmentation."
            ),
        )
        gui.separator(widget=self.regexBox, height=3)
        self.regexAnnotationCombo = gui.comboBox(
            widget=self.regexBox,
            master=self,
            value='regexAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether the regex pattern specified\n"
                u"below should be applied to annotation values\n"
                u"corresponding to a specific annotation key or\n"
                u"directly to the content of input segments (value\n"
                u"'none')."
            ),
        )
        gui.separator(widget=self.regexBox, height=3)
        gui.lineEdit(
            widget=self.regexBox,
            master=self,
            value='regex',
            orientation='horizontal',
            label=u'Regex:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The regex pattern that must be matched by input\n"
                u"segments content or annotation values in order\n"
                u"for the segment to be included in or excluded\n"
                u"from the output segmentation."
            ),
        )
        gui.separator(widget=self.regexBox, height=3)
        regexBoxLine4 = gui.widgetBox(
            widget=self.regexBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=regexBoxLine4,
            master=self,
            value='ignoreCase',
            label=u'Ignore case (i)',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Regex pattern is case-insensitive."
            ),
        )
        gui.checkBox(
            widget=regexBoxLine4,
            master=self,
            value='unicodeDependent',
            label=u'Unicode dependent (u)',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Built-in character classes are Unicode-aware."
            ),
        )
        regexBoxLine5 = gui.widgetBox(
            widget=self.regexBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=regexBoxLine5,
            master=self,
            value='multiline',
            label=u'Multiline (m)',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Anchors '^' and '$' match the beginning and\n"
                u"end of each line (rather than just the beginning\n"
                u"and end of each input segment)."
            ),
        )
        gui.checkBox(
            widget=regexBoxLine5,
            master=self,
            value='dotAll',
            label=u'Dot matches all (s)',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Meta-character '.' matches any character (rather\n"
                u"than any character but newline)."
            ),
        )
        gui.separator(widget=self.regexBox, height=3)

        # Sample box...
        self.sampleBox = gui.widgetBox(
            widget=self.selectBox,
            orientation='vertical',
        )
        self.sampleSizeModeCombo = gui.comboBox(
            widget=self.sampleBox,
            master=self,
            value='sampleSizeMode',
            sendSelectedValue=True,
            items=[u'Count', u'Proportion'],
            orientation='horizontal',
            label=u'Sample size expressed as:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether sample size will be expressed as\n"
                u"a number of tokens (value 'Count') or as a given\n"
                u"proportion of the input segments ('Proportion')."
            ),
        )
        gui.separator(widget=self.sampleBox, height=3)
        self.sampleSizeSpin = gui.spin(
            widget=self.sampleBox,
            master=self,
            value='sampleSize',
            minv=1,
            maxv=1,
            orientation='horizontal',
            label=u'Sample size:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The number of segments that will be sampled."
            ),
        )
        self.samplingRateSpin = gui.spin(
            widget=self.sampleBox,
            master=self,
            value='samplingRate',
            minv=1,
            maxv=100,
            orientation='horizontal',
            label=u'Sampling rate (%):',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The proportion of segments that will be sampled."
            ),
        )
        gui.separator(widget=self.sampleBox, height=3)

        # Threshold box...
        self.thresholdBox = gui.widgetBox(
            widget=self.selectBox,
            orientation='vertical',
        )
        self.thresholdAnnotationCombo = gui.comboBox(
            widget=self.thresholdBox,
            master=self,
            value='thresholdAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether the frequency thresholds\n"
                u"specified below should be applied to annotation\n"
                u"values corresponding to a specific annotation\n"
                u"key or directly to the content of input segments\n"
                u"(value 'none')."
            ),
        )
        gui.separator(widget=self.thresholdBox, height=3)
        self.thresholdModeCombo = gui.comboBox(
            widget=self.thresholdBox,
            master=self,
            value='thresholdMode',
            sendSelectedValue=True,
            items=[u'Count', u'Proportion'],
            orientation='horizontal',
            label=u'Threshold expressed as:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether frequency thresholds will be\n"
                u"expressed as numbers of tokens (value 'Count')\n"
                u"or as relative frequencies (value 'Proportion')."
            ),
        )
        gui.separator(widget=self.thresholdBox, height=3)
        self.minCountLine = gui.widgetBox(
            widget=self.thresholdBox,
            box=False,
            orientation='horizontal',
        )
        self.minCountSpin = gui.spin(
            widget=self.minCountLine,
            master=self,
            value='minCount',
            label=u'Min. count:',
            labelWidth=180,
            controlWidth=None,
            checked='applyMinThreshold',
            minv=1,
            maxv=100,
            callback=self.sendButton.settingsChanged,
            checkCallback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Minimum count for a type to be selected."
            ),
        )
        self.minProportionLine = gui.widgetBox(
            widget=self.thresholdBox,
            box=False,
            orientation='horizontal',
        )
        self.minProportionSpin = gui.spin(
            widget=self.minProportionLine,
            master=self,
            value='minProportion',
            label=u'Min. proportion (%):',
            labelWidth=180,
            controlWidth=None,
            checked='applyMinThreshold',
            minv=1,
            maxv=100,
            callback=self.sendButton.settingsChanged,
            checkCallback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Minimum relative frequency for a type to be selected."
            ),
        )
        gui.separator(widget=self.thresholdBox, height=3)
        self.maxCountLine = gui.widgetBox(
            widget=self.thresholdBox,
            box=False,
            orientation='horizontal',
        )
        self.maxCountSpin = gui.spin(
            widget=self.maxCountLine,
            master=self,
            value='maxCount',
            label=u'Max. count:',
            labelWidth=180,
            controlWidth=None,
            checked='applyMaxThreshold',
            minv=1,
            maxv=100,
            callback=self.sendButton.settingsChanged,
            checkCallback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Maximum count for a type to be selected."
            ),
        )
        self.maxProportionLine = gui.widgetBox(
            widget=self.thresholdBox,
            box=False,
            orientation='horizontal',
        )
        self.maxProportionSpin = gui.spin(
            widget=self.maxProportionLine,
            master=self,
            value='maxProportion',
            label=u'Max. proportion (%):',
            labelWidth=180,
            controlWidth=None,
            checked='applyMaxThreshold',
            minv=1,
            maxv=100,
            callback=self.sendButton.settingsChanged,
            checkCallback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Maximum count for a type to be selected."
            ),
        )
        gui.separator(widget=self.thresholdBox, height=3)
        self.advancedSettings.advancedWidgets.append(self.selectBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Options box...
        self.optionsBox = self.create_widgetbox(
            box=u'Options',
            orientation='vertical',
            addSpace=False,
            )

        optionsBoxLine2 = gui.widgetBox(
            widget=self.optionsBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumber',
            label=u'Auto-number with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotate output segments with increasing numeric\n"
                u"indices."
            ),
        )
        self.autoNumberKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for output segment auto-numbering."
            ),
        )
        gui.separator(widget=self.optionsBox, height=3)
        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value='copyAnnotations',
            label=u'Copy annotations',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Copy all annotations from input to output segments."
            ),
        )
        gui.separator(widget=self.optionsBox, height=2)
        self.advancedSettings.advancedWidgets.append(self.optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Basic Select box
        self.basicSelectBox = self.create_widgetbox(
            box=u'Select',
            orientation='vertical',
            addSpace=False,
            )

        self.basicRegexModeCombo = gui.comboBox(
            widget=self.basicSelectBox,
            master=self,
            value='regexMode',
            sendSelectedValue=True,
            items=[u'Include', u'Exclude'],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether input segments matching the regex\n"
                u"pattern should be included in or excluded from\n"
                u"the output segmentation."
            ),
        )
        gui.separator(widget=self.basicSelectBox, height=3)
        self.basicRegexAnnotationCombo = gui.comboBox(
            widget=self.basicSelectBox,
            master=self,
            value='regexAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether the regex pattern specified\n"
                u"below should be applied to annotation values\n"
                u"corresponding to a specific annotation key or\n"
                u"directly to the content of input segments (value\n"
                u"'none')."
            ),
        )
        gui.separator(widget=self.basicSelectBox, height=3)
        gui.lineEdit(
            widget=self.basicSelectBox,
            master=self,
            value='regex',
            orientation='horizontal',
            label=u'Regex:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The regex pattern that must be matched by input\n"
                u"segments content or annotation values in order\n"
                u"for the segment to be included in or excluded\n"
                u"from the output segmentation."
            ),
        )
        gui.separator(widget=self.basicSelectBox, height=3)
        self.advancedSettings.basicWidgets.append(self.basicSelectBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        gui.rubber(self.controlArea)

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Outputs
        selected_data, discarded_data = f.result()
            
        # Send data
        message = u'%i segment@p sent to output.' % len(selected_data)
        message = pluralize(message, len(selected_data))
        self.infoBox.setText(message)

        self.send('Selected data', selected_data) # AS 10.2023: removed self
        self.send('Discarded data', discarded_data) # AS 10.2023: removed self

    def sendData(self):
        """(Have LTTL.Segmenter) perform the actual selection"""

        # Check that there's something on input...
        if not self.segmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Selected data', None) # AS 10.2023: removed self
            self.send('Discarded data', None) # AS 10.2023: removed self
            return

        # TODO: remove message 'No label was provided.' from docs

        # Advanced settings...
        if self.displayAdvancedSettings:

            # If mode is Regex...
            if self.method == u'Regex':

                # Check that regex is not empty...
                if not self.regex:
                    self.infoBox.setText(u'Please enter a regex.', 'warning')
                    self.send('Selected data', None) # AS 10.2023: removed self
                    self.send('Discarded data', None) # AS 10.2023: removed self
                    return

                # Prepare regex...
                regex_string = self.regex
                if (
                     self.ignoreCase
                     or self.unicodeDependent
                     or self.multiline
                     or self.dotAll
                ):
                    flags = ''
                    if self.ignoreCase:
                        flags += 'i'
                    if self.unicodeDependent:
                        flags += 'u'
                    if self.multiline:
                        flags += 'm'
                    if self.dotAll:
                        flags += 's'
                    regex_string = f"(?{flags}){regex_string}"
                try:
                    regex = re.compile(regex_string)
                except re.error as re_error:
                    try:
                        message = u'Please enter a valid regex (error: %s).' % \
                                  re_error.msg
                    except AttributeError:
                        message = u'Please enter a valid regex.'
                    self.infoBox.setText(message, 'error')
                    self.send('Selected data', None) # AS 10.2023: removed self
                    self.send('Discarded data', None) # AS 10.2023: removed self
                    return

                # Get number of iterations...
                num_iterations = len(self.segmentation)

            # Else if mode is Sample...
            elif self.method == u'Sample':

                # Get sample size...
                if self.sampleSizeMode == u'Proportion':
                    sampleSize = iround(
                        len(self.segmentation)
                        * (self.samplingRate / 100)
                    )
                else:
                    sampleSize = self.sampleSize
                if sampleSize <= 0:
                    self.infoBox.setText(
                        message='Please enter a larger sample size',
                        state="error",
                    )
                    self.send('Selected data', None) # AS 10.2023: removed self
                    self.send('Discarded data', None) # AS 10.2023: removed self
                    return

                # Get number of iterations...
                num_iterations = len(self.segmentation)

            # Else if mode is Threshold...
            elif self.method == u'Threshold':

                # Get min and max count...
                if self.thresholdMode == u'Proportion':
                    minCount = iround(
                        math.ceil(
                            len(self.segmentation)
                            * (self.minProportion / 100)
                        )
                    )
                    maxCount = iround(
                        math.floor(
                            len(self.segmentation)
                            * (self.maxProportion / 100)
                        )
                    )
                else:
                    minCount = self.minCount
                    maxCount = self.maxCount
                if not self.applyMinThreshold:
                    minCount = 1
                if not self.applyMaxThreshold:
                    maxCount = len(self.segmentation)

                # Get number of iterations...
                num_iterations = len(self.segmentation)

            # Check that autoNumberKey is not empty (if necessary)...
            if self.autoNumber:
                if self.autoNumberKey:
                    autoNumberKey = self.autoNumberKey
                else:
                    self.infoBox.setText(
                        u'Please enter an annotation key for auto-numbering.',
                        'warning'
                    )
                    self.send('Selected data', None) # AS 10.2023: removed self
                    self.send('Discarded data', None) # AS 10.2023: removed self
                    return
            else:
                autoNumberKey = None

            # Various cases...
            if self.method == u'Regex':
                regexAnnotationKeyParam = self.regexAnnotationKey
                if regexAnnotationKeyParam == u'(none)':
                    regexAnnotationKeyParam = None
                    
                # Function for threading
                threaded_function = partial(
                    Segmenter.select,
                    caller=self,
                    segmentation=self.segmentation,
                    regex=regex,
                    mode=self.regexMode.lower(),
                    annotation_key=regexAnnotationKeyParam or None,
                    label=self.captionTitle,
                    copy_annotations=self.copyAnnotations,
                    auto_number_as=autoNumberKey,
                )
                
            elif self.method == u'Sample':
            
                # Function for threading
                threaded_function = partial(
                    Segmenter.sample,
                    caller=self,
                    segmentation=self.segmentation,
                    sample_size=sampleSize,
                    mode='random',
                    label=self.captionTitle,
                    copy_annotations=self.copyAnnotations,
                    auto_number_as=autoNumberKey,
                )
                
            elif self.method == u'Threshold':
                if (
                            (minCount == 1 or not self.applyMinThreshold)
                        and (
                                        maxCount == len(self.segmentation)
                                or not self.applyMaxThreshold
                        )
                ):
                    # Function for threading
                    threaded_function = partial(
                        Segmenter.bypass,
                        segmentation=self.segmentation,
                        label=self.captionTitle,
                    )
                    
                else:
                    thresholdAnnotationKeyParam = self.thresholdAnnotationKey
                    if thresholdAnnotationKeyParam == u'(none)':
                        thresholdAnnotationKeyParam = None
                    
                    # Function for threading
                    threaded_function = partial(
                        Segmenter.threshold,
                        caller=self,
                        segmentation=self.segmentation,
                        annotation_key=(
                            thresholdAnnotationKeyParam
                            or None
                        ),
                        min_count=minCount,
                        max_count=maxCount,
                        label=self.captionTitle,
                        copy_annotations=self.copyAnnotations,
                        auto_number_as=autoNumberKey,
                    )

            # Perform selection...
            if self.autoNumber:
                self.infoBox.setText(u"Step 1/3: Processing...", "warning")
            else:
                self.infoBox.setText(u"Processing...", "warning")
            self.progressBarInit()

        # Basic settings:
        else:

            # Check that regex is not empty...
            if not self.regex:
                self.infoBox.setText(u'Please enter a regex.', 'warning')
                self.send('Selected data', None) # AS 10.2023: removed self
                self.send('Discarded data', None) # AS 10.2023: removed self
                return

            # Get number of iterations...
            num_iterations = len(self.segmentation)

            regexAnnotationKeyParam = self.regexAnnotationKey
            if regexAnnotationKeyParam == u'(none)':
                regexAnnotationKeyParam = None
            
            # Function for threading
            threaded_function = partial(
                Segmenter.select,
                caller=self,
                segmentation=self.segmentation,
                regex=re.compile(self.regex + '(?u)'),
                mode=self.regexMode.lower(),
                annotation_key=regexAnnotationKeyParam or None,
                label=self.captionTitle,
                copy_annotations=True,
                auto_number_as=None,
            )
            
            # Perform selection...
            self.infoBox.setText(u"Processing...", "warning")
            self.progressBarInit()

        # Threading ...
        self.threading(threaded_function)

    def inputData(self, segmentation):
        """Process incoming segmentation"""
        # Cancel pending tasks, if any
        self.cancel()
        
        self.closeContext()
        self.segmentation = segmentation
        self.infoBox.inputChanged()
        self.updateGUI()
        if segmentation is not None:
            self.openContext(segmentation)
        self.sendButton.sendIf()

    def updateGUI(self):
        """Update GUI state"""

        if self.displayAdvancedSettings and self.autoNumber:
            self.autoNumberKeyLineEdit.setDisabled(False)
        else:
            self.autoNumberKeyLineEdit.setDisabled(True)

        self.selectBox.setDisabled(not self.segmentation)
        self.basicSelectBox.setDisabled(not self.segmentation)

        if self.displayAdvancedSettings:
            if self.method == u'Regex':
                self.sampleBox.setVisible(False)
                self.thresholdBox.setVisible(False)
                self.regexAnnotationCombo.clear()
                self.regexAnnotationCombo.addItem(u'(none)')
                if self.segmentation is not None:
                    for k in self.segmentation.get_annotation_keys():
                        self.regexAnnotationCombo.addItem(k)
                    self.regexAnnotationKey = self.regexAnnotationKey
                self.regexBox.setVisible(True)

            elif self.method == u'Sample':
                self.regexBox.setVisible(False)
                self.thresholdBox.setVisible(False)
                if self.sampleSizeMode == u'Count':
                    self.samplingRateSpin.box.setVisible(False)
                    if (
                                    self.segmentation is not None
                            and len(self.segmentation)
                    ):
                        self.sampleSizeSpin.setRange(
                            1,
                            len(self.segmentation),
                        )
                        if self.sampleSize > len(self.segmentation):
                            self.sampleSize = len(self.segmentation)
                    else:
                        self.sampleSizeSpin.setRange(1, 1)
                    self.sampleSize = self.sampleSize or 1
                    self.sampleSizeSpin.box.setVisible(True)
                elif self.sampleSizeMode == u'Proportion':
                    self.sampleSizeSpin.box.setVisible(False)
                    self.samplingRate = self.samplingRate or 1
                    self.samplingRateSpin.box.setVisible(True)
                self.sampleBox.setVisible(True)

            elif self.method == u'Threshold':
                self.regexBox.setVisible(False)
                self.sampleBox.setVisible(False)
                self.thresholdAnnotationCombo.clear()
                self.thresholdAnnotationCombo.addItem(u'(none)')
                if self.segmentation is not None:
                    for k in self.segmentation.get_annotation_keys():
                        self.thresholdAnnotationCombo.addItem(k)
                    self.thresholdAnnotationKey = self.thresholdAnnotationKey
                if self.thresholdMode == u'Count':
                    self.minProportionLine.setVisible(False)
                    self.maxProportionLine.setVisible(False)
                    if (
                                    self.segmentation is not None
                            and len(self.segmentation)
                    ):
                        self.maxCount = (
                            self.maxCount
                            or len(self.segmentation)
                        )
                        if self.applyMaxThreshold:
                            maxValue = self.maxCount
                        else:
                            maxValue = len(self.segmentation)
                        self.minCountSpin[1].setRange(
                            1,
                            maxValue,
                        )
                        self.minCount = self.minCount or 1
                        if self.applyMinThreshold:
                            minValue = self.minCount
                        else:
                            minValue = 1
                        self.maxCountSpin[1].setRange(
                            minValue,
                            len(self.segmentation),
                        )
                    else:
                        self.minCountSpin[1].setRange(1, 1)
                        self.maxCountSpin[1].setRange(1, 1)
                        pass
                    self.minCountLine.setVisible(True)
                    self.maxCountLine.setVisible(True)
                elif self.thresholdMode == u'Proportion':
                    self.minCountLine.setVisible(False)
                    self.maxCountLine.setVisible(False)
                    if (
                                    self.segmentation is not None
                            and len(self.segmentation)
                    ):
                        if self.applyMaxThreshold:
                            maxValue = self.maxProportion
                        else:
                            maxValue = 100
                        self.minProportionSpin[1].setRange(
                            1,
                            maxValue,
                        )
                        self.minProportion = self.minProportion or 1
                        if self.applyMinThreshold:
                            minValue = self.minProportion
                        else:
                            minValue = 1
                        self.maxProportionSpin[1].setRange(
                            minValue,
                            100,
                        )
                        self.maxProportion = self.maxProportion or 100
                    else:
                        self.minProportionSpin[1].setRange(1, 100)
                        self.maxProportionSpin[1].setRange(1, 100)
                    self.minProportionLine.setVisible(True)
                    self.maxProportionLine.setVisible(True)
                self.thresholdBox.setVisible(True)

            self.advancedSettings.setVisible(True)

        else:
            self.basicRegexAnnotationCombo.clear()
            self.basicRegexAnnotationCombo.addItem(u'(none)')
            if self.segmentation is not None:
                for k in self.segmentation.get_annotation_keys():
                    self.basicRegexAnnotationCombo.addItem(k)
                self.regexAnnotationKey = self.regexAnnotationKey
            self.advancedSettings.setVisible(False)

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.cancel() # Cancel current operation
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    appl = QApplication(sys.argv)
    ow = OWTextableSelect()
    ow.show()
    appl.exec_()
    ow.saveSettings()

