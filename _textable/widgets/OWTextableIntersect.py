#=============================================================================
# Class OWTextableIntersect, v0.08
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
<name>Intersect</name>
<description>In-/exclude segments based on another segmentation</description>
<icon>icons/Intersect.png</icon>
<priority>4004</priority>
"""

import uuid

from LTTL.Segmenter    import Segmenter
from LTTL.Segmentation import Segmentation

from TextableUtils      import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableIntersect(OWWidget):

    """Orange widget for segment in-/exclusion based on other segmentation"""
    
    settingsList = [
            'mode',
            'copyAnnotations',
            'autoSend',
            'label',
            'autoNumber',
            'autoNumberKey',
            'displayAdvancedSettings',
            'uuid',
            'savedSourceSenderUuid',                                                  
            'savedSourceAnnotationKey',                                               
            'savedFilteringSenderUuid',                                                  
            'savedFilteringAnnotationKey',                                               
    ]

    def __init__(self, parent=None, signalManager=None):

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                'TextableIntersect',
                wantMainArea=0,
        )

        # Input and output channels...
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [
            ('Filtered data', Segmentation, Default),
            ('Discarded data', Segmentation)
        ]
        
        # Settings...
        self.copyAnnotations                = True
        self.autoSend                       = False
        self.label                          = u'filtered_data'
        self.mode                           = u'Include'
        self.autoNumber                     = False
        self.autoNumberKey                  = u'num'
        self.displayAdvancedSettings        = False
        self.uuid                           = uuid.uuid4()
        self.savedSourceSenderUuid          = None                                      
        self.savedSourceAnnotationKey       = None                                      
        self.savedFilteringSenderUuid       = None                                      
        self.savedFilteringAnnotationKey    = None                                      
        self.loadSettings()

        # Other attributes...
        self.segmenter              = Segmenter()
        self.segmentations          = []
        self.source                 = None
        self.sourceAnnotationKey    = None
        self.filtering              = None
        self.filteringAnnotationKey = None
        self.settingsRestored       = False                                         
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

        # Intersect box
        self.intersectBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Intersect',
                orientation         = 'vertical',
        )
        self.modeCombo = OWGUI.comboBox(
                widget              = self.intersectBox,
                master              = self,
                value               = 'mode',
                sendSelectedValue   = True,
                items               = [u'Include', u'Exclude'],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Specify whether source segments whose type is\n"
                        u"present in the filter segmentation should be\n"
                        u"included in or excluded from the output\n"
                        u"segmentation."
                ),
        )
        self.modeCombo.setMinimumWidth(140)
        OWGUI.separator(
                widget              = self.intersectBox,
                height              = 3,
        )
        self.sourceCombo = OWGUI.comboBox(
                widget              = self.intersectBox,
                master              = self,
                value               = 'source',
                orientation         = 'horizontal',
                label               = u'Source segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation from which a subset of segments\n"
                        u"will be selected to build the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.intersectBox,
                height              = 3,
        )
        self.sourceAnnotationCombo = OWGUI.comboBox(
                widget              = self.intersectBox,
                master              = self,
                value               = 'sourceAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Source annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether source segments will be selected\n"
                        u"based on annotation values corresponding to a\n"
                        u"specific annotation key or rather on their content\n"
                        u"(value 'none')."
                ),
        )
        OWGUI.separator(
                widget              = self.intersectBox,
                height              = 3,
        )
        self.filteringCombo = OWGUI.comboBox(
                widget              = self.intersectBox,
                master              = self,
                value               = 'filtering',
                orientation         = 'horizontal',
                label               = u'Filter segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose types will be used to\n"
                        u"include source segments in (or exclude them from)\n"
                        u"the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.intersectBox,
                height              = 3,
        )
        self.filteringAnnotationCombo = OWGUI.comboBox(
                widget              = self.intersectBox,
                master              = self,
                value               = 'filteringAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Filter annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether filter segment types are based\n"
                        u"on annotation values corresponding to a specific\n"
                        u"annotation key or rather on segment content\n"
                        u"(value 'none')."
                ),
        )
        OWGUI.separator(
                widget              = self.intersectBox,
                height              = 3,
        )
        self.advancedSettings.advancedWidgets.append(self.intersectBox)
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
                addSpace            = True,
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

        # Basic intersect box
        self.basicIntersectBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Intersect',
                orientation         = 'vertical',
        )
        self.basicModeCombo = OWGUI.comboBox(
                widget              = self.basicIntersectBox,
                master              = self,
                value               = 'mode',
                sendSelectedValue   = True,
                items               = [u'Include', u'Exclude'],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Specify whether source segments whose type is\n"
                        u"present in the filter segmentation should be\n"
                        u"included in or excluded from the output\n"
                        u"segmentation."
                ),
        )
        self.basicModeCombo.setMinimumWidth(140)
        OWGUI.separator(
                widget              = self.basicIntersectBox,
                height              = 3,
        )
        self.basicSourceCombo = OWGUI.comboBox(
                widget              = self.basicIntersectBox,
                master              = self,
                value               = 'source',
                orientation         = 'horizontal',
                label               = u'Source segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation from which a subset of segments\n"
                        u"will be selected to build the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.basicIntersectBox,
                height              = 3,
        )
        self.basicSourceAnnotationCombo = OWGUI.comboBox(
                widget              = self.basicIntersectBox,
                master              = self,
                value               = 'sourceAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Source annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether source segments will be selected\n"
                        u"based on annotation values corresponding to a\n"
                        u"specific annotation key or rather on their content\n"
                        u"(value 'none')."
                ),
        )
        OWGUI.separator(
                widget              = self.basicIntersectBox,
                height              = 3,
        )
        self.basicFilteringCombo = OWGUI.comboBox(
                widget              = self.basicIntersectBox,
                master              = self,
                value               = 'filtering',
                orientation         = 'horizontal',
                label               = u'Filter segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose types will be used to\n"
                        u"include source segments in (or exclude them from)\n"
                        u"the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = self.basicIntersectBox,
                height              = 3,
        )
        self.advancedSettings.basicWidgets.append(self.basicIntersectBox)
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
    
        """(Have LTTL.Segmenter) perform the actual filtering"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.noDataSent(u'No input.')
            self.send('Filtered data', None)
            return

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(u'No label was provided.')
            self.send('Filtered data', None)
            return

        # Source and filtering parameter...
        source = {'segmentation': self.segmentations[self.source][1]}
        if self.sourceAnnotationKey == u'(none)':
            source['annotation_key'] = None
        filtering = {
                'segmentation':     self.segmentations[self.filtering][1],
        }
        if self.displayAdvancedSettings:
            filtering['annotation_key'] = self.filteringAnnotationKey or None
            if filtering['annotation_key'] == u'(none)':
                filtering['annotation_key'] = None
        else:
            filtering['annotation_key'] = None

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey  = self.autoNumberKey
                num_iterations = 2 * len(source['segmentation'])
            else:
                self.infoBox.noDataSent(
                        u'No annotation key was provided for auto-numbering.'
                )
                self.send('Filtered data', None)
                return
        else:
            autoNumberKey = None
            num_iterations = len(source['segmentation'])

        # Basic settings...
        if self.displayAdvancedSettings:
            copyAnnotations   = self.copyAnnotations
        else:
            copyAnnotations   = True

        # Perform filtering...
        progressBar = OWGUI.ProgressBar(
                self,
                iterations = num_iterations
        )
        (filtered_data, discarded_data) = self.segmenter.intersect(
            source              = source,
            filtering           = filtering,
            mode                = self.mode.lower(),
            label               = self.label,
            copy_annotations    = self.copyAnnotations,
            auto_numbering_as   = autoNumberKey,
            progress_callback   = progressBar.advance,
        )
        progressBar.finish()
        message = u'Data contains %i segment@p.' % len(filtered_data)
        message = pluralize(message, len(filtered_data))
        self.infoBox.dataSent(message)

        self.send( 'Filtered data', filtered_data )
        self.send( 'Discarded data', discarded_data )
        self.sendButton.resetSettingsChangedFlag()


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
        if index < self.source:
            self.source -= 1
        elif        index == self.source \
                and self.source == len(self.segmentations)-1:
            self.source -= 1
            if self.source < 0:
                self.source = None
        if index < self.filtering:
            self.filtering -= 1
        elif        index == self.filtering \
                and self.filtering == len(self.segmentations)-1:
            self.filtering -= 1
            if self.filtering < 0:
                self.filtering = None


    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            sourceCombo                 = self.sourceCombo
            filteringCombo              = self.filteringCombo
            intersectBox                = self.intersectBox
        else:
            sourceCombo                 = self.basicSourceCombo
            filteringCombo              = self.basicFilteringCombo
            intersectBox                = self.basicIntersectBox
        sourceCombo.clear()
        self.sourceAnnotationCombo.clear()
        self.basicSourceAnnotationCombo.clear()
        self.sourceAnnotationCombo.addItem(u'(none)')
        self.basicSourceAnnotationCombo.addItem(u'(none)')
        self.advancedSettings.setVisible(self.displayAdvancedSettings)
        if len(self.segmentations) == 0:
            self.source                 = None
            self.sourceAnnotationKey    = u''
            intersectBox.setDisabled(True)
            self.adjustSize()
            return
        else:
            if len(self.segmentations) == 1:
                self.source = 0
            for segmentation in self.segmentations:
                sourceCombo.addItem(segmentation[1].label)
            self.source = self.source
            sourceAnnotationKeys \
                    = self.segmentations[self.source][1].get_annotation_keys()
            for k in sourceAnnotationKeys:
                self.sourceAnnotationCombo.addItem(k)
                self.basicSourceAnnotationCombo.addItem(k)
            if self.sourceAnnotationKey not in sourceAnnotationKeys:
                self.sourceAnnotationKey = u'(none)'
            self.sourceAnnotationKey = self.sourceAnnotationKey
            intersectBox.setDisabled(False)
        self.autoNumberKeyLineEdit.setDisabled(not self.autoNumber)
        filteringCombo.clear()
        for index in range(len(self.segmentations)):
            filteringCombo.addItem(self.segmentations[index][1].label)
        self.filtering = self.filtering or 0
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
                if segmentation[0][0].uuid == self.savedSourceSenderUuid:
                    self.source = segIndex
                if segmentation[0][0].uuid == self.savedFilteringSenderUuid:
                    self.filtering = segIndex
            self.updateGUI()
            if self.source is not None:
                segmentation         = self.segmentations[self.source]
                sourceAnnotationKeys = [u'(none)']
                sourceAnnotationKeys.extend(
                        segmentation[1].get_annotation_keys()
                )
                for key in sourceAnnotationKeys:
                    if key == self.savedSourceAnnotationKey:
                        self.sourceAnnotationKey = key
                        break
                if self.displayAdvancedSettings:
                    if self.filtering is not None:
                        segmentation = self.segmentations[self.filtering]
                        filteringAnnotationKeys = [u'(none)']
                        filteringAnnotationKeys.extend(
                                segmentation[1].get_annotation_keys()
                        )
                        for key in filteringAnnotationKeys:
                            if key == self.savedFilteringAnnotationKey:
                                self.filteringAnnotationKey = key
                                break
            self.sendButton.sendIf()

    def storeSettings(self):
        """When a scheme file is saved, store those settings that depend
        on the particular segmentations that enter this widget.
        """
        if self.settingsRestored:
            if self.source is not None:
                segmentation                 = self.segmentations[self.source]
                self.savedSourceSenderUuid   = segmentation[0][0].uuid
                self.savedSourceAnnotationKey = self.sourceAnnotationKey
                segmentation = self.segmentations[self.filtering]
            else:
                self.savedSourceSenderUuid    = None
                self.savedSourceAnnotationKey = None
            if self.filtering is not None:
                self.savedFilteringSenderUuid = segmentation[0][0].uuid
                if self.displayAdvancedSettings:
                    self.savedFilteringAnnotationKey \
                            = self.filteringAnnotationKey
            else:
                self.savedFilteringSenderUuid    = None
                self.savedFilteringAnnotationKey = None



if __name__ == '__main__':
    from LTTL.Segmenter import Segmenter
    from LTTL.Input     import Input
    appl = QApplication(sys.argv)
    ow   = OWTextableIntersect()
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
