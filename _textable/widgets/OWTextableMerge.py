"""
Class OWTextableMerge
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

__version__ = '0.20.2'      # TODO change subversion?

"""
<name>Merge</name>
<description>Merge two or more segmentations</description>
<icon>icons/Merge.png</icon>
<priority>4001</priority>
"""

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter

from TextableUtils import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI


class OWTextableMerge(OWWidget):
    """Orange widget for merging segmentations"""

    settingsList = [
        'autoSend',
        'copyAnnotations',
        'importLabels',
        'labelKey',
        'autoNumber',
        'autoNumberKey',
        'mergeDuplicates',
        'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):

        OWWidget.__init__(
            self,
            parent,
            signalManager,
            wantMainArea=0,
            wantStateInfoWidget=0,
        )

        # Input and output channels...
        self.inputs = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [('Merged data', Segmentation)]

        # Settings...
        self.autoSend = True
        self.importLabels = True
        self.labelKey = u'input_label'     # TODO update docs
        self.autoNumber = False
        self.autoNumberKey = u'num'
        self.copyAnnotations = True
        self.mergeDuplicates = False
        self.savedSenderUuidOrder = list()
        self.uuid = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.texts = list();
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Options box...
        optionsBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
        )
        optionsBoxLine1 = OWGUI.widgetBox(
            widget=optionsBox,
            box=False,
            orientation='horizontal',
        )
        OWGUI.checkBox(
            widget=optionsBoxLine1,
            master=self,
            value='importLabels',
            label=u'Import labels with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import labels of input segmentations as annotations."
            ),
        )
        self.labelKeyLineEdit = OWGUI.lineEdit(
            widget=optionsBoxLine1,
            master=self,
            value='labelKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for importing input segmentation\n"
                u"labels."
            ),
        )
        OWGUI.separator(widget=optionsBox, height=3)
        optionsBoxLine2 = OWGUI.widgetBox(
            widget=optionsBox,
            box=False,
            orientation='horizontal',
        )
        OWGUI.checkBox(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumber',
            label=u'Auto-number with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotate input segments with increasing numeric\n"
                u"indices\n\n"
                u"Note that a distinct index will be assigned to\n"
                u"each segment of each input segmentation."
            ),
        )
        self.autoNumberKeyLineEdit = OWGUI.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for input segment auto-numbering."
            ),
        )
        OWGUI.separator(widget=optionsBox, height=3)
        OWGUI.checkBox(
            widget=optionsBox,
            master=self,
            value='copyAnnotations',
            label=u'Copy annotations',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Copy all annotations from input to output segments."
            ),
        )
        OWGUI.separator(widget=optionsBox, height=3)
        OWGUI.checkBox(
            widget=optionsBox,
            master=self,
            value='mergeDuplicates',
            label=u'Fuse duplicates',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Fuse segments that have the same address.\n\n"
                u"The annotation of merged segments will be fused\n"
                u"as well. In the case where fused segments have\n"
                u"distinct values for the same annotation key, only\n"
                u"the value of the last one (in address order)\n"
                u"will be kept."
            ),
        )
        OWGUI.separator(widget=optionsBox, height=2)
        OWGUI.separator(widget=self.controlArea, height=3)

        OWGUI.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    def sendData(self):

        """Check inputs, build merged segmentation, then send it"""

        # Check that there's something on input...
        if not self.texts:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Merged data', None, self)
            return

        # TODO: remove message 'No label was provided.' from docs

        # Extract segmentations from self.texts and get number of segments...
        segmentations = [text[1] for text in self.texts]
        num_segments = sum([len(s) for s in segmentations])

        # Check that labelKey is not empty (if necessary)...
        if self.importLabels:
            if self.labelKey:
                labelKey = self.labelKey
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for imported labels.',
                    'warning'
                )
                self.send('Merged data', None, self)
                return
        else:
            labelKey = None

        # Check that autoNumberKey is not empty (if necessary)...
        if self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for auto-numbering.',
                    'warning'
                )
                self.send('Merged data', None, self)
                return
        else:
            autoNumberKey = None

        # Initialize progress bar...
        progressBar = OWGUI.ProgressBar(
            self,
            iterations=num_segments
        )

        # Perform concatenation.
        concatenation = Segmenter.concatenate(
            segmentations,
            label=self.captionTitle,
            copy_annotations=self.copyAnnotations,
            import_labels_as=labelKey,
            sort=True,
            auto_number_as=autoNumberKey,
            merge_duplicates=self.mergeDuplicates,
            progress_callback=progressBar.advance,
        )
        progressBar.finish()
        message = u'%i segment@p sent to output.' % len(concatenation)
        message = pluralize(message, len(concatenation))
        self.infoBox.setText(message)

        self.send('Merged data', concatenation, self)
        self.sendButton.resetSettingsChangedFlag()

    def inputData(self, newItem, newId=None):
        """Process incoming data."""
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
        self.adjustSizeWithTimer()

    def adjustSizeWithTimer(self):
        qApp.processEvents()
        QTimer.singleShot(50, self.adjustSize)

    def setCaption(self, title):
        if 'captionTitle' in dir(self) and title != 'Orange Widget':
            OWWidget.setCaption(self, title)
            self.sendButton.settingsChanged()
        else:
            OWWidget.setCaption(self, title)

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
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
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableMerge()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'cruel world', label=u'text2')
    seg3 = Segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = Segmenter.tokenize(seg3,
                              [(r'\w+(?u)', u'tokenize', {'type': 'mot'})],
                              label=u'words')
    ow.inputData(seg3, 1)
    ow.inputData(seg4, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
    QMessageBox()
