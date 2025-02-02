"""
Class OWTextableURLs
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

__version__ = '0.14.12'

import os
import codecs
import re
import json
import http
from unicodedata import normalize
from urllib.request import urlopen

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QFileDialog

import chardet

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.SegmenterThread as Segmenter

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    JSONMessage, InfoBox, SendButton, AdvancedSettings,
    addSeparatorAfterDefaultEncodings, addAutoDetectEncoding,
    normalizeCarriageReturns, getPredefinedEncodings, pluralize,
    Task
)

from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial


class OWTextableURLs(OWTextableBaseWidget):
    """Orange widget for fetching text from URLs"""

    name = "URLs"
    description = "Fetch text data online"
    icon = "icons/URLs.png"
    priority = 3

    inputs = [
        ('Message', JSONMessage, "inputMessage", widget.Single)
    ]
    outputs = [('Text data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    URLs = settings.Setting([])
    encoding = settings.Setting('(auto-detect)')
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    importURLs = settings.Setting(True)
    importURLsKey = settings.Setting(u'url')
    lastLocation = settings.Setting('.')
    displayAdvancedSettings = settings.Setting(False)
    URL = settings.Setting(u'')

    want_main_area = False

    def __init__(self):
        super().__init__()

        # Other attributes...
        self.segmentation = None
        self.createdInputs = list()
        self.URLLabel = list()
        self.selectedURLLabel = list()
        self.newURL = u''
        self.newAnnotationKey = u''
        self.newAnnotationValue = u''
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = self.create_advancedSettings()


        # GUI...

        # Advanced settings checkbox...
        self.advancedSettings.draw()

        # BASIC GUI...

        # Basic URL box
        self.basicURLBox = self.create_widgetbox(
            box=u'Source',
            orientation='vertical',
            addSpace=False,
            )

        basicURLBoxLine1 = gui.widgetBox(
            widget=self.basicURLBox,
            box=False,
            orientation='horizontal',
        )
        gui.lineEdit(
            widget=basicURLBoxLine1,
            master=self,
            value='URL',
            orientation='horizontal',
            label=u'URL:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The URL whose content will be imported."
            ),
        )
        gui.separator(widget=self.basicURLBox, height=3)
        advancedEncodingsCombobox = gui.comboBox(
            widget=self.basicURLBox,
            master=self,
            value='encoding',
            items=getPredefinedEncodings(),
            sendSelectedValue=True,
            orientation='horizontal',
            label=u'Encoding:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Select URL's encoding."
            ),
        )
        addSeparatorAfterDefaultEncodings(advancedEncodingsCombobox)
        addAutoDetectEncoding(advancedEncodingsCombobox)
        gui.separator(widget=self.basicURLBox, height=3)
        self.advancedSettings.basicWidgets.append(self.basicURLBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # ADVANCED GUI...

        # URL box
        self.URLBox = self.create_widgetbox(
            box=u'Sources',
            orientation='vertical',
            addSpace=False,
            )

        URLBoxLine1 = gui.widgetBox(
            widget=self.URLBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        self.fileListbox = gui.listBox(
            widget=URLBoxLine1,
            master=self,
            value='selectedURLLabel',
            labels='URLLabel',
            callback=self.updateURLBoxButtons,
            tooltip=(
                u"The list of URLs whose content will be imported.\n"
                u"\nIn the output segmentation, the content of each\n"
                u"URL appears in the same position as in the list.\n"
                u"\nColumn 1 shows the URL.\n"
                u"Column 2 shows the associated annotation (if any).\n"
                u"Column 3 shows the associated encoding."
            ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.fileListbox.setFont(font)
        URLBoxCol2 = gui.widgetBox(
            widget=URLBoxLine1,
            orientation='vertical',
        )
        self.moveUpButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Move Up',
            callback=self.moveUp,
            tooltip=(
                u"Move the selected URL upward in the list."
            ),
        )
        self.moveDownButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Move Down',
            callback=self.moveDown,
            tooltip=(
                u"Move the selected URL downward in the list."
            ),
        )
        self.removeButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Remove',
            callback=self.remove,
            tooltip=(
                u"Remove the selected URL from the list."
            ),
        )
        self.clearAllButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all URLs from the list."
            ),
        )
        self.exportButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Export JSON',
            callback=self.exportList,
            tooltip=(
                u"Open a dialog for selecting a file where the URL\n"
                u"list can be exported in JSON format."
            ),
        )
        self.importButton = gui.button(
            widget=URLBoxCol2,
            master=self,
            label=u'Import JSON',
            callback=self.importList,
            tooltip=(
                u"Open a dialog for selecting an URL list to\n"
                u"import (in JSON format). URLs from this list will\n"
                u"be added to those already imported."
            ),
        )
        URLBoxLine2 = gui.widgetBox(
            widget=self.URLBox,
            box=False,
            orientation='vertical',
        )
        # Add URL box
        addURLBox = gui.widgetBox(
            widget=URLBoxLine2,
            box=True,
            orientation='vertical',
            addSpace=False,
        )
        gui.lineEdit(
            widget=addURLBox,
            master=self,
            value='newURL',
            orientation='horizontal',
            label=u'URL(s):',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"The URL(s) that will be added to the list when\n"
                u"button 'Add' is clicked.\n\n"
                u"Successive URLs must be separated with ' / ' \n"
                u"(space + slash + space). Their order in the list\n"
                u" will be the same as in this field."
            ),
        )
        gui.separator(widget=addURLBox, height=3)
        basicEncodingsCombobox = gui.comboBox(
            widget=addURLBox,
            master=self,
            value='encoding',
            items=getPredefinedEncodings(),
            sendSelectedValue=True,
            orientation='horizontal',
            label=u'Encoding:',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"Select URL's encoding."
            ),
        )
        addSeparatorAfterDefaultEncodings(basicEncodingsCombobox)
        addAutoDetectEncoding(basicEncodingsCombobox)
        self.encoding = self.encoding
        gui.separator(widget=addURLBox, height=3)
        gui.lineEdit(
            widget=addURLBox,
            master=self,
            value='newAnnotationKey',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"This field lets you specify a custom annotation\n"
                u"key associated with each URL that is about to be\n"
                u"added to the list."
            ),
        )
        gui.separator(widget=addURLBox, height=3)
        gui.lineEdit(
            widget=addURLBox,
            master=self,
            value='newAnnotationValue',
            orientation='horizontal',
            label=u'Annotation value:',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"This field lets you specify the annotation value\n"
                u"associated with the above annotation key."
            ),
        )
        gui.separator(widget=addURLBox, height=3)
        self.addButton = gui.button(
            widget=addURLBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
                u"Add the URL currently displayed in the 'URL'\n"
                u"text field to the list."
            ),
        )
        self.advancedSettings.advancedWidgets.append(self.URLBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Options box...
        self.optionsBox = self.create_widgetbox(
            box=u'Options',
            orientation='vertical',
            addSpace=False,
            )

        optionsBoxLine1 = gui.widgetBox(
            widget=self.optionsBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=optionsBoxLine1,
            master=self,
            value='importURLs',
            label=u'Import URLs with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import URLs as annotations."
            ),
        )
        self.importURLsKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine1,
            master=self,
            value='importURLsKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for importing URLs."
            ),
        )
        gui.separator(widget=self.optionsBox, height=3)
        optionsBoxLine2 = gui.widgetBox(
            widget=self.optionsBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumber',
            label=u'Auto-number with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotate URLs with increasing numeric indices."
            ),
        )
        self.autoNumberKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for URL auto-numbering."
            ),
        )
        gui.separator(widget=self.optionsBox, height=3)
        self.advancedSettings.advancedWidgets.append(self.optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        gui.rubber(self.controlArea)

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.adjustSizeWithTimer()
        QTimer.singleShot(0, self.sendButton.sendIf)
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Data outputs of Segment.Recode
        processed_data = f.result()

        if processed_data:
            message = u'%i segment@p sent to output ' % len(processed_data)
            message = pluralize(message, len(processed_data))
            numChars = 0
            for segment in processed_data:
                segmentLength = len(Segmentation.get_data(segment.str_index))
                numChars += segmentLength
            message += u'(%i character@p).' % numChars
            message = pluralize(message, numChars)
            self.infoBox.setText(message)
            self.send('Text data', processed_data) # AS 11.2023: removed self
            
    def process_data(self, myURLs):
        """ Process data in a worker thread
        instead of the main thread so that
        the operations can be cancelled """
        
        # Emit 1%
        self.signal_prog.emit(1, False)
        
        # Progress bar
        max_itr = len(myURLs)
        cur_itr = 1
        
        URLContents = list()
        annotations = list()
        counter = 1
        
        # Process each URL successively...
        for myURL in myURLs:

            URL = myURL[0]
            if not URL.startswith("http"):
                URL = "http://" + URL
            encoding = myURL[1]
            encoding = re.sub(r"[ ]\(.+", "", encoding)
            annotation_key = myURL[2]
            annotation_value = myURL[3]

            # Try to fetch URL content...
            self.error()
            URLContent = ""
            try:
                URLHandle = urlopen(URL)
                URLContent = URLHandle.read()
                URLHandle.close()
            except http.client.IncompleteRead as e:
                URLContent = e.partial
            except IOError:
                if len(myURLs) > 1:
                    message = u"Couldn't retrieve %s." % URL
                else:
                    message = u"Couldn't retrieve URL."
                
                # Emit message
                self.signal_text.emit(message, 'error')
                
                # Emit finished
                self.signal_prog.emit(100, False)
                
                # Send None
                self.send('Text data', None) # AS 11.2023: removed self
                
                return
            try:
                if encoding == "(auto-detect)":
                    encoding = chardet.detect(URLContent)['encoding']
                URLContent = URLContent.decode(encoding)

            except UnicodeError:
                if len(myURLs) > 1:
                    message = u"Please select another encoding "    \
                              + u"for URL %s." % URL
                else:
                    message = u"Please select another encoding."

                # Emit message
                self.signal_text.emit(message, 'error')
                
                # Emit finished
                self.signal_prog.emit(100, False)
                
                # Send None
                self.send('Text data', None) # AS 11.2023: removed self

                return

            # Replace newlines with '\n'...
            # URLContent = URLContent.replace('\r\n', '\n').replace('\r', '\n')

            # TODO: check if this is more efficient than replace above...
            URLContent = '\n'.join(URLContent.splitlines())

            # Remove utf-8 BOM if necessary...
            if encoding == u'utf-8':
                URLContent = URLContent.lstrip(
                    codecs.BOM_UTF8.decode('utf-8')
                )

            # Normalize text (canonical decomposition then composition)...
            URLContent = normalize('NFC', URLContent)

            URLContents.append(URLContent)

            # Annotations...
            annotation = dict()
            if self.displayAdvancedSettings:
                if annotation_key and annotation_value:
                    annotation[annotation_key] = annotation_value
                if self.importURLs and self.importURLsKey:
                    annotation[self.importURLsKey] = URL
                if self.autoNumber and self.autoNumberKey:
                    annotation[self.autoNumberKey] = counter
                    counter += 1
            annotations.append(annotation)
            
            # Update progress bar manually
            self.signal_prog.emit(int(100*cur_itr/max_itr), False)
            cur_itr += 1
            
            # Cancel operation if requested by user
            if self.cancel_operation:
                self.signal_prog.emit(100, False)
                return

        # Create an LTTL.Input for each URL...
        if len(URLContents) == 1:
            label = self.captionTitle
        else:
            label = None
        for index in range(len(URLContents)):
            myInput = Input(URLContents[index], label)
            segment = myInput[0]
            segment.annotations.update(annotations[index])
            myInput[0] = segment
            self.createdInputs.append(myInput)
            
        # Update infobox and reset progress bar
        self.signal_text.emit(u"Step 2/2: Post-processing...", "warning")
        self.signal_prog.emit(1, True)

        # If there's only one URL, the widget's output is the created Input.
        if len(URLContents) == 1:
            return self.createdInputs[0]
        # Otherwise the widget's output is a concatenation...
        else:
            return Segmenter.concatenate(
                caller=self,
                segmentations=self.createdInputs,
                label=self.captionTitle,
                copy_annotations=True,
                import_labels_as=None,
                sort=False,
                auto_number_as=None,
                merge_duplicates=False,
            )

    def sendData(self):

        """Fetch URL content, create and send segmentation"""

        # Check that there's something on input...
        if (
            (self.displayAdvancedSettings and not self.URLs) or
            not (self.URL or self.displayAdvancedSettings)
        ):
            self.infoBox.setText(u'Please select source URL.', 'warning')
            self.send('Text data', None) # AS 11.2023: removed self
            return

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for auto-numbering.',
                    'warning'
                )
                self.send('Text data', None) # AS 11.2023: removed self
                return
        else:
            autoNumberKey = None

        # Clear created Inputs...
        self.clearCreatedInputs()

        if self.displayAdvancedSettings:
            myURLs = self.URLs
        else:
            myURLs = [[self.URL, self.encoding, u'', u'']]

        # Infobox & progress bar
        self.infoBox.setText(u"Step 1/2: Processing...", "warning")
        self.progressBarInit()        

        # Partial function
        threaded_function = partial(
            self.process_data,
            myURLs
        )

        # Threading ...
        self.threading(threaded_function)
        
    def inputMessage(self, message):
        """Handle JSON message on input connection"""
        if not message:
            return
        self.displayAdvancedSettings = True
        self.advancedSettings.setVisible(True)
        self.clearAll()
        self.infoBox.inputChanged()
        try:
            json_data = json.loads(message.content)
            temp_URLs = list()
            for entry in json_data:
                URL = entry.get('url', '')
                encoding = entry.get('encoding', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                if URL == '' or encoding == '':
                    self.infoBox.setText(
                        u"Please verify keys and values of incoming "
                        u"JSON message.",
                        'error'
                    )
                    self.send('Text data', None) # AS 11.2023: removed self
                    return
                temp_URLs.append((
                    URL,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.URLs.extend(temp_URLs)
            self.sendButton.settingsChanged()
        except ValueError:
            self.infoBox.setText(
                u"Please make sure that incoming message is valid JSON.",
                'error'
            )
            self.send('Text data', None) # AS 11.2023: removed self
            return

    def clearCreatedInputs(self):
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def importList(self):
        """Display a FileDialog and import URL list"""
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            u'Import URL List',
            self.lastLocation,
            u'Text files (*)'
        )
        if not filePath:
            return

        self.file = os.path.normpath(filePath)
        self.lastLocation = os.path.dirname(filePath)
        self.error()
        try:
            fileHandle = codecs.open(filePath, encoding='utf8')
            fileContent = fileHandle.read()
            fileHandle.close()
        except IOError:
            QMessageBox.warning(
                None,
                'Textable',
                "Couldn't open file.",
                QMessageBox.Ok
            )
            return
        try:
            json_data = json.loads(fileContent)
            temp_URLs = list()
            for entry in json_data:
                URL = entry.get('url', '')
                encoding = entry.get('encoding', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                if URL == '' or encoding == '':
                    QMessageBox.warning(
                        None,
                        'Textable',
                        "Selected JSON file doesn't have the right keys "
                        "and/or values.",
                        QMessageBox.Ok
                    )
                    return
                temp_URLs.append((
                    URL,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.URLs.extend(temp_URLs)
            if temp_URLs:
                self.sendButton.settingsChanged()
        except ValueError:
            QMessageBox.warning(
                None,
                'Textable',
                "Selected file is not in JSON format.",
                QMessageBox.Ok
            )
            return

    def exportList(self):
        """Display a FileDialog and export URL list"""
        toDump = list()
        for URL in self.URLs:
            toDump.append({
                'url': URL[0],
                'encoding': URL[1],
            })
            if URL[2] and URL[3]:
                toDump[-1]['annotation_key'] = URL[2]
                toDump[-1]['annotation_value'] = URL[3]
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            u'Export URL List',
            self.lastLocation,
        )

        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            outputFile = codecs.open(
                filePath,
                encoding='utf8',
                mode='w',
                errors='xmlcharrefreplace',
            )
            outputFile.write(
                normalizeCarriageReturns(
                    json.dumps(toDump, sort_keys=True, indent=4)
                )
            )
            outputFile.close()
            QMessageBox.information(
                None,
                'Textable',
                'URL list correctly exported',
                QMessageBox.Ok
            )

    def moveUp(self):
        """Move URL upward in URLs listbox"""
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            if index > 0:
                temp = self.URLs[index-1]
                self.URLs[index-1] = self.URLs[index]
                self.URLs[index] = temp
                self.selectedURLLabel = [index-1]
                self.sendButton.settingsChanged()

    def moveDown(self):
        """Move URL downward in URLs listbox"""
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            if index < len(self.URLs) - 1:
                temp = self.URLs[index+1]
                self.URLs[index+1] = self.URLs[index]
                self.URLs[index] = temp
                self.selectedURLLabel = [index+1]
                self.sendButton.settingsChanged()

    def clearAll(self):
        """Remove all URLs from URLs attr"""
        del self.URLs[:]
        del self.selectedURLLabel[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove URL from URLs attr"""
        if self.selectedURLLabel:
            index = self.selectedURLLabel[0]
            self.URLs.pop(index)
            del self.selectedURLLabel[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add URLs to URLs attr"""
        URLList = re.split(r' +/ +', self.newURL)
        for URL in URLList:
            encoding = re.sub(r"[ ]\(.+", "", self.encoding)
            self.URLs.append((
                URL,
                encoding,
                self.newAnnotationKey,
                self.newAnnotationValue,
            ))
        self.sendButton.settingsChanged()

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedURLLabel:
                cachedLabel = self.selectedURLLabel[0]
            else:
                cachedLabel = None
            del self.URLLabel[:]
            if self.URLs:
                URLs = [f[0] for f in self.URLs]
                encodings = [f[1] for f in self.URLs]
                annotations = ['{%s: %s}' % (f[2], f[3]) for f in self.URLs]
                maxURLLen = max([len(n) for n in URLs])
                maxAnnoLen = max([len(a) for a in annotations])
                for index in range(len(self.URLs)):
                    format = u'%-' + str(maxURLLen + 2) + u's'
                    URLLabel = format % URLs[index]
                    if maxAnnoLen > 4:
                        if len(annotations[index]) > 4:
                            format = u'%-' + str(maxAnnoLen + 2) + u's'
                            URLLabel += format % annotations[index]
                        else:
                            URLLabel += u' ' * (maxAnnoLen + 2)
                    URLLabel += encodings[index]
                    self.URLLabel.append(URLLabel)
            self.URLLabel = self.URLLabel
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedURLLabel = [cachedLabel]
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newURL:
                if (
                    (self.newAnnotationKey and self.newAnnotationValue) or
                    (not self.newAnnotationKey and not self.newAnnotationValue)
                ):
                    self.addButton.setDisabled(False)
                else:
                    self.addButton.setDisabled(True)
            else:
                self.addButton.setDisabled(True)
            if self.autoNumber:
                self.autoNumberKeyLineEdit.setDisabled(False)
            else:
                self.autoNumberKeyLineEdit.setDisabled(True)
            if self.importURLs:
                self.importURLsKeyLineEdit.setDisabled(False)
            else:
                self.importURLsKeyLineEdit.setDisabled(True)
            self.updateURLBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)

    def updateURLBoxButtons(self):
        """Update state of File box buttons"""
        if self.selectedURLLabel:
            self.removeButton.setDisabled(False)
            if self.selectedURLLabel[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedURLLabel[0] < len(self.URLs) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if len(self.URLs):
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(False)
        else:
            self.clearAllButton.setDisabled(True)
            self.exportButton.setDisabled(True)

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.cancel() # Cancel current operation
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.clearCreatedInputs()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    appl = QApplication(sys.argv)
    ow = OWTextableURLs()
    ow.show()
    appl.exec_()
    ow.saveSettings()
