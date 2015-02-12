#=============================================================================
# Class OWTextablePreprocess
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

__version__ = '0.10'

"""
<name>Preprocess</name>
<description>Basic text preprocessing</description>
<icon>icons/Preprocess.png</icon>
<priority>2001</priority>
"""

from LTTL.Recoder       import Recoder
from LTTL.Segmentation  import Segmentation

from TextableUtils import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextablePreprocess(OWWidget):

    """Orange widget for standard text preprocessing"""

    settingsList = [
            'copyAnnotations',
            'label',
            'applyCaseTransform',
            'caseTransform',
            'removeAccents',
            'displayAdvancedSettings',
            'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):
        
        """Initialize a Preprocess widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )
        
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Single)]
        self.outputs = [('Preprocessed data', Segmentation)]
        
        # Settings...
        self.copyAnnotations            = True
        self.label                      = u'preprocessed_data'
        self.applyCaseTransform         = False
        self.caseTransform              = 'to lower'
        self.removeAccents              = False
        self.autoSend                   = True
        self.displayAdvancedSettings    = False
        self.uuid                       = None
        self.loadSettings()
        self.uuid                       = getWidgetUuid(self)

        # Other attributes...
        self.createdInputIndices    = []
        self.segmentation           = None
        self.recoder                = Recoder()
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

        # Advanced settings checkbox...
        self.advancedSettings.draw()

        # Preprocessing box
        preprocessingBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Preprocessing',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.preprocessingBoxLine1 = OWGUI.widgetBox(
                widget              = preprocessingBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.preprocessingBoxLine1,
                master              = self,
                value               = 'applyCaseTransform',
                label               = u'Transform case:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Apply systematic case conversion."
                ),
        )
        self.caseTransformCombo = OWGUI.comboBox(
                widget              = self.preprocessingBoxLine1,
                master              = self,
                value               = 'caseTransform',
                items               = [u'to lower', u'to upper'],
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Case conversion mode: to lowercase or uppercase."
                ),
        )
        self.caseTransformCombo.setMinimumWidth(120)
        OWGUI.separator(
                widget              = preprocessingBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = preprocessingBox,
                master              = self,
                value               = 'removeAccents',
                label               = u'Remove accents',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Replace accented characters with non-accented ones."
                ),
        )
        OWGUI.separator(
                widget              = preprocessingBox,
                height              = 3,
        )

        # (Advanced) options box...
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

        # (Basic) options box...
        basicOptionsBox = BasicOptionsBox(self.controlArea, self)
        self.advancedSettings.basicWidgets.append(basicOptionsBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # Info box...
        self.infoBox.draw()

        # Send button and checkbox
        self.sendButton.draw()

        self.sendButton.sendIf()


    def inputData(self, newInput):
        """Process incoming data."""
        self.segmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()


    def sendData(self):
        """Preprocess and send data"""
        if not self.segmentation:
            self.infoBox.noDataSent(u'No input.')
            self.send('Preprocessed data', None, self)
            return
        if not self.segmentation.is_non_overlapping():
            self.infoBox.noDataSent(u'Input segmentation is overlapping.')
            self.send('Preprocessed data', None, self)
            return
        if not self.label:
            self.infoBox.noDataSent(u'No label was provided.')
            self.send('Preprocessed data', None, self)
            return
        if self.applyCaseTransform:
            if self.caseTransform == 'to lower':
                self.recoder.case = 'lower'
            else:
                self.recoder.case = 'upper'
        else:
            self.recoder.case = None
        self.recoder.remove_accents = self.removeAccents
        self.clearCreatedInputIndices()
        previousNumInputs = len(Segmentation.data)
        if self.displayAdvancedSettings:
            copyAnnotations = self.copyAnnotations
        else:
            copyAnnotations = True
        progressBar = OWGUI.ProgressBar(
                self,
                iterations = len(self.segmentation)
        )
        preprocessed_data = self.recoder.apply(
                self.segmentation,
                mode                = 'standard',
                label               = self.label,
                copy_annotations    = copyAnnotations,
                progress_callback   = progressBar.advance,
        )
        progressBar.finish()
        newNumInputs = len(Segmentation.data)
        self.createdInputIndices = range(previousNumInputs, newNumInputs)
        self.send('Preprocessed data', preprocessed_data, self)
        message = u'Data contains %i segment@p.' % len(preprocessed_data)
        message = pluralize(message, len(preprocessed_data))
        self.infoBox.dataSent(message)
        self.sendButton.resetSettingsChangedFlag()

        
    def clearCreatedInputIndices(self):
        for i in self.createdInputIndices:
            Segmentation.data[i] = None
        for i in reversed(xrange(len(Segmentation.data))):
            if Segmentation.data[i] is None:
                Segmentation.data.pop(i)
            else:
                break


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


    def onDeleteWidget(self):
        self.clearCreatedInputIndices()


    def getSettings(self, *args, **kwargs):
        settings = OWWidget.getSettings(self, *args, **kwargs)
        settings["settingsDataVersion"] = __version__.split('.')
        return settings

    def setSettings(self, settings):
        if settings.get("settingsDataVersion", None) == __version__.split('.'):
            settings = settings.copy()
            del settings["settingsDataVersion"]
            OWWidget.setSettings(self, settings)


if __name__ == '__main__':
    appl = QApplication(sys.argv)
    ow   = OWTextablePreprocess()
    ow.show()
    appl.exec_()
    ow.saveSettings()
