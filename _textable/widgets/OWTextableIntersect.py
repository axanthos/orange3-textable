"""
Class OWTextableIntersect
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

__version__ = '0.15.4'


import LTTL.SegmenterThread as Segmenter
from LTTL.Segmentation import Segmentation

from .TextableUtils import (
    OWTextableBaseWidget, InfoBox, SendButton, AdvancedSettings,
    pluralize, updateMultipleInputs, SegmentationListContextHandler,
    SegmentationsInputList, ProgressBar,
    Task
)

from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableIntersect(OWTextableBaseWidget):
    """Orange widget for segment in-/exclusion based on other segmentation"""

    name = "Intersect"
    description = "In-/exclude segments based on another segmentation"
    icon = "icons/Intersect.png"
    priority = 4004

    # Input and output channels...
    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [
        ('Selected data', Segmentation, widget.Default),
        ('Discarded data', Segmentation)
    ]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    segmentations = SegmentationsInputList()  # type: list

    # Settings...
    copyAnnotations = settings.Setting(True)
    mode = settings.Setting(u'Include')
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting('num')
    displayAdvancedSettings = settings.Setting(False)

    source = settings.ContextSetting(0)
    filtering = settings.ContextSetting(0)
    sourceAnnotationKey = settings.ContextSetting(u'(none)')
    filteringAnnotationKey = settings.ContextSetting(u'(none)')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        # TODO: update docs to match removal of source annotation from basic

        self.advancedSettings.draw()

        # Intersect box
        self.intersectBox = self.create_widgetbox(
            box=u'Intersect',
            orientation='vertical',
            addSpace=False,
            )

        self.modeCombo = gui.comboBox(
            widget=self.intersectBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[u'Include', u'Exclude'],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether source segments whose type is\n"
                u"present in the filter segmentation should be\n"
                u"included in or excluded from the output\n"
                u"segmentation."
            ),
        )
        self.modeCombo.setMinimumWidth(140)
        gui.separator(widget=self.intersectBox, height=3)
        self.sourceCombo = gui.comboBox(
            widget=self.intersectBox,
            master=self,
            value='source',
            orientation='horizontal',
            label=u'Source segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation from which a subset of segments\n"
                u"will be selected to build the output segmentation."
            ),
        )
        gui.separator(widget=self.intersectBox, height=3)
        self.sourceAnnotationCombo = gui.comboBox(
            widget=self.intersectBox,
            master=self,
            value='sourceAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Source annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether source segments will be selected\n"
                u"based on annotation values corresponding to a\n"
                u"specific annotation key or rather on their content\n"
                u"(value 'none')."
            ),
        )
        gui.separator(widget=self.intersectBox, height=3)
        self.filteringCombo = gui.comboBox(
            widget=self.intersectBox,
            master=self,
            value='filtering',
            orientation='horizontal',
            label=u'Filter segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose types will be used to\n"
                u"include source segments in (or exclude them from)\n"
                u"the output segmentation."
            ),
        )
        gui.separator(widget=self.intersectBox, height=3)
        self.filteringAnnotationCombo = gui.comboBox(
            widget=self.intersectBox,
            master=self,
            value='filteringAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Filter annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether filter segment types are based\n"
                u"on annotation values corresponding to a specific\n"
                u"annotation key or rather on segment content\n"
                u"(value 'none')."
            ),
        )
        gui.separator(widget=self.intersectBox, height=3)
        self.advancedSettings.advancedWidgets.append(self.intersectBox)
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
            addSpace=True,
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

        # Basic intersect box
        self.basicIntersectBox = self.create_widgetbox(
            box=u'Intersect',
            orientation='vertical',
            )

        self.basicModeCombo = gui.comboBox(
            widget=self.basicIntersectBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[u'Include', u'Exclude'],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether source segments whose type is\n"
                u"present in the filter segmentation should be\n"
                u"included in or excluded from the output\n"
                u"segmentation."
            ),
        )
        self.basicModeCombo.setMinimumWidth(140)
        gui.separator(widget=self.basicIntersectBox, height=3)
        self.basicSourceCombo = gui.comboBox(
            widget=self.basicIntersectBox,
            master=self,
            value='source',
            orientation='horizontal',
            label=u'Source segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation from which a subset of segments\n"
                u"will be selected to build the output segmentation."
            ),
        )
        gui.separator(widget=self.basicIntersectBox, height=3)
        self.basicFilteringCombo = gui.comboBox(
            widget=self.basicIntersectBox,
            master=self,
            value='filtering',
            orientation='horizontal',
            label=u'Filter segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose types will be used to\n"
                u"include source segments in (or exclude them from)\n"
                u"the output segmentation."
            ),
        )
        gui.separator(widget=self.basicIntersectBox, height=3)
        self.advancedSettings.basicWidgets.append(self.basicIntersectBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        gui.rubber(self.controlArea)

        # Send button & Infobox
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Outputs
        filtered_data, discarded_data = f.result()

        # Send data
        message = u'%i segment@p sent to output.' % len(filtered_data)
        message = pluralize(message, len(filtered_data))
        self.infoBox.setText(message)

        self.send('Selected data', filtered_data) # AS 11.2023: removed self
        self.send('Discarded data', discarded_data) # AS 11.2023: removed self

    def sendData(self):
        """(Have LTTL.Segmenter) perform the actual filtering"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Selected data', None) # 11.2023: Removed self
            self.send('Discarded data', None) # 11.2023: Removed self
            return

        assert self.source >= 0
        assert self.filtering >= 0

        # TODO: remove message 'No label was provided.' from docs

        # Source and filtering parameter...
        source = self.segmentations[self.source][1]
        filtering = self.segmentations[self.filtering][1]
        if self.displayAdvancedSettings:
            source_annotation_key = self.sourceAnnotationKey or None
            if self.sourceAnnotationKey == u'(none)':
                source_annotation_key = None
            filtering_annotation_key = self.filteringAnnotationKey or None
            if filtering_annotation_key == u'(none)':
                filtering_annotation_key = None
        else:
            source_annotation_key = None
            filtering_annotation_key = None

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for auto-numbering.',
                    'warning'
                )
                self.send('Selected data', None) # 11.2023: Removed self
                self.send('Discarded data', None) # 11.2023: Removed self
                return
        else:
            autoNumberKey = None

        # Basic settings...
        if self.displayAdvancedSettings:
            copyAnnotations = self.copyAnnotations
        else:
            copyAnnotations = True

        # Infobox and progress bar
        if self.autoNumber and self.displayAdvancedSettings:
            self.infoBox.setText(f"Step 1/3: Processing...", "warning")
        else:
            self.infoBox.setText(u"Processing...", "warning")

        self.progressBarInit()

        # Threaded function
        threaded_function = partial(
            Segmenter.intersect,
            caller=self,
            source=source,
            source_annotation_key=source_annotation_key,
            filtering=filtering,
            filtering_annotation_key=filtering_annotation_key,
            mode=self.mode.lower(),
            label=self.captionTitle,
            copy_annotations=self.copyAnnotations,
            auto_number_as=autoNumberKey,
        )

        # Threading ...
        self.threading(threaded_function)

    def inputData(self, newItem, newId=None):
        """Process incoming data."""
        # Cancel pending tasks, if any
        self.cancel()
        
        self.closeContext()
        updateMultipleInputs(
            self.segmentations,
            newItem,
            newId,
            self.onInputRemoval
        )
        self.infoBox.inputChanged()
        self.updateGUI()

    def onInputRemoval(self, index):
        """Handle removal of input with given index"""
        if index < self.source:
            self.source -= 1
        elif index == self.source \
                and self.source == len(self.segmentations) - 1:
            self.source -= 1
        if index < self.filtering:
            self.filtering -= 1
        elif index == self.filtering \
                and self.filtering == len(self.segmentations) - 1:
            self.filtering -= 1

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            sourceCombo = self.sourceCombo
            filteringCombo = self.filteringCombo
            intersectBox = self.intersectBox
        else:
            sourceCombo = self.basicSourceCombo
            filteringCombo = self.basicFilteringCombo
            intersectBox = self.basicIntersectBox
        sourceCombo.clear()
        self.sourceAnnotationCombo.clear()
        self.sourceAnnotationCombo.addItem(u'(none)')
        self.advancedSettings.setVisible(self.displayAdvancedSettings)
        if len(self.segmentations) == 0:
            self.source = -1
            self.sourceAnnotationKey = u''
            intersectBox.setDisabled(True)
            return
        else:
            if len(self.segmentations) == 1:
                self.source = 0
            for segmentation in self.segmentations:
                sourceCombo.addItem(segmentation[1].label)
            self.source = max(self.source, 0)
            sourceAnnotationKeys \
                = self.segmentations[self.source][1].get_annotation_keys()
            for k in sourceAnnotationKeys:
                self.sourceAnnotationCombo.addItem(k)
            if self.sourceAnnotationKey not in sourceAnnotationKeys:
                self.sourceAnnotationKey = u'(none)'
            self.sourceAnnotationKey = self.sourceAnnotationKey
            intersectBox.setDisabled(False)
        self.autoNumberKeyLineEdit.setDisabled(not self.autoNumber)
        filteringCombo.clear()
        for index in range(len(self.segmentations)):
            filteringCombo.addItem(self.segmentations[index][1].label)
        self.filtering = max(self.filtering, 0)
        segmentation = self.segmentations[self.filtering]
        if self.displayAdvancedSettings:
            self.filteringAnnotationCombo.clear()
            self.filteringAnnotationCombo.addItem(u'(none)')
            filteringAnnotationKeys = segmentation[1].get_annotation_keys()
            for key in filteringAnnotationKeys:
                self.filteringAnnotationCombo.addItem(key)
            if self.filteringAnnotationKey not in filteringAnnotationKeys:
                self.filteringAnnotationKey = u'(none)'
            self.filteringAnnotationKey = self.filteringAnnotationKey

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.cancel() # Cancel current operation
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext(self.uuid, self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()


if __name__ == '__main__':
    import sys
    import re

    from PyQt5.QtWidgets import QApplication
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableIntersect()
    seg1 = Input(u'hello world', 'text')
    seg2 = Segmenter.tokenize(
        seg1,
        [
            (re.compile(r'hello'), u'tokenize', {'tag': 'interj'}),
            (re.compile(r'world'), u'tokenize', {'tag': 'noun'}),
        ],
        label='words',
    )
    seg3 = Segmenter.tokenize(
        seg2,
        [(re.compile(r'[aeiou]'), u'tokenize')],
        label='V'
    )
    seg4 = Segmenter.tokenize(
        seg2,
        [(re.compile(r'[hlwrdc]'), u'tokenize')],
        label='C'
    )
    seg5 = Segmenter.tokenize(
        seg2,
        [(re.compile(r' '), u'tokenize')],
        label='S'
    )
    seg6 = Segmenter.concatenate(
        [seg3, seg4, seg5],
        import_labels_as='category',
        label='chars',
        sort=True,
        merge_duplicates=True,
    )
    seg7 = Segmenter.tokenize(
        seg6,
        [(re.compile(r'l'), u'tokenize')],
        label='pivot'
    )
    ow.inputData(seg2, 1)
    ow.inputData(seg6, 2)
    ow.inputData(seg7, 3)
    ow.show()
    appl.exec_()
    ow.saveSettings()
