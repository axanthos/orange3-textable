"""
Class OWTextableVariety
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange-Textable package v2.0.

Orange-Textable v2.0 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange-Textable v2.0 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable v2.0. If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '0.13.2'

"""
<name>Variety</name>
<description>Measure the variety of segments</description>
<icon>icons/Variety.png</icon>
<priority>8004</priority>
"""

from LTTL.Table import Table
from LTTL.Segmentation import Segmentation
import LTTL.Processor as Processor

from TextableUtils import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI


class OWTextableVariety(OWWidget):
    """Orange widget for mesuring variety of text units"""

    contextHandlers = {
        '': SegmentationListContextHandler(
            '', [
                ContextInputListField('segmentations'),
                ContextInputIndex('units'),
                ContextInputIndex('_contexts'),
                'mode',
                'unitAnnotationKey',
                'categoryAnnotationKey',
                'contextAnnotationKey',
                'sequenceLength',
                'windowSize',
                'subsampleSize',
                'uuid',
            ]
        )
    }

    settingsList = [
        'autoSend',
        'sequenceLength',
        'measurePerCategory',
        'mode',
        'mergeContexts',
        'windowSize',
        'unitPosMarker',
        'unitWeighting',
        'categoryWeighting',
        'applyResampling',
        'numSubsamples',
        'subsampleSize',
    ]

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Variety widget"""

        OWWidget.__init__(
            self,
            parent,
            signalManager,
            wantMainArea=0,
            wantStateInfoWidget=0,
        )

        self.inputs = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [('Textable Table', Table)]

        # Settings...
        self.autoSend = False
        self.sequenceLength = 1
        self.mode = u'No context'
        self.mergeContexts = False
        self.windowSize = 1
        self.unitWeighting = False
        self.measurePerCategory = False
        self.categoryWeighting = False
        self.applyResampling = False
        self.numSubsamples = 100
        self.subsampleSize = 50
        self.uuid = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.segmentations = list()
        self.units = None
        self.unitAnnotationKey = None
        self.categoryAnnotationKey = None
        self._contexts = None
        self.contextAnnotationKey = None
        self.settingsRestored = False
        self.infoBox = InfoBox(
            widget=self.controlArea,
            stringClickSend=u", please click 'Send' when ready.",
        )
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            buttonLabel=u'Send',
            checkboxLabel=u'Send automatically',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Units box
        self.unitsBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Units',
            orientation='vertical',
            addSpace=True,
        )
        self.unitSegmentationCombo = OWGUI.comboBox(
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
        OWGUI.separator(widget=self.unitsBox, height=3)
        self.unitAnnotationCombo = OWGUI.comboBox(
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
        OWGUI.separator(widget=self.unitsBox, height=3)
        self.sequenceLengthSpin = OWGUI.spin(
            widget=self.unitsBox,
            master=self,
            value='sequenceLength',
            min=1,
            max=1,
            step=1,
            orientation='horizontal',
            label=u'Sequence length:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether to measure the variety of\n"
                u"single segments or rather of sequences of 2,\n"
                u"3,... segments (n-grams).\n\n"
                u"Note that this parameter cannot be set to a\n"
                u"value larger than 1 if variety is to be\n"
                u"measured per category."
            ),
        )
        OWGUI.separator(widget=self.unitsBox, height=3)
        OWGUI.checkBox(
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
        OWGUI.separator(widget=self.unitsBox, height=3)

        # Categories box
        self.categoriesBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Categories',
            orientation='vertical',
            addSpace=True,
        )
        self.measurePerCategoryCheckbox = OWGUI.checkBox(
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
        OWGUI.separator(widget=self.categoriesBox, height=3)
        iBox = OWGUI.indentedBox(
            widget=self.categoriesBox,
        )
        self.categoryAnnotationCombo = OWGUI.comboBox(
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
        OWGUI.separator(widget=iBox, height=3)
        OWGUI.checkBox(
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
        self.measurePerCategoryCheckbox.disables.append(iBox)
        if self.measurePerCategory:
            iBox.setDisabled(False)
        else:
            iBox.setDisabled(True)
        OWGUI.separator(widget=self.categoriesBox, height=3)

        # Contexts box...
        self.contextsBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Contexts',
            orientation='vertical',
            addSpace=True,
        )
        self.modeCombo = OWGUI.comboBox(
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
                u"crosstab.\n\n"
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
        self.slidingWindowBox = OWGUI.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        OWGUI.separator(widget=self.slidingWindowBox, height=3)
        self.windowSizeSpin = OWGUI.spin(
            widget=self.slidingWindowBox,
            master=self,
            value='windowSize',
            min=1,
            max=1,
            step=1,
            orientation='horizontal',
            label=u'Window size:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The length of segment sequences defining contexts."
            ),
        )
        self.containingSegmentationBox = OWGUI.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        OWGUI.separator(widget=self.containingSegmentationBox, height=3)
        self.contextSegmentationCombo = OWGUI.comboBox(
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
        OWGUI.separator(widget=self.containingSegmentationBox, height=3)
        self.contextAnnotationCombo = OWGUI.comboBox(
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
        OWGUI.separator(widget=self.containingSegmentationBox, height=3)
        OWGUI.checkBox(
            widget=self.containingSegmentationBox,
            master=self,
            value='mergeContexts',
            label=u'Merge contexts',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box if you want to treat all segments\n"
                u"of the above specified segmentation as forming\n"
                u"a single context (hence the resulting crosstab\n"
                u"contains a single row)."
            ),
        )
        OWGUI.separator(widget=self.contextsBox, height=3)

        # Resampling box...
        self.resamplingBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Resampling',
            orientation='vertical',
            addSpace=True,
        )
        applyResamplingCheckBox = OWGUI.checkBox(
            widget=self.resamplingBox,
            master=self,
            value='applyResampling',
            label=u'Apply Resampling',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box if you want to compute the average\n"
                u"variety per subsample."
            ),
        )
        OWGUI.separator(widget=self.resamplingBox, height=3)
        iBox2 = OWGUI.indentedBox(
            widget=self.resamplingBox,
        )
        self.subsampleSizeSpin = OWGUI.spin(
            widget=iBox2,
            master=self,
            value='subsampleSize',
            min=1,
            max=1,
            step=1,
            orientation='horizontal',
            label=u'Subsample size:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The number of segments per subsample."
            ),
        )
        OWGUI.separator(widget=iBox2, height=3)
        self.numSubsampleSpin = OWGUI.spin(
            widget=iBox2,
            master=self,
            value='numSubsamples',
            min=1,
            max=100000,
            step=1,
            orientation='horizontal',
            label=u'Number of subsamples:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The number of subsamples (per context)."
            ),
        )
        applyResamplingCheckBox.disables.append(iBox2)
        if self.applyResampling:
            iBox2.setDisabled(False)
        else:
            iBox2.setDisabled(True)
        OWGUI.separator(widget=self.resamplingBox, height=3)

        OWGUI.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    def inputData(self, newItem, newId=None):
        """Process incoming data."""
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
            if self.units < 0:
                self.units = None
        if self.mode == u'Containing segmentation':
            if index == self._contexts:
                self.mode = u'No context'
                self._contexts = None
            elif index < self._contexts:
                self._contexts -= 1
                if self._contexts < 0:
                    self.mode = u'No context'
                    self._contexts = None

    def sendData(self):

        """Check input, compute variety, then send table"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Textable Table', None)
            return

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
        }
        if categories['annotation_key'] == u'(none)':
            categories['annotation_key'] = None

        # Case 1: sliding window...
        if self.mode == 'Sliding window':

            num_iterations = len(units['segmentation']) - (self.windowSize - 1)
            if self.applyResampling:
                num_iterations += num_iterations * self.numSubsamples
            else:
                num_iterations *= 2

            # Measure...
            progressBar = OWGUI.ProgressBar(
                self,
                iterations=num_iterations
            )
            table = Processor.variety_in_window(
                units,
                categories,
                measure_per_category=self.measurePerCategory,
                window_size=self.windowSize,
                apply_resampling=self.applyResampling,
                subsample_size=self.subsampleSize,
                num_subsamples=self.numSubsamples,
                progress_callback=progressBar.advance,
            )
            progressBar.finish()

        # Case 2: Containing segmentation or no context...
        else:

            # Parameters for mode 'Containing segmentation'...
            if self.mode == 'Containing segmentation':
                contexts = {
                    'segmentation': self.segmentations[self._contexts][1],
                    'annotation_key': self.contextAnnotationKey or None,
                    'merge': self.mergeContexts,
                }
                if contexts['annotation_key'] == u'(none)':
                    contexts['annotation_key'] = None
                num_contexts = len(contexts['segmentation'])
                num_iterations = num_contexts
            # Parameters for mode 'No context'...
            else:
                contexts = None
                num_iterations = (
                    len(units['segmentation']) - (self.sequenceLength - 1)
                )
                num_contexts = 1
            if self.applyResampling:
                num_iterations += num_contexts * self.numSubsamples
            else:
                num_iterations += num_contexts

            # Measure...
            progressBar = OWGUI.ProgressBar(
                self,
                iterations=num_iterations
            )
            table = Processor.variety_in_context(
                units,
                categories,
                contexts,
                measure_per_category=self.measurePerCategory,
                apply_resampling=self.applyResampling,
                subsample_size=self.subsampleSize,
                num_subsamples=self.numSubsamples,
                progress_callback=progressBar.advance,
            )
            progressBar.finish()

        if not len(table.row_ids):
            self.infoBox.setText(u'Resulting table is empty.', 'warning')
            self.send('Textable Table', None)
        else:
            self.infoBox.setText(u'Table sent to output.')
            self.send('Textable Table', table)

        self.sendButton.resetSettingsChangedFlag()

    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')
        self.categoryAnnotationCombo.clear()
        self.categoryAnnotationCombo.addItem(u'(none)')

        if self.mode == u'No context':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(False)

        if len(self.segmentations) == 0:
            self.units = None
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
            self.categoryAnnotationKey = u''
            self.categoriesBox.setDisabled(True)
            self.mode = 'No context'
            self.contextsBox.setDisabled(True)
            self.adjustSize()
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
            for segmentation in self.segmentations:
                self.unitSegmentationCombo.addItem(segmentation[1].label)
            self.units = self.units
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
            self.sequenceLengthSpin.control.setRange(
                1,
                len(self.segmentations[self.units][1])
            )
            self.sequenceLength = self.sequenceLength or 1
            if self.sequenceLength > 1:
                self.categoriesBox.setDisabled(True)
            else:
                self.categoriesBox.setDisabled(False)
            if self.measurePerCategory:
                self.sequenceLengthSpin.setDisabled(True)
            else:
                self.sequenceLengthSpin.setDisabled(False)
            self.contextsBox.setDisabled(False)
            self.subsampleSizeSpin.control.setRange(
                1,
                len(self.segmentations[self.units][1])
            )
            self.subsampleSize = self.subsampleSize or 1

        if self.mode == u'Sliding window':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)

            self.windowSizeSpin.control.setRange(
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
            self._contexts = self._contexts or 0
            segmentation = self.segmentations[self._contexts]
            self.contextAnnotationCombo.clear()
            self.contextAnnotationCombo.addItem(u'(none)')
            contextAnnotationKeys = segmentation[1].get_annotation_keys()
            for key in contextAnnotationKeys:
                self.contextAnnotationCombo.addItem(key)
            if self.contextAnnotationKey not in contextAnnotationKeys:
                self.contextAnnotationKey = u'(none)'
            self.contextAnnotationKey = self.contextAnnotationKey

        self.adjustSizeWithTimer()

    def adjustSizeWithTimer(self):
        qApp.processEvents()
        QTimer.singleShot(50, self.adjustSize)

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext("", self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()

    def getSettings(self, *args, **kwargs):
        settings = OWWidget.getSettings(self, *args, **kwargs)
        settings["settingsDataVersion"] = __version__.split('.')[:2]
        return settings

    def setSettings(self, settings):
        if settings.get("settingsDataVersion", None) \
                == __version__.split('.')[:2]:
            settings = settings.copy()
            del settings["settingsDataVersion"]
            OWWidget.setSettings(self, settings)


if __name__ == '__main__':
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
