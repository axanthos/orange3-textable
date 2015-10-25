#=============================================================================
# Class OWTextableMerge
# Copyright 2012-2015 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the Textable (v1.5) extension to Orange Canvas.
#
# Textable v1.5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Textable v1.5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Textable v1.5. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

__version__ = '0.20.1'

"""
<name>Merge</name>
<description>Merge two or more segmentations</description>
<icon>icons/Merge.png</icon>
<priority>4001</priority>
"""

from LTTL.Segmentation import Segmentation
from LTTL.Input        import Input
from LTTL.Segmenter    import Segmenter

from TextableUtils      import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI


class OWTextableMerge(OWWidget):

    """Orange widget for merging segmentations"""
    
    contextHandlers = {
        "": SegmentationListContextHandler(
            "", [
                ContextInputListField("texts"),
                ContextListField("textLabels", selected="selectedTextLabels")
            ],
        )
    }

    settingsList = [
            'autoSend',
            'copyAnnotations',
            'label',
            'importLabels',
            'labelKey',
            'autoNumber',
            'autoNumberKey',
            'sortSegments',
            'mergeDuplicates',
            'displayAdvancedSettings',
            'uuid',
    ]
    
    def __init__(self, parent=None, signalManager=None):

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )
        
        # Input and output channels...
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [('Merged data', Segmentation)]

        # Settings...
        self.autoSend                   = True
        self.label                      = u'merged_data'
        self.importLabels               = True
        self.labelKey                   = u'component_labels'
        self.autoNumber                 = False
        self.autoNumberKey              = u'num'
        self.copyAnnotations            = True
        self.sortSegments               = False
        self.mergeDuplicates            = False
        self.displayAdvancedSettings    = False
        self.savedSenderUuidOrder       = []
        self.uuid                       = None
        self.loadSettings()
        self.uuid                       = getWidgetUuid(self)

        # Other attributes...
        self.segmenter              = Segmenter();
        self.texts                  = [];
        self.textLabels             = [];
        self.selectedTextLabels     = [];
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

        # Ordering box
        orderingBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Ordering',
                orientation         = 'vertical',
                addSpace            = True,
        )
        orderingBoxLine1 = OWGUI.widgetBox(
                widget              = orderingBox,
                orientation         = 'horizontal',
        )
        self.textListbox = OWGUI.listBox(
                widget              = orderingBoxLine1,
                master              = self,
                value               = 'selectedTextLabels',
                labels              = 'textLabels',
                callback            = self.updateGUI,
                tooltip             = (
                        u"List of segmentations that will be merged\n\n"
                        u"By default, segments of the input segmentations\n"
                        u"appear in the same order in the output segmentation"
                        u"\nas in the list (see 'Sort segments' below)."
                ),
        )
        orderingBoxCol2 = OWGUI.widgetBox(
                widget              = orderingBoxLine1,
                orientation         = 'vertical',
        )
        self.moveUpButton = OWGUI.button(
                widget              = orderingBoxCol2,
                master              = self,
                label               = u'Move Up',
                callback            = self.moveUp,
                tooltip             = (
                        u"Move the selected segmentation upward in the list."
                ),
        )
        self.moveDownButton = OWGUI.button(
                widget              = orderingBoxCol2,
                master              = self,
                label               = u'Move Down',
                callback            = self.moveDown,
                tooltip             = (
                       u"Move the selected segmentation downward in the list."
                ),
        )
        OWGUI.separator(
                widget              = orderingBox,
                height              = 3,
        )

        # Advanced Options box...
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
                labelWidth          = 160,
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
                value               = 'importLabels',
                label               = u'Import labels with key:',
                labelWidth          = 160,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                       u"Import labels of input segmentations as annotations."
                ),
        )
        self.labelKeyLineEdit = OWGUI.lineEdit(
                widget              = optionsBoxLine2,
                master              = self,
                value               = 'labelKey',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotation key for importing input segmentation\n"
                        u"labels."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        optionsBoxLine3 = OWGUI.widgetBox(
                widget              = optionsBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = optionsBoxLine3,
                master              = self,
                value               = 'autoNumber',
                label               = u'Auto-number with key:',
                labelWidth          = 160,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotate input segments with increasing numeric\n"
                        u"indices\n\n"
                        u"Note that a distinct index will be assigned to\n"
                        u"each segment of each input segmentation."
                ),
        )
        self.autoNumberKeyLineEdit = OWGUI.lineEdit(
                widget              = optionsBoxLine3,
                master              = self,
                value               = 'autoNumberKey',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotation key for input segment auto-numbering."
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
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = optionsBox,
                master              = self,
                value               = 'sortSegments',
                label               = u'Sort segments',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Re-order segments in the output segmentation.\n\n"
                        u"Output segments will be sorted by 'string_index',\n"
                        u"then by start position, and finally by end position."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = optionsBox,
                master              = self,
                value               = 'mergeDuplicates',
                label               = u'Fuse duplicates',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Fuse segments that have the same address.\n\n"
                        u"The annotation of merged segments will be fused\n"
                        u"as well. In the case where fused segments have\n"
                        u"distinct values for the same annotation key, only\n"
                        u"the value of the last one (in the list order)\n"
                        u"will be kept."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Basic Options box...
        basicOptionsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Options',
                orientation         = 'vertical',
        )
        OWGUI.lineEdit(
                widget              = basicOptionsBox,
                master              = self,
                value               = 'label',
                orientation         = 'horizontal',
                label               = u'Output segmentation label:',
                labelWidth          = 160,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Label of the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = basicOptionsBox,
                height              = 3,
        )
        basicOptionsBoxLine2 = OWGUI.widgetBox(
                widget              = basicOptionsBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = basicOptionsBoxLine2,
                master              = self,
                value               = 'importLabels',
                label               = u'Import labels with key:',
                labelWidth          = 160,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                       u"Import labels of input segmentations as annotations."
                ),
        )
        self.labelKeyLineEdit = OWGUI.lineEdit(
                widget              = basicOptionsBoxLine2,
                master              = self,
                value               = 'labelKey',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotation key for importing input segmentation\n"
                        u"labels."
                ),
        )
        OWGUI.separator(
                widget              = basicOptionsBox,
                height              = 3,
        )
        self.advancedSettings.basicWidgets.append(basicOptionsBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()

        self.updateGUI()

        self.sendButton.sendIf()


    def sendData(self):

        """Check inputs, build merged segmentation, then send it"""

        # Check that there's something on input...
        if not self.texts:
            self.infoBox.noDataSent(u': no input segmentation.')
            self.send('Merged data', None, self)
            return

        # Extract segmentations from self.texts and get number of segments...
        segmentations = [text[1] for text in self.texts]
        num_segments  = sum([len(s) for s in segmentations])

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(warning = u'No label was provided.')
            self.send('Merged data', None, self)
            return

        # Check that labelKey is not empty (if necessary)...
        if self.importLabels:
            if self.labelKey:
                labelKey = self.labelKey
            else:
                self.infoBox.noDataSent(
                        warning = u'No annotation key was provided '
                                  u'for imported labels.'
                )
                self.send('Merged data', None, self)
                return
        else:
            labelKey = None

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
                num_iterations = num_segments * 2
            else:
                self.infoBox.noDataSent(
                        warning = u'No annotation key was provided '
                                  u'for auto-numbering.'
                )
                self.send('Merged data', None, self)
                return
        else:
            autoNumberKey = None
            num_iterations = num_segments

        # Basic settings...
        if self.displayAdvancedSettings:
            sortSegments    = self.sortSegments
            copyAnnotations = self.copyAnnotations
            mergeDuplicates = self.mergeDuplicates
            if mergeDuplicates:
                num_iterations += num_segments
        else:
            sortSegments    = False
            mergeDuplicates = False
            copyAnnotations = True

        # Initialize progress bar...
        if self.mergeDuplicates:
            num_iterations += num_segments
        progressBar = OWGUI.ProgressBar(
                self,
                iterations = num_iterations
        )

        # Perform concatenation.
        concatenation = self.segmenter.concatenate(
            segmentations,
            label               = self.label,
            copy_annotations    = copyAnnotations,
            import_labels_as    = labelKey,
            auto_numbering_as   = autoNumberKey,
            sort                = sortSegments,
            merge_duplicates    = mergeDuplicates,
            progress_callback   = progressBar.advance,
        )
        progressBar.finish()
        message = u'%i segment@p.' % len(concatenation)
        message = pluralize(message, len(concatenation))
        self.infoBox.dataSent(message)

        self.send('Merged data', concatenation, self)
        self.sendButton.resetSettingsChangedFlag()


    def inputData(self, newItem, newId=None):
        """Process incoming data."""
        self.closeContext()
        updateMultipleInputs(self.texts, newItem, newId)
        self.textLabels = [text[1].label for text in self.texts]
        self.infoBox.inputChanged()


    def updateGUI(self):
        """Update GUI state"""
        if self.importLabels:
            self.labelKeyLineEdit.setDisabled(False)
        else:
            self.labelKeyLineEdit.setDisabled(True)
        if self.autoNumber:
            self.autoNumberKeyLineEdit.setDisabled(False)
        else:
            self.autoNumberKeyLineEdit.setDisabled(True)
        if self.selectedTextLabels:
            if self.selectedTextLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedTextLabels[0] < len(self.texts) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)

        if self.displayAdvancedSettings:
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)


    def moveUp(self):
        """Move text upward in Ordering listbox"""
        if self.selectedTextLabels:
            index = self.selectedTextLabels[0]
            if index > 0:
                temp                = self.texts[index-1]
                self.texts[index-1] = self.texts[index]
                self.texts[index]   = temp
                self.textLabels     = [text[1].label for text in self.texts]
                self.selectedTextLabels.listBox.item(index-1).setSelected(1)
                self.sendButton.settingsChanged()


    def moveDown(self):
        """Move text downward in Ordering listbox"""
        if self.selectedTextLabels:
            index = self.selectedTextLabels[0]
            if index < len(self.texts)-1:
                temp                = self.texts[index+1]
                self.texts[index+1] = self.texts[index]
                self.texts[index]   = temp
                self.textLabels     = [text[1].label for text in self.texts]
                self.selectedTextLabels.listBox.item(index+1).setSelected(1)
                self.sendButton.settingsChanged()


    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext("", self.texts)
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
    from LTTL.Segmenter import Segmenter
    from LTTL.Input     import Input
    appl = QApplication(sys.argv)
    ow   = OWTextableMerge()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'cruel world', label=u'text2')
    segmenter = Segmenter()
    seg3 = segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = segmenter.tokenize(seg3, [(r'\w+(?u)',u'tokenize',{'type':'mot'})], label=u'words')
    ow.inputData(seg3, 1)
    ow.inputData(seg4, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
    QMessageBox()
