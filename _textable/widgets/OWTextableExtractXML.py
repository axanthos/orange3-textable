"""
Class OWTextableExtractXML
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
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

__version__ = '0.15.6'

import re

from PyQt4.QtGui import QFont

import LTTL.Segmenter as Segmenter
from LTTL.Segmentation import Segmentation

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    pluralize,SendButton, InfoBox, AdvancedSettings
)

from Orange.widgets import widget, gui, settings


class OWTextableExtractXML(OWTextableBaseWidget):
    """Orange widget for xml markup extraction"""

    name = "Extract XML"
    description = "Create a new segmentation based on XML markup"
    icon = "icons/ExtractXML.png"
    priority = 4005

    # Input and output channels...
    inputs = [('Segmentation', Segmentation, "inputData", widget.Single)]
    outputs = [('Extracted data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    autoSend = settings.Setting(True)
    conditions = settings.Setting([])
    importAnnotations = settings.Setting(True)
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    element = settings.Setting(u'')
    importElementAs = settings.Setting(u'')
    mergeDuplicates = settings.Setting(False)
    preserveLeaves = settings.Setting(False)
    deleteMarkup = settings.Setting(False)
    displayAdvancedSettings = settings.Setting(False)

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = u'extracted_xml'
        self.importElement = False

        # Other attributes...
        self.inputSegmentation = None
        self.conditionsLabels = list()
        self.selectedConditionsLabels = list()
        self.newConditionAttribute = u''
        self.newConditionRegex = r''
        self.ignoreCase = False
        self.unicodeDependent = True
        self.multiline = False
        self.dotAll = False
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.sendButton.settingsChanged,
        )

        # GUI...

        self.advancedSettings.draw()

        # XML extraction box
        xmlExtractionBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'XML Extraction',
            orientation='vertical',
        )
        gui.lineEdit(
            widget=xmlExtractionBox,
            master=self,
            value='element',
            orientation='horizontal',
            label=u'XML element:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The XML element that will be extracted from the\n"
                u"input segmentation."
            ),
        )
        gui.separator(widget=xmlExtractionBox, height=3)
        xmlExtractionBoxLine2 = gui.widgetBox(
            widget=xmlExtractionBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        gui.checkBox(
            widget=xmlExtractionBoxLine2,
            master=self,
            value='importElement',
            label=u'Import element with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Associate each output segment with an annotation\n"
                u"whose value is the above specified XML element."
            ),
        )
        self.importElementAsLineEdit = gui.lineEdit(
            widget=xmlExtractionBoxLine2,
            master=self,
            value='importElementAs',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for the XML element."
            ),
        )
        gui.checkBox(
            widget=xmlExtractionBox,
            master=self,
            value='deleteMarkup',
            label=u'Remove markup',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box to remove all XML markup occurring\n"
                u"within the above specified XML element."
            ),
        )
        gui.separator(widget=xmlExtractionBox, height=3)
        gui.checkBox(
            widget=xmlExtractionBox,
            master=self,
            value='preserveLeaves',
            label=u'Prioritize shallow attributes',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"This box lets you indicate how you want to solve\n"
                u"conflicts that may occur in the case where two\n"
                u"or more occurrences of the above specified XML\n"
                u"element are nested and have different values for\n"
                u"the same attribute\n\n"
                u"By default, the attribute value associated with\n"
                u"the deepest element will be used. Check this box\n"
                u"if you would rather use the value of the most\n"
                u"shallow element."
            ),
        )
        gui.separator(widget=xmlExtractionBox, height=3)
        conditionsBox = gui.widgetBox(
            widget=xmlExtractionBox,
            box=u'Conditions',
            orientation='vertical',
        )
        xmlExtractionBoxLine4 = gui.widgetBox(
            widget=conditionsBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        self.conditionsListbox = gui.listBox(
            widget=xmlExtractionBoxLine4,
            master=self,
            value='selectedConditionsLabels',
            labels='conditionsLabels',
            callback=self.updateConditionsBoxButtons,
            tooltip=(
                u"The list of conditions on attribute values that\n"
                u"will be applied to in-/exclude each occurrence\n"
                u"of the above specified XML element in the output\n"
                u"segmentation.\n\n"
                u"Note that all conditions must be satisfied for an\n"
                u"element occurrence to be included.\n\n"
                u"Column 1 shows the name of the attribute.\n"
                u"Column 2 shows the corresponding regex pattern.\n"
                u"Column 3 shows the associated flags."
            ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.conditionsListbox.setFont(font)
        xmlExtractionBoxCol2 = gui.widgetBox(
            widget=xmlExtractionBoxLine4,
            orientation='vertical',
        )
        self.removeButton = gui.button(
            widget=xmlExtractionBoxCol2,
            master=self,
            label=u'Remove',
            callback=self.remove,
            tooltip=(
                u"Remove the selected condition from the list."
            ),
        )
        self.clearAllButton = gui.button(
            widget=xmlExtractionBoxCol2,
            master=self,
            label=u'Clear All',
            callback=self.clearAll,
            tooltip=(
                u"Remove all conditions from the list."
            ),
        )
        xmlExtractionBoxLine5 = gui.widgetBox(
            widget=conditionsBox,
            box=False,
            orientation='vertical',
        )
        # Add condition box
        addConditionBox = gui.widgetBox(
            widget=xmlExtractionBoxLine5,
            box=False,
            orientation='vertical',
        )
        gui.lineEdit(
            widget=addConditionBox,
            master=self,
            value='newConditionAttribute',
            orientation='horizontal',
            label=u'Attribute:',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"The name of attribute in the condition that will\n"
                u"be added to the list when button 'Add' is clicked."
            ),
        )
        gui.separator(widget=addConditionBox, height=3)
        gui.lineEdit(
            widget=addConditionBox,
            master=self,
            value='newConditionRegex',
            orientation='horizontal',
            label=u'Regex:',
            labelWidth=131,
            callback=self.updateGUI,
            tooltip=(
                u"The regex pattern associated with the condition\n"
                u"that will be added to the list when button 'Add'\n"
                u"is clicked."
            ),
        )
        gui.separator(widget=addConditionBox, height=3)
        addConditionBoxLine3 = gui.widgetBox(
            widget=addConditionBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=addConditionBoxLine3,
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
            widget=addConditionBoxLine3,
            master=self,
            value='unicodeDependent',
            label=u'Unicode dependent (u)',
            callback=self.updateGUI,
            tooltip=(
                u"Built-in character classes are Unicode-aware."
            ),
        )
        addConditionBoxLine4 = gui.widgetBox(
            widget=addConditionBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=addConditionBoxLine4,
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
            widget=addConditionBoxLine4,
            master=self,
            value='dotAll',
            label=u'Dot matches all (s)',
            callback=self.updateGUI,
            tooltip=(
                u"Meta-character '.' matches any character (rather\n"
                u"than any character but newline)."
            ),
        )
        gui.separator(widget=addConditionBox, height=3)
        self.addButton = gui.button(
            widget=addConditionBox,
            master=self,
            label=u'Add',
            callback=self.add,
            tooltip=(
                u"Add the current condition to the list."
            ),
        )
        self.advancedSettings.advancedWidgets.append(xmlExtractionBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Options box...
        optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=False,
        )
        optionsBoxLine2 = gui.widgetBox(
            widget=optionsBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
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
        gui.checkBox(
            widget=optionsBox,
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
        gui.separator(widget=optionsBox, height=3)
        gui.checkBox(
            widget=optionsBox,
            master=self,
            value='mergeDuplicates',
            label=u'Fuse duplicates',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Fuse segments that have the same address.\n\n"
                u"The annotation of fused segments will be fused\n"
                u"as well. In the case where fused segments have\n"
                u"distinct values for the same annotation key, only\n"
                u"the value of the last one will be kept."
            ),
        )
        gui.separator(widget=optionsBox, height=2)
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Basic) XML extraction box
        basicXmlExtractionBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'XML Extraction',
            orientation='vertical',
            addSpace=False,
        )
        gui.lineEdit(
            widget=basicXmlExtractionBox,
            master=self,
            value='element',
            orientation='horizontal',
            label=u'XML element:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The XML element that will be extracted from the\n"
                u"input segmentation."
            ),
        )
        gui.separator(widget=basicXmlExtractionBox, height=3)
        gui.checkBox(
            widget=basicXmlExtractionBox,
            master=self,
            value='deleteMarkup',
            label=u'Remove markup',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box to remove all XML markup occurring\n"
                u"within the above specified XML element."
            ),
        )
        gui.separator(widget=basicXmlExtractionBox, height=2)
        self.advancedSettings.basicWidgets.append(basicXmlExtractionBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    def sendData(self):

        """(Have LTTL.Segmenter) perform the actual tokenization"""

        # Check that there's something on input...
        if not self.inputSegmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Extracted data', None, self)
            return

        # Check that element field is not empty...
        if not self.element:
            self.infoBox.setText(u'Please type an XML element', 'warning')
            self.send('Extracted data', None, self)
            return

        # TODO: update docs to indicate that angle brackets are optional
        # TODO: remove message 'No label was provided.' from docs

        # Check that importElementAs is not empty (if necessary)...
        if self.displayAdvancedSettings and self.importElement:
            if self.importElementAs:
                importElementAs = self.importElementAs
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for element import.',
                    'warning'
                )
                self.send('Extracted data', None)
                return
        else:
            importElementAs = None

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
                num_iterations = (2 * len(self.inputSegmentation))
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for auto-numbering.',
                    'warning'
                )
                self.send('Extracted data', None, self)
                return
        else:
            autoNumberKey = None
            num_iterations = len(self.inputSegmentation)

        # Prepare conditions...
        conditions = dict()
        if self.displayAdvancedSettings:
            for condition_idx in range(len(self.conditions)):
                condition = self.conditions[condition_idx]
                attribute = condition[0]
                regex_string = condition[1]
                if (
                    condition[2] or condition[3] or condition[4] or condition[5]
                ):
                    flags = ''
                    if condition[2]:
                        flags += 'i'
                    if condition[3]:
                        flags += 'u'
                    if condition[4]:
                        flags += 'm'
                    if condition[5]:
                        flags += 's'
                    regex_string += '(?%s)' % flags

                try:
                    conditions[attribute] = re.compile(regex_string)
                except re.error as re_error:
                    try:
                        message = u'Please enter a valid regex (error: %s' %   \
                                  re_error.msg
                        if len(self.conditions) > 1:
                            message += u', condition #%i' % (condition_idx + 1)
                        message += u').'
                    except AttributeError:
                        message = u'Please enter a valid regex'
                        if len(self.conditions) > 1:
                            message += u' (condition #%i)' % (condition_idx + 1)
                        message += u'.'
                    self.infoBox.setText(message, 'error')
                    self.send('Extracted data', None, self)
                    return

        # Basic settings...
        if self.displayAdvancedSettings:
            importAnnotations = self.importAnnotations
            preserveLeaves = self.preserveLeaves
            mergeDuplicates = self.mergeDuplicates
            if mergeDuplicates:
                num_iterations += len(self.inputSegmentation)
        else:
            importAnnotations = True
            mergeDuplicates = False
            preserveLeaves = False

        # Perform tokenization...
        progressBar = gui.ProgressBar(
            self,
            iterations=num_iterations
        )
        try:
            xml_extracted_data = Segmenter.import_xml(
                segmentation=self.inputSegmentation,
                element=self.element,
                conditions=conditions,
                import_element_as=importElementAs,
                label=self.captionTitle,
                import_annotations=importAnnotations,
                auto_number_as=autoNumberKey,
                remove_markup=self.deleteMarkup,
                merge_duplicates=mergeDuplicates,
                preserve_leaves=preserveLeaves,
                progress_callback=progressBar.advance,
            )
            message = u'%i segment@p sent to output.' % len(xml_extracted_data)
            message = pluralize(message, len(xml_extracted_data))
            self.infoBox.setText(message)
            self.send('Extracted data', xml_extracted_data, self)
        except ValueError:
            self.infoBox.setText(
                message=u'Please make sure that input is well-formed XML.',
                state='error',
            )
            self.send('Extracted data', None, self)
        self.sendButton.resetSettingsChangedFlag()
        progressBar.finish()

    def inputData(self, segmentation):
        """Process incoming segmentation"""
        self.inputSegmentation = segmentation
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def clearAll(self):
        """Remove all conditions"""
        del self.conditions[:]
        del self.selectedConditionsLabels[:]
        self.sendButton.settingsChanged()

    def remove(self):
        """Remove selected condition"""
        if self.selectedConditionsLabels:
            index = self.selectedConditionsLabels[0]
            self.conditions.pop(index)
            del self.selectedConditionsLabels[:]
            self.sendButton.settingsChanged()

    def add(self):
        """Add condition"""
        self.conditions.append((
            self.newConditionAttribute,
            self.newConditionRegex,
            self.ignoreCase,
            self.unicodeDependent,
            self.multiline,
            self.dotAll,
        ))
        self.sendButton.settingsChanged()

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedConditionsLabels:
                cachedLabel = self.selectedConditionsLabels[0]
            else:
                cachedLabel = None
            del self.conditionsLabels[:]
            if len(self.conditions):
                attrs = [c[0] for c in self.conditions]
                regexes = [c[1] for c in self.conditions]
                maxAttrLen = max([len(a) for a in attrs])
                maxRegexLen = max([len(r) for r in regexes])
                for index in range(len(self.conditions)):
                    format = u'%-' + str(maxAttrLen + 2) + u's'
                    label = format % attrs[index]
                    format = u'%-' + str(maxRegexLen + 2) + u's'
                    label += format % regexes[index]
                    flags = list()
                    if self.conditions[index][2]:
                        flags.append(u'i')
                    if self.conditions[index][3]:
                        flags.append(u'u')
                    if self.conditions[index][4]:
                        flags.append(u'm')
                    if self.conditions[index][5]:
                        flags.append(u's')
                    if len(flags):
                        label += u'[%s]' % ','.join(flags)
                    self.conditionsLabels.append(label)
            self.conditionsLabels = self.conditionsLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedConditionsLabels.listBox.item(
                    cachedLabel
                ).setSelected(1)
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newConditionAttribute and self.newConditionRegex:
                self.addButton.setDisabled(False)
            else:
                self.addButton.setDisabled(True)
            if self.importElement:
                self.importElementAsLineEdit.setDisabled(False)
            else:
                self.importElementAsLineEdit.setDisabled(True)
            if self.autoNumber:
                self.autoNumberKeyLineEdit.setDisabled(False)
            else:
                self.autoNumberKeyLineEdit.setDisabled(True)
            self.updateConditionsBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)

    def updateConditionsBoxButtons(self):
        """Update state of Conditions box buttons"""
        if self.selectedConditionsLabels:
            self.removeButton.setDisabled(False)
        else:
            self.removeButton.setDisabled(True)
        if self.conditions:
            self.clearAllButton.setDisabled(False)
        else:
            self.clearAllButton.setDisabled(True)

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication

    appl = QApplication(sys.argv)
    ow = OWTextableExtractXML()
    ow.show()
    appl.exec_()
    ow.saveSettings()
