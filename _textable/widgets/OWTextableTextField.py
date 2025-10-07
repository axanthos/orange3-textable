"""
Class OWTextableTextField
Copyright 2012-2025 Aris Xanthos
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

from unicodedata import normalize

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input as LTTL_Input

from AnyQt.QtWidgets import QPlainTextEdit

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    pluralize, InfoBox, SendButton
)
from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview


class OWTextableTextField(OWTextableBaseWidget):
    """Orange widget for typing text data"""

    name = "Text Field"
    description = "Import text data from keyboard input"
    icon = "icons/TextField.png"
    priority = 1

    openclass = True
    
    # Input and output channels...
    class Inputs:
        text_data = Input("Text data", Segmentation, auto_summary=False)
    class Outputs:
        text_data = Output("Text data", Segmentation, auto_summary=False)

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings ...
    textFieldContent = settings.Setting(u''.encode('utf-8'))
    encoding = settings.Setting(u'utf-8')

    want_main_area = False

    def __init__(self):
        """Initialize a Text File widget"""

        super().__init__()

        # Other attributes...
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
        )

        # LTTL.Input object (token that will be sent).
        self.segmentation = LTTL_Input(text="")

        # GUI...

        # Text Field...
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(self.textFieldContent.decode('utf-8'))
        self.controlArea.layout().addWidget(self.editor)
        self.editor.textChanged.connect(self.sendButton.settingsChanged)
        self.setMinimumWidth(250)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()

    @Inputs.text_data
    def inputTextData(self, segmentation):
        """Handle text data on input connection"""
        if not segmentation:
            return
        self.editor.setPlainText(
            ''.join([s.get_content() for s in segmentation])
        )
        self.sendButton.settingsChanged()

    def sendData(self):
        """Normalize content, then create and send segmentation"""
        textFieldContent = self.editor.toPlainText()
        self.textFieldContent = textFieldContent.encode('utf-8')
        textFieldContent \
            = textFieldContent.replace('\r\n', '\n').replace('\r', '\n')
        textFieldContent = normalize('NFC', textFieldContent)

        # Check that text field is not empty...
        if not self.textFieldContent:
            self.infoBox.setText(
                message=u'Please type or paste some text above.',
                state='warning',
            )
            self.sendNoneToOutputs()
            return

        # TODO: remove message 'No label was provided.' from docs

        # Set status to OK...
        message = u'1 segment (%i character@p) sent to output.' %   \
                  len(textFieldContent)
        message = pluralize(message, len(textFieldContent))
        self.infoBox.setText(message)

        # Update segmentation.
        self.segmentation.update(textFieldContent, label=self.captionTitle)

        # Send token...
        self.Outputs.text_data.send(self.segmentation)
        self.sendButton.resetSettingsChangedFlag()

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.segmentation.clear()
        self.segmentation.__del__()


if __name__ == '__main__':
    WidgetPreview(OWTextableTextField).run()
