#=============================================================================
# Class OWTextableConvert, v0.07
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
<name>Convert</name>
<description>Convert a Textable table to Orange format</description>
<icon>icons/Convert.png</icon>
<priority>10001</priority>
"""

import os, codecs

from LTTL.Table import *

from TextableUtils import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableConvert(OWWidget):

    """Orange widget for converting a Textable table to an Orange table"""

    settingsList = [
            'conversionEncoding',
            'exportEncoding',
            'includeOrangeHeaders',
            'sortRows',
            'sortRowsReverse',
            'sortCols',
            'sortColsReverse',
            'normalize',
            'normalizeMode',
            'normalizeType',
            'transpose',
            'reformat',
            'autoSend',
            'lastLocation',
            'displayAdvancedSettings',
    ]

    # Predefined list of available encodings...
    encodings = getPredefinedEncodings()

    def __init__(self, parent=None, signalManager=None):
        
        """Initialize a Transform widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                'TextableConvert',
                wantMainArea=0,
        )
        
        self.inputs  = [('Textable table', Table, self.inputData, Single)]
        self.outputs = [('Orange table', ExampleTable)]

        # Settings...
        self.sortRows                   = False
        self.sortRowsReverse            = False
        self.sortCols                   = False
        self.sortColsReverse            = False
        self.normalize                  = False
        self.normalizeMode              = 'rows'
        self.normalizeType              = 'l1'
        self.transpose                  = False
        self.reformat                   = False
        self.autoSend                   = True
        self.conversionEncoding         = 'iso-8859-15'
        self.exportEncoding             = 'utf-8'
        self.includeOrangeHeaders       = False
        self.lastLocation               = '.'
        self.displayAdvancedSettings    = False
        self.loadSettings()

        # Other attributes...
        self.targetFormat           = None
        self.sortRowsKeyId          = None
        self.sortColsKeyId          = None
        self.table                  = None
        self.infoBox                = InfoBox(widget=self.controlArea)
        self.sendButton             = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
                sendIfPreCallback   = self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendButton.settingsChanged,
        )

        # GUI...

        # Advanced settings checkbox...
        self.advancedSettings.draw()

        # Transform box
        self.transformBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Transform',
                orientation         = 'vertical',
        )
        self.transformBoxLine1 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine1,
                master              = self,
                value               = 'sortRows',
                label               = u'Sort rows by column:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort table rows."
                ),
        )
        self.sortRowsKeyIdCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine1,
                master              = self,
                value               = 'sortRowsKeyId',
                items               = [],
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Column whose values will be used for sorting rows."
                ),
        )
        self.sortRowsKeyIdCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine1,
                width               = 5,
        )
        self.sortRowsReverseCheckBox = OWGUI.checkBox(
                widget              = self.transformBoxLine1,
                master              = self,
                value               = 'sortRowsReverse',
                label               = u'Reverse',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort rows in reverse (i.e. decreasing) order."
                ),
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transformBoxLine2 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine2,
                master              = self,
                value               = 'sortCols',
                label               = u'Sort columns by row:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort table columns."
                ),
        )
        self.sortColsKeyIdCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine2,
                master              = self,
                value               = 'sortColsKeyId',
                items               = [],
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Row whose values will be used for sorting columns."
                ),
        )
        self.sortColsKeyIdCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine2,
                width               = 5,
        )
        self.sortColsReverseCheckBox = OWGUI.checkBox(
                widget              = self.transformBoxLine2,
                master              = self,
                value               = 'sortColsReverse',
                label               = u'Reverse',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort columns in reverse (i.e. decreasing) order."
                ),
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transposeCheckBox = OWGUI.checkBox(
                widget              = self.transformBox,
                master              = self,
                value               = 'transpose',
                label               = u'Transpose',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Transpose table (i.e. exchange rows and columns)."
                ),
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transformBoxLine4 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine4,
                master              = self,
                value               = 'normalize',
                label               = u'Normalize:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Normalize table."
                ),
        )
        self.normalizeModeCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine4,
                master              = self,
                value               = 'normalizeMode',
                items               = [u'rows', u'columns', u'table'],
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Select the units to which normalization will be\n"
                        u"applied: rows, columns, or the entire table."
                ),
        )
        self.normalizeModeCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine4,
                width               = 5,
        )
        self.normalizeTypeCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine4,
                master              = self,
                orientation         = 'horizontal',
                value               = 'normalizeType',
                items               = [u'L1', u'L2'],
                sendSelectedValue   = True,
                label               = u'Norm:',
                labelWidth          = 40,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Norm type.\n\n"
                        u"L1: divide each value by the sum of the enclosing\n"
                        u"normalization unit (row/column/table)\n\n"
                        u"L2: divide each value by the sum of squares of the\n"
                        u"enclosing normalization unit, then take square root."
                ),
        )
        self.normalizeTypeCombo.setMinimumWidth(60)
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transformBoxLine5 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine5,
                master              = self,
                value               = 'reformat',
                label               = u'Reformat to:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Apply crosstab format conversion."
                ),
        )
        self.targetFormatCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine5,
                master              = self,
                value               = 'targetFormat',
                items               = [],
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Crosstab format conversion.\n\n"
                        u"Available conversions depend on the format ot the\n"
                        u"input crosstab.\n\n"
                        u"Pivot crosstab: standard, human-readable format\n"
                        u"for contigency tables, where each row and column\n"
                        u"corresponds to a category and the value in each\n"
                        u"cell is the joint count of categories.\n\n"
                        u"Flat crosstab: machine-readable format where each\n"
                        u"row corresponds to an occurrence of a pair of\n"
                        u"categories (needed for correspondence analysis in\n"
                        u"Orange Canvas, notably).\n\n"
                        u"Weighted flat crosstab: similar to flat crosstab,\n"
                        u"but each row corresponds to a type of category\n"
                        u"pair and an extra column indicates the number of\n"
                        u"occurrences of this type."
                ),
        )
        self.targetFormatCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine5,
                width               = 5,
        )
        dummyLabel = OWGUI.widgetLabel(
                widget              = self.transformBoxLine5,
                label               = '',
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.advancedSettings.advancedWidgets.append(self.transformBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Conversion box
        conversionBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Conversion',
                orientation         = 'vertical',
                addSpace            = True,
        )
        conversionBoxLine1 = OWGUI.widgetBox(
                widget              = conversionBox,
                orientation         = 'horizontal',
        )
        OWGUI.widgetLabel(
                widget              = conversionBoxLine1,
                labelWidth          = 180,
                label               = u'Orange table encoding:',
        )
        conversionEncodingCombo = OWGUI.comboBox(
                widget              = conversionBoxLine1,
                master              = self,
                value               = 'conversionEncoding',
                items               = type(self).encodings,
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                orientation         = 'horizontal',
                tooltip             = (
                        u"Select Orange table encoding."
                ),
        )
        conversionEncodingCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = conversionBoxLine1,
                width               = 5,
        )
        dummyLabel = OWGUI.widgetLabel(
                widget              = conversionBoxLine1,
                label               = '',
        )
        OWGUI.separator(
                widget              = conversionBox,
                height              = 3,
        )

        # Export box
        exportBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Export',
                orientation         = 'vertical',
                addSpace            = True,
        )
        exportBoxLine1 = OWGUI.widgetBox(
                widget              = exportBox,
                orientation         = 'horizontal',
        )
        OWGUI.widgetLabel(
                widget              = exportBoxLine1,
                labelWidth          = 180,
                label               = u'Output file encoding:',
        )
        exportEncodingCombo = OWGUI.comboBox(
                widget              = exportBoxLine1,
                master              = self,
                value               = 'exportEncoding',
                items               = type(self).encodings,
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                orientation         = 'horizontal',
                tooltip             = (
                        u"Select output file encoding."
                ),
        )
        exportEncodingCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = exportBoxLine1,
                width               = 5,
        )
        dummyLabel = OWGUI.widgetLabel(
                widget              = exportBoxLine1,
                label               = '',
        )
        OWGUI.separator(
                widget              = exportBox,
                height              = 2,
        )
        OWGUI.checkBox(
                widget              = exportBox,
                master              = self,
                value               = 'includeOrangeHeaders',
                label               = u'Include Orange headers',
                tooltip             = (
                        u"Include Orange table headers in output file."
                ),
        )
        OWGUI.separator(
                widget              = exportBox,
                height              = 2,
        )
        self.exportButton = OWGUI.button(
                widget              = exportBox,
                master              = self,
                label               = u'Export',
                callback            = self.exportFile,
                tooltip             = (
                        u"Open a dialog for selecting the output file."
                ),
        )
        OWGUI.separator(
                widget              = exportBox,
                height              = 2,
        )

        # Info box...
        self.infoBox.draw()

        # Send button and checkbox
        self.sendButton.draw()

        self.sendButton.sendIf()


    def inputData(self, newInput):
        """Process incoming data."""
        self.table = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()


    def sendData(self):

        """Convert and send table"""

        # Check that there is something on input...
        if not self.table:
            self.infoBox.noDataSent(u'No input.')
            self.send('Orange table', None)
            return

        transformed_table = self.table

        if self.displayAdvancedSettings:

            # Sort if needed...
            if self.sortRows or self.sortCols:
                rows = {'reverse': self.sortRowsReverse}
                cols = {'reverse': self.sortColsReverse}
                if self.sortRows:
                    if self.sortRowsKeyId == 0:
                        rows['key_id'] = transformed_table.header_col['id']
                    else:
                        rows['key_id'] = transformed_table.col_ids[
                                self.sortRowsKeyId - 1
                        ]
                if self.sortCols:
                    if self.sortColsKeyId == 0:
                        cols['key_id'] = transformed_table.header_row['id']
                    else:
                        cols['key_id'] = transformed_table.row_ids[
                                self.sortColsKeyId - 1
                        ]
                transformed_table = transformed_table.to_sorted(rows, cols)

            # Transpose if needed...
            if self.transpose:
                transformed_table = transformed_table.to_transposed()

            # Normalize if needed...
            if self.normalize:
                transformed_table = transformed_table.to_normalized(
                        self.normalizeMode,
                        self.normalizeType.lower()
                )

            # Convert if needed...
            if self.reformat:
                format = self.targetFormatCombo.itemText(self.targetFormat)
                if format == 'pivot crosstab':
                    transformed_table = transformed_table.to_pivot()
                elif format == 'flat crosstab':
                    transformed_table = transformed_table.to_flat()
                elif format == 'weighted flat crosstab':
                    transformed_table = transformed_table.to_weighted_flat()
                    
        self.transformed_table = transformed_table

        orangeTable = transformed_table.to_orange_table(
            encoding = self.conversionEncoding,
        )

        self.send('Orange table', orangeTable)
        message = 'Table has %i rows and %i columns.' % (
                len(transformed_table.row_ids),
                len(transformed_table.col_ids)+1,
        )
        self.infoBox.dataSent(message)
        self.sendButton.resetSettingsChangedFlag()


    def exportFile(self):
        """Display a FileDialog and save table to file"""
        filePath = unicode(
                QFileDialog.getSaveFileName(
                        self,
                        u'Export Table to File',
                        self.lastLocation,
                )
        )
        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            outputString = self.transformed_table.to_string(
                    output_orange_headers = self.includeOrangeHeaders,
            )
            outputFile = codecs.open(
                    filePath,
                    encoding    = self.exportEncoding,
                    mode        = 'w',
                    errors      = 'xmlcharrefreplace',
            )
            outputFile.write(outputString)
            outputFile.close()
            QMessageBox.information(
                    None,
                    'Textable',
                    'Table correctly exported',
                    QMessageBox.Ok
            )



    def updateGUI(self):

        """Update GUI state"""

        if not self.table:
            self.transformBox.setDisabled(True)
            self.exportButton.setDisabled(True)

        else:
            self.transformBox.setDisabled(False)
            self.exportButton.setDisabled(False)

            if self.displayAdvancedSettings:
                if self.sortRows:
                    self.sortRowsKeyIdCombo.clear()
                    self.sortRowsKeyIdCombo.addItem(
                        self.table.header_col['id']
                    )
                    for col_id in self.table.col_ids:
                        self.sortRowsKeyIdCombo.addItem(col_id)
                    self.sortRowsKeyId = self.sortRowsKeyId or 0
                    self.sortRowsKeyIdCombo.setDisabled(False)
                    self.sortRowsReverseCheckBox.setDisabled(False)
                else:
                    self.sortRowsKeyIdCombo.setDisabled(True)
                    self.sortRowsKeyIdCombo.clear()
                    self.sortRowsReverseCheckBox.setDisabled(True)

                if self.sortCols:
                    self.sortColsKeyIdCombo.clear()
                    self.sortColsKeyIdCombo.addItem(
                        self.table.header_row['id']
                    )
                    for row_id in self.table.row_ids:
                        self.sortColsKeyIdCombo.addItem(row_id)
                    self.sortColsKeyId = self.sortColsKeyId or 0
                    self.sortColsKeyIdCombo.setDisabled(False)
                    self.sortColsReverseCheckBox.setDisabled(False)
                else:
                    self.sortColsKeyIdCombo.setDisabled(True)
                    self.sortColsKeyIdCombo.clear()
                    self.sortColsReverseCheckBox.setDisabled(True)

                if isinstance(self.table, Crosstab):
                    self.targetFormatCombo.clear()
                    if isinstance(self.table, FlatCrosstab):
                        self.targetFormatCombo.addItem(u'pivot crosstab')
                        self.targetFormatCombo.addItem(
                                u'weighted flat crosstab'
                        )
                        self.targetFormat = self.targetFormat or 0
                    elif isinstance(self.table, WeightedFlatCrosstab):
                        self.targetFormatCombo.addItem(u'pivot crosstab')
                        self.targetFormatCombo.addItem(u'flat crosstab')
                        self.targetFormat = self.targetFormat or 0
                    self.transformBoxLine5.setDisabled(False)
                    if self.reformat:
                        self.targetFormatCombo.setDisabled(False)
                    else:
                        self.targetFormatCombo.setDisabled(True)
                else:
                    self.transformBoxLine5.setDisabled(True)
                    self.reformat = False

                if isinstance(self.table, PivotCrosstab):
                    self.targetFormatCombo.addItem(u'flat crosstab')
                    self.targetFormatCombo.addItem(u'weighted flat crosstab')
                    self.targetFormat = self.targetFormat or 0
                    if not self.reformat:
                        self.transformBoxLine4.setDisabled(False)
                        if self.normalize:
                            self.normalizeModeCombo.setDisabled(False)
                            self.normalizeTypeCombo.setDisabled(False)
                            self.transformBoxLine5.setDisabled(True)
                        else:
                            self.normalizeModeCombo.setDisabled(True)
                            self.normalizeTypeCombo.setDisabled(True)
                            self.transformBoxLine5.setDisabled(False)
                    else:
                        self.transformBoxLine4.setDisabled(True)
                    self.transposeCheckBox.setDisabled(False)
                else:
                    self.transformBoxLine4.setDisabled(True)
                    self.normalize = False
                    self.transposeCheckBox.setDisabled(True)
                    self.transpose = False

        self.advancedSettings.setVisible(self.displayAdvancedSettings)



if __name__ == '__main__':
    from LTTL.Table import *
    appl = QApplication(sys.argv)
    ow   = OWTextableConvert()
    ow.show()
    t = PivotCrosstab(
            ['c', 'a', 'b'],
            ['B', 'C', 'A'],
            {
                    ('a', 'A'): 2,
                    ('a', 'B'): 3,
                    ('b', 'A'): 4,
                    ('b', 'C'): 2,
                    ('c', 'A'): 1,
                    ('c', 'B'): 4,
                    ('c', 'C'): 1,
            },
            header_row = {
                    'id':   u'__unit__',
                    'type': u'discrete',
            },
            header_col = {
                    'id':   u'__context__',
                    'type': u'discrete',
            },
            missing = 0
    )
    ow.inputData(t)
    appl.exec_()
    ow.saveSettings()
