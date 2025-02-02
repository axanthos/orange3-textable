"""
Class OWTextableSegment
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

__version__ = '0.21.11'

import os, re, codecs, json

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import LTTL.SegmenterThread as Segmenter
from LTTL.Segmentation import Segmentation

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    JSONMessage, InfoBox, SendButton, AdvancedSettings,
    normalizeCarriageReturns, pluralize,
    Task
)

import Orange
from Orange.widgets import widget, gui, settings

# Threading
from AnyQt.QtCore import QThread, pyqtSlot, pyqtSignal
import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableSegment(OWTextableBaseWidget):
    """Orange widget for regex-based tokenization"""

    name = "Segment"
    description = "Subdivide a segmentation using regular expressions"
    icon = "icons/Segment.png"
    priority = 4002

    # Input and output channels...
    inputs = [
        ('Segmentation', Segmentation, "inputData",),
        ('Message', JSONMessage, "inputMessage",)
    ]
    outputs = [('Segmented data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    regexes = settings.Setting([])
    segmentType = settings.Setting(u'Segment into words')
    importAnnotations = settings.Setting(True)
    mergeDuplicates = settings.Setting(False)
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    displayAdvancedSettings = settings.Setting(False)
    lastLocation = settings.Setting('.')
    regex = settings.Setting(u'')
    mode = settings.Setting(u'Tokenize')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Manual cancel (cancel button)
        manualCancel = partial(self.cancel, True) # True = "Aborted by user!"

        self.inputSegmentation = None
        self.regexLabels = list()
        self.selectedRegexLabels = list()
        self.newRegex = r''
        self.newAnnotationKey = r''
        self.newAnnotationValue = r''
        self.ignoreCase = False
        self.unicodeDependent = True
        self.multiline = False
        self.dotAll = False
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=manualCancel, # Manual cancel button
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = self.create_advancedSettings()

        # GUI...

        self.advancedSettings.draw()

        # Regexes box
        self.regexBox = self.create_widgetbox(
            box =u'Regexes',
            orientation='vertical',
            addSpace=False,
        )
        regexBoxLine1 = gui.widgetBox(
            widget=self.regexBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        self.regexListbox = gui.listBox(
            widget=regexBoxLine1,
            master=self,
            value='selectedRegexLabels',
            labels='regexLabels',
            callback=self.updateRegexBoxButtons,
            tooltip=(
                u"The list of regexes that will be applied to each\n"
                u"segment of the input segmentation.\n\n"
                u"Regexes will be applied in the same order as they\n"
                u"appear in the list.\n\n"
                u"Column 1 shows the segmentation mode.\n"
                u"Column 2 shows the regex pattern.\n"
                u"Column 3 shows the associated annotation (if any).\n"
                u"Column 4 shows the associated flags."
            ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.regexListbox.setFont(font)
        regexBoxCol2 = gui.widgetBox(
            widget=regexBoxLine1,
            orientation='vertical',
        )
        self.moveUpButton = gui.button(
            widget=regexBoxCol2,
            master=self,
            label=u'Move Up',
            callback=self.moveUp,
            tooltip=(
                u"Move the selected regex upward in the list."
            ),
        )
        self.moveDownButton = gui.button(
            widget=regexBoxCol2,
            master=self,
            label=u'Move Down',
            callback=self.moveDown,
            tooltip=(
                u"Move the selected regex downward in the list."
            ),
        )
        self.removeButton = gui.button(
            widget=regexBoxCol2,
            master=self,
            label=u'Remove',
            callback=self.remove,
            tooltip=(
                u"Remove the selected regex from the list."
            ),
        )
        self.clearAllButton = gui.button(
            widget=regexBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all regexes from the list."
            ),
        )
        self.exportButton = gui.button(
            widget=regexBoxCol2,
            master=self,
            label=u'Export JSON',
            callback=self.exportList,
            tooltip=(
                u"Open a dialog for selecting a file where the\n"
                u"regex list can be exported in JSON format."
            ),
        )
        self.importButton = gui.button(
            widget=regexBoxCol2,
            master=self,
            label=u'Import JSON',
            callback=self.importList,
            tooltip=(
                u"Open a dialog for selecting a regex list to\n"
                u"import (in JSON format). Regexes from this list\n"
                u"will be added to the existing ones."
            ),
        )
        regexBoxLine2 = gui.widgetBox(
            widget=self.regexBox,
            box=False,
            orientation='vertical',
        )
        # Add regex box
        addRegexBox = gui.widgetBox(
            widget=regexBoxLine2,
            box=True,
            orientation='vertical',
            addSpace=False,
        )
        self.modeCombo = gui.comboBox(
            widget=addRegexBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[u'Tokenize', u'Split'],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=131,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Segmentation mode.\n\n"
                u"'Tokenize': the regex specifies the form of\n"
                u"segments themselves.\n\n"
                u"'Split': the regex specifies the form of\n"
                u"character sequences occuring between the segments."
            ),
        )
        self.modeCombo.setMinimumWidth(120)
        gui.separator(
            widget=addRegexBox,
            height=3,
        )
        gui.lineEdit(
            widget=addRegexBox,
            master=self,
            value='newRegex',
            orientation='horizontal',
            label=u'Regex:',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"The regex pattern that will be added to the list\n"
                u"when button 'Add' is clicked. Commonly used\n"
                u"segmentation units include:\n"
                u"1) .\tcharacters (except newline)\n"
                u'2) \w\t"letters" (alphanumeric chars and underscores)\n'
                u'3) \w+\t"words" (sequences of "letters")\n'
                u"4) .+\tlines\n"
                u"and so on."
            ),
        )
        gui.separator(
            widget=addRegexBox,
            height=3,
        )
        gui.lineEdit(
            widget=addRegexBox,
            master=self,
            value='newAnnotationKey',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"This field lets you specify a custom annotation\n"
                u"key for segments identified by the regex pattern\n"
                u"about to be added to the list.\n\n"
                u"Groups of characters captured by parentheses in\n"
                u"the regex pattern may be inserted in the\n"
                u"annotation value by using the form '&' (ampersand)\n"
                u"immediately followed by a digit indicating the\n"
                u"captured group number (e.g. '&1', '&2', etc.)."
            ),
        )
        gui.separator(
            widget=addRegexBox,
            height=3,
        )
        gui.lineEdit(
            widget=addRegexBox,
            master=self,
            value='newAnnotationValue',
            orientation='horizontal',
            label=u'Annotation value:',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"This field lets you specify a custom annotation\n"
                u"value for segments identified by the regex pattern\n"
                u"about to be added to the list.\n\n"
                u"Groups of characters captured by parentheses in\n"
                u"the regex pattern may be inserted in the\n"
                u"annotation value by using the form '&' (ampersand)\n"
                u"immediately followed by a digit indicating the\n"
                u"captured group number (e.g. '&1', '&2', etc.)."
            ),
        )
        gui.separator(
            widget=addRegexBox,
            height=3,
        )
        addRegexBoxLine1 = gui.widgetBox(
            widget=addRegexBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=addRegexBoxLine1,
            master=self,
            value='ignoreCase',
            label=u'Ignore case (i)',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"Regex pattern is case-insensitive."
            ),
        )
        gui.checkBox(
            widget=addRegexBoxLine1,
            master=self,
            value='unicodeDependent',
            label=u'Unicode dependent (u)',
            callback=self.updateGUI,
            tooltip=(
                u"Built-in character classes are Unicode-aware."
            ),
        )
        addRegexBoxLine2 = gui.widgetBox(
            widget=addRegexBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=addRegexBoxLine2,
            master=self,
            value='multiline',
            label=u'Multiline (m)',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"Anchors '^' and '$' match the beginning and\n"
                u"end of each line (rather than just the beginning\n"
                u"and end of each input segment)."
            ),
        )
        gui.checkBox(
            widget=addRegexBoxLine2,
            master=self,
            value='dotAll',
            label=u'Dot matches all (s)',
            callback=self.updateGUI,
            tooltip=(
                u"Meta-character '.' matches any character (rather\n"
                u"than any character but newline)."
            ),
        )
        gui.separator(
            widget=addRegexBox,
            height=3,
        )
        self.addButton = gui.button(
            widget=addRegexBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
                u"Add the regex pattern currently displayed in the\n"
                u"'Regex' text field to the list."
            ),
        )
        self.advancedSettings.advancedWidgets.append(self.regexBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Advanced) options box...
        self.optionsBox = self.create_widgetbox(
            box=u'Options',
            orientation='vertical',
            addSpace=False,
            )

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
                u"Annotate output segments with increasing numeric\n"
                u"indices."
            ),
        )
        self.autoNumberKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for output segment auto-numbering."
            ),
        )
        gui.separator(
            widget=self.optionsBox,
            height=3,
        )
        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value='importAnnotations',
            label=u'Import annotations',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Add to each output segment the annotation keys\n"
                u"and values associated with the corresponding\n"
                u"input segment."
            ),
        )
        gui.separator(
            widget=self.optionsBox,
            height=3,
        )
        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value='mergeDuplicates',
            label=u'Fuse duplicates',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Fuse segments that have the same address.\n\n"
                u"The annotation of merged segments will be fused\n"
                u"as well. In the case where fused segments have\n"
                u"distinct values for the same annotation key, only\n"
                u"the value of the last one (in order of regex\n"
                u"application) will be kept."
            ),
        )
        gui.separator(
            widget=self.optionsBox,
            height=2,
        )
        self.advancedSettings.advancedWidgets.append(self.optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Basic) Regex box...
        self.basicRegexBox = self.create_widgetbox(
            box=u'Segment type',
            orientation='vertical',
            addSpace=False,)

        self.segmentTypeCombo = gui.comboBox(
            widget=self.basicRegexBox,
            master=self,
            value='segmentType',
            sendSelectedValue=True,
            items=[
                u'Segment into letters',
                u'Segment into words',
                u'Segment into lines',
                u'Use a regular expression',
            ],
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify the kind of units into which the data will\n"
                u"be segmented (letters, words, lines, or custom\n"
                u"units defined using a regular expression)."
            ),
        )
        self.basicRegexFieldBox = gui.widgetBox(
            widget=self.basicRegexBox,
            box=False,
            orientation='vertical',
        )
        gui.separator(
            widget=self.basicRegexFieldBox,
            height=2,
        )
        gui.lineEdit(
            widget=self.basicRegexFieldBox,
            master=self,
            value='regex',
            orientation='horizontal',
            label=u'Regex:',
            labelWidth=60,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"A pattern that specifies the form of units into\n"
                u"which the data will be segmented."
            ),
        )
        gui.separator(
            widget=self.basicRegexBox,
            height=3,
        )
        self.advancedSettings.basicWidgets.append(self.basicRegexBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        gui.rubber(self.controlArea)

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    def inputMessage(self, message):
        """Handle JSON message on input connection"""
        if not message:
            self.warning()
            self.sendButton.settingsChanged()
            return
        self.displayAdvancedSettings = True
        self.advancedSettings.setVisible(True)
        self.regexes = list()
        self.infoBox.inputChanged()
        try:
            json_data = json.loads(message.content)
            temp_regexes = list()
            for entry in json_data:
                regex = entry.get('regex', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                ignoreCase = entry.get('ignore_case', False)
                unicodeDependent = entry.get('unicode_dependent', False)
                multiline = entry.get('multiline', False)
                dotAll = entry.get('dot_all', False)
                mode = entry.get('mode', '')
                if regex == '' or mode == '':
                    self.infoBox.setText(
                        u"Please verify keys and values of incoming "
                        u"JSON message.",
                        'error'
                    )
                    self.send('Segmented data', None) # AS 10.2023: removed self
                    return
                temp_regexes.append(
                    (
                        regex,
                        annotationKey,
                        annotationValue,
                        ignoreCase,
                        unicodeDependent,
                        multiline,
                        dotAll,
                        mode,
                    )
                )
            self.regexes.extend(temp_regexes)
            self.sendButton.settingsChanged()
        except ValueError:
            self.infoBox.setText(
                u"Please make sure that incoming message is valid JSON.",
                'error'
            )
            self.send('Segmented data', None) # AS 10.2023: removed self
            return
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Data outputs
        try:
            segmented_data = f.result()
        # If operation was started again while processing,
        # f.result() is None and it raises a TypeError
        except TypeError:
            self.infoBox.setText(
                    u'Operation was cancelled.',
                    'warning'
                )
            self.send('Segmented data', None)
            self.manageGuiVisibility(False) # Processing done/cancelled!
            return

        # Processing results
        message = u'%i segment@p sent to output.' % len(segmented_data)
        message = pluralize(message, len(segmented_data))
        self.infoBox.setText(message)
        self.send('Segmented data', segmented_data) # AS 10.2023: removed self

    def sendData(self):
        """(Have LTTL.Segmenter) perform the actual tokenization"""

        # Check that there's something on input...
        if not self.inputSegmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Segmented data', None) # AS 10.2023: removed self
            return

        # Check that there's at least one regex (if needed)...
        if (
            (self.displayAdvancedSettings and not self.regexes) or (
                self.segmentType == 'Use a regular expression' and
                not (self.regex or self.displayAdvancedSettings)
            )
        ):
            self.infoBox.setText(u'Please enter a regex.', 'warning')
            self.send('Segmented data', None) # AS 10.2023: removed self
            return

        # Get regexes from basic or advanced settings...
        regexForType = {
            u'Segment into letters': r'\w',
            u'Segment into words': r'\w+',
            u'Segment into lines': r'.+',
        }
        if self.displayAdvancedSettings:
            myRegexes = self.regexes
        elif self.segmentType == 'Use a regular expression':
            myRegexes = [
                [
                    self.regex,
                    None,
                    None,
                    False,
                    True,
                    False,
                    False,
                    u'tokenize',
                ]
            ]
        else:
            myRegexes = [
                [
                    regexForType[self.segmentType],
                    None,
                    None,
                    False,
                    True,
                    False,
                    False,
                    u'tokenize',
                ]
            ]

        # TODO: remove message 'No label was provided.' from docs

        if self.displayAdvancedSettings:
            importAnnotations = self.importAnnotations
            if self.autoNumber:
                autoNumberKey = self.autoNumberKey
                if autoNumberKey == '':
                    self.infoBox.setText(
                        u'Please enter an annotation key for auto-numbering.',
                        'warning'
                    )
                    self.send('Segmented data', None) # AS 10.2023: removed self
                    return
            else:
                autoNumberKey = None
            mergeDuplicates = self.mergeDuplicates
        else:
            importAnnotations = True
            autoNumberKey = None
            mergeDuplicates = False

        # Prepare regexes...
        regexes = list()
        for regex_idx in range(len(myRegexes)):
            regex = myRegexes[regex_idx]
            regex_string = regex[0]
            if regex[3] or regex[4] or regex[5] or regex[6]:
                flags = ''
                if regex[3]:
                    flags += 'i'
                if regex[4]:
                    flags += 'u'
                if regex[5]:
                    flags += 'm'
                if regex[6]:
                    flags += 's'
                regex_string = f"(?{flags}){regex_string}"
            try:
                if regex[1] and regex[2]:
                    regexes.append(
                        (
                            re.compile(regex_string),
                            (regex[7].lower()),
                            {regex[1]: regex[2]}
                        )
                    )
                else:
                    regexes.append((re.compile(regex_string), regex[7].lower()))
            except re.error as re_error:
                try:
                    message = u'Please enter a valid regex (error: %s' %    \
                              re_error.msg
                    if self.displayAdvancedSettings and len(myRegexes) > 1:
                        message += u', regex #%i' % (regex_idx + 1)
                    message += u').'
                except AttributeError:
                    message = u'Please enter a valid regex'
                    if self.displayAdvancedSettings and len(myRegexes) > 1:
                        message += u' (regex #%i)' % (regex_idx + 1)
                    message += u'.'
                self.infoBox.setText(message, 'error')
                self.send('Segmented data', None) # AS 10.2023: removed self
                return
        
        # Deal with amount of steps
        total_steps = 1 # minimum amount of steps
        if mergeDuplicates:
            total_steps += 1
        if autoNumberKey:
            total_steps += 1

        # Infobox and progress bar
        self.progressBarInit()
        
        if total_steps == 1:
            self.infoBox.setText(u'Processing...', 'warning')
        else:
            self.infoBox.setText(f'Step 1/{total_steps}: Processing...', 'warning')
        
        # Partial function for threading
        threaded_function = partial(
            Segmenter.tokenize,
            segmentation=self.inputSegmentation,
            regexes=regexes,
            caller=self,
            label=self.captionTitle,
            import_annotations=importAnnotations,
            merge_duplicates=mergeDuplicates,
            auto_number_as=autoNumberKey,
            total_steps=total_steps,
        )

        # Threading ...
        self.threading(threaded_function)

    def inputData(self, segmentation):
        """Process incoming segmentation"""
        # Cancel pending tasks, if any
        self.cancel()

        self.inputSegmentation = segmentation
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def importList(self):
        """Display a FileDialog and import regex list"""
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            u'Import Regex List',
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
            temp_regexes = list()
            for entry in json_data:
                regex = entry.get('regex', '')
                annotationKey = entry.get('annotation_key', '')
                annotationValue = entry.get('annotation_value', '')
                ignoreCase = entry.get('ignore_case', False)
                unicodeDependent = entry.get('unicode_dependent', False)
                multiline = entry.get('multiline', False)
                dotAll = entry.get('dot_all', False)
                mode = entry.get('mode', '')
                if regex == '' or mode == '':
                    QMessageBox.warning(
                        None,
                        'Textable',
                        "Selected JSON file doesn't have the right keys "
                        "and/or values.",
                        QMessageBox.Ok
                    )
                    return
                temp_regexes.append(
                    (
                        regex,
                        annotationKey,
                        annotationValue,
                        ignoreCase,
                        unicodeDependent,
                        multiline,
                        dotAll,
                        mode,
                    )
                )
            self.regexes.extend(temp_regexes)
            if temp_regexes:
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
        """Display a FileDialog and export regex list"""
        toDump = list()
        for regex in self.regexes:
            toDump.append({
                'regex': regex[0],
                'mode': regex[7],
            })
            if regex[1] and regex[2]:
                toDump[-1]['annotation_key'] = regex[1]
                toDump[-1]['annotation_value'] = regex[2]
            if regex[3]:
                toDump[-1]['ignore_case'] = regex[3]
            if regex[4]:
                toDump[-1]['unicode_dependent'] = regex[4]
            if regex[5]:
                toDump[-1]['multiline'] = regex[5]
            if regex[6]:
                toDump[-1]['dot_all'] = regex[6]
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            u'Export Regex List',
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
                'Regex list correctly exported',
                QMessageBox.Ok
            )

    def moveUp(self):
        """Move regex upward in Regexes listbox"""
        if self.selectedRegexLabels:
            index = self.selectedRegexLabels[0]
            if index > 0:
                temp = self.regexes[index-1]
                self.regexes[index-1] = self.regexes[index]
                self.regexes[index] = temp
                self.selectedRegexLabels = [index-1]
                self.sendButton.settingsChanged()

    def moveDown(self):
        """Move regex downward in Regexes listbox"""
        if self.selectedRegexLabels:
            index = self.selectedRegexLabels[0]
            if index < len(self.regexes)-1:
                temp = self.regexes[index+1]
                self.regexes[index+1] = self.regexes[index]
                self.regexes[index] = temp
                self.selectedRegexLabels = [index+1]
                self.sendButton.settingsChanged()

    def clearAll(self):
        """Remove all regexes from Regexes"""
        del self.regexes[:]
        del self.selectedRegexLabels[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove regex from regexes attr"""
        if self.selectedRegexLabels:
            index = self.selectedRegexLabels[0]
            self.regexes.pop(index)
            del self.selectedRegexLabels[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add regex to regexes attr"""
        
        # AS 11.2023
        # Verify validity of regex
        try:
            re.compile(self.newRegex)
        except re.error as re_error:
            try:
                message = u'Please enter a valid regex (error: %s' %    \
                          re_error.msg + u')'
            except AttributeError:
                    message = u'Please enter a valid regex'
            self.infoBox.setText(message, 'error')
            return

        self.regexes.append((
            self.newRegex,
            self.newAnnotationKey,
            self.newAnnotationValue,
            self.ignoreCase,
            self.unicodeDependent,
            self.multiline,
            self.dotAll,
            self.mode,
        ))
        self.sendButton.settingsChanged()
        
        # AS 11.2023
        # Regex correctly added message
        self.infoBox.setText(u'Regex correctly added', 'warning')

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedRegexLabels:
                cachedLabel = self.selectedRegexLabels[0]
            else:
                cachedLabel = None
            del self.regexLabels[:]
            if len(self.regexes):
                regexes = [r[0] for r in self.regexes]
                annotations = [
                    '{%s: %s}' % (r[1], r[2]) for r in self.regexes
                    ]
                maxRegexLen = max([len(r) for r in regexes])
                maxAnnoLen = max([len(a) for a in annotations])
                for index in range(len(self.regexes)):
                    regexLabel = u'(%s)  ' % self.regexes[index][7][0].lower()
                    format = u'%-' + str(maxRegexLen + 2) + u's'
                    regexLabel += format % regexes[index]
                    if maxAnnoLen > 4:
                        if len(annotations[index]) > 4:
                            format = u'%-' + str(maxAnnoLen + 2) + u's'
                            regexLabel += format % annotations[index]
                        else:
                            regexLabel += u' ' * (maxAnnoLen + 2)
                    flags = list()
                    if self.regexes[index][3]:
                        flags.append(u'i')
                    if self.regexes[index][4]:
                        flags.append(u'u')
                    if self.regexes[index][5]:
                        flags.append(u'm')
                    if self.regexes[index][6]:
                        flags.append(u's')
                    if len(flags):
                        regexLabel += u'[%s]' % ','.join(flags)
                    self.regexLabels.append(regexLabel)
            self.regexLabels = self.regexLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedRegexLabels = [cachedLabel]
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newRegex:
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
            self.updateRegexBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)
            self.basicRegexFieldBox.setVisible(
                self.segmentType == 'Use a regular expression'
            )

    def updateRegexBoxButtons(self):
        """Update state of Regex box buttons"""
        if self.selectedRegexLabels:
            self.removeButton.setDisabled(False)
            if self.selectedRegexLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedRegexLabels[0] < len(self.regexes) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if self.regexes:
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

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableSegment()
    ow.inputData(Input('a simple example'))
    ow.show()
    appl.exec_()
    ow.saveSettings()
