#=============================================================================
# Class OWTextableTextField
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

__version__ = '0.13.1'

"""
<name>Text Field</name>
<description>Import text data from keyboard input</description>
<icon>icons/TextField.png</icon>
<priority>1</priority>
"""

import textwrap

from unicodedata        import normalize
from PyQt4              import QtCore
from LTTL.Segmentation  import Segmentation
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
                wantMainArea=0,
        )

        # Input and output channels...
        self.inputs  = [
            ('Text data', Segmentation, self.inputTextData, Single)
        ]
        self.outputs            = [('Text data', Segmentation)]

        # Settings...
        self.textFieldContent   = u''.encode('utf-8')
        self.encoding           = u'utf-8'
        self.autoSend           = True
        self.label              = u'text_string'
        self.uuid               = None
        self.loadSettings()
        self.uuid               = getWidgetUuid(self)

        # Other attributes...
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
            self.infoBox.noDataSent(u': text field is empty.')
            self.send('Text data', None, self)
            return

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(warning = u'No label was provided.')
            self.send('Text data', None, self)
            return

        # Set status to OK...
        message = u'1 segment (%i character@p).' % len(textFieldContent)
        message = pluralize(message, len(textFieldContent))
        self.infoBox.dataSent(message)

        # Update segmentation.
        self.segmentation.update(textFieldContent, label=self.label)

        # Send token...
        self.send('Text data', self.segmentation, self)
        self.sendButton.resetSettingsChangedFlag()


    def onDeleteWidget(self):
        self.segmentation.clear()

    def adjustSizeWithTimer(self):
        qApp.processEvents()
        QTimer.singleShot(50, self.adjustSize)

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
    ow   = OWTextableTextField()
    ow.show()
    appl.exec_()
    ow.saveSettings()
