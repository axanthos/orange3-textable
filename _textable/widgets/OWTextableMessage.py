#=============================================================================
# Class OWTextableJSONMessage
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

__version__ = '0.01.1'

"""
<name>Message</name>
<description>Parse JSON data in segmentation and use them to control other
widgets</description>
<icon>icons/Message.png</icon>
<priority>10002</priority>
"""


import json, textwrap
from LTTL.Segmentation  import Segmentation
from TextableUtils import *

import Orange
from OWWidget import *
import OWGUI

class OWTextableMessage(OWWidget):

    """Orange widget for parsing JSON data in segmentation"""

    settingsList = [
            'autoSend',
            'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Message widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )

        self.inputs = [("Segmentation", Segmentation, self.inputData, Single)]
        self.outputs = [("Message", JSONMessage, Single)]

        # Settings...
        self.autoSend                   = True
        self.uuid                       = None
        self.loadSettings()
        self.uuid                       = getWidgetUuid(self)

        # Other attributes...
        self.segmentation = None
        self.infoBox                = InfoBox(widget=self.controlArea)
        self.sendButton             = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
        )


        # GUI
        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()

        self.sendButton.sendIf()
        self.resize(50,50)

    def inputData(self, newInput):
        """Process incoming data"""
        self.segmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()


    def sendData(self):
        """Parse JSON data and send message"""
        if not self.segmentation:
            self.infoBox.noDataSent(u': no input segmentation.')
            self.send('Message', None, self)
            return
        if len(self.segmentation) > 1:
            warning = "Input segmentation contains more than 1 segment."
            self.infoBox.noDataSent(warning = warning)
            self.send('Message', None, self)
            return
        self.infoBox.inputChanged()
        try:
            content = self.segmentation[0].get_content()
            jsonList = json.loads(content)
            jsonMessage = JSONMessage(content)
            self.send('Message', jsonMessage, self)
            message = u'%i item@p.' % len(jsonList)
            message = pluralize(message, len(jsonList))
            self.infoBox.dataSent(message)
        except ValueError:
            error = "JSON parsing error."
            self.infoBox.noDataSent(error = error)
            self.send('Message', None, self)
            return
        self.sendButton.resetSettingsChangedFlag()


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

if __name__=="__main__":
    appl = QApplication(sys.argv)
    ow = OWTextableMessage()
    ow.show()
    appl.exec_()
