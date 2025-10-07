"""
Class OWTextableMessage
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

__version__ = '0.01.6'


import json
from LTTL.Segmentation import Segmentation
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    JSONMessage, SendButton, InfoBox, pluralize
)

from Orange.widgets import gui, settings
from Orange.widgets.widget import Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview


class OWTextableMessage(OWTextableBaseWidget):
    """Orange widget for parsing JSON data in segmentation"""

    name = "Message"
    description = "Parse JSON data in segmentation and use them to control" \
                  "other widgets"
    icon = "icons/Message.png"
    priority = 10002

    class Inputs:
        segmentation = Input("Segmentation", Segmentation, auto_summary=False)
    class Outputs:
        message = Output("Message", JSONMessage, auto_summary=False)

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    want_main_area = False
    resizing_enabled = False

    def __init__(self, *args, **kwargs):
        """Initialize a Message widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.segmentation = None
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
        )

        # GUI
        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.setMinimumWidth(150)

        self.sendButton.sendIf()

    @Inputs.segmentation
    def inputData(self, newInput):
        """Process incoming data"""
        self.segmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):
        """Parse JSON data and send message"""
        if not self.segmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.sendNoneToOutputs()
            return
        if len(self.segmentation) > 1:
            self.infoBox.setText(
                u'Please make sure that input contains only one segment.',
                'error',
            )
            self.sendNoneToOutputs()
            return
        self.infoBox.inputChanged()
        try:
            content = self.segmentation[0].get_content()
            jsonList = json.loads(content)
            jsonMessage = JSONMessage(content)
            message = u'%i item@p sent to output.' % len(jsonList)
            message = pluralize(message, len(jsonList))
            self.infoBox.setText(message)
            self.Outputs.message.send(jsonMessage)
        except ValueError:
            self.infoBox.setText(
                u"Please make sure that input contains valid JSON data.",
                'error'
            )
            self.sendNoneToOutputs()
            return
        self.sendButton.resetSettingsChangedFlag()


if __name__ == "__main__":
    WidgetPreview(OWTextableMessage).run()
    
    # Old command-line testing code...

    # import sys
    # from AnyQt.QtWidgets import QApplication
    # appl = QApplication(sys.argv)
    # ow = OWTextableMessage()
    # ow.show()
    # appl.exec_()
