#=============================================================================
# Class OWTextableContext, v0.03
# Copyright 2012-2013 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the Textable (v1.3) extension to Orange Canvas.
#
# Textable v1.3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Textable v1.3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Textable v1.3. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

"""
<name>Context</name>
<description>Explore the context of segments</description>
<icon>icons/Context.png</icon>
<priority>8000</priority>
"""

from LTTL.Table        import Table
from LTTL.Processor    import Processor
from LTTL.Segmentation import Segmentation

from TextableUtils      import *

import Orange
from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableContext(OWWidget):

    """Orange widget for building concordances and studying collocations"""

    settingsList = [
            'autoSend',
            'mode',
            'separateAnnotation',
            'applyMaxLength',
            'maxLength',
            'applyMaxDistance',
            'maxDistance',
            'minFrequency',
            'useCollocationFormat',
            'savedUnitSenderUuid',
            'savedUnitAnnotationKey',
            'savedContextSenderUuid',
            'savedContextAnnotationKey',
    ]

    def __init__(self, parent=None, signalManager=None):
        
        """Initialize a Context widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                'TextableContext',
                wantMainArea=0,
        )
        
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [('Textable Table', Table)]
        
        # Settings...
        self.autoSend                   = False
        self.mode                       = u'Neighboring segments'
        self.separateAnnotation         = False
        self.maxLength                  = 25
        self.maxDistance                = 10
        self.minFrequency               = 1
        self.applyMaxLength             = True
        self.applyMaxDistance           = True
        self.useCollocationFormat       = False
        self.savedUnitSenderUuid        = None
        self.savedUnitAnnotationKey     = None
        self.savedContextSenderUuid     = None
        self.savedContextAnnotationKey  = None
        self.loadSettings()

        # Other attributes...
        self.processor              = Processor()
        self.segmentations          = []
        self.units                  = None
        self.unitAnnotationKey      = None
        self.contexts               = None
        self.contextAnnotationKey   = None
        self.settingsRestored       = False
        self.infoBox                = InfoBox(
                widget          = self.controlArea,
                stringClickSend = u"Please click 'Compute' when ready.",
        )
        self.sendButton             = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
                buttonLabel         = u'Compute',
                checkboxLabel       = u'Compute automatically',
                sendIfPreCallback   = self.updateGUI,
        )

        # GUI...

        # Units box
        self.unitsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Units',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.unitSegmentationCombo = OWGUI.comboBox(
                widget              = self.unitsBox,
                master              = self,
                value               = 'units',
                orientation         = 'horizontal',
                label               = u'Segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation that will be used to specify\n"
                        u"'pivot' segments."
                ),
        )
        self.unitSegmentationCombo.setMinimumWidth(120)
        OWGUI.separator(
                widget              = self.unitsBox,
                height              = 3,
        )

        self.unitsSubBox = OWGUI.widgetBox(
                widget              = self.unitsBox,
                orientation         = 'vertical',
        )
        self.unitAnnotationCombo = OWGUI.comboBox(
                widget              = self.unitsSubBox,
                master              = self,
                value               = 'unitAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether somme annotation value must\n"
                        u"be displayed in place of (or in addition to) the\n"
                        u"content of segments in the above specified\n"
                        u"segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.unitsSubBox,
                height              = 3,
        )
        self.separateAnnotationCheckBox = OWGUI.checkBox(
                widget              = self.unitsSubBox,
                master              = self,
                value               = 'separateAnnotation',
                label               = u'Separate annotation',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Check this box in order to display the annotation\n"
                        u"of pivot segments in a separate column rather\n"
                        u"than in place of pivot segment content."
                ),
        )

        # Contexts box...
        self.contextsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Contexts',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.modeCombo = OWGUI.comboBox(
                widget              = self.contextsBox,
                master              = self,
                value               = 'mode',
                sendSelectedValue   = True,
                items               = [
                        u'Neighboring segments',
                        u'Containing segmentation',
                ],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Context specification mode.\n\n"
                        u"'Neighboring segments': context will consist\n"
                        u"of entire segments to the left and right of pivot\n"
                        u"segments (hence the output table possibly\n"
                        u"contains a large number of columns, depending on\n"
                        u"the 'maximum distance' parameter.\n\n"
                        u"'Containing segmentation': contexts are defined\n"
                        u"as the characters occurring immediately to the\n"
                        u"left and right of pivot segments (hence the\n"
                        u"output table usually contains 3 columns)."
                ),
        )
        OWGUI.separator(
                widget              = self.contextsBox,
                height              = 3,
        )
        self.contextSegmentationCombo = OWGUI.comboBox(
                widget              = self.contextsBox,
                master              = self,
                value               = 'contexts',
                orientation         = 'horizontal',
                label               = u'Segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation on which the context definition\n"
                        u"is based."
                ),
        )
        OWGUI.separator(
                widget              = self.contextsBox,
                height              = 3,
        )
        self.contextAnnotationCombo = OWGUI.comboBox(
                widget              = self.contextsBox,
                master              = self,
                value               = 'contextAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"In 'Neighboring segments' mode, indicate whether\n"
                        u"the content of context segments should be\n"
                        u"displayed (value 'none') or rather their\n"
                        u"annotation value for a specific annotation key.\n\n"
                        u"In 'Containing segmentation' mode, indicate\n"
                        u"whether an annotation value of context segments\n"
                        u"should be displayed in a separate column."
                ),
        )
        self.neighboringSegmentsBox = OWGUI.widgetBox(
                widget              = self.contextsBox,
                orientation         = 'vertical',
        )
        OWGUI.separator(
                widget              = self.neighboringSegmentsBox,
                height              = 3,
        )
        self.maxDistanceLine = OWGUI.widgetBox(
                widget              = self.neighboringSegmentsBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        self.maxDistanceSpin = OWGUI.checkWithSpin(
                widget              = self.maxDistanceLine,
                master              = self,
                value               = 'maxDistance',
                label               = u'Max. distance:',
                labelWidth          = 180,
                controlWidth        = None,
                checked             = 'applyMaxDistance',
                min                 = 1,
                max                 = 100,
                spinCallback        = self.sendButton.settingsChanged,
                checkCallback       = self.sendButton.settingsChanged,
                tooltip             = (
                      u"Maximal distance between pivot and context segments."
                ),
        )
        OWGUI.separator(
                widget              = self.neighboringSegmentsBox,
                height              = 3,
        )
        self.useCollocationFormatCheckbox = OWGUI.checkBox(
                widget              = self.neighboringSegmentsBox,
                master              = self,
                value               = 'useCollocationFormat',
                label               = u'Use collocation format',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Check this box in order to view the pivot's\n"
                        u"collocates rather than its contexts of\n"
                        u"occurrence."
                ),
        )
        OWGUI.separator(
                widget              = self.neighboringSegmentsBox,
                height              = 3,
        )
        iBox = OWGUI.indentedBox(
                widget              = self.neighboringSegmentsBox,
        )
        self.minFrequencySpin = OWGUI.spin(
                widget              = iBox,
                master              = self,
                value               = 'minFrequency',
                min                 = 1,
                max                 = 1,
                step                = 1,
                orientation         = 'horizontal',
                label               = u'Min. frequency:',
                labelWidth          = 160,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The minimum frequency of context segment types."
                ),
        )
        self.containingSegmentationBox = OWGUI.widgetBox(
                widget              = self.contextsBox,
                orientation         = 'vertical',
        )
        OWGUI.separator(
                widget              = self.containingSegmentationBox,
                height              = 3,
        )
        self.maxLengthLine = OWGUI.widgetBox(
                widget              = self.containingSegmentationBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        self.maxLengthSpin = OWGUI.checkWithSpin(
                widget              = self.maxLengthLine,
                master              = self,
                value               = 'maxLength',
                label               = u'Max. length:',
                labelWidth          = 180,
                controlWidth        = None,
                checked             = 'applyMaxLength',
                min                 = 1,
                max                 = 100,
                spinCallback        = self.sendButton.settingsChanged,
                checkCallback       = self.sendButton.settingsChanged,
                tooltip             = (
                      u"Maximal number of characters in immediate left\n"
                      u"and right contexts."
                ),
        )
        OWGUI.separator(
                widget              = self.contextsBox,
                height              = 3,
        )

        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()

        self.sendButton.sendIf()



    def inputData(self, newItem, newId=None):
        """Process incoming data."""
        updateMultipleInputs(
                self.segmentations,
                newItem,
                newId,
                self.onInputRemoval
        )
        self.infoBox.inputChanged()
        self.sendButton.sendIf()


    def onInputRemoval(self, index):
        """Handle removal of input with given index"""
        if index < self.units:
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations)-1:
            self.units -= 1
            if self.units < 0:
                self.units = None
        if index < self.contexts:
            self.contexts -= 1
        elif index == self.contexts \
             and self.contexts == len(self.segmentations)-1:
            self.contexts -= 1
            if self.contexts < 0:
                self.contexts = None


    def sendData(self):

        """Check input, compute variety, then send table"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.noDataSent(u'No input.')
            self.send('Textable Table', None)
            return

        progressBar = OWGUI.ProgressBar(
                self,
                iterations = len(self.segmentations[self.contexts][1]),
        )

        # Case 1: Neighboring segments...
        if self.mode == u'Neighboring segments':

            # Contexts parameter...
            contexts = {
                'segmentation':     self.segmentations[self.contexts][1],
                'annotation_key':   self.contextAnnotationKey or None,
            }
            if contexts['annotation_key'] == u'(none)':
                contexts['annotation_key'] = None
            if self.applyMaxDistance:
                contexts['max_distance'] = self.maxDistance
                
            # Case 1a: Concordance format...
            if not self.useCollocationFormat:

                # Units parameter...
                units = {
                    'segmentation':         self.segmentations[self.units][1],
                    'annotation_key':       self.unitAnnotationKey or None,
                    'separate_annotation':  self.separateAnnotation,
                }
                if units['annotation_key'] == u'(none)':
                    units['annotation_key'] = None
                    
                # Process...
                table = self.processor.neighbors(
                        units,
                        contexts,
                        progress_callback = progressBar.advance,
                )
                progressBar.finish()

            # Case 1b: Collocation format...
            else:

                # Units parameter...
                units = self.segmentations[self.units][1]
                
                # Contexts parameter...
                contexts['min_frequency'] = self.minFrequency
                
                # Process...
                table = self.processor.collocations(
                        units,
                        contexts,
                        progress_callback = progressBar.advance,
                )
                progressBar.finish()

        # Case 2: Containing segmentation...
        else:

            # Units parameter...
            units = {
                'segmentation':         self.segmentations[self.units][1],
                'annotation_key':       self.unitAnnotationKey or None,
                'separate_annotation':  self.separateAnnotation,
            }
            if units['annotation_key'] == u'(none)':
                units['annotation_key'] = None

            # Parameters for mode 'Containing segmentation'...
            if self.mode == 'Containing segmentation':
                contexts = {
                    'segmentation':     self.segmentations[self.contexts][1],
                    'annotation_key':   self.contextAnnotationKey or None,
                    'max_num_chars':    self.maxLength,
                }
            if contexts['annotation_key'] == u'(none)':
                contexts['annotation_key'] = None
            if not self.applyMaxLength:
                contexts['max_num_chars'] = None

            # Process...
            table = self.processor.context(
                    units,
                    contexts,
                    progress_callback = progressBar.advance,
            )
            progressBar.finish()

        if not len(table.row_ids):
            self.infoBox.noDataSent(u'Resulting table is empty.')
            self.send('Textable Table', None)
        else:
            self.send('Textable Table', table)
            self.infoBox.dataSent()

        self.sendButton.resetSettingsChangedFlag()


    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')
        self.contextSegmentationCombo.clear()
        self.contextAnnotationCombo.clear()
        self.contextAnnotationCombo.addItem(u'(none)')

        if len(self.segmentations) == 0:
            self.units                  = None
            self.unitAnnotationKey      = u''
            self.unitsBox.setDisabled(True)
            self.contextsBox.setDisabled(True)
            self.adjustSize()
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
                self.contexts = 0
            for segmentation in self.segmentations:
                self.unitSegmentationCombo.addItem(segmentation[1].label)
            self.units = self.units
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
            self.contexts = self.contexts or 0
            self.contextsBox.setDisabled(False)
            segmentation = self.segmentations[self.contexts][1]
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
                    self.maxDistance = (self.maxDistance or len(segmentation))
                    self.maxDistanceSpin[1].setRange(
                            1,
                            len(segmentation),
                    )
                if self.useCollocationFormat:
                    self.unitsSubBox.setDisabled(True)
                    self.minFrequencySpin.control.setRange(
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

        self.adjustSize()



    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.restoreSettings()

    def getSettings(self, alsoContexts = True, globalContexts=False):
        """Overridden: called when a file is saved (among other situations)"""
        self.storeSettings()
        return super(type(self), self).getSettings(
                alsoContexts = True, globalContexts=False
        )

    def restoreSettings(self):
        """When a scheme file is opened, restore those settings that depend
        on the particular segmentations that enter this widget.
        """
        if not self.settingsRestored:
            self.settingsRestored = True
            for segIndex in xrange(len(self.segmentations)):
                segmentation = self.segmentations[segIndex]
                if segmentation[0][0].uuid == self.savedUnitSenderUuid:
                    self.units = segIndex
                if segmentation[0][0].uuid == self.savedContextSenderUuid:
                    self.contexts = segIndex
            self.updateGUI()
            if self.units is not None:
                segmentation       = self.segmentations[self.units]
                unitAnnotationKeys = [u'(none)']
                unitAnnotationKeys.extend(segmentation[1].get_annotation_keys())
                for key in unitAnnotationKeys:
                    if key == self.savedUnitAnnotationKey:
                        self.unitAnnotationKey = key
            if self.contexts is not None:
                segmentation          = self.segmentations[self.contexts]
                contextAnnotationKeys = [u'(none)']
                contextAnnotationKeys.extend(
                        segmentation[1].get_annotation_keys()
                )
                for key in contextAnnotationKeys:
                    if key == self.savedContextAnnotationKey:
                        self.contextAnnotationKey = key
                        break
            self.sendButton.sendIf()

    def storeSettings(self):
        """When a scheme file is saved, store those settings that depend
        on the particular segmentations that enter this widget.
        """
        if self.settingsRestored:
            if self.units is not None:
                segmentation                = self.segmentations[self.units]
                self.savedUnitSenderUuid    = segmentation[0][0].uuid
                self.savedUnitAnnotationKey = self.unitAnnotationKey
            else:
                self.savedUnitSenderUuid    = None
                self.savedUnitAnnotationKey = None
            if self.contexts is not None:
                segmentation = self.segmentations[self.contexts]
                self.savedContextSenderUuid    = segmentation[0][0].uuid
                self.savedContextAnnotationKey = self.contextAnnotationKey
            else:
                self.savedContextSenderUuid    = None
                self.savedContextAnnotationKey = None



if __name__ == '__main__':
    from LTTL.Segmenter import Segmenter
    from LTTL.Input     import Input
    appl = QApplication(sys.argv)
    ow   = OWTextableContext()
    seg1 = Input(u'hello world', 'text')
    segmenter = Segmenter()
    seg2 = segmenter.tokenize(
        seg1,
        [
            (re.compile(r'hello'), u'Tokenize', {'tag': 'interj'}),
            (re.compile(r'world'), u'Tokenize', {'tag': 'noun'}),
        ],
        label = 'words',
    )
    seg3 = segmenter.tokenize(
        seg2,
        [(re.compile(r'[aeiou]'), u'Tokenize')],
        label = 'V'
    )
    seg4 = segmenter.tokenize(
        seg2,
        [(re.compile(r'[hlwrdc]'), u'Tokenize')],
        label = 'C'
    )
    seg5 = segmenter.tokenize(
        seg2,
        [(re.compile(r' '), u'Tokenize')],
        label = 'S'
    )
    seg6 = segmenter.concatenate(
        [seg3, seg4, seg5],
        import_labels_as    = 'category',
        label               = 'chars',
        sort                = True,
        merge_duplicates    = True,
    )
    seg7 = segmenter.tokenize(
        seg6,
        [(re.compile(r'l'), u'Tokenize')],
        label               = 'pivot'
    )
    ow.inputData(seg2, 1)
    ow.inputData(seg6, 2)
    ow.inputData(seg7, 3)
    ow.show()
    appl.exec_()
    ow.saveSettings()
