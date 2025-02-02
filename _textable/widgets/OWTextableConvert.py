"""
Class OWTextableConvert
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

__version__ = '0.19.12'

import os
import codecs
import re

from PyQt5.QtWidgets import QMessageBox, QApplication, QFileDialog
import Orange.data
from Orange.widgets import widget, gui, settings

from LTTL.TableThread import Table, PivotCrosstab, IntPivotCrosstab, Crosstab
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    InfoBox, SendButton, AdvancedSettings, pluralize,
    getPredefinedEncodings, addSeparatorAfterDefaultEncodings,
    Task
)

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

ColumnDelimiters = [
    ('tabulation (\\t)', u'\t'),
    ('comma (,)',  u','),
    ('semi-colon (;)', u';'),
]

class OWTextableConvert(OWTextableBaseWidget):
    """Orange widget for converting a Textable table to an Orange table"""

    name = "Convert"
    description = "Convert, transform, or export Orange Textable tables."
    icon = "icons/Convert.png"
    priority = 10001

    inputs = [('Textable table', Table, "inputData", widget.Single)]
    outputs = [
        ('Orange table', Orange.data.Table, widget.Default),
        ('Textable table', Table, widget.Dynamic),
        ('Segmentation', Segmentation)
    ]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    exportEncoding = settings.Setting('utf8')
    colDelimiter_idx = settings.Setting(0)

    includeOrangeHeaders = settings.Setting(False)

    sortRows = settings.Setting(False)
    sortRowsReverse = settings.Setting(False)
    sortCols = settings.Setting(False)
    sortColsReverse = settings.Setting(False)
    normalize = settings.Setting(False)
    normalizeMode = settings.Setting('rows')
    normalizeType = settings.Setting('l1')

    convert = settings.Setting(False)
    conversionType = settings.Setting('association matrix')
    associationBias = settings.Setting('none')
    transpose = settings.Setting(False)
    reformat = settings.Setting(False)
    unweighted = settings.Setting(False)

    lastLocation = settings.Setting('.')
    displayAdvancedSettings = settings.Setting(False)

    # Predefined list of available encodings...
    encodings = getPredefinedEncodings()

    want_main_area = False

    @property
    def colDelimiter(self):
        _, delimiter = ColumnDelimiters[self.colDelimiter_idx]
        return delimiter

    def __init__(self, *args, **kwargs):

        """Initialize a Convert widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.sortRowsKeyId = 0  # None
        self.sortColsKeyId = 0  # None
        self.table = None
        self.segmentation = None
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

        # Transform box
        self.transformBox = self.create_widgetbox(
            box=u'Transform',
            orientation='vertical',
            addSpace=False,
            )

        self.transformBoxLine1 = gui.widgetBox(
            widget=self.transformBox,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=self.transformBoxLine1,
            master=self,
            value='sortRows',
            label=u'Sort rows by column:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Sort table rows."
            ),
        )
        self.sortRowsKeyIdCombo = gui.comboBox(
            widget=self.transformBoxLine1,
            master=self,
            value='sortRowsKeyId',
            items=list(),
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Column whose values will be used for sorting rows."
            ),
        )
        self.sortRowsKeyIdCombo.setMinimumWidth(150)
        gui.separator(widget=self.transformBoxLine1, width=5)
        self.sortRowsReverseCheckBox = gui.checkBox(
            widget=self.transformBoxLine1,
            master=self,
            value='sortRowsReverse',
            label=u'Reverse',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Sort rows in reverse (i.e. decreasing) order."
            ),
        )
        gui.separator(widget=self.transformBox, height=3)
        self.transformBoxLine2 = gui.widgetBox(
            widget=self.transformBox,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=self.transformBoxLine2,
            master=self,
            value='sortCols',
            label=u'Sort columns by row:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Sort table columns."
            ),
        )
        self.sortColsKeyIdCombo = gui.comboBox(
            widget=self.transformBoxLine2,
            master=self,
            value='sortColsKeyId',
            items=list(),
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Row whose values will be used for sorting columns."
            ),
        )
        self.sortColsKeyIdCombo.setMinimumWidth(150)
        gui.separator(widget=self.transformBoxLine2, width=5)
        self.sortColsReverseCheckBox = gui.checkBox(
            widget=self.transformBoxLine2,
            master=self,
            value='sortColsReverse',
            label=u'Reverse',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Sort columns in reverse (i.e. decreasing) order."
            ),
        )
        gui.separator(widget=self.transformBox, height=3)
        self.transposeCheckBox = gui.checkBox(
            widget=self.transformBox,
            master=self,
            value='transpose',
            label=u'Transpose',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Transpose table (i.e. exchange rows and columns)."
            ),
        )
        gui.separator(widget=self.transformBox, height=3)
        self.transformBoxLine4 = gui.widgetBox(
            widget=self.transformBox,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=self.transformBoxLine4,
            master=self,
            value='normalize',
            label=u'Normalize:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Normalize table."
            ),
        )
        self.normalizeModeCombo = gui.comboBox(
            widget=self.transformBoxLine4,
            master=self,
            value='normalizeMode',
            items=[
                u'rows',
                u'columns',
                u'quotients',
                u'TF-IDF',
                u'presence/absence'
            ],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Normalization mode:\n\n"
                u"Row: L1 or L2 normalization by rows.\n\n"
                u"Column: L1 or L2 normalization by columns.\n\n"
                u"Quotients: the count stored in each cell is\n"
                u"divided by the corresponding theoretical count\n"
                u"under independence: the result is greater than 1\n"
                u"in case of attraction between line and column,\n"
                u"lesser than 1 in case of repulsion, and 1 if\n"
                u"there is no specific interaction between them.\n\n"
                u"TF-IDF: the count stored in each cell is multiplied\n"
                u"by the natural log of the ratio of the number of\n"
                u"rows (i.e. contexts) having nonzero count for this\n"
                u"column (i.e. unit) to the total number of rows.\n\n"
                u"Presence/absence: counts greater than 0 are\n"
                u"replaced with 1."
            ),
        )
        self.normalizeModeCombo.setMinimumWidth(150)
        gui.separator(widget=self.transformBoxLine4, width=5)
        self.normalizeTypeCombo = gui.comboBox(
            widget=self.transformBoxLine4,
            master=self,
            orientation='horizontal',
            value='normalizeType',
            items=[u'L1', u'L2'],
            sendSelectedValue=True,
            label=u'Norm:',
            labelWidth=40,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Norm type.\n\n"
                u"L1: divide each value by the sum of the enclosing\n"
                u"normalization unit (row/column)\n\n"
                u"L2: divide each value by the sum of squares of the\n"
                u"enclosing normalization unit, then take square root."
            ),
        )
        self.normalizeTypeCombo.setMinimumWidth(70)
        gui.separator(widget=self.transformBox, height=3)
        self.transformBoxLine5 = gui.widgetBox(
            widget=self.transformBox,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=self.transformBoxLine5,
            master=self,
            value='convert',
            label=u'Convert to:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Apply crosstab conversions."
            ),
        )
        self.conversionTypeCombo = gui.comboBox(
            widget=self.transformBoxLine5,
            master=self,
            value='conversionType',
            items=[
                'document frequency',
                'association matrix',
            ],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Crosstab conversions.\n\n"
                u"'document frequency': based on a pivot crosstab,\n"
                u"return a new crosstab giving, for each column,\n"
                u"the number of distinct rows that have nonzero\n"
                u"frequency (hence the resulting crosstab contains\n"
                u"a single row).\n\n"
                u"'association matrix': based on a pivot crosstab,\n"
                u"return a symmetric table with a measure of\n"
                u"associativity between each pair of columns of the\n"
                u"original table (see also the effect of the 'bias'\n"
                u"parameter)."
            ),
        )
        self.conversionTypeCombo.setMinimumWidth(150)
        gui.separator(widget=self.transformBoxLine5, width=5)
        self.associationBiasCombo = gui.comboBox(
            widget=self.transformBoxLine5,
            master=self,
            orientation='horizontal',
            value='associationBias',
            items=[u'frequent', u'none', u'rare'],
            sendSelectedValue=True,
            label=u'Bias:',
            labelWidth=40,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Association bias (alpha parameter in Deneulin,\n"
                u"Gautier, Le Fur, & Bavaud 2014).\n\n"
                u"'frequent': emphasizes strong associations\n"
                u"between frequent units (alpha=1).\n\n"
                u"'none': balanced compromise between\n"
                u"frequent and rare units (alpha=0.5).\n\n"
                u"'rare': emphasizes strong associations\n"
                u"between rare units (alpha=0). Note that in this\n"
                u"particular case, values greater than 1 express an\n"
                u"attraction and values lesser than 1 a repulsion."
            ),
        )
        self.associationBiasCombo.setMinimumWidth(70)
        gui.separator(widget=self.transformBox, height=3)
        self.transformBoxLine6 = gui.widgetBox(
            widget=self.transformBox,
            orientation='vertical',
        )
        self.reformatCheckbox = gui.checkBox(
            widget=self.transformBoxLine6,
            master=self,
            value='reformat',
            label=u'Reformat to sparse crosstab',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Reformat a crosstab to sparse format, where each\n"
                u"row corresponds to a pair 'row-column' of the\n"
                u"original crosstab."
            ),
        )
        gui.separator(widget=self.transformBoxLine6, height=3)
        iBox = gui.indentedBox(
            widget=self.transformBoxLine6,
        )
        self.unweightedCheckbox = gui.checkBox(
            widget=iBox,
            master=self,
            value='unweighted',
            label=u'Encode counts by repeating rows',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"This option (only available for crosstabs with\n"
                u"integer values) specifies that values will be\n"
                u"encoded in the sparse matrix by the number of\n"
                u"times each row (i.e. each pair row-column of the\n"
                u"original crosstab) is repeated. Otherwise each\n"
                u"row-column pair will appear only once and the\n"
                u"corresponding value will be stored explicitely\n"
                u"in a separate column with label '__weight__'.\n"
            ),
        )
        gui.separator(widget=self.transformBox, height=3)
        self.advancedSettings.advancedWidgets.append(self.transformBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # This "dummy" box is the reason why an extra (and unwanted) pixel
        # appears just below the Advanced Settings checkbox. It is necessary
        # for the widget's size to adjust properly when switching between
        # modes...
        dummyBox = gui.widgetBox(
            widget=self.controlArea,
            addSpace=False,
        )
        self.advancedSettings.basicWidgets.append(dummyBox)

        # Conversion box
        self.encodingBox = self.create_widgetbox(
            box=u'Encoding',
            orientation='horizontal',
            addSpace=False,
            )

        gui.widgetLabel(
            widget=self.encodingBox,
            labelWidth=180,
            label=u'Output file:',
        )
        conversionEncodingCombo = gui.comboBox(
            widget=self.encodingBox,
            master=self,
            value='exportEncoding',
            items=type(self).encodings,
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            orientation='horizontal',
            tooltip=(
                u"Select the encoding of the table that can be\n"
                u"saved to a file by clicking the 'Export' button\n"
                u"below.\n\n"
                u"Note that the table that is copied to the\n"
                u"clipboard by clicking the 'Copy to clipboard'\n"
                u"button below is always encoded in utf-8."
            ),
        )
        conversionEncodingCombo.setMinimumWidth(150)
        addSeparatorAfterDefaultEncodings(conversionEncodingCombo)
        gui.separator(widget=self.encodingBox, width=5)
        gui.widgetLabel(
            widget=self.encodingBox,
            label='',
        )

        # Export box
        self.exportBox = self.create_widgetbox(
            box=u'Export',
            orientation='vertical',
            addSpace=False,
            )

        exportBoxLine2 = gui.widgetBox(
            widget=self.exportBox,
            orientation='horizontal',
        )
        gui.widgetLabel(
            widget=exportBoxLine2,
            labelWidth=180,
            label=u'Column delimiter:',
        )
        colDelimiterCombo = gui.comboBox(
            widget=exportBoxLine2,
            master=self,
            value='colDelimiter_idx',
            callback=self.sendButton.settingsChanged,
            orientation='horizontal',
            items=[text for text, _ in ColumnDelimiters],
            tooltip=(
                u"Select the character used for delimiting columns."
            ),
        )
        colDelimiterCombo.setMinimumWidth(150)
        gui.separator(widget=exportBoxLine2, width=5)
        dummyLabel = gui.widgetLabel(
            widget=exportBoxLine2,
            label='',
        )
        gui.separator(widget=self.exportBox, height=2)
        gui.checkBox(
            widget=self.exportBox,
            master=self,
            value='includeOrangeHeaders',
            label=u'Include Orange headers',
            tooltip=(
                u"Include Orange table headers in output file."
            ),
        )
        gui.separator(widget=self.exportBox, height=2)
        exportBoxLine3 = gui.widgetBox(
            widget=self.exportBox,
            orientation='horizontal',
        )
        self.exportButton = gui.button(
            widget=exportBoxLine3,
            master=self,
            label=u'Export to file',
            callback=self.exportFile,
            tooltip=(
                u"Open a dialog for selecting the output file to\n"
                u"which the table will be saved."
            ),
        )
        self.copyButton = gui.button(
            widget=exportBoxLine3,
            master=self,
            label=u'Copy to clipboard',
            callback=self.copyToClipboard,
            tooltip=(
                u"Copy table to clipboard, in order to paste it in\n"
                u"another application (typically in a spreadsheet)."
                u"\n\nNote that the only possible encoding is utf-8."
            ),
        )
        gui.separator(widget=self.exportBox, height=2)
        self.advancedSettings.advancedWidgets.append(self.exportBox)

        # Export box
        self.basicExportBox = self.create_widgetbox(
            box=u'Export',
            orientation='vertical',
            addSpace=True,
            )

        basicExportBoxLine1 = gui.widgetBox(
            widget=self.basicExportBox,
            orientation='horizontal',
        )
        self.basicExportButton = gui.button(
            widget=basicExportBoxLine1,
            master=self,
            label=u'Export to file',
            callback=self.exportFile,
            tooltip=(
                u"Open a dialog for selecting the output file to\n"
                u"which the table will be saved."
            ),
        )
        self.basicCopyButton = gui.button(
            widget=basicExportBoxLine1,
            master=self,
            label=u'Copy to clipboard',
            callback=self.copyToClipboard,
            tooltip=(
                u"Copy table to clipboard, in order to paste it in\n"
                u"another application (typically in a spreadsheet)."
                u"\n\nNote that the only possible encoding is utf-8."
            ),
        )
        gui.separator(widget=self.basicExportBox, height=2)
        self.advancedSettings.basicWidgets.append(self.basicExportBox)

        gui.rubber(self.controlArea)

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()
        
        # Progress bar variables
        self.progress_bar_max = 0
        self.progress_bar_cur = 0

    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
    # Data outputs
        transformed_table, orangeTable, outputString = f.result()

        if transformed_table and orangeTable and outputString:

            if self.segmentation is None:
                self.segmentation = Input(label=u'table', text=outputString)
            else:
                self.segmentation.update(outputString, label=u'table')
                
            message = 'Table with %i row@p' % len(transformed_table.row_ids)
            message = pluralize(message, len(transformed_table.row_ids))
            message += ' and %i column@p ' % (len(transformed_table.col_ids) + 1)
            message = pluralize(message, len(transformed_table.col_ids) + 1)
            message += 'sent to output.'

            self.infoBox.setText(message)

            self.send('Orange table', orangeTable)
            self.send('Textable table', transformed_table)
            self.send('Segmentation', self.segmentation) # AS 11.2023: removed self
                
        else:
            self.send('Orange table', None)
            self.send('Textable table', None)
            self.send('Segmentation', None)

    def process_data(self, caller, transformed_table, numIterations):
        """ Process data in a worker thread
        instead of the main thread so that
        the operations can be cancelled """

        if self.displayAdvancedSettings:
            # Set max iterations
            self.progress_bar_max = numIterations
            self.progress_bar_cur = 0

            # Sort if needed...
            if self.sortRows or self.sortCols:
                if self.sortRows:
                    if self.sortRowsKeyId == 0:
                        key_col_id = transformed_table.header_col_id
                    else:
                        key_col_id = transformed_table.col_ids[
                            self.sortRowsKeyId - 1
                        ]
                else:
                    key_col_id = None

                if self.sortCols:
                    if self.sortColsKeyId == 0:
                        key_row_id = transformed_table.header_row_id
                    else:
                        key_row_id = transformed_table.row_ids[
                            self.sortColsKeyId - 1
                        ]
                else:
                    key_row_id = None

                transformed_table = transformed_table.to_sorted(
                    key_col_id,
                    self.sortRowsReverse,
                    key_row_id,
                    self.sortColsReverse,
                    caller=caller,
                )

            # Check if thread was cancelled
            if not transformed_table:
                caller.signal_prog.emit(100, False)
                return

            # Transpose if needed...
            if self.transpose:
                transformed_table = transformed_table.to_transposed(
                    caller=caller,
                )
                
            # Check if thread was cancelled
            if not transformed_table:
                caller.signal_prog.emit(100, False)
                return

            # Normalize if needed...
            if self.normalize:
                transformed_table = transformed_table.to_normalized(
                    mode=self.normalizeMode,
                    type=self.normalizeType.lower(),
                    caller=self,
                )
                
            # Check if thread was cancelled
            if not transformed_table:
                caller.signal_prog.emit(100, False)
                return

            # Convert if needed...
            elif self.convert:
                if self.conversionType == 'document frequency':
                    transformed_table = transformed_table.to_document_frequency(
                        caller=self,
                    )
                elif self.conversionType == 'association matrix':
                    transformed_table = transformed_table.to_association_matrix(
                        bias=self.associationBias,
                        caller=self,
                    )
                    
            # Check if thread was cancelled
            if not transformed_table:
                caller.signal_prog.emit(100, False)
                return

            # Reformat if needed...
            if self.reformat:
                if self.unweighted:
                    transformed_table = transformed_table.to_flat(
                        caller=self,
                    )
                else:
                    transformed_table = transformed_table.to_weighted_flat(
                        caller=self,
                    )

            # Check if thread was cancelled
            if not transformed_table:
                caller.signal_prog.emit(100, False)
                return

        self.transformed_table = transformed_table

        # Post-processing: Orange table
        caller.signal_text.emit('Step 2/3: Post-processing...', 'warning')
        caller.signal_prog.emit(1, True)

        orangeTable = transformed_table.to_orange_table(caller=self)
        
        # Check if thread was cancelled
        if not orangeTable:
            caller.signal_prog.emit(100, False)
            return
        
        # Post-processing: Output string
        caller.signal_text.emit('Step 3/3: Post-processing...', 'warning')
        caller.signal_prog.emit(1, True)

        if self.displayAdvancedSettings:
            colDelimiter = self.colDelimiter
            includeOrangeHeaders = self.includeOrangeHeaders
        else:
            colDelimiter = '\t'
            includeOrangeHeaders = False
            
        outputString = transformed_table.to_string(
            output_orange_headers=includeOrangeHeaders,
            col_delimiter=colDelimiter,
        )
        
        # Check if thread was cancelled
        if not outputString:
            caller.signal_prog.emit(100, False)
            return
        
        return transformed_table, orangeTable, outputString

    def sendData(self):

        """Convert and send table"""

        # Check that there is something on input...
        if not self.table:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Orange table', None)
            self.send('Textable table', None)
            self.send('Segmentation', None)
            if self.segmentation is not None:
                self.segmentation.clear()
                self.segmentation = None
            return

        transformed_table = self.table
        numIterations = 0

        if self.displayAdvancedSettings:

            # Precompute number of iterations...
            if self.transpose:
                num_cols = len(transformed_table.row_ids)
                num_rows = len(transformed_table.col_ids)
            else:
                num_rows = len(transformed_table.row_ids)
                num_cols = len(transformed_table.col_ids)
            if self.normalize:
                if self.normalizeMode == 'rows':
                    numIterations += num_rows
                elif self.normalizeMode == 'columns':
                    numIterations += num_cols
                elif self.normalizeMode == 'presence/absence':
                    numIterations += num_cols * num_rows
                elif self.normalizeMode == 'quotients':
                    numIterations += num_cols * (num_rows + 1)
                elif self.normalizeMode == 'TF-IDF':
                    numIterations += num_cols
            elif self.convert:
                numIterations += num_cols
            if self.reformat:
                numIterations += num_rows
            
            # Info box & progress bar
            self.infoBox.setText(u"Step 1/3: Processing...", "warning")
            self.progressBarInit()

        # Threading...

        # Partial function
        threaded_function = partial(
            self.process_data,
            self,
            transformed_table,
            numIterations,
        )

        # Threading ...
        self.threading(threaded_function)          
        
    def inputData(self, newInput):
        """Process incoming data."""
        # Cancel pending tasks, if any
        self.cancel()

        self.table = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def exportFile(self):
        """Display a FileDialog and save table to file"""
        if getattr(self, self.sendButton.changedFlag):
            QMessageBox.warning(
                None,
                'Textable',
                'Input data and/or settings have changed.\nPlease click '
                "'Send' or check 'Send automatically' before proceeding.",
                QMessageBox.Ok
            )
            return
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            u'Export Table to File',
            self.lastLocation,
        )
        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            encoding = re.sub(r"[ ]\(.+", "", self.exportEncoding)
            outputFile = codecs.open(
                filePath,
                encoding=encoding,
                mode='w',
                errors='xmlcharrefreplace',
            )
            outputFile.write(self.segmentation[0].get_content())
            outputFile.close()
            QMessageBox.information(
                None,
                'Textable',
                'Table successfully exported to file.',
                QMessageBox.Ok
            )

    def copyToClipboard(self):
        """Copy output table to clipboard"""
        if getattr(self, self.sendButton.changedFlag):
            QMessageBox.warning(
                None,
                'Textable',
                'Input data and/or settings have changed.\nPlease click '
                "'Send' or check 'Send automatically' before proceeding.",
                QMessageBox.Ok
            )
            return
        QApplication.clipboard().setText(self.segmentation[0].get_content())
        QMessageBox.information(
            None,
            'Textable',
            'Table successfully copied to clipboard.',
            QMessageBox.Ok
        )

    def updateGUI(self):

        """Update GUI state"""
        if not self.table:
            if self.displayAdvancedSettings:
                self.transformBox.setDisabled(True)
                self.exportButton.setDisabled(True)
                self.copyButton.setDisabled(True)
            else:
                self.basicExportButton.setDisabled(True)
                self.basicCopyButton.setDisabled(True)
        else:
            if self.displayAdvancedSettings:
                self.transformBox.setDisabled(False)
                self.exportButton.setDisabled(False)
                self.copyButton.setDisabled(False)
            else:
                self.basicExportButton.setDisabled(False)
                self.basicCopyButton.setDisabled(False)

            if self.displayAdvancedSettings:
                self.normalizeTypeCombo.setDisabled(True)
                self.associationBiasCombo.setDisabled(True)
                if self.sortRows:
                    self.sortRowsKeyIdCombo.clear()
                    self.sortRowsKeyIdCombo.addItem(
                        str(self.table.header_col_id)
                    )
                    if isinstance(self.table.col_ids[0], int):
                        tableColIds = [str(i) for i in self.table.col_ids]
                    else:
                        tableColIds = self.table.col_ids
                    for col_id in tableColIds:
                        self.sortRowsKeyIdCombo.addItem(str(col_id))
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
                        str(self.table.header_row_id)
                    )
                    if isinstance(self.table.row_ids[0], int):
                        tableRowIds = [str(i) for i in self.table.row_ids]
                    else:
                        tableRowIds = self.table.row_ids
                    for row_id in tableRowIds:
                        self.sortColsKeyIdCombo.addItem(str(row_id))
                    self.sortColsKeyId = self.sortColsKeyId or 0
                    self.sortColsKeyIdCombo.setDisabled(False)
                    self.sortColsReverseCheckBox.setDisabled(False)
                else:
                    self.sortColsKeyIdCombo.setDisabled(True)
                    self.sortColsKeyIdCombo.clear()
                    self.sortColsReverseCheckBox.setDisabled(True)

                # Crosstab...
                if isinstance(self.table, Crosstab):
                    self.transposeCheckBox.setDisabled(False)
                    self.transformBoxLine4.setDisabled(False)
                    self.transformBoxLine5.setDisabled(False)
                    self.transformBoxLine6.setDisabled(False)
                    self.normalizeModeCombo.setDisabled(True)
                    self.normalizeTypeCombo.setDisabled(True)
                    self.conversionTypeCombo.setDisabled(True)
                    self.associationBiasCombo.setDisabled(True)
                    self.reformatCheckbox.setDisabled(False)
                    self.unweightedCheckbox.setDisabled(False)
                    # IntPivotCrosstab...
                    if isinstance(self.table, IntPivotCrosstab):
                        # Normalize...
                        if self.normalize:
                            self.normalizeModeCombo.setDisabled(False)
                            self.transformBoxLine5.setDisabled(True)
                            self.convert = False
                            self.unweightedCheckbox.setDisabled(True)
                            self.unweighted = False
                            if (
                                self.normalizeMode == u'rows' or
                                self.normalizeMode == u'columns'
                            ):
                                self.normalizeTypeCombo.setDisabled(False)
                        # Convert...
                        elif self.convert:
                            self.conversionTypeCombo.setDisabled(False)
                            self.transformBoxLine4.setDisabled(True)
                            self.normalize = False
                            self.unweightedCheckbox.setDisabled(True)
                            self.unweighted = False
                            if self.conversionType == 'association matrix':
                                self.associationBiasCombo.setDisabled(False)
                        # Reformat...
                        if self.reformat:
                            # Flat crosstab
                            if self.unweighted:
                                self.transformBoxLine4.setDisabled(True)
                                self.normalize = False
                                self.transformBoxLine5.setDisabled(True)
                                self.convert = False
                        else:
                            self.unweightedCheckbox.setDisabled(True)
                    # Not IntPivotCrosstab...
                    else:
                        self.transformBoxLine4.setDisabled(True)
                        self.normalize = False
                        self.transformBoxLine5.setDisabled(True)
                        self.convert = False
                        self.unweightedCheckbox.setDisabled(True)
                    # PivotCrosstab...
                    if isinstance(self.table, PivotCrosstab):
                        self.transposeCheckBox.setDisabled(False)
                # Not Crosstab...
                else:
                    self.transposeCheckBox.setDisabled(True)
                    self.transpose = False
                    self.transformBoxLine4.setDisabled(True)
                    self.normalize = False
                    self.transformBoxLine5.setDisabled(True)
                    self.convert = False
                    self.transformBoxLine6.setDisabled(True)
                    self.reformat = False

        self.advancedSettings.setVisible(self.displayAdvancedSettings)

    def onDeleteWidget(self):
        if self.segmentation is not None:
            self.segmentation.clear()


if __name__ == '__main__':
    import sys
    appl = QApplication(sys.argv)
    ow = OWTextableConvert()
    ow.show()
    t = IntPivotCrosstab(
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
        header_row_id=u'__unit__',
        header_row_type=u'discrete',
        header_col_id=u'__context__',
        header_col_type=u'discrete',
        missing=0
    )
    ow.inputData(t)
    appl.exec_()
    ow.saveSettings()
