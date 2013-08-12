#=============================================================================
# Class OWTextableTextField, v0.06
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
<name>Text Field</name>
<description>Type text data and output a segmentation</description>
<icon>icons/TextField.png</icon>
<priority>1</priority>
"""

import uuid

from unicodedata        import normalize
from PyQt4              import QtCore
from LTTL.Input         import Input

from TextableUtils      import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableTextField(OWWidget):

    """Orange widget for typing text data"""

    settingsList = [
            'textFieldContent',
            'encoding',
            'autoSend',
            'label',
            'uuid',
    ]

    # Predefined list of available encodings...
    encodings = getPredefinedEncodings()

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Text File widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                'TextableTextField',
                wantMainArea=0,
        )

        # Input and output channels...
        self.inputs             = []
        self.outputs            = [('Text data', Input)]

        # Settings...
        self.textFieldContent   = u''.encode('utf-8')
        self.encoding           = u'utf-8'
        self.autoSend           = True
        self.label              = u'text_string'
        self.uuid               = uuid.uuid4()
        self.loadSettings()

        # Other attributes...
        self.fileIndex          = 0
        self.infoBox            = InfoBox(widget=self.controlArea)
        self.sendButton         = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
                sendIfPreCallback   = self.adjustSize(),
        )

        # LTTL.Input object (token that will be sent).
        self.segmentation       = Input(label=self.label, text=u'')

        # GUI...

        # Text Field...
        OWGUI.separator(
                widget          = self.controlArea,
                height          = 3,
        )
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(self.textFieldContent.decode('utf-8'))
        self.controlArea.layout().addWidget(self.editor)
        self.connect(
                self.editor,
                SIGNAL('textChanged()'),
                self.sendButton.settingsChanged
        )
        OWGUI.separator(
                widget          = self.controlArea,
                height          = 3,
        )

        # (Basic) options box...
        basicOptionsBox = BasicOptionsBox(self.controlArea, self, True)

        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()

        self.sendButton.sendIf()


    def sendData(self):

        """Open file, read and normalize content, then send Text object"""

        # Get, convert and normalize field content...
        textFieldContent = unicode(
                QtCore.QTextCodec.codecForName('UTF-16').fromUnicode(
                        self.editor.toPlainText()
                ),
                'UTF-16'
        )
        self.textFieldContent = textFieldContent.encode('utf-8')
        textFieldContent \
                = textFieldContent.replace('\r\n', '\n').replace('\r','\n')
        textFieldContent = normalize('NFC', textFieldContent)
            
        # Check that text field is not empty...
        if not self.textFieldContent:
            self.infoBox.noDataSent(u'Text field is empty.')
            self.send('Text data', None)
            return

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(u'No label was provided.')
            self.send('Text data', None)
            return

        # Set status to OK...
        message = u'Data contains %i character@p.' % len(textFieldContent)
        message = pluralize(message, len(textFieldContent))
        self.infoBox.dataSent(message)

        # Store content in the data array and set associated label.
        self.segmentation.update(textFieldContent, label=self.label)

        # Send token...
        self.send('Text data', self.segmentation)
        self.sendButton.resetSettingsChangedFlag()


    def onDeleteWidget(self):
        self.segmentation.clear()



if __name__ == '__main__':
    appl = QApplication(sys.argv)
    ow   = OWTextableTextField()
    ow.show()
    appl.exec_()
    ow.saveSettings()
