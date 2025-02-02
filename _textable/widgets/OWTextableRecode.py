"""
Class OWTextableRecode
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

__version__ = '0.13.11'

import os, re, codecs, json

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import LTTL.SegmenterThread as Segmenter
from LTTL.Segmentation import Segmentation

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, JSONMessage, ProgressBar,
    InfoBox, SendButton, AdvancedSettings, pluralize, normalizeCarriageReturns,
    Task
)

from Orange.widgets import gui, settings

# Threading
from AnyQt.QtCore import QThread, pyqtSlot, pyqtSignal
import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableRecode(OWTextableBaseWidget):
    """Orange widget for regex-based recoding"""

    name= "Recode"
    description = "Custom text recoding using regular expressions"
    icon = "icons/Recode.png"
    priority = 2002

    # Input and output channels...
    inputs = [
        ('Segmentation', Segmentation, "inputData"),
        ('Message', JSONMessage, "inputMessage")
    ]
    outputs = [('Recoded data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    substitutions = settings.Setting([])
    copyAnnotations = settings.Setting(True)
    displayAdvancedSettings = settings.Setting(False)
    lastLocation = settings.Setting('.')
    regex = settings.Setting(u'')
    replString = settings.Setting(u'')

    want_main_area = False

    def __init__(self, *args, **kwargs):

        """Initialize a Recode widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.createdInputIndices = list()
        self.segmentation = None
        self.substLabels = list()
        self.selectedSubstLabels = list()
        self.newRegex = r''
        self.newReplString = r''
        self.ignoreCase = False
        self.unicodeDependent = True
        self.multiline = False
        self.dotAll = False
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually, # Manual cancel button
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = self.create_advancedSettings()

        # GUI...

        self.advancedSettings.draw()

        # Substitutions box
        self.substBox = self.create_widgetbox(
            box=u'Substitutions',
            orientation='vertical',
            addSpace=False,
            )

        substBoxLine1 = gui.widgetBox(
            widget=self.substBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        self.substListbox = gui.listBox(
            widget=substBoxLine1,
            master=self,
            value='selectedSubstLabels',
            labels='substLabels',
            callback=self.updateSubstBoxButtons,
            tooltip=(
                u"The list of substitutions that will be applied to\n"
                u"each segment of the input segmentation.\n\n"
                u"Substitutions will be applied in the same order\n"
                u"as they appear in the list.\n\n"
                u"Column 1 shows the regex pattern.\n"
                u"Column 2 shows the associated replacement string\n"
                u"(if not empty).\n"
                u"Column 3 shows the associated flags."
            ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.substListbox.setFont(font)
        substBoxCol2 = gui.widgetBox(
            widget=substBoxLine1,
            orientation='vertical',
        )
        self.moveUpButton = gui.button(
            widget=substBoxCol2,
            master=self,
            label=u'Move Up',
            callback=self.moveUp,
            tooltip=(
                u"Move the selected substitution upward in the list."
            ),
        )
        self.moveDownButton = gui.button(
            widget=substBoxCol2,
            master=self,
            label=u'Move Down',
            callback=self.moveDown,
            tooltip=(
                u"Move the selected substitution downward in the list."
            ),
        )
        self.removeButton = gui.button(
            widget=substBoxCol2,
            master=self,
            label=u'Remove',
            callback=self.remove,
            tooltip=(
                u"Remove the selected substitution from the list."
            ),
        )
        self.clearAllButton = gui.button(
            widget=substBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all substitutions from the list."
            ),
        )
        self.exportButton = gui.button(
            widget=substBoxCol2,
            master=self,
            label=u'Export JSON',
            callback=self.exportList,
            tooltip=(
                u"Open a dialog for selecting a file where the\n"
                u"substitution list can be exported in JSON format."
            ),
        )
        self.importButton = gui.button(
            widget=substBoxCol2,
            master=self,
            label=u'Import JSON',
            callback=self.importList,
            tooltip=(
                u"Open a dialog for selecting a substitution list\n"
                u"to import (in JSON format). Substitutions from\n"
                u"this list will be added to the existing ones."
            ),
        )
        substBoxLine2 = gui.widgetBox(
            widget=self.substBox,
            box=False,
            orientation='vertical',
        )
        # Add regex box
        addSubstBox = gui.widgetBox(
            widget=substBoxLine2,
            box=True,
            orientation='vertical',
        )
        gui.lineEdit(
            widget=addSubstBox,
            master=self,
            value='newRegex',
            orientation='horizontal',
            label=u'Regex:',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"The regex pattern that will be added to the list\n"
                u"when button 'Add' is clicked."
            ),
        )
        gui.separator(widget=addSubstBox, height=3)
        gui.lineEdit(
            widget=addSubstBox,
            master=self,
            value='newReplString',
            orientation='horizontal',
            label=u'Replacement string:',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"The (possibly empty) replacement string that will\n"
                u"be added to the list when button 'Add' is clicked.\n\n"
                u"Groups of characters captured by parentheses in\n"
                u"the regex pattern may be inserted in the\n"
                u"replacement string by using the form '&'\n"
                u"(ampersand) immediately followed by a digit\n"
                u" indicating the captured group number (e.g. '&1',\n"
                u"'&2', etc.)."

            ),
        )
        gui.separator(widget=addSubstBox, height=3)
        addSubstBoxLine3 = gui.widgetBox(
            widget=addSubstBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=addSubstBoxLine3,
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
            widget=addSubstBoxLine3,
            master=self,
            value='unicodeDependent',
            label=u'Unicode dependent (u)',
            callback=self.updateGUI,
            tooltip=(
                u"Built-in character classes are Unicode-aware."
            ),
        )
        addSubstBoxLine4 = gui.widgetBox(
            widget=addSubstBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=addSubstBoxLine4,
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
            widget=addSubstBoxLine4,
            master=self,
            value='dotAll',
            label=u'Dot matches all (s)',
            callback=self.updateGUI,
            tooltip=(
                u"Meta-character '.' matches any character (rather\n"
                u"than any character but newline)."
            ),
        )
        gui.separator(widget=addSubstBox, height=3)
        self.addButton = gui.button(
            widget=addSubstBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
                u"Add the current substitution to the list."
            ),
        )
        self.advancedSettings.advancedWidgets.append(self.substBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Advanced) Options box...
        self.optionsBox = self.create_widgetbox(
            box=u'Options',
            orientation='vertical',
            addSpace=False,
            )

        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value='copyAnnotations',
            label=u'Copy annotations',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Copy all annotations from input to output segments."
            ),
        )
        gui.separator(widget=self.optionsBox, height=2)
        self.advancedSettings.advancedWidgets.append(self.optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Basic) Substitution box...
        self.basicSubstBox = self.create_widgetbox(
            box=u'Substitution',
            orientation='vertical',
            addSpace=False,
            )

        gui.lineEdit(
            widget=self.basicSubstBox,
            master=self,
            value='regex',
            orientation='horizontal',
            label=u'Regex:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The regex that will be applied to each segment in\n"
                u"the input segmentation."
            ),
        )
        gui.separator(widget=self.basicSubstBox, height=3)
        gui.lineEdit(
            widget=self.basicSubstBox,
            master=self,
            value='replString',
            orientation='horizontal',
            label=u'Replacement string:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The string that will be used for replacing each\n"
                u"match of the above regex in the input segmentation."
            ),
        )
        gui.separator(widget=self.basicSubstBox, height=3)
        self.advancedSettings.basicWidgets.append(self.basicSubstBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        gui.rubber(self.controlArea)

        # Send button and Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Recoded data
        recoded_data, num_subs = f.result()
            
        # Compute difference
        newNumInputs = len(Segmentation.data)
        self.createdInputIndices = range(self.previousNumInputs, newNumInputs)
            
        message = u'%i segment@p sent to output' % len(recoded_data)
        message = pluralize(message, len(recoded_data))
        if num_subs:
            message += u' (%i replacement@p performed).' % num_subs
            message = pluralize(message, num_subs)
        else:
            message += u" (no replacements performed)."
        self.infoBox.setText(message)
        self.send('Recoded data', recoded_data) # AS 10.2023: removed self

    def sendData(self):
        """(Have LTTL.Segmenter) perform the actual recoding"""

        # Check that there's something on input...
        if not self.segmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Recoded data', None) # AS 10.2023: removed self
            return

        # Check that segmentation is non-overlapping...
        if not self.segmentation.is_non_overlapping():
            self.infoBox.setText(
                message=u'Please make sure that input segments are not ' +  \
                        u'overlapping.',
                state='error'
            )
            self.send('Recoded data', None) # AS 10.2023: removed self
            return

        # TODO: remove label message in doc

        # Get substitutions from basic or advanced settings...
        if self.displayAdvancedSettings:
            mySubstitutions = self.substitutions
        else:
            mySubstitutions = [
                [
                    self.regex,
                    self.replString,
                    False,
                    True,
                    False,
                    False,
                ]
            ]
        # Basic settings...
        if self.displayAdvancedSettings:
            copyAnnotations = self.copyAnnotations
        else:
            copyAnnotations = True

        # Prepare regexes...
        substitutions = list()
        for subst_idx in range(len(mySubstitutions)):
            subst = mySubstitutions[subst_idx]
            regex_string = subst[0]
            if subst[2] or subst[3] or subst[4] or subst[5]:
                flags = ''
                if subst[2]:
                    flags += 'i'
                if subst[3]:
                    flags += 'u'
                if subst[4]:
                    flags += 'm'
                if subst[5]:
                    flags += 's'
                regex_string = f"(?{flags}){regex_string}"
            try:
                substitutions.append((re.compile(regex_string), subst[1]))
            except re.error as re_error:
                try:
                    message = u'Please enter a valid regex (error: %s' %    \
                              re_error.msg
                    if self.displayAdvancedSettings and len(mySubstitutions) > 1:
                        message += u', substitution #%i' % (subst_idx + 1)
                    message += u').'
                except AttributeError:
                    message = u'Please enter a valid regex'
                    if self.displayAdvancedSettings and len(mySubstitutions) > 1:
                        message += u' (substitution #%i)' % (subst_idx + 1)
                    message += u'.'
                self.infoBox.setText(
                    message, 'error'
                )
                self.send('Recoded data', None) # AS 10.2023: removed self
                return

        # Perform recoding...
        self.clearCreatedInputIndices()
        self.previousNumInputs = len(Segmentation.data)
        
        # Infobox and progress bar
        self.infoBox.setText(u'Processing...', 'warning')
        self.progressBarInit()
        
        # Partial function
        threaded_function = partial(
            Segmenter.recode,
            caller=self,
            segmentation=self.segmentation,
            substitutions=substitutions,
            label=self.captionTitle,
            copy_annotations=copyAnnotations,
            check_overlap=False,
        )

        # Threading ...
        self.threading(threaded_function)

    def inputMessage(self, message):
        """Handle JSON message on input connection"""
        if not message:
            self.warning()
            self.sendButton.settingsChanged()
            return
        self.displayAdvancedSettings = True
        self.advancedSettings.setVisible(True)
        self.substitutions = list()
        self.infoBox.inputChanged()
        try:
            json_data = json.loads(message.content)
            temp_substitutions = list()
            for entry in json_data:
                regex = entry.get('regex', '')
                replString = entry.get('replacement_string', '')
                ignoreCase = entry.get('ignore_case', False)
                unicodeDependent = entry.get('unicode_dependent', False)
                multiline = entry.get('multiline', False)
                dotAll = entry.get('dot_all', False)
                if regex == '':
                    self.infoBox.setText(
                        u"Please verify keys and values of incoming "
                        u"JSON message.",
                        'error'
                    )
                    self.send('Recoded data', None) # AS 10.2023: removed self
                    return
                temp_substitutions.append((
                    regex,
                    replString,
                    ignoreCase,
                    unicodeDependent,
                    multiline,
                    dotAll,
                ))
            self.substitutions.extend(temp_substitutions)
            self.sendButton.settingsChanged()
        except ValueError:
            self.infoBox.setText(
                u"Please make sure that incoming message is valid JSON.",
                'error'
            )
            self.send('Recoded data', None) # AS 10.2023: removed self
            return

    def inputData(self, segmentation):
        """Process incoming segmentation"""
        # Cancel pending tasks, if any
        self.cancel()
        
        self.segmentation = segmentation
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def importList(self):
        """Display a FileDialog and import substitution list"""
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
            temp_substitutions = list()
            for entry in json_data:
                regex = entry.get('regex', '')
                replString = entry.get('replacement_string', '')
                ignoreCase = entry.get('ignore_case', False)
                unicodeDependent = entry.get('unicode_dependent', False)
                multiline = entry.get('multiline', False)
                dotAll = entry.get('dot_all', False)
                if regex == '':
                    QMessageBox.warning(
                        None,
                        'Textable',
                        "Selected JSON file doesn't have the right keys "
                        "and/or values.",
                        QMessageBox.Ok
                    )
                    return
                temp_substitutions.append((
                    regex,
                    replString,
                    ignoreCase,
                    unicodeDependent,
                    multiline,
                    dotAll,
                ))
            self.substitutions.extend(temp_substitutions)
            if temp_substitutions:
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
        """Display a FileDialog and export substitution list"""
        toDump = list()
        for substitution in self.substitutions:
            toDump.append({
                'regex': substitution[0],
                'replacement_string': substitution[1],
            })
            if substitution[2]:
                toDump[-1]['ignore_case'] = substitution[2]
            if substitution[3]:
                toDump[-1]['unicode_dependent'] = substitution[3]
            if substitution[4]:
                toDump[-1]['multiline'] = substitution[4]
            if substitution[5]:
                toDump[-1]['dot_all'] = substitution[5]
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            u'Export Substitution List',
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
                'Substitution list correctly exported',
                QMessageBox.Ok
            )

    def moveUp(self):
        """Move substitution upward in Substitutions listbox"""
        if self.selectedSubstLabels:
            index = self.selectedSubstLabels[0]
            if index > 0:
                temp = self.substitutions[index-1]
                self.substitutions[index-1] = self.substitutions[index]
                self.substitutions[index] = temp
                self.selectedSubstLabels = [index-1]
                self.sendButton.settingsChanged()

    def moveDown(self):
        """Move substitution downward in Substitutions listbox"""
        if self.selectedSubstLabels:
            index = self.selectedSubstLabels[0]
            if index < len(self.substitutions) - 1:
                temp = self.substitutions[index+1]
                self.substitutions[index+1] = self.substitutions[index]
                self.substitutions[index] = temp
                self.selectedSubstLabels = [index+1]
                self.sendButton.settingsChanged()

    def clearAll(self):
        """Remove all substitutions from Substitutions"""
        del self.substitutions[:]
        del self.selectedSubstLabels[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove substitution from substitutions attr"""
        if self.selectedSubstLabels:
            index = self.selectedSubstLabels[0]
            self.substitutions.pop(index)
            del self.selectedSubstLabels[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add substitution to substitutions attr"""
        self.substitutions.append((
            self.newRegex,
            self.newReplString,
            self.ignoreCase,
            self.unicodeDependent,
            self.multiline,
            self.dotAll,
        ))
        self.sendButton.settingsChanged()

    def clearCreatedInputIndices(self):
        for i in self.createdInputIndices:
            Segmentation.set_data(i, None)

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedSubstLabels:
                cachedLabel = self.selectedSubstLabels[0]
            else:
                cachedLabel = None
            del self.substLabels[:]
            if len(self.substitutions):
                regexes = [r[0] for r in self.substitutions]
                replStrings = [r[1] for r in self.substitutions]
                maxRegexLen = max([len(r) for r in regexes])
                maxReplStringLen = max([len(r) for r in replStrings])
                for index in range(len(self.substitutions)):
                    format = u'%-' + str(maxRegexLen + 2) + u's'
                    substLabel = format % regexes[index]
                    format = u'%-' + str(maxReplStringLen + 2) + u's'
                    substLabel += format % replStrings[index]
                    flags = list()
                    if self.substitutions[index][2]:
                        flags.append(u'i')
                    if self.substitutions[index][3]:
                        flags.append(u'u')
                    if self.substitutions[index][4]:
                        flags.append(u'm')
                    if self.substitutions[index][5]:
                        flags.append(u's')
                    if len(flags):
                        substLabel += u'[%s]' % ','.join(flags)
                    self.substLabels.append(substLabel)
            self.substLabels = self.substLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedSubstLabels = [cachedLabel]
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newRegex:
                self.addButton.setDisabled(False)
            else:
                self.addButton.setDisabled(True)
            self.updateSubstBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)

    def updateSubstBoxButtons(self):
        """Update state of Regex box buttons"""
        if self.selectedSubstLabels:
            self.removeButton.setDisabled(False)
            if self.selectedSubstLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedSubstLabels[0] < len(self.substitutions) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if self.substitutions:
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(False)
        else:
            self.clearAllButton.setDisabled(True)
            self.exportButton.setDisabled(True)

    def onDeleteWidget(self):
        self.clearCreatedInputIndices()

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
    appl = QApplication(sys.argv)
    ow = OWTextableRecode()
    ow.show()
    appl.exec_()
    ow.saveSettings()
