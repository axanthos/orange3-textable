"""
Class OWTextableTextField
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

__version__ = '0.13.2'      # TODO change subversion?

from unicodedata import normalize

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input

from PyQt4.QtGui import QPlainTextEdit

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    getPredefinedEncodings, pluralize,
    InfoBox, SendButton
)
from Orange.widgets import widget, gui, settings


class OWTextableTextField(OWTextableBaseWidget):
    """Orange widget for typing text data"""

    name = "Text Field"
    description = "Import text data from keyboard input"
    icon = "icons/TextField.png"
    priority = 1

    # Input and output channels...
    inputs = [('Text data', Segmentation, "inputTextData", widget.Single)]
    outputs = [('Text data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings ...
    textFieldContent = settings.Setting(u''.encode('utf-8'))
    encoding = settings.Setting(u'utf-8')

    # Predefined list of available encodings...
    encodings = getPredefinedEncodings()

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
            sendIfPreCallback=self.adjustSize(),
        )

        # LTTL.Input object (token that will be sent).
        self.segmentation = Input(text=u'')

        # GUI...

        # Text Field...
        gui.separator(
            widget=self.controlArea,
            height=3,
        )
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(self.textFieldContent.decode('utf-8'))
        self.controlArea.layout().addWidget(self.editor)
        self.editor.textChanged.connect(self.sendButton.settingsChanged)
        gui.separator(
            widget=self.controlArea,
            height=3,
        )
        self.setMinimumWidth(250)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()

    def inputTextData(self, segmentation):
        """Handle text data on input connection"""
        self.segmentation.clear()
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
            self.send('Text data', None, self)
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
        self.send('Text data', self.segmentation, self)
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
    import sys
    from PyQt4.QtGui import  QApplication
    appl = QApplication(sys.argv)
    ow = OWTextableTextField()
    ow.show()
    appl.exec_()
    ow.saveSettings()
