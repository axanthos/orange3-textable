"""
Class OWTextableTreetagger
Copyright 2017 LangTech Sarl
Based on an original prototype developed by Xavier Barros
-------------------------------------------------------------------------------
This file is part of the Orange-Textable package v3.0.

Orange-Textable v3.0 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange-Textable v3.0 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable v3.0. If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = u"0.1.6"

import os
import re

from Orange.widgets import gui, settings

from PyQt4.QtGui import QFileDialog, QMessageBox

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
import LTTL.Segmenter as Segmenter

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton
)

import appdirs
import treetaggerwrapper
import pycountry


class Treetagger(OWTextableBaseWidget):
    """Orange widget for POS-tagging and lemmatization with Treetagger"""

    name = "Treetagger"
    description = "POS-tagging and lemmatization with Treetagger"
    icon = "icons/treetagger.svg"
    priority = 2003

    inputs = [("Segmentation", Segmentation, "inputData")]
    outputs = [("Tagged data", Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    autoSend = settings.Setting(False)
    language = settings.Setting(0)
    replaceUnknown = settings.Setting(False)
    outputFormat = settings.Setting("segment into words")

    want_main_area = False

    configFilePath = os.path.normpath(
        appdirs.user_data_dir("textable", "langtech") + "/treetagger_path"
    )

    def __init__(self, *args, **kwargs):
        """Initialize a Message widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.segmentation = None
        self.createdInputs = list()
        self.noLanguageParameterWarning = (
            "Please make sure that at least one language parameter "
            "file is installed in your Treetagger 'lib' directory, "
            "then click 'Reload language parameter files'."
        )
        self.noTreetaggerPathWarning = (
            "Please click 'Locate Treetagger' below and select the "
            "base directory of a valid Treetagger distribution."
        )
        self.TreetaggerPath = (
            treetaggerwrapper.locate_treetagger() or
            self.lookupSavedTreetaggerPath()
        )

        self.infoBox = InfoBox(widget=self.controlArea)

        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute=u"infoBox",
            sendIfPreCallback=self.updateGUI
        )

        gui.separator(self.controlArea, height=3)

        self.optionsBox = gui.widgetBox(
            self.controlArea,
            u"Options",
        )

        self.languageCombobox = gui.comboBox(
            widget=self.optionsBox,
            master=self,
            value="language",
            items=list(),
            sendSelectedValue=True,
            orientation=u"horizontal",
            label="Input language:",
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"TODO."
            ),
        )
        self.languageCombobox.setMinimumWidth(120)

        gui.separator(self.optionsBox, height=3)

        gui.comboBox(
            widget=self.optionsBox,
            master=self,
            value="outputFormat",
            items=[
                "segment into words",
                "add XML tags",
            ],
            sendSelectedValue=True,
            orientation=u"horizontal",
            label="Output format:",
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"TODO."
            ),
        )

        gui.separator(self.optionsBox, height=3)

        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value="replaceUnknown",
            label="Output token in place of [unknown] lemmas",
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"TODO."
            ),
        )

        gui.rubber(self.controlArea)

        self.sendButton.draw()
        self.infoBox.draw()

        self.locateTreetaggerBox=gui.widgetBox(
            self.controlArea,
            addSpace=False,
        )

        gui.separator(self.locateTreetaggerBox, height=3)

        self.treetaggerButton = gui.button(
            widget=self.locateTreetaggerBox,
            master=self,
            label="Locate Treetagger",
            callback=self.validateTreetagger,
            tooltip=(
                u"TODO."
            ),
        )

        self.sendButton.sendIf()

        self.adjustSizeWithTimer()

    def inputData(self, inputData):
        """Process incoming data."""
        self.segmentation = inputData
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):

        # Clear created Inputs...
        self.clearCreatedInputs()

        if not self.TreetaggerPath:
            self.infoBox.setText(self.noTreetaggerPathWarning, "warning")
            self.send("Tagged data", None)
            return
        elif not self.getAvailableLanguages():
            self.infoBox.setText(self.noLanguageParameterWarning, "warning")
            self.send("Tagged data", None)
            return
        elif not self.segmentation:
            self.infoBox.setText(
                u"Widget needs input",
                "warning"
            )
            self.send("Tagged data", None)
            return

        self.infoBox.setText(
            u"Treetagger is running...",
            "warning"
        )

        # Initialize progress bar.
        self.progressBar = gui.ProgressBar(
            self,
            iterations = 5
        )

        # Create a copy of input seg, storing annotations in temp attr...
        copy_of_input_seg = Segmentation()
        copy_of_input_seg.label = self.segmentation.label
        for seg_idx, segment in enumerate(self.segmentation):
            attr = " ".join(
                ["%s='%s'" % item for item in segment.annotations.items()]
            )
            segment.annotations["tt_ax"] = attr
            copy_of_input_seg.append(segment)

        self.progressBar.advance()

        # Dump segmentation in unique string to avoid multiple calls to TT...
        concatenated_text = copy_of_input_seg.to_string(
            formatting="<ax_tt %(tt_ax)s>%(__content__)s</ax_tt>",
            display_all=True,
        )

        self.progressBar.advance()

        # Tag the segmentation contents...
        tagopt = '-token -lemma -sgml -quiet'
        if self.replaceUnknown:
            tagopt += " -no-unknown"
        tagger = treetaggerwrapper.TreeTagger(
            TAGLANG=pycountry.languages.get(name=self.language).alpha_2,
            TAGOPT=tagopt,
            TAGDIR=self.TreetaggerPath,
        )
        tagged_lines = tagger.tag_text(
            concatenated_text,
            notagurl=True,
            notagemail=True,
            notagip=True,
            notagdns=True,
        )
        tagged_input = Input("\n".join(tagged_lines))
        self.createdInputs.append(tagged_input)

        # Re-segment to match the original segmentation structure.
        tagged_segmentation = Segmenter.import_xml(tagged_input, "ax_tt")

        self.progressBar.advance()

        # Replace <unknown> with [unknown], " with &quot; and place
        # each output line of Treetagger in an xml tag with annotations...
        xml_segmentation, _ = Segmenter.recode(
            tagged_segmentation,
            substitutions = [
                (re.compile(r"<unknown>"), "[unknown]"),
                (re.compile(
                    r"(.+)\t(.+)\t(.+?)(?=[\r\n])"),
                    '<w lemma="&3" pos-tag="&2">&1</w>'
                ),
                (re.compile(r'"""'), '"&quot;"'),
                (re.compile(r'^\n|\n$'), ''),
            ],
        )
        # Segment into individual tokens if XML output option is disabled...
        if self.outputFormat == "add XML tags":
            output_segmentation = xml_segmentation
        else:
            try:
                output_segmentation = Segmenter.import_xml(
                    xml_segmentation,
                    "w"
                )
            except ValueError:
                self.infoBox.setText(
                    "Please check that either the input contains well-formed "
                    "XML, or it doesn't contain instances of '&#60;' and '\x3e'",
                    "error"
                )
                self.send("Tagged data", None)
                self.progressBar.finish()
                return

        self.progressBar.finish()

        output_segmentation.label = self.captionTitle
        message = u'%i segment@p sent to output.' % len(output_segmentation)
        message = pluralize(message, len(output_segmentation))
        self.infoBox.setText(message)
        self.send('Tagged data', output_segmentation, self)
        self.sendButton.resetSettingsChangedFlag()

    def updateGUI(self):
        """Update GUI state"""
        if self.TreetaggerPath:
            self.optionsBox.setDisabled(False)
            self.locateTreetaggerBox.setVisible(False)
            self.languageCombobox.clear()
            languages = self.getAvailableLanguages()
            if not languages:
                self.infoBox.setText(self.noLanguageParameterWarning, "warning")
                self.optionsBox.setDisabled(True)
                self.locateTreetaggerBox.setVisible(True)
                self.treetaggerButton.setText("Reload language parameter files")
            else:
                self.language = self.language or languages[0]
        else:
            self.infoBox.setText(self.noTreetaggerPathWarning, "warning")
            self.optionsBox.setDisabled(True)
            self.locateTreetaggerBox.setVisible(True)
        self.adjustSizeWithTimer()

    def getAvailableLanguages(self):
        languages = list()
        for lang_code in sorted(treetaggerwrapper.g_langsupport):
            if lang_code.startswith("__"):
                continue
            try:
                treetaggerwrapper.TreeTagger(
                    TAGLANG=lang_code,
                    TAGDIR=self.TreetaggerPath,
                )
                language = pycountry.languages.get(alpha_2=lang_code).name
                self.languageCombobox.addItem(language)
                languages.append(language)
            except:
                pass
        return languages

    def lookupSavedTreetaggerPath(self):
        """Look for a saved Treetagger base dir path in app data"""
        if os.path.exists(self.__class__.configFilePath):
            try:
                inputFile = open(self.__class__.configFilePath, "r")
                TreetaggerSavedPath = inputFile.read()
                inputFile.close()
                if self.checkTreetaggerPath(TreetaggerSavedPath):
                    return TreetaggerSavedPath
                else:
                    os.remove(self.__class__.configFilePath)
                    return None
            except IOError:
                pass

    def validateTreetagger(self):
        """Respond to user actions needed to validate Treetagger path"""

        # If the Treetagger path is known, make sure there are language files...
        if self.TreetaggerPath:
            if self.getAvailableLanguages():
                self.sendButton.settingsChanged()
                self.updateGUI()
            else:
                QMessageBox.warning(
                    None,
                    'Textable',
                    'Language parameter files not found.',
                    QMessageBox.Ok
                )
            return

        # Else if the path is not known...

        # First try to locate it automatically...
        TreetaggerPath = treetaggerwrapper.locate_treetagger()

        # If it fails, let the user locate it manually...
        if not (TreetaggerPath and self.checkTreetaggerPath(TreetaggerPath)):

            TreetaggerManualPath = os.path.normpath(
                str(
                    QFileDialog.getExistingDirectory(
                        self, u"Please locate Treetagger base directory"
                    )
                )
            )

            # If user selected a dir...
            if TreetaggerManualPath:

                # Check if selected dir contains Treetagger binary...
                if self.checkTreetaggerPath(TreetaggerManualPath):
                    TreetaggerPath = TreetaggerManualPath
                else:
                    QMessageBox.warning(
                        None,
                        'Textable',
                        'Not a valid Treetagger base directory.',
                        QMessageBox.Ok
                    )

        # If a valid path was found somehow, save config to app data...
        if TreetaggerPath:
            try:
                user_data_editor_dir = os.path.normpath(
                    self.__class__.configFilePath + "/../.."
                )
                if not os.path.exists(user_data_editor_dir):
                    os.makedirs(user_data_editor_dir)
                user_data_software_dir = os.path.normpath(
                    self.__class__.configFilePath + "/.."
                )
                if not os.path.exists(user_data_software_dir):
                    os.makedirs(user_data_software_dir)
                outputFile = open(self.__class__.configFilePath, "w")
                outputFile.write(TreetaggerPath)
                outputFile.close()
            except IOError:
                pass
            self.TreetaggerPath = TreetaggerPath

            self.sendButton.settingsChanged()

    def checkTreetaggerPath(self, path):
        """Check if path is a valid Treetagger base dir"""
        return os.path.exists(
            os.path.normpath(
                path + "/bin/tree-tagger" + (".exe" if os.name == "nt" else "")
            )
        )

    def clearCreatedInputs(self):
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]

    def onDeleteWidget(self):
        """Free memory when widget is deleted (overriden method)"""
        self.clearCreatedInputs()

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)


if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    myApplication = QApplication(sys.argv)
    myWidget = Treetagger()
    myWidget.show()
    myWidget.segmentation = Input("My tailor is rich.")
    myWidget.language = "English"
    myWidget.sendData()
    myApplication.exec_()
