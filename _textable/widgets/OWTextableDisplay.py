"""
Class OWTextableDisplay
Copyright 2012-2019 LangTech Sarl (info@langtech.ch)
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

__version__ = '0.16.12'

import sys
import os
import codecs
import re

from PyQt5.QtWidgets import QTextBrowser, QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import QUrl

import LTTL
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    SendButton, InfoBox, getPredefinedEncodings, pluralize,
    addSeparatorAfterDefaultEncodings, normalizeCarriageReturns
)

from Orange.widgets import widget, gui, settings


class OWTextableDisplay(OWTextableBaseWidget):
    """A widget for displaying segmentations"""
    name = "Display"
    description = "Display or export the details of a segmentation"
    icon = "icons/Display.png"
    priority = 6001

    inputs = [('Segmentation', Segmentation, "inputData", widget.Single)]
    outputs = [
        ('Bypassed segmentation', Segmentation, widget.Default),
        ('Displayed segmentation', Segmentation)
    ]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    displayAdvancedSettings = settings.Setting(False)
    customFormatting = settings.Setting(False)
    limitNumberOfSegments = settings.Setting(True)
    customFormat = settings.Setting(u'%(__content__)s')
    segmentDelimiter = settings.Setting(u'\\n')
    header = settings.Setting(u'')
    footer = settings.Setting(u'')
    encoding = settings.Setting('utf8')
    lastLocation = settings.Setting('.')
    basicFormatHTML = settings.Setting(True)

    # Predefined list of available encodings...
    encodings = getPredefinedEncodings()

    want_main_area = True

    def __init__(self, *args, **kwargs):
        """Initialize a Display widget"""
        super().__init__(*args, **kwargs)
        # Current general warning and error messages (as submited
        # through self.error(text) and self.warning(text)
        self._currentErrorMessage = ""
        self._currentWarningMessage = ""

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
        self.advancedSettingsCheckBoxLeft = gui.checkBox(
            widget=self.controlArea,
            master=self,
            value='displayAdvancedSettings',
            label=u'Advanced settings',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Toggle advanced settings on and off."
            ),
        )
        gui.separator(widget=self.controlArea, height=3)

        # Options box...
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=True,
        )
        gui.checkBox(
            widget=optionsBox,
            master=self,
            value='limitNumberOfSegments',
            label=u'Limit number of displayed segments',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                "By default, the number of displayed segments is limited to\n"
                "%i, to keep the widget's execution time reasonably short.\n"
                "Unchecking this box makes it possible to display all the\n"
                "segments. Use with caution, as execution time can become\n"
                "prohibitively long for segmentations with more than a few\n."
                "thousand segments." % LTTL.Segmentation.MAX_SEGMENT_STRING
            ),
        )
        
        # Custom formatting box...
        formattingBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Formatting',
            orientation='vertical',
            addSpace=True,
        )
        gui.checkBox(
            widget=formattingBox,
            master=self,
            value='customFormatting',
            label=u'Apply custom formatting',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box to apply custom formatting."
            ),
        )
        gui.separator(widget=formattingBox, height=3)
        self.formattingIndentedBox = gui.indentedBox(
            widget=formattingBox,
        )
        headerLineEdit = gui.lineEdit(
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
        gui.separator(widget=self.formattingIndentedBox, height=3)
        gui.lineEdit(
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
        gui.separator(widget=self.formattingIndentedBox, height=3)
        gui.lineEdit(
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
        gui.separator(widget=self.formattingIndentedBox, height=3)
        gui.lineEdit(
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
        gui.separator(widget=self.formattingIndentedBox, height=3)

        # Advanced export box
        self.advancedExportBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Export',
            orientation='vertical',
            addSpace=True,
        )
        encodingCombo = gui.comboBox(
            widget=self.advancedExportBox,
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
        addSeparatorAfterDefaultEncodings(encodingCombo)
        gui.separator(widget=self.advancedExportBox, height=3)
        exportBoxLine2 = gui.widgetBox(
            widget=self.advancedExportBox,
            orientation='horizontal',
        )
        gui.button(
            widget=exportBoxLine2,
            master=self,
            label=u'Export to file',
            callback=self.exportFile,
            tooltip=(
                u"Open a dialog for selecting the output file to\n"
                u"which the displayed segmentation will be saved."
            ),
        )
        gui.button(
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

        gui.rubber(self.controlArea)

        # Send button and checkbox
        self.sendButton.draw()

        # Main area

        # NB: This is the second copy of the advanced settings checkbox,
        # see above...
        self.advancedSettingsRightBox = gui.widgetBox(
            widget=self.mainArea,
            orientation='vertical',
        )
        self.advancedSettingsCheckBoxRight = gui.checkBox(
            widget=self.advancedSettingsRightBox,
            master=self,
            value='displayAdvancedSettings',
            label=u'Advanced settings',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Toggle advanced settings on and off."
            ),
        )
        gui.separator(widget=self.advancedSettingsRightBox, height=3)

        self.advancedSettingsCheckBoxRightPlaceholder = gui.separator(
            widget=self.mainArea,
            height=25,
        )

        self.basicFormatBox = gui.widgetBox(
            widget=self.mainArea,
            orientation='vertical',
            box=u'Format',
            addSpace=False,
        )
        gui.checkBox(
            widget=self.basicFormatBox,
            master=self,
            value='basicFormatHTML',
            label=u'Display segmentation in rich text format (HTML)',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"TODO."
            ),
        )
        self.navigationBox = gui.widgetBox(
            widget=self.mainArea,
            orientation='vertical',
            box=u'Navigation',
            addSpace=True,
        )
        self.gotoSpin = gui.spin(
            widget=self.navigationBox,
            master=self,
            value='goto',
            minv=1,
            maxv=1,
            orientation='horizontal',
            label=u'Go to segment:',
            labelWidth=180,
            callback=self.gotoSegment,
            tooltip=(
                u"Jump to a specific segment number."
            ),
        )
        self.mainArea.layout().addWidget(self.browser)

        # Advanced export box
        gui.separator(widget=self.mainArea, height=3)
        self.basicExportBox = gui.widgetBox(
            widget=self.mainArea,
            box=u'Export',
            orientation='horizontal',
            addSpace=True,
        )
        gui.button(
            widget=self.basicExportBox,
            master=self,
            label=u'Save to file',
            callback=self.exportFile,
            tooltip=(
                u"Open a dialog for selecting the output file to\n"
                u"which the displayed segmentation will be saved."
            ),
        )
        gui.button(
            widget=self.basicExportBox,
            master=self,
            label=u'Copy to clipboard',
            callback=self.copyToClipboard,
            tooltip=(
                u"Copy the displayed segmentation to clipboard, in\n"
                u"order to paste it in another application."
            ),
        )

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
        # TODO: Check if this is correct replacement for textable v1.*, v2.*
        if 'format' in self._currentWarningMessage or \
                'format' in self._currentErrorMessage:
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
        # TODO: Differes only in capitalization with a check before
        #       Is this intentional?
        if "Format" not in self._currentErrorMessage:
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
        self.basicFormatBox.setVisible(
            not self.displayAdvancedSettings
        )
        self.basicExportBox.setVisible(
            not self.displayAdvancedSettings
        )
        self.browser.clear()
        if self.segmentation:
            if self.displayAdvancedSettings:
                customFormatting = self.customFormatting
            else:
                customFormatting = False
                self.autoSend = True

            self.controlArea.setDisabled(True)
            self.mainArea.setDisabled(True)
            self.infoBox.setText(u"Processing, please wait...", "warning")

            if customFormatting:
                self.navigationBox.setVisible(False)
                self.navigationBox.setDisabled(True)
                self.advancedExportBox.setDisabled(True)
                self.formattingIndentedBox.setDisabled(False)
                displayedString = u''
                progressBar = ProgressBar(
                    self,
                    iterations=len(self.segmentation)
                )
                try:
                    displayedString = self.segmentation.to_string(
                        codecs.decode(self.customFormat, 'unicode_escape'),
                        codecs.decode(self.segmentDelimiter, 'unicode_escape'),
                        codecs.decode(self.header, 'unicode_escape'),
                        codecs.decode(self.footer, 'unicode_escape'),
                        True,
                        progress_callback=progressBar.advance,
                        display_all=not self.limitNumberOfSegments,
                    )
                    self.infoBox.settingsChanged()
                    self.advancedExportBox.setDisabled(False)
                    self.warning()
                    self.error()
                except TypeError as type_error:
                    try:
                        self.infoBox.setText(type_error.message, 'error')
                    except AttributeError:
                        message = "Please enter a valid format (type error)."
                        self.infoBox.setText(message, 'error')
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
                self.navigationBox.setVisible(self.basicFormatHTML)
                self.formattingIndentedBox.setDisabled(True)
                self.warning()
                self.error()
                progressBar = ProgressBar(
                    self,
                    iterations=len(self.segmentation)
                )
                if self.displayAdvancedSettings:
                    displayedString, summarized = self.segmentation.to_html(
                        True,
                        progressBar.advance,
                        display_all=not self.limitNumberOfSegments,
                    )
                    self.navigationBox.setEnabled(
                        len(self.segmentation) > 1 and not summarized
                    )
                elif self.basicFormatHTML:
                    displayedString, summarized = self.segmentation.to_html(
                        True,
                        progressBar.advance,
                    )
                    self.navigationBox.setEnabled(
                        len(self.segmentation) > 1 and not summarized
                    )
                else:
                    displayedString = self.segmentation.to_string(
                        formatting="%(__content__)s",
                        segment_delimiter="\n",
                        progress_callback=progressBar.advance,
                        #display_all=not self.limitNumberOfSegments,
                    )
                self.browser.append(displayedString)
                self.displayedSegmentation.update(
                    displayedString,
                    label=self.captionTitle,
                )
                self.gotoSpin.setRange(1, len(self.segmentation))
                if self.goto:
                    self.browser.setSource(QUrl("#%i" % self.goto))
                else:
                    self.browser.setSource(QUrl("#top"))
                self.advancedExportBox.setDisabled(False)
                self.infoBox.settingsChanged()
                progressBar.finish()

            self.controlArea.setDisabled(False)
            self.mainArea.setDisabled(False)

        else:
            self.goto = 0
            self.gotoSpin.setRange(0, 1)
            self.advancedExportBox.setDisabled(True)
            self.navigationBox.setVisible(True)
            self.navigationBox.setEnabled(False)
            self.formattingIndentedBox.setDisabled(True)

    def gotoSegment(self):
        if self.goto:
            self.browser.setSource(QUrl("#%i" % self.goto))
        else:
            self.browser.setSource(QUrl("#top"))

    def exportFile(self):
        """Display a FileDialog and export segmentation to file"""
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            u'Export segmentation to File',
            self.lastLocation,
        )
        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            if self.displayAdvancedSettings:
                encoding = re.sub(r"[ ]\(.+", "", self.encoding)
            else:
                encoding = "utf8"
            outputFile = codecs.open(
                filePath,
                encoding=encoding,
                mode='w',
                errors='xmlcharrefreplace',
            )
            outputFile.write(
                #normalizeCarriageReturns(
                    self.displayedSegmentation[0].get_content()
                #)
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
            #normalizeCarriageReturns(
                self.displayedSegmentation[0].get_content()
            #)
        )
        QMessageBox.information(
            None,
            'Textable',
            'Segmentation correctly copied to clipboard',
            QMessageBox.Ok
        )

    def onDeleteWidget(self):
        if self.displayedSegmentation is not None:
            self.displayedSegmentation.clear()

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def error(self, *args, **kwargs):
        # Reimplemented to track the current active error message
        if args:
            text_or_id = args[0]
        else:
            text_or_id = kwargs.get("text_or_id", None)

        if isinstance(text_or_id, str) or text_or_id is None:
            self._currentErrorMessage = text_or_id or ""
        return super().error(*args, **kwargs)

    def warning(self, *args, **kwargs):
        # Reimplemented to track the current active warning message
        if args:
            text_or_id = args[0]
        else:
            text_or_id = kwargs.get("text_or_id", None)

        if isinstance(text_or_id, str) or text_or_id is None:
            self._currentWarningMessage = text_or_id or ""
        return super().warning(*args, **kwargs)


if __name__ == '__main__':
    appl = QApplication(sys.argv)
    ow = OWTextableDisplay()
    ow.show()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'cruel world', label=u'text2')
    seg3 = Segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = Segmenter.tokenize(seg3, [(r'\w+(?u)', u'tokenize')], label=u'words')
    ow.inputData(seg4)
    appl.exec_()
