"""
Class OWTextableDisplay
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

__version__ = '0.16.3'

"""
<name>Display</name>
<description>Display or export the details of a segmentation</description>
<icon>icons/Display.png</icon>
<priority>6001</priority>
"""

import os, codecs, uuid

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from TextableUtils import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI


class OWTextableDisplay(OWWidget):
    """A widget for displaying segmentations"""

    settingsList = [
        'displayAdvancedSettings',
        'autoSend',
        'customFormatting',
        'customFormat',
        'segmentDelimiter',
        'header',
        'footer',
        'encoding',
        'lastLocation',
        'uuid',
    ]

    # Predefined list of available encodings...
    encodings = getPredefinedEncodings()

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Display widget"""

        OWWidget.__init__(
            self,
            parent,
            signalManager,
            wantMainArea=1,
            wantStateInfoWidget=0,
        )

        self.inputs = [('Segmentation', Segmentation, self.inputData, Single)]
        self.outputs = [
            ('Bypassed segmentation', Segmentation, Default),
            ('Displayed segmentation', Segmentation)
        ]

        # Settings...
        self.displayAdvancedSettings = False
        self.customFormatting = False
        self.customFormat = u'%(__content__)s'
        self.segmentDelimiter = ur'\n'
        self.header = u''
        self.footer = u''
        self.encoding = 'utf-8'
        self.lastLocation = '.'
        self.autoSend = True
        self.uuid = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.segmentation = None
        self.displayedSegmentation = Input(
            label=u'displayed_segmentation',
            text=u''
        )
        self.goto = 0
        self.browser = QTextBrowser()
        self.infoBox = InfoBox(widget=self.mainArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            sendIfPreCallback=self.updateGUI,
            infoBoxAttribute='infoBox',
        )

        # GUI...

        # NB: These are "custom" advanced settings, not those provided by
        # TextableUtils. Note also that there are two copies of the checkbox
        # controlling the same attribute, to simulate its moving from one
        # side of the widget to the other...
        self.advancedSettingsCheckBoxLeft = OWGUI.checkBox(
            widget=self.controlArea,
            master=self,
            value='displayAdvancedSettings',
            label=u'Advanced settings',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Toggle advanced settings on and off."
            ),
        )
        OWGUI.separator(widget=self.controlArea, height=3)

        # Custom formatting box...
        formattingBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Formatting',
            orientation='vertical',
            addSpace=True,
        )
        OWGUI.checkBox(
            widget=formattingBox,
            master=self,
            value='customFormatting',
            label=u'Apply custom formatting',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box to apply custom formatting."
            ),
        )
        OWGUI.separator(widget=formattingBox, height=3)
        self.formattingIndentedBox = OWGUI.indentedBox(
            widget=formattingBox,
        )
        headerLineEdit = OWGUI.lineEdit(
            widget=self.formattingIndentedBox,
            master=self,
            value='header',
            label=u'Header:',
            labelWidth=131,
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"String that will be appended at the beginning of\n"
                u"the formatted segmentation."
            ),
        )
        headerLineEdit.setMinimumWidth(200)
        OWGUI.separator(widget=self.formattingIndentedBox, height=3)
        OWGUI.lineEdit(
            widget=self.formattingIndentedBox,
            master=self,
            value='customFormat',
            label=u'Format:',
            labelWidth=131,
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"String specifying how to format the segmentation.\n\n"
                u"See user guide for detailed instructions."
            ),
        )
        OWGUI.separator(widget=self.formattingIndentedBox, height=3)
        OWGUI.lineEdit(
            widget=self.formattingIndentedBox,
            master=self,
            value='segmentDelimiter',
            label=u'Segment delimiter:',
            labelWidth=131,
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Delimiter that will be inserted between segments.\n\n"
                u"Note that '\\n' stands for carriage return and\n"
                u"'\\t' for tabulation."
            ),
        )
        OWGUI.separator(widget=self.formattingIndentedBox, height=3)
        OWGUI.lineEdit(
            widget=self.formattingIndentedBox,
            master=self,
            value='footer',
            label=u'Footer:',
            labelWidth=131,
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"String that will be appended at the end of the\n"
                u"formatted segmentation."
            ),
        )
        headerLineEdit.setMinimumWidth(200)
        OWGUI.separator(widget=self.formattingIndentedBox, height=3)

        # Export box
        self.exportBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Export',
            orientation='vertical',
            addSpace=True,
        )
        encodingCombo = OWGUI.comboBox(
            widget=self.exportBox,
            master=self,
            value='encoding',
            items=type(self).encodings,
            sendSelectedValue=True,
            orientation='horizontal',
            label=u'File encoding:',
            labelWidth=151,
            tooltip=(
                u"Select the encoding of the file into which a\n"
                u"displayed segmentation can be saved by clicking\n"
                u"the 'Export' button below.\n\n"
                u"Note that the displayed segmentation that is\n"
                u"copied to the clipboard by clicking the 'Copy\n"
                u"to clipboard' button below is always encoded\n"
                u"in utf-8."
            ),
        )
        OWGUI.separator(widget=self.exportBox, height=3)
        exportBoxLine2 = OWGUI.widgetBox(
            widget=self.exportBox,
            orientation='horizontal',
        )
        exportButton = OWGUI.button(
            widget=exportBoxLine2,
            master=self,
            label=u'Export to file',
            callback=self.exportFile,
            tooltip=(
                u"Open a dialog for selecting the output file to\n"
                u"which the displayed segmentation will be saved."
            ),
        )
        self.copyButton = OWGUI.button(
            widget=exportBoxLine2,
            master=self,
            label=u'Copy to clipboard',
            callback=self.copyToClipboard,
            tooltip=(
                u"Copy the displayed segmentation to clipboard, in\n"
                u"order to paste it in another application."
                u"\n\nNote that the only possible encoding is utf-8."
            ),
        )

        OWGUI.rubber(self.controlArea)

        # Send button and checkbox
        self.sendButton.draw()

        # Main area

        # NB: This is the second copy of the advanced settings checkbox,
        # see above...
        self.advancedSettingsRightBox = OWGUI.widgetBox(
            widget=self.mainArea,
            orientation='vertical',
        )
        self.advancedSettingsCheckBoxRight = OWGUI.checkBox(
            widget=self.advancedSettingsRightBox,
            master=self,
            value='displayAdvancedSettings',
            label=u'Advanced settings',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Toggle advanced settings on and off."
            ),
        )
        OWGUI.separator(widget=self.advancedSettingsRightBox, height=3)

        self.advancedSettingsCheckBoxRightPlaceholder = OWGUI.separator(
            widget=self.mainArea,
            height=25,
        )

        self.navigationBox = OWGUI.widgetBox(
            widget=self.mainArea,
            orientation='vertical',
            box=u'Navigation',
            addSpace=True,
        )
        self.gotoSpin = OWGUI.spin(
            widget=self.navigationBox,
            master=self,
            value='goto',
            min=1,
            max=1,
            orientation='horizontal',
            label=u'Go to segment:',
            labelWidth=180,
            callback=self.gotoSegment,
            tooltip=(
                u"Jump to a specific segment number."
            ),
        )
        OWGUI.separator(widget=self.navigationBox, height=3)
        self.mainArea.layout().addWidget(self.browser)

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()

    def inputData(self, newInput):
        """Process incoming data."""
        self.segmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):
        """Send segmentation to output"""
        if not self.segmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Bypassed segmentation', None, self)
            self.send('Displayed segmentation', None, self)
            return
        self.send(
            'Bypassed segmentation',
            Segmenter.bypass(self.segmentation, self.captionTitle),
            self
        )
        if (
            (
                0 in self.widgetState['Warning'] and
                'format' in self.widgetState['Warning'][0]
            )
            or
            (
                0 in self.widgetState['Error'] and
                'format' in self.widgetState['Error'][0]
            )
        ):
            self.send('Displayed segmentation', None, self)
            return
        if len(self.displayedSegmentation[0].get_content()) > 0:
            self.send(
                'Displayed segmentation',
                self.displayedSegmentation,
                self
            )
        else:
            self.send('Displayed segmentation', None, self)
        if 'Format' not in self.widgetState['Error'].get(0, u''):
            message = u'%i segment@p sent to output.' % len(self.segmentation)
            message = pluralize(message, len(self.segmentation))
            self.infoBox.setText(message)
        self.sendButton.resetSettingsChangedFlag()

    def updateGUI(self):
        """Update GUI state"""
        self.controlArea.setVisible(self.displayAdvancedSettings)
        self.advancedSettingsCheckBoxRightPlaceholder.setVisible(
            self.displayAdvancedSettings
        )
        self.advancedSettingsCheckBoxLeft.setVisible(
            self.displayAdvancedSettings
        )
        self.advancedSettingsRightBox.setVisible(
            not self.displayAdvancedSettings
        )
        self.browser.clear()
        if self.segmentation:
            if self.displayAdvancedSettings:
                customFormatting = self.customFormatting
            else:
                customFormatting = False
                self.autoSend = True
            if customFormatting:
                self.navigationBox.setDisabled(True)
                self.exportBox.setDisabled(True)
                self.formattingIndentedBox.setDisabled(False)
                displayedString = u''
                progressBar = OWGUI.ProgressBar(
                    self,
                    iterations=len(self.segmentation)
                )
                try:
                    displayedString = self.segmentation.to_string(
                        self.customFormat.decode('string_escape'),
                        self.segmentDelimiter.decode('string_escape'),
                        self.header.decode('string_escape'),
                        self.footer.decode('string_escape'),
                        True,
                        progress_callback=progressBar.advance,
                    )
                    self.infoBox.settingsChanged()
                    self.exportBox.setDisabled(False)
                    self.warning(0)
                    self.error(0)
                except TypeError as type_error:
                    self.infoBox.setText(type_error.message, 'error')
                except KeyError:
                    message = "Please enter a valid format (error: missing name)."
                    self.infoBox.setText(message, 'error')
                except ValueError:
                    message = "Please enter a valid format (error: missing "   \
                        + "variable type)."
                    self.infoBox.setText(message, 'error')
                self.browser.append(displayedString)
                self.displayedSegmentation.update(
                    displayedString,
                    label=self.captionTitle,
                )
                progressBar.finish()
            else:
                self.formattingIndentedBox.setDisabled(True)
                self.warning(0)
                self.error(0)
                progressBar = OWGUI.ProgressBar(
                    self,
                    iterations=len(self.segmentation)
                )
                displayedString, summarized = self.segmentation.to_html(
                    True,
                    progressBar.advance,
                )
                self.browser.append(displayedString)
                self.displayedSegmentation.update(
                    displayedString,
                    label=self.captionTitle,
                )
                self.navigationBox.setDisabled(False)
                self.gotoSpin.control.setRange(1, len(self.segmentation))
                if self.goto:
                    self.browser.setSource(QUrl("#%i" % self.goto))
                else:
                    self.browser.setSource(QUrl("#top"))
                self.exportBox.setDisabled(False)
                self.infoBox.settingsChanged()
                progressBar.finish()
                self.navigationBox.setVisible(not summarized)
        else:
            self.goto = 0
            self.exportBox.setDisabled(True)
            self.navigationBox.setVisible(False)
            self.formattingIndentedBox.setDisabled(True)
        self.adjustSize()

    def gotoSegment(self):
        if self.goto:
            self.browser.setSource(QUrl("#%i" % self.goto))
        else:
            self.browser.setSource(QUrl("#top"))

    def exportFile(self):
        """Display a FileDialog and export segmentation to file"""
        filePath = unicode(
            QFileDialog.getSaveFileName(
                self,
                u'Export segmentation to File',
                self.lastLocation,
            )
        )
        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            outputFile = codecs.open(
                filePath,
                encoding=self.encoding,
                mode='w',
                errors='xmlcharrefreplace',
            )
            outputFile.write(
                normalizeCarriageReturns(
                    self.displayedSegmentation[0].get_content()
                )
            )
            outputFile.close()
            QMessageBox.information(
                None,
                'Textable',
                'Segmentation correctly exported',
                QMessageBox.Ok
            )

    def copyToClipboard(self):
        """Copy displayed segmentation to clipboard"""
        QApplication.clipboard().setText(
            normalizeCarriageReturns(
                self.displayedSegmentation[0].get_content()
            )
        )
        QMessageBox.information(
            None,
            'Textable',
            'Segmentation correctly copied to clipboard',
            QMessageBox.Ok
        )

    def onDeleteWidget(self):
        self.displayedSegmentation.clear()
        self.segmentation.__del__()


    def adjustSizeWithTimer(self):
        qApp.processEvents()
        QTimer.singleShot(50, self.adjustSize)

    def setCaption(self, title):
        if 'captionTitle' in dir(self) and title != 'Orange Widget':
            OWWidget.setCaption(self, title)
            self.sendButton.settingsChanged()
        else:
            OWWidget.setCaption(self, title)

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
    import LTTL.Segmenter as Segmenter
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableDisplay()
    ow.show()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'cruel world', label=u'text2')
    seg3 = Segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = Segmenter.tokenize(seg3, [(r'\w+(?u)', u'tokenize')], label=u'words')
    ow.inputData(seg4)
    appl.exec_()
