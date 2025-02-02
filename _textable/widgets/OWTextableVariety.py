"""
Class OWTextableVariety
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

__version__ = '0.13.9'


from LTTL.TableThread import Table
from LTTL.Segmentation import Segmentation
import LTTL.ProcessorThread as Processor

from .TextableUtils import (
    OWTextableBaseWidget, SegmentationListContextHandler, ProgressBar,
    SegmentationsInputList, InfoBox, SendButton, updateMultipleInputs,
    Task
)
import Orange.data
from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableVariety(OWTextableBaseWidget):
    """Orange widget for measuring variety of text units"""

    name = "Variety"
    description = "Measure the variety of segments"
    icon = "icons/Variety.png"
    priority = 8004

    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [('Textable table', Table, widget.Default),
               ('Orange table', Orange.data.Table)]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    segmentations = SegmentationsInputList()

    # Settings...
    sequenceLength = settings.ContextSetting(1)
    mode = settings.ContextSetting(u'No context')
    mergeContexts = settings.Setting(False)
    windowSize = settings.ContextSetting(1)
    unitWeighting = settings.Setting(False)
    measurePerCategory = settings.Setting(False)
    categoryWeighting = settings.Setting(False)
    adjustSubsampleSize = settings.Setting(True)
    applyResampling = settings.Setting(False)
    numSubsamples = settings.Setting(100)
    subsampleSize = settings.ContextSetting(50)

    units = settings.ContextSetting(-1)
    _contexts = settings.ContextSetting(-1)
    unitAnnotationKey = settings.ContextSetting(u'(none)')
    categoryAnnotationKey = settings.ContextSetting(u'(none)')
    contextAnnotationKey = settings.ContextSetting(u'(none)')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a Variety widget"""

        super().__init__(*args, **kwargs)

        self.infoBox = InfoBox(
            widget=self.controlArea,
            stringClickSend=u", please click 'Send' when ready.",
        )
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually, # Manual cancel button
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
                u"The segmentation whose variety will be measured."
            ),
        )
        self.unitSegmentationCombo.setMinimumWidth(120)
        gui.separator(widget=self.unitsBox, height=3)
        self.unitAnnotationCombo = gui.comboBox(
            widget=self.unitsBox,
            master=self,
            value='unitAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether the variety of the above\n"
                u"specified segmentation must be measured on the\n"
                u"segments' content (value 'none') or on their\n"
                u"annotation values for a specific annotation key."
            ),
        )
        gui.separator(widget=self.unitsBox, height=3)
        self.sequenceLengthSpin = gui.spin(
            widget=self.unitsBox,
            master=self,
            value='sequenceLength',
            minv=1,
            maxv=1,
            step=1,
            orientation='horizontal',
            label=u'Sequence length:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Indicate whether to measure the variety of\n"
                u"single segments or rather of sequences of 2,\n"
                u"3,... segments (n-grams).\n\n"
                u"Note that this parameter cannot be set to a\n"
                u"value larger than 1 if variety is to be\n"
                u"measured per category."
            ),
        )
        gui.separator(widget=self.unitsBox, height=3)
        gui.checkBox(
            widget=self.unitsBox,
            master=self,
            value='unitWeighting',
            label=u'Weigh by frequency',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box in order to apply unit frequency\n"
                u"weighting (i.e. use perplexity instead of variety)."
            ),
        )
        gui.separator(widget=self.unitsBox, height=3)

        # Categories box
        self.categoriesBox = self.create_widgetbox(
            box=u'Categories',
            orientation='vertical',
            addSpace=True,
            )
        """ self.categoriesBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Categories',
            orientation='vertical',
            addSpace=True,
        )
        self.guiElements.append(self.categoriesBox) """
        self.measurePerCategoryCheckbox = gui.checkBox(
            widget=self.categoriesBox,
            master=self,
            value='measurePerCategory',
            label=u'Measure variety per category',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box in order to measure the average\n"
                u"variety per category."
            ),
        )
        gui.separator(widget=self.categoriesBox, height=3)
        iBox = gui.indentedBox(
            widget=self.categoriesBox,
        )
        self.categoryAnnotationCombo = gui.comboBox(
            widget=iBox,
            master=self,
            value='categoryAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether categories are defined by the\n"
                u"segments' content (value 'none') or by their\n"
                u"annotation values for a specific annotation key."
            ),
        )
        gui.separator(widget=iBox, height=3)
        gui.checkBox(
            widget=iBox,
            master=self,
            value='categoryWeighting',
            label=u'Weigh by frequency',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box in order to apply category\n"
                u"frequency weighting (i.e. compute a weighted\n"
                u"rather than unweighted average)."
            ),
        )
        gui.separator(widget=iBox, height=3)
        self.adjustSubsampleSizeCheckbox = gui.checkBox(
            widget=iBox,
            master=self,
            value='adjustSubsampleSize',
            label=u'Dynamically adjust subsample size',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Attempt to make variety estimation more robust\n"
                u"by using the RMSP subsample size adjustment method\n"
                u"described in Xanthos and Guex 2015."
            ),
        )
        self.measurePerCategoryCheckbox.disables.append(iBox)
        if self.measurePerCategory:
            iBox.setDisabled(False)
        else:
            iBox.setDisabled(True)
        gui.separator(widget=self.categoriesBox, height=3)

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
                u'No context',
                u'Sliding window',
                u'Containing segmentation',
            ],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Context specification mode.\n\n"
                u"Contexts define the rows of the resulting\n"
                u"table.\n\n"
                u"'No context': variety will be measured\n"
                u"irrespective of the context (hence the output\n"
                u"table contains a single row).\n\n"
                u"'Sliding window': contexts are defined as all the\n"
                u"successive, overlapping sequences of n segments\n"
                u"in the 'Units' segmentation.\n\n"
                u"'Containing segmentation': contexts are defined\n"
                u"as the distinct segments occurring in a given\n"
                u"segmentation."
            ),
        )
        self.slidingWindowBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.slidingWindowBox, height=3)
        self.windowSizeSpin = gui.spin(
            widget=self.slidingWindowBox,
            master=self,
            value='windowSize',
            minv=1,
            maxv=1,
            step=1,
            orientation='horizontal',
            label=u'Window size:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The length of segment sequences defining contexts."
            ),
        )
        self.containingSegmentationBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        self.contextSegmentationCombo = gui.comboBox(
            widget=self.containingSegmentationBox,
            master=self,
            value='_contexts',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segment types define\n"
                u"the contexts in which the variety of segments\n"
                u"in the 'Units' segmentation will be measured."
            ),
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        self.contextAnnotationCombo = gui.comboBox(
            widget=self.containingSegmentationBox,
            master=self,
            value='contextAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether context types are defined by\n"
                u"the content of segments in the above specified\n"
                u"segmentation (value 'none') or by their annotation\n"
                u"values for a specific annotation key."
            ),
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        gui.checkBox(
            widget=self.containingSegmentationBox,
            master=self,
            value='mergeContexts',
            label=u'Merge contexts',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box if you want to treat all segments\n"
                u"of the above specified segmentation as forming\n"
                u"a single context (hence the resulting table\n"
                u"contains a single row)."
            ),
        )
        gui.separator(widget=self.contextsBox, height=3)

        # Resampling box...
        self.resamplingBox = self.create_widgetbox(
            box=u'Resampling',
            orientation='vertical',
            addSpace=True,
            )

        applyResamplingCheckBox = gui.checkBox(
            widget=self.resamplingBox,
            master=self,
            value='applyResampling',
            label=u'Apply Resampling',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box if you want to compute the average\n"
                u"(or expected) variety per subsample."
            ),
        )
        # TODO: document RMSP!
        gui.separator(widget=self.resamplingBox, height=3)
        iBox2 = gui.indentedBox(
            widget=self.resamplingBox,
        )
        self.subsampleSizeSpin = gui.spin(
            widget=iBox2,
            master=self,
            value='subsampleSize',
            minv=1,
            maxv=1,
            step=1,
            orientation='horizontal',
            label=u'Subsample size:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The number of segments per subsample."
            ),
        )
        gui.separator(widget=iBox2, height=3)
        self.numSubsampleSpin = gui.spin(
            widget=iBox2,
            master=self,
            value='numSubsamples',
            minv=1,
            maxv=100000,
            step=1,
            orientation='horizontal',
            label=u'Number of subsamples:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The number of subsamples (per context)."
            ),
        )
        applyResamplingCheckBox.disables.append(iBox2)
        if self.applyResampling:
            iBox2.setDisabled(False)
        else:
            iBox2.setDisabled(True)
        gui.separator(widget=self.resamplingBox, height=3)

        gui.rubber(self.controlArea)

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Result data
        textable_table, orange_table = f.result()

        if not len(textable_table.row_ids):
            self.infoBox.setText(u'Resulting table is empty.', 'warning')
            self.send('Textable table', None)
            self.send('Orange table', None)
        else:
            self.infoBox.setText(u'Table sent to output.')
            self.send('Textable table', textable_table)
            self.send('Orange table', orange_table)

    def sendData(self):
        """Check input, compute variety, then send table"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Textable table', None)
            self.send('Orange table', None)
            return
        assert self.units >= 0
        # Units parameter...
        units = {
            'segmentation': self.segmentations[self.units][1],
            'annotation_key': self.unitAnnotationKey or None,
            'seq_length': self.sequenceLength,
            'weighting': self.unitWeighting,
        }
        if units['annotation_key'] == u'(none)':
            units['annotation_key'] = None

        # Categories parameter...
        categories = {
            'annotation_key': self.categoryAnnotationKey or None,
            'weighting': self.categoryWeighting,
            'adjust': self.adjustSubsampleSize,
        }
        if categories['annotation_key'] == u'(none)':
            categories['annotation_key'] = None
        
        # Infobox and progress bar
        self.progressBarInit()

        # Case 1: sliding window...
        if self.mode == 'Sliding window':

            num_rows = len(units['segmentation']) - (self.windowSize - 1)
            if self.measurePerCategory:
                if self.applyResampling:
                    num_iterations = num_rows * 3
                else:
                    num_iterations = num_rows * 2
            else:
                num_iterations = num_rows / 2

            # Measure...
            threaded_function = partial(
                Processor.variety_in_window,
                caller=self,
                units=units,
                categories=categories,
                measure_per_category=self.measurePerCategory,
                window_size=self.windowSize,
                apply_resampling=self.applyResampling,
                subsample_size=self.subsampleSize,
                num_subsamples=self.numSubsamples,
            )

        # Case 2: Containing segmentation or no context...
        else:

            # Parameters for mode 'Containing segmentation'...
            if self.mode == 'Containing segmentation':
                assert self._contexts >= 0
                contexts = {
                    'segmentation': self.segmentations[self._contexts][1],
                    'annotation_key': self.contextAnnotationKey or None,
                    'merge': self.mergeContexts,
                }
                if contexts['annotation_key'] == u'(none)':
                    contexts['annotation_key'] = None
                num_contexts = len(contexts['segmentation'])
                if self.measurePerCategory and self.applyResampling:
                    num_iterations = num_contexts * 3
                else:
                    num_iterations = num_contexts
            # Parameters for mode 'No context'...
            else:
                contexts = None
                num_iterations = (
                    len(units['segmentation']) - (self.sequenceLength - 1)
                )
                if self.measurePerCategory and self.applyResampling:
                    num_iterations *= 2

            # Measure...
            threaded_function = partial(
                Processor.variety_in_context,
                caller=self,
                units=units,
                categories=categories,
                contexts=contexts,
                measure_per_category=self.measurePerCategory,
                apply_resampling=self.applyResampling,
                subsample_size=self.subsampleSize,
                num_subsamples=self.numSubsamples,
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
        if index < self.units:
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations) - 1:
            self.units -= 1
        if self.mode == u'Containing segmentation':
            if index == self._contexts:
                self.mode = u'No context'
                self._contexts = -1
            elif index < self._contexts:
                self._contexts -= 1
                if self._contexts < 0:
                    self.mode = u'No context'

    def updateGUI(self):
        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')
        self.categoryAnnotationCombo.clear()
        self.categoryAnnotationCombo.addItem(u'(none)')

        self.adjustSubsampleSizeCheckbox.setDisabled(not self.applyResampling)

        if self.mode == u'No context':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(False)

        if len(self.segmentations) == 0:
            self.units = -1
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
            self.categoryAnnotationKey = u''
            self.categoriesBox.setDisabled(True)
            self.mode = 'No context'
            self.contextsBox.setDisabled(True)
            self.resamplingBox.setDisabled(True)
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
            for segmentation in self.segmentations:
                self.unitSegmentationCombo.addItem(segmentation[1].label)
            self.units = max(self.units, 0)
            unitAnnotationKeys \
                = self.segmentations[self.units][1].get_annotation_keys()
            for k in unitAnnotationKeys:
                self.unitAnnotationCombo.addItem(k)
                self.categoryAnnotationCombo.addItem(k)
            if self.unitAnnotationKey not in unitAnnotationKeys:
                self.unitAnnotationKey = u'(none)'
            self.unitAnnotationKey = self.unitAnnotationKey
            if self.categoryAnnotationKey not in unitAnnotationKeys:
                self.categoryAnnotationKey = u'(none)'
            self.categoryAnnotationKey = self.categoryAnnotationKey
            self.unitsBox.setDisabled(False)
            self.sequenceLengthSpin.setRange(
                1,
                len(self.segmentations[self.units][1])
            )
            self.sequenceLength = self.sequenceLength or 1
            self.categoriesBox.setDisabled(self.sequenceLength > 1)
            self.sequenceLengthSpin.setDisabled(self.measurePerCategory)
            # if self.mode == u'Sliding window':
            #     self.numSubsampleSpin.setDisabled(False)
            # else:
            self.resamplingBox.setDisabled(False)
            self.numSubsampleSpin.setDisabled(
                not(self.measurePerCategory or self.unitWeighting)
            )
            self.contextsBox.setDisabled(False)
            self.subsampleSizeSpin.setRange(
                1,
                len(self.segmentations[self.units][1])
            )
            self.subsampleSize = self.subsampleSize or 1

        if self.mode == u'Sliding window':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)

            self.windowSizeSpin.setRange(
                self.sequenceLength,
                len(self.segmentations[self.units][1])
            )
            self.windowSize = self.windowSize

        elif self.mode == u'Containing segmentation':
            self.slidingWindowBox.setVisible(False)
            self.containingSegmentationBox.setVisible(True)
            self.contextSegmentationCombo.clear()
            for index in range(len(self.segmentations)):
                self.contextSegmentationCombo.addItem(
                    self.segmentations[index][1].label
                )
            self._contexts = max(self._contexts, 0)
            segmentation = self.segmentations[self._contexts]
            self.contextAnnotationCombo.clear()
            self.contextAnnotationCombo.addItem(u'(none)')
            contextAnnotationKeys = segmentation[1].get_annotation_keys()
            for key in contextAnnotationKeys:
                self.contextAnnotationCombo.addItem(key)
            if self.contextAnnotationKey not in contextAnnotationKeys:
                self.contextAnnotationKey = u'(none)'
            self.contextAnnotationKey = self.contextAnnotationKey

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
    ow = OWTextableVariety()
    seg1 = Input(u'aabccc', 'text1')
    seg2 = Input(u'abci', 'text2')
    seg3 = Segmenter.concatenate(
        [seg1, seg2],
        import_labels_as='string',
        label='corpus'
    )
    seg4 = Segmenter.tokenize(
        seg3,
        regexes=[(re.compile(r'\w+'), u'tokenize',)],
    )
    seg5 = Segmenter.tokenize(
        seg4,
        regexes=[(re.compile(r'[ai]'), u'tokenize',)],
        label='V'
    )
    seg6 = Segmenter.tokenize(
        seg4,
        regexes=[(re.compile(r'[bc]'), u'tokenize',)],
        label='C'
    )
    seg7 = Segmenter.concatenate(
        [seg5, seg6],
        import_labels_as='category',
        label='letters',
        sort=True,
        merge_duplicates=True,
    )
    ow.inputData(seg4, 1)
    ow.inputData(seg7, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
