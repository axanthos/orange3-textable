#=============================================================================
# Class OWTextableSelect, v0.12
# Copyright 2012-2014 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the Textable (v1.4) extension to Orange Canvas.
#
# Textable v1.4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Textable v1.4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Textable v1.4. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

"""
<name>Select</name>
<description>Select a subset of segments in a segmentation</description>
<icon>icons/Select.png</icon>
<priority>4003</priority>
"""

from __future__ import division

import re, math

from LTTL.Segmenter    import Segmenter
from LTTL.Segmentation import Segmentation
from LTTL.Utils        import iround

from TextableUtils      import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableSelect(OWWidget):

    """Orange widget for segment in-/exclusion based on intrisic properties"""
    
    contextHandlers = {
        '': SegmentationContextHandler(
            '', [
                'regexAnnotationKey',
                'thresholdAnnotationKey'
                'sampleSize',
                'minCount',
                'maxCount',
            ],
        )
    }

    settingsList = [
            'regex',
            'method',
            'regexMode',
            'ignoreCase',
            'unicodeDependent',
            'multiline',
            'dotAll',
            'sampleSizeMode',
            'sampleSize',
            'samplingRate',
            'thresholdMode',
            'applyMinThreshold',
            'applyMaxThreshold',
            'minCount',
            'maxCount',
            'minProportion',
            'maxProportion',
            'copyAnnotations',
            'autoSend',
            'label',
            'autoNumber',
            'autoNumberKey',
            'displayAdvancedSettings',
            'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                'TextableSelect',
                wantMainArea=0,
        )

        # Input and output channels...
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Single)]
        self.outputs = [
                ('Selected data', Segmentation, Default),
                ('Discarded data', Segmentation)
        ]
        
        # Settings...
        self.method                     = u'Regex'
        self.copyAnnotations            = True
        self.autoSend                   = False
        self.label                      = u'selected_data'
        self.autoNumber                 = False
        self.autoNumberKey              = u'num'
        self.regex                      = r''
        self.regexMode                  = u'Include'
        self.ignoreCase                 = False
        self.unicodeDependent           = True
        self.multiline                  = False
        self.dotAll                     = False
        self.sampleSizeMode             = u'Count'
        self.sampleSize                 = 1
        self.samplingRate               = 1
        self.thresholdMode              = u'Count'
        self.applyMinThreshold          = True
        self.applyMaxThreshold          = True
        self.minCount                   = 1
        self.maxCount                   = 1
        self.minProportion              = 1
        self.maxProportion              = 100
        self.displayAdvancedSettings    = False
        self.uuid                       = None
        self.loadSettings()
        self.uuid                       = getWidgetUuid(self)

        # Other attributes...
        self.segmenter              = Segmenter()
        self.segmentation           = None
        self.regexAnnotationKey     = None
        self.thresholdAnnotationKey = None
        self.infoBox                = InfoBox(widget=self.controlArea)
        self.sendButton             = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
                sendIfPreCallback   = self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendButton.settingsChanged,
        )

        # GUI...

        self.advancedSettings.draw()

        # Select box
        self.selectBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Select',
                orientation         = 'vertical',
        )
        self.methodCombo = OWGUI.comboBox(
                widget              = self.selectBox,
                master              = self,
                value               = 'method',
                sendSelectedValue   = True,
                items               = [u'Regex', u'Sample', u'Threshold'],
                orientation         = 'horizontal',
                label               = u'Method:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
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
        OWGUI.separator(
                widget              = self.selectBox,
                height              = 3,
        )
        # Regex box...
        self.regexBox = OWGUI.widgetBox(
                widget              = self.selectBox,
                orientation         = 'vertical',
        )
        self.regexModeCombo = OWGUI.comboBox(
                widget              = self.regexBox,
                master              = self,
                value               = 'regexMode',
                sendSelectedValue   = True,
                items               = [u'Include', u'Exclude'],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Specify whether input segments matching the regex\n"
                        u"pattern should be included in or excluded from\n"
                        u"the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.regexBox,
                height              = 3,
        )
        self.regexAnnotationCombo = OWGUI.comboBox(
                widget              = self.regexBox,
                master              = self,
                value               = 'regexAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether the regex pattern specified\n"
                        u"below should be applied to annotation values\n"
                        u"corresponding to a specific annotation key or\n"
                        u"directly to the content of input segments (value\n"
                        u"'none')."
                ),
        )
        OWGUI.separator(
                widget              = self.regexBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = self.regexBox,
                master              = self,
                value               = 'regex',
                orientation         = 'horizontal',
                label               = u'Regex:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The regex pattern that must be matched by input\n"
                        u"segments content or annotation values in order\n"
                        u"for the segment to be included in or excluded\n"
                        u"from the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.regexBox,
                height              = 3,
        )
        regexBoxLine4 = OWGUI.widgetBox(
                widget              = self.regexBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = regexBoxLine4,
                master              = self,
                value               = 'ignoreCase',
                label               = u'Ignore case (i)',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Regex pattern is case-insensitive."
                ),
        )
        OWGUI.checkBox(
                widget              = regexBoxLine4,
                master              = self,
                value               = 'unicodeDependent',
                label               = u'Unicode dependent (u)',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Built-in character classes are Unicode-aware."
                ),
        )
        regexBoxLine5 = OWGUI.widgetBox(
                widget              = self.regexBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = regexBoxLine5,
                master              = self,
                value               = 'multiline',
                label               = u'Multiline (m)',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Anchors '^' and '$' match the beginning and\n"
                        u"end of each line (rather than just the beginning\n"
                        u"and end of each input segment)."
                ),
        )
        OWGUI.checkBox(
                widget              = regexBoxLine5,
                master              = self,
                value               = 'dotAll',
                label               = u'Dot matches all (s)',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Meta-character '.' matches any character (rather\n"
                        u"than any character but newline)."
                ),
        )
        OWGUI.separator(
                widget              = self.regexBox,
                height              = 3,
        )
        
        # Sample box...
        self.sampleBox = OWGUI.widgetBox(
                widget              = self.selectBox,
                orientation         = 'vertical',
        )
        self.sampleSizeModeCombo = OWGUI.comboBox(
                widget              = self.sampleBox,
                master              = self,
                value               = 'sampleSizeMode',
                sendSelectedValue   = True,
                items               = [u'Count', u'Proportion'],
                orientation         = 'horizontal',
                label               = u'Sample size expressed as:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Specify whether sample size will be expressed as\n"
                        u"a number of tokens (value 'Count') or as a given\n"
                        u"proportion of the input segments ('Proportion')."
                ),
        )
        OWGUI.separator(
                widget              = self.sampleBox,
                height              = 3,
        )
        self.sampleSizeSpin = OWGUI.spin(
                widget              = self.sampleBox,
                master              = self,
                value               = 'sampleSize',
                min                 = 1,
                max                 = 1,
                orientation         = 'horizontal',
                label               = u'Sample size:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The number of segments that will be sampled."
                ),
        )
        self.samplingRateSpin = OWGUI.spin(
                widget              = self.sampleBox,
                master              = self,
                value               = 'samplingRate',
                min                 = 1,
                max                 = 100,
                orientation         = 'horizontal',
                label               = u'Sampling rate (%):',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The proportion of segments that will be sampled."
                ),
        )
        OWGUI.separator(
                widget              = self.sampleBox,
                height              = 3,
        )
        
        # Threshold box...
        self.thresholdBox = OWGUI.widgetBox(
                widget              = self.selectBox,
                orientation         = 'vertical',
        )
        self.thresholdAnnotationCombo = OWGUI.comboBox(
                widget              = self.thresholdBox,
                master              = self,
                value               = 'thresholdAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether the frequency thresholds\n"
                        u"specified below should be applied to annotation\n"
                        u"values corresponding to a specific annotation\n"
                        u"key or directly to the content of input segments\n"
                        u"(value 'none')."
                ),
        )
        OWGUI.separator(
                widget              = self.thresholdBox,
                height              = 3,
        )
        self.thresholdModeCombo = OWGUI.comboBox(
                widget              = self.thresholdBox,
                master              = self,
                value               = 'thresholdMode',
                sendSelectedValue   = True,
                items               = [u'Count', u'Proportion'],
                orientation         = 'horizontal',
                label               = u'Threshold expressed as:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Specify whether frequency thresholds will be\n"
                        u"expressed as numbers of tokens (value 'Count')\n"
                        u"or as relative frequencies (value 'Proportion')."
                ),
        )
        OWGUI.separator(
                widget              = self.thresholdBox,
                height              = 3,
        )
        self.minCountLine = OWGUI.widgetBox(
                widget              = self.thresholdBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        self.minCountSpin = OWGUI.checkWithSpin(
                widget              = self.minCountLine,
                master              = self,
                value               = 'minCount',
                label               = u'Min. count:',
                labelWidth          = 180,
                controlWidth        = None,
                checked             = 'applyMinThreshold',
                min                 = 1,
                max                 = 100,
                spinCallback        = self.sendButton.settingsChanged,
                checkCallback       = self.sendButton.settingsChanged,
                tooltip             = (
                      u"Minimum count for a type to be selected."
                ),
        )
        self.minProportionLine = OWGUI.widgetBox(
                widget              = self.thresholdBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        self.minProportionSpin = OWGUI.checkWithSpin(
                widget              = self.minProportionLine,
                master              = self,
                value               = 'minProportion',
                label               = u'Min. proportion (%):',
                labelWidth          = 180,
                controlWidth        = None,
                checked             = 'applyMinThreshold',
                min                 = 1,
                max                 = 100,
                spinCallback        = self.sendButton.settingsChanged,
                checkCallback       = self.sendButton.settingsChanged,
                tooltip             = (
                      u"Minimum relative frequency for a type to be selected."
                ),
        )
        OWGUI.separator(
                widget              = self.thresholdBox,
                height              = 3,
        )
        self.maxCountLine = OWGUI.widgetBox(
                widget              = self.thresholdBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        self.maxCountSpin = OWGUI.checkWithSpin(
                widget              = self.maxCountLine,
                master              = self,
                value               = 'maxCount',
                label               = u'Max. count:',
                labelWidth          = 180,
                controlWidth        = None,
                checked             = 'applyMaxThreshold',
                min                 = 1,
                max                 = 100,
                spinCallback        = self.sendButton.settingsChanged,
                checkCallback       = self.sendButton.settingsChanged,
                tooltip             = (
                      u"Maximum count for a type to be selected."
                ),
        )
        self.maxProportionLine = OWGUI.widgetBox(
                widget              = self.thresholdBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        self.maxProportionSpin = OWGUI.checkWithSpin(
                widget              = self.maxProportionLine,
                master              = self,
                value               = 'maxProportion',
                label               = u'Max. proportion (%):',
                labelWidth          = 180,
                controlWidth        = None,
                checked             = 'applyMaxThreshold',
                min                 = 1,
                max                 = 100,
                spinCallback        = self.sendButton.settingsChanged,
                checkCallback       = self.sendButton.settingsChanged,
                tooltip             = (
                      u"Maximum count for a type to be selected."
                ),
        )
        OWGUI.separator(
                widget              = self.thresholdBox,
                height              = 3,
        )
        self.advancedSettings.advancedWidgets.append(self.selectBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Options box...
        optionsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Options',
                orientation         = 'vertical',
        )
        OWGUI.lineEdit(
                widget              = optionsBox,
                master              = self,
                value               = 'label',
                orientation         = 'horizontal',
                label               = u'Output segmentation label:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Label of the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        optionsBoxLine2 = OWGUI.widgetBox(
                widget              = optionsBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = optionsBoxLine2,
                master              = self,
                value               = 'autoNumber',
                label               = u'Auto-number with key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotate output segments with increasing numeric\n"
                        u"indices."
                ),
        )
        self.autoNumberKeyLineEdit = OWGUI.lineEdit(
                widget              = optionsBoxLine2,
                master              = self,
                value               = 'autoNumberKey',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotation key for output segment auto-numbering."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = optionsBox,
                master              = self,
                value               = 'copyAnnotations',
                label               = u'Copy annotations',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Copy all annotations from input to output segments."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 2,
        )
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Basic Select box
        self.basicSelectBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Select',
                orientation         = 'vertical',
        )
        self.basicRegexModeCombo = OWGUI.comboBox(
                widget              = self.basicSelectBox,
                master              = self,
                value               = 'regexMode',
                sendSelectedValue   = True,
                items               = [u'Include', u'Exclude'],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Specify whether input segments matching the regex\n"
                        u"pattern should be included in or excluded from\n"
                        u"the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.basicSelectBox,
                height              = 3,
        )
        self.basicRegexAnnotationCombo = OWGUI.comboBox(
                widget              = self.basicSelectBox,
                master              = self,
                value               = 'regexAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether the regex pattern specified\n"
                        u"below should be applied to annotation values\n"
                        u"corresponding to a specific annotation key or\n"
                        u"directly to the content of input segments (value\n"
                        u"'none')."
                ),
        )
        OWGUI.separator(
                widget              = self.basicSelectBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = self.basicSelectBox,
                master              = self,
                value               = 'regex',
                orientation         = 'horizontal',
                label               = u'Regex:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The regex pattern that must be matched by input\n"
                        u"segments content or annotation values in order\n"
                        u"for the segment to be included in or excluded\n"
                        u"from the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.basicSelectBox,
                height              = 3,
        )
        self.advancedSettings.basicWidgets.append(self.basicSelectBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # (Basic) options box...
        basicOptionsBox = BasicOptionsBox(self.controlArea, self)
        self.advancedSettings.basicWidgets.append(basicOptionsBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()

        self.sendButton.sendIf()


    def sendData(self):
    
        """(Have LTTL.Segmenter) perform the actual selection"""

        # Check that there's something on input...
        if not self.segmentation:
            self.infoBox.noDataSent(u'No input.')
            self.send('Selected data', None, self)
            return

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(u'No label was provided.')
            self.send('Selected data', None, self)
            return

        # Advanced settings...
        if self.displayAdvancedSettings:

            # If mode is Regex...
            if self.method == u'Regex':

                # Check that regex is not empty...
                if not self.regex:
                    self.infoBox.noDataSent(u'No regex defined.')
                    self.send('Selected data', None, self)
                    return

                # Prepare regex...
                regex_string = self.regex
                if (
                        self.ignoreCase
                    or  self.unicodeDependent
                    or  self.multiline
                    or  self.dotAll
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
                    regex_string += '(?%s)' % flags
                regex = re.compile(regex_string)

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
                    self.infoBox.noDataSent(u'Sample size too small.')
                    self.send('Selected data', None, self)
                    return

                # Get number of iterations...
                num_iterations = sampleSize

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
                    autoNumberKey  = self.autoNumberKey
                    num_iterations *= 2
                else:
                    self.infoBox.noDataSent(
                            u'No annotation key was provided for auto-numbering.'
                    )
                    self.send('Selected data', None, self)
                    return
            else:
                autoNumberKey = None

            # Perform selection...
            progressBar = OWGUI.ProgressBar(
                    self,
                    iterations = num_iterations
            )
            if self.method == u'Regex':
                regexAnnotationKeyParam = self.regexAnnotationKey
                if regexAnnotationKeyParam == u'(none)':
                    regexAnnotationKeyParam = None
                (selected_data, discarded_data) = self.segmenter.select(
                    segmentation        = self.segmentation,
                    regex               = regex,
                    mode                = self.regexMode.lower(),
                    annotation_key      = regexAnnotationKeyParam or None,
                    label               = self.label,
                    copy_annotations    = self.copyAnnotations,
                    auto_numbering_as   = autoNumberKey,
                    progress_callback   = progressBar.advance,
                )
            elif self.method == u'Sample':
                (selected_data, discarded_data) = self.segmenter.sample(
                    segmentation        = self.segmentation,
                    sample_size         = sampleSize,
                    mode                = 'random',
                    label               = self.label,
                    copy_annotations    = self.copyAnnotations,
                    auto_numbering_as   = autoNumberKey,
                    progress_callback   = progressBar.advance,
                )
            elif self.method == u'Threshold':
                if (
                        (minCount == 1 or not self.applyMinThreshold)
                    and (
                            maxCount == len(self.segmentation)
                         or not self.applyMaxThreshold
                        )
                ):
                    (selected_data, discarded_data) = self.segmenter.bypass(
                            segmentation    = self.segmentation,
                            label           = self.label,
                    )
                else:
                    thresholdAnnotationKeyParam = self.thresholdAnnotationKey
                    if thresholdAnnotationKeyParam == u'(none)':
                        thresholdAnnotationKeyParam = None
                    (selected_data, discarded_data) = self.segmenter.threshold(
                        segmentation        = self.segmentation,
                        annotation_key      = (
                                thresholdAnnotationKeyParam
                             or None
                        ),
                        min_count           = minCount,
                        max_count           = maxCount,
                        label               = self.label,
                        copy_annotations    = self.copyAnnotations,
                        auto_numbering_as   = autoNumberKey,
                        progress_callback   = progressBar.advance,
                    )

        # Basic settings:
        else:

            # Check that regex is not empty...
            if not self.regex:
                self.infoBox.noDataSent(u'No regex defined.')
                self.send('Selected data', None, self)
                return

            # Get number of iterations...
            num_iterations = len(self.segmentation)

            # Perform selection...
            progressBar = OWGUI.ProgressBar(
                    self,
                    iterations = num_iterations
            )
            regexAnnotationKeyParam = self.regexAnnotationKey
            if regexAnnotationKeyParam == u'(none)':
                regexAnnotationKeyParam = None
            (selected_data, discarded_data) = self.segmenter.select(
                segmentation        = self.segmentation,
                regex               = re.compile(self.regex + '(?u)'),
                mode                = self.regexMode.lower(),
                annotation_key      = regexAnnotationKeyParam or None,
                label               = self.label,
                copy_annotations    = True,
                auto_numbering_as   = None,
                progress_callback   = progressBar.advance,
            )

        progressBar.finish()

        message = u'Data contains %i segment@p.' % len(selected_data)
        message = pluralize(message, len(selected_data))
        self.infoBox.dataSent(message)

        self.send( 'Selected data', selected_data, self)
        self.send( 'Discarded data', discarded_data, self)
        self.sendButton.resetSettingsChangedFlag()


    def inputData(self, segmentation):
        """Process incoming segmentation"""
        self.closeContext()
        self.segmentation = segmentation
        self.infoBox.inputChanged()
        self.updateGUI()
        if segmentation is not None:
            self.openContext("", segmentation)
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
                    self.samplingRateSpin.setVisible(False)
                    if (
                            self.segmentation is not None
                        and len(self.segmentation)
                    ):
                        self.sampleSizeSpin.control.setRange(
                                1,
                                len(self.segmentation),
                        )
                    else:
                        self.sampleSizeSpin.control.setRange(1, 1)
                    self.sampleSize = self.sampleSize or 1
                    self.sampleSizeSpin.setVisible(True)
                elif self.sampleSizeMode == u'Proportion':
                    self.sampleSizeSpin.setVisible(False)
                    self.samplingRate = self.samplingRate or 1
                    self.samplingRateSpin.setVisible(True)
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




if __name__ == '__main__':
    appl = QApplication(sys.argv)
    ow   = OWTextableSelect()
    ow.show()
    appl.exec_()
    ow.saveSettings()
