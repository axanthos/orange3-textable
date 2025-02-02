"""
Class OWTextableContext
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

__version__ = '0.10.8'

from LTTL.TableThread import Table
from LTTL.Segmentation import Segmentation
import LTTL.ProcessorThread as Processor

from .TextableUtils import (
    OWTextableBaseWidget, ProgressBar,
    InfoBox, SendButton, updateMultipleInputs, SegmentationListContextHandler,
    SegmentationsInputList,
    Task
)
import Orange.data
from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableContext(OWTextableBaseWidget):
    """Orange widget for building concordances and studying collocations"""
    
    name = "Context"
    description = "Explore the context of segments"
    icon = "icons/Context.png"
    priority = 8001

    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [('Textable table', Table, widget.Default),
               ('Orange table', Orange.data.Table)]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.rsplit(".", 1)[0],
    )
    segmentations = SegmentationsInputList()  # type: list

    # Settings...
    mode = settings.Setting(u'Neighboring segments')
    separateAnnotation = settings.ContextSetting(False)
    maxLength = settings.Setting(25)
    maxDistance = settings.ContextSetting(5)
    minFrequency = settings.ContextSetting(1)
    applyMaxLength = settings.Setting(True)
    applyMaxDistance = settings.Setting(True)
    useCollocationFormat = settings.Setting(False)
    mergeStrings = settings.Setting(False)

    # Other attributes...
    units = settings.ContextSetting(-1)  # type: int
    unitAnnotationKey = settings.ContextSetting(u'(none)')  # type: str
    _contexts = settings.ContextSetting(-1)  # type: int
    contextAnnotationKey = settings.ContextSetting(u'(none)')  # type: str

    want_main_area = False

    def __init__(self):
        """Initialize a Context widget"""
        super().__init__()

        self.infoBox = InfoBox(
            widget=self.controlArea,
            stringClickSend=u", please click 'Send' when ready.",
        )
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually,
            infoBoxAttribute='infoBox',
            buttonLabel=u'Send',
            checkboxLabel=u'Send automatically',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Units box
        self.unitsBox = self.create_widgetbox(
            box=u'Units',
            orientation='vertical',
            addSpace=True,
            )

        self.unitSegmentationCombo = gui.comboBox(
            widget=self.unitsBox,
            master=self,
            value='units',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation that will be used to specify\n"
                u"'key' segments."
            ),
        )
        self.unitSegmentationCombo.setMinimumWidth(120)
        gui.separator(widget=self.unitsBox, height=3)

        self.unitsSubBox = gui.widgetBox(
            widget=self.unitsBox,
            orientation='vertical',
        )
        self.unitAnnotationCombo = gui.comboBox(
            widget=self.unitsSubBox,
            master=self,
            value='unitAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether some annotation value must\n"
                u"be displayed in place of (or in addition to) the\n"
                u"content of segments in the above specified\n"
                u"segmentation."
            ),
        )
        gui.separator(widget=self.unitsSubBox, height=3)
        self.separateAnnotationCheckBox = gui.checkBox(
            widget=self.unitsSubBox,
            master=self,
            value='separateAnnotation',
            label=u'Separate annotation',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box in order to display the annotation\n"
                u"of 'key' segments in a separate column rather\n"
                u"than in place of their content."
            ),
        )

        # Contexts box...
        self.contextsBox = self.create_widgetbox(
            box=u'Contexts',
            orientation='vertical',
            addSpace=True,
            )

        self.modeCombo = gui.comboBox(
            widget=self.contextsBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[
                u'Neighboring segments',
                u'Containing segmentation',
            ],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Context specification mode.\n\n"
                u"'Neighboring segments': context will consist\n"
                u"of entire segments to the left and right of 'key'\n"
                u"segments (hence the output table possibly\n"
                u"contains a large number of columns, depending on\n"
                u"the 'maximum distance' parameter.\n\n"
                u"'Containing segmentation': contexts are defined\n"
                u"as the characters occurring immediately to the\n"
                u"left and right of 'key' segments (hence the\n"
                u"output table usually contains 3 columns)."
            ),
        )
        gui.separator(widget=self.contextsBox, height=3)
        self.contextSegmentationCombo = gui.comboBox(
            widget=self.contextsBox,
            master=self,
            value='_contexts',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation on which the context definition\n"
                u"is based."
            ),
        )
        gui.separator(widget=self.contextsBox, height=3)
        self.contextAnnotationCombo = gui.comboBox(
            widget=self.contextsBox,
            master=self,
            value='contextAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"In 'Neighboring segments' mode, indicate whether\n"
                u"the content of context segments should be\n"
                u"displayed (value 'none') or rather their\n"
                u"annotation value for a specific annotation key.\n\n"
                u"In 'Containing segmentation' mode, indicate\n"
                u"whether an annotation value of context segments\n"
                u"should be displayed in a separate column."
            ),
        )
        self.neighboringSegmentsBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.neighboringSegmentsBox, height=3)
        self.maxDistanceLine = gui.widgetBox(
            widget=self.neighboringSegmentsBox,
            box=False,
            orientation='horizontal',
        )
        self.maxDistanceSpin = gui.spin(
            widget=self.maxDistanceLine,
            master=self,
            value='maxDistance',
            label=u'Max. distance:',
            labelWidth=180,
            controlWidth=None,
            checked='applyMaxDistance',
            minv=1,
            maxv=100,
            callback=self.sendButton.settingsChanged,
            checkCallback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Maximal distance between 'key' and context segments."
            ),
        )
        gui.separator(widget=self.neighboringSegmentsBox, height=3)
        self.useCollocationFormatCheckbox = gui.checkBox(
            widget=self.neighboringSegmentsBox,
            master=self,
            value='useCollocationFormat',
            label=u'Use collocation format',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box in order to view the 'key'\n"
                u"segment's collocates rather than its contexts of\n"
                u"occurrence."
            ),
        )
        gui.separator(widget=self.neighboringSegmentsBox, height=3)
        iBox = gui.indentedBox(
            widget=self.neighboringSegmentsBox,
        )
        self.minFrequencySpin = gui.spin(
            widget=iBox,
            master=self,
            value='minFrequency',
            minv=1,
            maxv=1,
            step=1,
            orientation='horizontal',
            label=u'Min. frequency:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The minimum frequency of context segment types."
            ),
        )
        self.containingSegmentationBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        self.maxLengthLine = gui.widgetBox(
            widget=self.containingSegmentationBox,
            box=False,
            orientation='horizontal',
        )
        self.maxLengthSpin = gui.spin(
            widget=self.maxLengthLine,
            master=self,
            value='maxLength',
            label=u'Max. length:',
            labelWidth=180,
            controlWidth=None,
            checked='applyMaxLength',
            minv=1,
            maxv=100,
            callback=self.sendButton.settingsChanged,
            checkCallback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Maximal number of characters in immediate left\n"
                u"and right contexts."
            ),
        )

        gui.separator(widget=self.neighboringSegmentsBox, height=3)
        gui.checkBox(
            widget=self.neighboringSegmentsBox,
            master=self,
            value='mergeStrings',
            label=u'Treat distinct strings as contiguous',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box if you want to treat separate strings\n"
                u"as if they were actually contiguous, so that the end of\n"
                u"each string is adjacent to the beginning of the next string."
            ),
        )
        gui.separator(widget=self.contextsBox, height=3)

        gui.rubber(self.controlArea)

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Data outputs
        textable_table, orange_table = f.result()
            
        # Data treatment
        if not len(textable_table.row_ids):
            self.infoBox.setText(u'Resulting table is empty.', 'warning')
            self.send('Textable table', None) # AS 10.2023: removed self
            self.send('Orange table', None) # AS 10.2023: removed self
        else:
            self.send('Textable table', textable_table) # AS 10.2023: removed self
            self.send('Orange table', orange_table) # AS 10.2023: removed self
            self.infoBox.setText(u'Table sent to output.')

    def sendData(self):
        """Check input, compute variety, then send table"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Textable table', None) # AS 10.2023: removed self
            self.send('Orange table', None) # AS 10.2023: removed self
            return

        assert self.units >= 0
        assert self._contexts >= 0
        
        # Amount of iterations (max_itr in ProcessorThread)
        iterations = len(self.segmentations[self._contexts][1])

        # Case 1: Neighboring segments...
        if self.mode == u'Neighboring segments':

            # Contexts parameter...
            contexts = {
                'segmentation': self.segmentations[self._contexts][1],
                'annotation_key': self.contextAnnotationKey or None,
                'merge_strings': self.mergeStrings,
            }
            if contexts['annotation_key'] == u'(none)':
                contexts['annotation_key'] = None
            if self.applyMaxDistance:
                contexts['max_distance'] = self.maxDistance

            # Case 1a: Concordance format...
            if not self.useCollocationFormat:

                # Units parameter...
                units = {
                    'segmentation': self.segmentations[self.units][1],
                    'annotation_key': self.unitAnnotationKey or None,
                    'separate_annotation': self.separateAnnotation,
                }
                if units['annotation_key'] == u'(none)':
                    units['annotation_key'] = None

                # Function for threading...
                threaded_function = partial(
                    Processor.neighbors,
                    caller=self,
                    units=units,
                    contexts=contexts,
                    iterations=iterations,
                )

            # Case 1b: Collocation format...
            else:

                # Units parameter...
                units = self.segmentations[self.units][1]

                # Contexts parameter...
                contexts['min_frequency'] = self.minFrequency
                contexts['merge_strings'] = self.mergeStrings

                # Function for threading...
                threaded_function = partial(
                    Processor.collocations,
                    caller=self,
                    units=units,
                    contexts=contexts,
                    iterations=iterations,
                )

        # Case 2: Containing segmentation...
        else:

            # Units parameter...
            units = {
                'segmentation': self.segmentations[self.units][1],
                'annotation_key': self.unitAnnotationKey or None,
                'separate_annotation': self.separateAnnotation,
            }
            if units['annotation_key'] == u'(none)':
                units['annotation_key'] = None

            # Parameters for mode 'Containing segmentation'...
            if self.mode == 'Containing segmentation':
                contexts = {
                    'segmentation': self.segmentations[self._contexts][1],
                    'annotation_key': self.contextAnnotationKey or None,
                    'max_num_chars': self.maxLength,
                }
            if contexts['annotation_key'] == u'(none)':
                contexts['annotation_key'] = None
            if not self.applyMaxLength:
                contexts['max_num_chars'] = None

            # Function for threading...
            threaded_function = partial(
                Processor.context,
                caller=self,
                units=units,
                contexts=contexts,
                iterations=iterations,
            )
            
        # Infobox and progress bar
        self.progressBarInit()
        self.infoBox.setText(u"Step 1/2: Processing...", "warning")

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
        if index < self.units:
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations) - 1:
            self.units -= 1
        if index < self._contexts:
            self._contexts -= 1
        elif index == self._contexts \
                and self._contexts == len(self.segmentations) - 1:
            self._contexts -= 1

    def updateGUI(self):
        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')
        self.contextSegmentationCombo.clear()
        self.contextAnnotationCombo.clear()
        self.contextAnnotationCombo.addItem(u'(none)')

        if len(self.segmentations) == 0:
            self.units = -1
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
            self.contextsBox.setDisabled(True)
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
                self._contexts = 0
            for segmentation in self.segmentations:
                self.unitSegmentationCombo.addItem(segmentation[1].label)
            self.units = max(self.units, 0)
            unitAnnotationKeys \
                = self.segmentations[self.units][1].get_annotation_keys()
            for k in unitAnnotationKeys:
                self.unitAnnotationCombo.addItem(k)
            if self.unitAnnotationKey not in unitAnnotationKeys:
                self.unitAnnotationKey = u'(none)'
            self.unitAnnotationKey = self.unitAnnotationKey
            if self.unitAnnotationKey == u'(none)':
                self.separateAnnotation = False
                self.separateAnnotationCheckBox.setDisabled(True)
            else:
                self.separateAnnotationCheckBox.setDisabled(False)
            self.unitsBox.setDisabled(False)
            for index in range(len(self.segmentations)):
                self.contextSegmentationCombo.addItem(
                    self.segmentations[index][1].label
                )
            self._contexts = max(self._contexts, 0)
            self.contextsBox.setDisabled(False)
            segmentation = self.segmentations[self._contexts][1]
            self.contextAnnotationCombo.clear()
            self.contextAnnotationCombo.addItem(u'(none)')
            contextAnnotationKeys = segmentation.get_annotation_keys()
            for key in contextAnnotationKeys:
                self.contextAnnotationCombo.addItem(key)
            if self.contextAnnotationKey not in contextAnnotationKeys:
                self.contextAnnotationKey = u'(none)'
            self.contextAnnotationKey = self.contextAnnotationKey

            if self.mode == u'Neighboring segments':
                self.containingSegmentationBox.setVisible(False)
                self.neighboringSegmentsBox.setVisible(True)
                if (segmentation is not None and len(segmentation)):
                    self.maxDistance = (
                        self.maxDistance or len(segmentation) - 1
                    )
                    if len(segmentation) == 1:
                        self.maxDistanceSpin[1].setDisabled(True)
                    else:
                        self.maxDistanceSpin[1].setDisabled(False)
                        self.maxDistanceSpin[1].setRange(
                            1,
                            len(segmentation) - 1,
                        )
                if self.useCollocationFormat:
                    self.unitsSubBox.setDisabled(True)
                    self.minFrequencySpin.setRange(
                        1,
                        len(segmentation),
                    )
                    self.minFrequencySpin.setDisabled(False)
                else:
                    self.unitsSubBox.setDisabled(False)
                    self.minFrequencySpin.setDisabled(True)
                self.minFrequency = (self.minFrequency or 1)

            elif self.mode == u'Containing segmentation':
                self.unitsSubBox.setDisabled(False)
                self.neighboringSegmentsBox.setVisible(False)
                self.containingSegmentationBox.setVisible(True)
                if (segmentation is not None and len(segmentation)):
                    self.maxLength = (self.maxLength or 200)
                    self.maxLengthSpin[1].setRange(
                        1,
                        200,
                    )

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext(self.uuid, self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()


if __name__ == '__main__':
    import sys, re
    from PyQt5.QtWidgets import QApplication
    import LTTL.Segmenter as Segmenter
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableContext()
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
        label='key_segment'
    )
    ow.inputData(seg2, 1)
    ow.inputData(seg6, 2)
    ow.inputData(seg7, 3)
    ow.handleNewSignals()
    ow.inputData(seg2, 1)
    ow.handleNewSignals()
    ow.show()
    appl.exec_()
    ow.saveSettings()
