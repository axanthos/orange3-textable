"""
Class OWTextablePreprocess
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

__version__ = '0.10.2'  # TODO change subversion?

"""
<name>Preprocess</name>
<description>Basic text preprocessing</description>
<icon>icons/Preprocess.png</icon>
<priority>2001</priority>
"""

import LTTL.Segmenter as Segmenter
from LTTL.Segmentation import Segmentation

from TextableUtils import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI


class OWTextablePreprocess(OWWidget):
    """Orange widget for standard text preprocessing"""

    settingsList = [
        'copyAnnotations',
        'applyCaseTransform',
        'caseTransform',
        'removeAccents',
        'displayAdvancedSettings',
        'autoSend',
        'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Preprocess widget"""

        OWWidget.__init__(
            self,
            parent,
            signalManager,
            wantMainArea=0,
            wantStateInfoWidget=0,
        )

        self.inputs = [('Segmentation', Segmentation, self.inputData, Single)]
        self.outputs = [('Preprocessed data', Segmentation)]

        # Settings...
        self.copyAnnotations = True
        self.applyCaseTransform = False
        self.caseTransform = 'to lower'
        self.removeAccents = False
        self.autoSend = True
        self.displayAdvancedSettings = False
        self.uuid = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.createdInputIndices = list()
        self.segmentation = None
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.sendButton.settingsChanged,
        )

        # GUI...

        # Advanced settings checkbox...
        self.advancedSettings.draw()

        # Preprocessing box
        preprocessingBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Preprocessing',
            orientation='vertical',
            addSpace=True,
        )
        self.preprocessingBoxLine1 = OWGUI.widgetBox(
            widget=preprocessingBox,
            orientation='horizontal',
        )
        OWGUI.checkBox(
            widget=self.preprocessingBoxLine1,
            master=self,
            value='applyCaseTransform',
            label=u'Transform case:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Apply systematic case conversion."
            ),
        )
        self.caseTransformCombo = OWGUI.comboBox(
            widget=self.preprocessingBoxLine1,
            master=self,
            value='caseTransform',
            items=[u'to lower', u'to upper'],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Case conversion mode: to lowercase or uppercase."
            ),
        )
        self.caseTransformCombo.setMinimumWidth(120)
        OWGUI.separator(widget=preprocessingBox, height=3)
        OWGUI.checkBox(
            widget=preprocessingBox,
            master=self,
            value='removeAccents',
            label=u'Remove accents',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Replace accented characters with non-accented ones."
            ),
        )
        OWGUI.separator(widget=preprocessingBox, height=3)

        # (Advanced) options box...
        optionsBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
        )
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
        OWGUI.separator(widget=optionsBox, height=2)
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        OWGUI.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    def inputData(self, newInput):
        """Process incoming data."""
        self.segmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):
        """Preprocess and send data"""
        if not self.segmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Preprocessed data', None, self)
            return
        if not self.segmentation.is_non_overlapping():
            self.infoBox.setText(
                message=u'Please make sure that input segments are not ' +
                        u'overlapping.',
                state='error'
            )
            self.send('Preprocessed data', None, self)
            return

        # TODO: remove label message in doc

        if self.applyCaseTransform:
            case = 'lower' if self.caseTransform == 'to lower' else 'upper'
        else:
            case = None
        self.clearCreatedInputIndices()
        previousNumInputs = len(Segmentation.data)
        if self.displayAdvancedSettings:
            copyAnnotations = self.copyAnnotations
        else:
            copyAnnotations = True
        progressBar = OWGUI.ProgressBar(
            self,
            iterations=len(self.segmentation)
        )
        preprocessed_data = Segmenter.recode(
            self.segmentation,
            case=case,
            remove_accents=self.removeAccents,
            label=self.captionTitle,
            copy_annotations=copyAnnotations,
            progress_callback=progressBar.advance,
        )
        progressBar.finish()
        newNumInputs = len(Segmentation.data)
        self.createdInputIndices = range(previousNumInputs, newNumInputs)
        message = u'%i segment@p sent to output.' % len(preprocessed_data)
        message = pluralize(message, len(preprocessed_data))
        self.infoBox.setText(message)
        self.send('Preprocessed data', preprocessed_data, self)
        self.sendButton.resetSettingsChangedFlag()

    def clearCreatedInputIndices(self):
        for i in self.createdInputIndices:
            Segmentation.set_data(i, None)

    def updateGUI(self):
        """Update GUI state"""
        if self.applyCaseTransform:
            self.caseTransformCombo.setDisabled(False)
        else:
            self.caseTransformCombo.setDisabled(True)
        if self.displayAdvancedSettings:
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)
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

    def onDeleteWidget(self):
        self.clearCreatedInputIndices()

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
    appl = QApplication(sys.argv)
    ow = OWTextablePreprocess()
    ow.show()
    appl.exec_()
    ow.saveSettings()
