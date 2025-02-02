"""
Class OWTextableTextFiles
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

__version__ = '0.17.12'


import codecs
import os
import re
import json
from unicodedata import normalize

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from chardet.universaldetector import UniversalDetector

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.SegmenterThread as Segmenter

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    JSONMessage, InfoBox, SendButton, AdvancedSettings,
    addSeparatorAfterDefaultEncodings, addAutoDetectEncoding,
    getPredefinedEncodings, normalizeCarriageReturns, pluralize,
    Task
)

from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

CHUNK_LENGTH = 1000000
CHUNK_NUM = 100


class OWTextableTextFiles(OWTextableBaseWidget):
    """Orange widget for loading text files"""

    name = "Text Files"
    description = "Import data from raw text files"
    icon = "icons/TextFiles.png"
    priority = 2

    # Input and output channels...
    inputs = [
        ('Message', JSONMessage, "inputMessage", widget.Single)
    ]
    outputs = [('Text data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    files = settings.Setting([])
    encoding = settings.Setting('(auto-detect)')
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    importFilenames = settings.Setting(True)
    importFilenamesKey = settings.Setting(u'filename')
    lastLocation = settings.Setting('.')
    displayAdvancedSettings = settings.Setting(False)
    file = settings.Setting(u'')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.createdInputs = list()
        self.fileLabels = list()
        self.selectedFileLabels = list()
        self.newFiles = u''
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

        # Basic file box
        self.basicFileBox = self.create_widgetbox(
            box=u'Source',
            orientation='vertical',
            addSpace=False,
            )

        basicFileBoxLine1 = gui.widgetBox(
            widget=self.basicFileBox,
            box=False,
            orientation='horizontal',
        )
        gui.lineEdit(
            widget=basicFileBoxLine1,
            master=self,
            value='file',
            orientation='horizontal',
            label=u'File path:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The path of the file."
            ),
        )
        gui.separator(widget=basicFileBoxLine1, width=5)
        gui.button(
            widget=basicFileBoxLine1,
            master=self,
            label=u'Browse',
            callback=self.browse,
            tooltip=(
                u"Open a dialog for selecting file."
            ),
        )
        gui.separator(widget=self.basicFileBox, width=3)
        advancedEncodingsCombobox = gui.comboBox(
            widget=self.basicFileBox,
            master=self,
            value='encoding',
            items=getPredefinedEncodings(),
            sendSelectedValue=True,
            orientation='horizontal',
            label=u'Encoding:',
            labelWidth=101,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Select input file(s) encoding."
            ),
        )
        addSeparatorAfterDefaultEncodings(advancedEncodingsCombobox)
        addAutoDetectEncoding(advancedEncodingsCombobox)
        gui.separator(widget=self.basicFileBox, width=3)
        self.advancedSettings.basicWidgets.append(self.basicFileBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # ADVANCED GUI...

        # File box
        self.fileBox = self.create_widgetbox(
            box=u'Sources',
            orientation='vertical',
            addSpace=False,
            )

        fileBoxLine1 = gui.widgetBox(
            widget=self.fileBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        self.fileListbox = gui.listBox(
            widget=fileBoxLine1,
            master=self,
            value='selectedFileLabels',
            labels='fileLabels',
            callback=self.updateFileBoxButtons,
            tooltip=(
                u"The list of files whose content will be imported.\n"
                u"\nIn the output segmentation, the content of each\n"
                u"file appears in the same position as in the list.\n"
                u"\nColumn 1 shows the file's name.\n"
                u"Column 2 shows the file's annotation (if any).\n"
                u"Column 3 shows the file's encoding."
            ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.fileListbox.setFont(font)
        fileBoxCol2 = gui.widgetBox(
            widget=fileBoxLine1,
            orientation='vertical',
        )
        self.moveUpButton = gui.button(
            widget=fileBoxCol2,
            master=self,
            label=u'Move Up',
            callback=self.moveUp,
            tooltip=(
                u"Move the selected file upward in the list."
            ),
        )
        self.moveDownButton = gui.button(
            widget=fileBoxCol2,
            master=self,
            label=u'Move Down',
            callback=self.moveDown,
            tooltip=(
                u"Move the selected file downward in the list."
            ),
        )
        self.removeButton = gui.button(
            widget=fileBoxCol2,
            master=self,
            label=u'Remove',
            callback=self.remove,
            tooltip=(
                u"Remove the selected file from the list."
            ),
        )
        self.clearAllButton = gui.button(
            widget=fileBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all files from the list."
            ),
        )
        self.exportButton = gui.button(
            widget=fileBoxCol2,
            master=self,
            label=u'Export JSON',
            callback=self.exportList,
            tooltip=(
                u"Open a dialog for selecting a file where the file\n"
                u"list can be exported in JSON format."
            ),
        )
        self.importButton = gui.button(
            widget=fileBoxCol2,
            master=self,
            label=u'Import JSON',
            callback=self.importList,
            tooltip=(
                u"Open a dialog for selecting a file list to\n"
                u"import (in JSON format). Files from this list\n"
                u"will be added to those already imported."
            ),
        )
        fileBoxLine2 = gui.widgetBox(
            widget=self.fileBox,
            box=False,
            orientation='vertical',
        )
        # Add file box
        addFileBox = gui.widgetBox(
            widget=fileBoxLine2,
            box=True,
            orientation='vertical',
        )
        addFileBoxLine1 = gui.widgetBox(
            widget=addFileBox,
            orientation='horizontal',
        )
        gui.lineEdit(
            widget=addFileBoxLine1,
            master=self,
            value='newFiles',
            orientation='horizontal',
            label=u'File path(s):',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"The paths of the files that will be added to the\n"
                u"list when button 'Add' is clicked.\n\n"
                u"Successive paths must be separated with ' / ' \n"
                u"(whitespace + slash + whitespace). Their order in\n"
                u"the list will be the same as in this field."
            ),
        )
        gui.separator(widget=addFileBoxLine1, width=5)
        gui.button(
            widget=addFileBoxLine1,
            master=self,
            label=u'Browse',
            callback=self.browse,
            tooltip=(
                u"Open a dialog for selecting files.\n\n"
                u"To select multiple files at once, either draw a\n"
                u"selection box around them, or use shift and/or\n"
                u"ctrl + click.\n\n"
                u"Selected file paths will appear in the field to\n"
                u"the left of this button afterwards, ready to be\n"
                u"added to the list when button 'Add' is clicked."
            ),
        )
        gui.separator(widget=addFileBox, width=3)
        basicEncodingsCombobox = gui.comboBox(
            widget=addFileBox,
            master=self,
            value='encoding',
            items=getPredefinedEncodings(),
            sendSelectedValue=True,
            orientation='horizontal',
            label=u'Encoding:',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"Select input file(s) encoding."
            ),
        )
        addSeparatorAfterDefaultEncodings(basicEncodingsCombobox)
        addAutoDetectEncoding(basicEncodingsCombobox)
        self.encoding = self.encoding
        gui.separator(widget=addFileBox, width=3)
        gui.lineEdit(
            widget=addFileBox,
            master=self,
            value='newAnnotationKey',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=101,
            callback=self.updateGUI,
            tooltip=(
                u"This field lets you specify a custom annotation\n"
                u"key associated with each file that is about to be\n"
                u"added to the list."
            ),
        )
        gui.separator(widget=addFileBox, width=3)
        gui.lineEdit(
            widget=addFileBox,
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
        gui.separator(widget=addFileBox, width=3)
        self.addButton = gui.button(
            widget=addFileBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
                u"Add the file(s) currently displayed in the\n"
                u"'Files' text field to the list.\n\n"
                u"Each of these files will be associated with the\n"
                u"specified encoding and annotation (if any).\n\n"
                u"Other files may be selected afterwards and\n"
                u"assigned a different encoding and annotation."
            ),
        )
        self.advancedSettings.advancedWidgets.append(self.fileBox)
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
            value='importFilenames',
            label=u'Import file names with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import file names as annotations."
            ),
        )
        self.importFilenamesKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine1,
            master=self,
            value='importFilenamesKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for importing file names."
            ),
        )
        gui.separator(widget=self.optionsBox, width=3)
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
                u"Annotate files with increasing numeric indices."
            ),
        )
        self.autoNumberKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for file auto-numbering."
            ),
        )
        gui.separator(widget=self.optionsBox, width=3)
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
        # Data outputs
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
            
    def process_data(self, myFiles):
        """ Process data in a worker thread
        instead of the main thread so that
        the operations can be cancelled """
        
        # Emit 1%
        self.signal_prog.emit(1, False)
        
        # Progress bar
        max_itr = len(myFiles)
        cur_itr = 1

        fileContents = list()
        annotations = list()
        counter = 1
    
        # Open and process each file successively...
        for myFile in myFiles:
            filePath = myFile[0]
            encoding = myFile[1]
            encoding = re.sub(r"[ ]\(.+", "", encoding)
            annotation_key = myFile[2]
            annotation_value = myFile[3]

            # Try to open the file...
            self.error()

            try:
                if encoding == "(auto-detect)":
                    detector = UniversalDetector()
                    fh = open(filePath, 'rb')
                    for line in fh:
                        detector.feed(line)
                        if detector.done: break
                    detector.close()
                    fh.close()
                    encoding = detector.result['encoding']
                fh = open(
                    filePath,
                    mode='r',
                    encoding=encoding,
                )
                try:
                    fileContent = ""
                    i = 0
                    chunks = list()
                    for chunk in iter(lambda: fh.read(CHUNK_LENGTH), ""):
                        chunks.append('\n'.join(chunk.splitlines()))
                        i += CHUNK_LENGTH
                        if i % (CHUNK_NUM * CHUNK_LENGTH) == 0:
                            fileContent += "".join(chunks)
                            chunks = list()
                    if len(chunks):
                        fileContent += "".join(chunks)
                    del chunks

                except UnicodeError:
                    if len(myFiles) > 1:
                        message = u"Please select another encoding "    \
                                  + u"for file %s." % filePath
                    else:
                        message = u"Please select another encoding."
                    
                    # Emit message
                    self.signal_text.emit(message, 'error')
                    
                    # Emit finished
                    self.signal_prog.emit(100, False)
                    
                    # Send None
                    self.send('Text data', None) # AS 11.2023: removed self
                    
                    return

                finally:
                    fh.close()

            except IOError:
                if len(myFiles) > 1:
                    message = u"Couldn't open file '%s'." % filePath
                else:
                    message = u"Couldn't open file."
                
                # Emit message
                self.signal_text.emit(message, 'error')
                
                # Emit finished
                self.signal_prog.emit(100, False)
                
                # Send None
                self.send('Text data', None) # AS 11.2023: removed self

                return

            # Remove utf-8 BOM if necessary...
            if encoding == u'utf-8':
                fileContent = fileContent.lstrip(
                    codecs.BOM_UTF8.decode('utf-8')
                )

            # Normalize text (canonical decomposition then composition)...
            fileContent = normalize('NFC', fileContent)

            fileContents.append(fileContent)

            # Annotations...
            annotation = dict()
            if self.displayAdvancedSettings:
                if annotation_key and annotation_value:
                    annotation[annotation_key] = annotation_value
                if self.importFilenames and self.importFilenamesKey:
                    filename = os.path.basename(filePath)
                    annotation[self.importFilenamesKey] = filename
                if self.autoNumber and self.autoNumberKey:
                    annotation[self.autoNumberKey] = counter
                    counter += 1
            annotations.append(annotation)

            # Update progress bar manually
            self.signal_prog.emit(int(100*cur_itr/max_itr), False)
            cur_itr += 1
            
            # Cancel operation if requested by uers
            if self.cancel_operation:
                self.signal_prog.emit(100, False)
                return

        # Create an LTTL.Input for each file...
        if len(fileContents) == 1:
            label = self.captionTitle
        else:
            label = None
        for index in range(len(fileContents)):
            myInput = Input(fileContents[index], label)
            segment = myInput[0]
            segment.annotations.update(annotations[index])
            myInput[0] = segment
            self.createdInputs.append(myInput)

        # Update infobox and reset progress bar
        self.signal_text.emit(u"Step 2/2: Post-processing...", "warning")
        self.signal_prog.emit(1, True)

        # If there's only one file, the widget's output is the created Input.
        if len(fileContents) == 1:
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

        """Load files, create and send segmentation"""

        # Check that there's something on input...
        if (
            (self.displayAdvancedSettings and not self.files) or
            not (self.file or self.displayAdvancedSettings)
        ):
            self.infoBox.setText(u'Please select input file.', 'warning')
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
            myFiles = self.files
        else:
            myFiles = [[self.file, self.encoding, u'', u'']]

        # Infobox & progress bar
        self.infoBox.setText(u"Step 1/2: Processing...", "warning")
        self.progressBarInit()

        # Partial function
        threaded_function = partial(
            self.process_data,
            myFiles
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
            temp_files = list()
            for entry in json_data:
                path = entry.get('path', '')
                encoding = entry.get('encoding', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                if path == '' or encoding == '':
                    self.infoBox.setText(
                        u"Please verify keys and values of incoming "
                        u"JSON message.",
                        'error'
                    )
                    self.send('Text data', None) # AS 11.2023: removed self
                    return
                temp_files.append((
                    path,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.files.extend(temp_files)
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
        """Display a FileDialog and import file list"""
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            u'Import File List',
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
            temp_files = list()
            for entry in json_data:
                path = entry.get('path', '')
                encoding = entry.get('encoding', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                if path == '' or encoding == '':
                    QMessageBox.warning(
                        None,
                        'Textable',
                        "Selected JSON file doesn't have the right keys "
                        "and/or values.",
                        QMessageBox.Ok
                    )
                    return
                temp_files.append((
                    path,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.files.extend(temp_files)
            if temp_files:
                self.sendButton.settingsChanged()
        except ValueError:
            QMessageBox.warning(
                None,
                'Textable',
                "JSON parsing error.",
                QMessageBox.Ok
            )
            return

    def exportList(self):
        """Display a FileDialog and export file list"""
        toDump = list()
        for myfile in self.files:
            toDump.append({
                'path': myfile[0],
                'encoding': myfile[1],
            })
            if myfile[2] and myfile[3]:
                toDump[-1]['annotation_key'] = myfile[2]
                toDump[-1]['annotation_value'] = myfile[3]
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            u'Export File List',
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
                'File list correctly exported',
                QMessageBox.Ok
            )

    def browse(self):
        """Display a FileDialog and select files"""
        if self.displayAdvancedSettings:
            filePathList, _ = QFileDialog.getOpenFileNames(
                self,
                u'Select Text File(s)',
                self.lastLocation,
                u'Text files (*)'
            )
            if not filePathList:
                return
            filePathList = [os.path.normpath(f) for f in filePathList]
            self.newFiles = u' / '.join(filePathList)
            self.lastLocation = os.path.dirname(filePathList[-1])
            self.updateGUI()
        else:
            filePath, _ = QFileDialog.getOpenFileName(
                self,
                u'Open Text File',
                self.lastLocation,
                u'Text files (*)'
            )
            if not filePath:
                return
            self.file = os.path.normpath(filePath)
            self.lastLocation = os.path.dirname(filePath)
            self.updateGUI()
            self.sendButton.settingsChanged()

    def moveUp(self):
        """Move file upward in Files listbox"""
        if self.selectedFileLabels:
            index = self.selectedFileLabels[0]
            if index > 0:
                temp = self.files[index-1]
                self.files[index-1] = self.files[index]
                self.files[index] = temp
                self.selectedFileLabels = [index-1]
                self.sendButton.settingsChanged()

    def moveDown(self):
        """Move file downward in Files listbox"""
        if self.selectedFileLabels:
            index = self.selectedFileLabels[0]
            if index < len(self.files) - 1:
                temp = self.files[index+1]
                self.files[index+1] = self.files[index]
                self.files[index] = temp
                self.selectedFileLabels = [index+1]
                self.sendButton.settingsChanged()

    def clearAll(self):
        """Remove all files from files attr"""
        del self.files[:]
        del self.selectedFileLabels[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove file from files attr"""
        if self.selectedFileLabels:
            index = self.selectedFileLabels[0]
            self.files.pop(index)
            del self.selectedFileLabels[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add files to files attr"""
        filePathList = re.split(r' +/ +', self.newFiles)
        for filePath in filePathList:
            encoding = re.sub(r"[ ]\(.+", "", self.encoding)
            self.files.append((
                filePath,
                encoding,
                self.newAnnotationKey,
                self.newAnnotationValue,
            ))
        self.sendButton.settingsChanged()

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedFileLabels:
                cachedLabel = self.selectedFileLabels[0]
            else:
                cachedLabel = None
            del self.fileLabels[:]
            if self.files:
                filePaths = [f[0] for f in self.files]
                filenames = [os.path.basename(p) for p in filePaths]
                encodings = [f[1] for f in self.files]
                annotations = ['{%s: %s}' % (f[2], f[3]) for f in self.files]
                maxFilenameLen = max([len(n) for n in filenames])
                maxAnnoLen = max([len(a) for a in annotations])
                for index in range(len(self.files)):
                    format = u'%-' + str(maxFilenameLen + 2) + u's'
                    fileLabel = format % filenames[index]
                    if maxAnnoLen > 4:
                        if len(annotations[index]) > 4:
                            format = u'%-' + str(maxAnnoLen + 2) + u's'
                            fileLabel += format % annotations[index]
                        else:
                            fileLabel += u' ' * (maxAnnoLen + 2)
                    fileLabel += encodings[index]
                    self.fileLabels.append(fileLabel)
            self.fileLabels = self.fileLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedFileLabels = [cachedLabel]
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newFiles:
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
            if self.importFilenames:
                self.importFilenamesKeyLineEdit.setDisabled(False)
            else:
                self.importFilenamesKeyLineEdit.setDisabled(True)
            self.updateFileBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)

    def updateFileBoxButtons(self):
        """Update state of File box buttons"""
        if self.selectedFileLabels:
            self.removeButton.setDisabled(False)
            if self.selectedFileLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedFileLabels[0] < len(self.files) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if len(self.files):
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
    ow = OWTextableTextFiles()
    ow.show()
    appl.exec_()
    ow.saveSettings()
