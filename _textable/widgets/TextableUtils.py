#=============================================================================
# Module TextableUtils.py, v0.04
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
# Provides classes:
# - SendButton
# - AdvancedSettings
# - InfoBox
# - BasicOptionsBox
#=============================================================================
# Provides functions:
# - pluralize
# - updateMultipleInputs
# - normalizeCarriageReturns
# - getPredefinedEncodings
#=============================================================================

import re, os

from Orange.OrangeWidgets import OWGUI


class SendButton(object):

    """A class encapsulating send button operations in Textable"""

    def __init__(
            self,
            widget,
            master,
            callback,
            checkboxValue       = 'autoSend',
            changedFlag         = 'settingsChanged',
            buttonLabel         = u'Send',
            checkboxLabel       = u'Send automatically',
            infoBoxAttribute    = None,
            sendIfPreCallback   = None,
            sendIfPostCallback  = None,
    ):
        """Initialize a new Send Button instance"""
        self.widget                 = widget
        self.master                 = master
        self.callback               = callback
        self.checkboxValue          = checkboxValue
        self.changedFlag            = changedFlag
        self.buttonLabel            = buttonLabel
        self.checkboxLabel          = checkboxLabel
        self.infoBoxAttribute       = infoBoxAttribute
        self.sendIfPreCallback      = sendIfPreCallback
        self.sendIfPostCallback     = sendIfPostCallback

    def draw(self):
        """Draw the send button and stopper on window"""
        sendButton = OWGUI.button(
                widget              = self.widget,
                master              = self.master,
                label               = self.buttonLabel,
                callback            = self.callback,
                tooltip             = (
                        u"Process input data and send results to output."
                ),
        )
        autoSendCheckbox = OWGUI.checkBox(
                widget              = self.widget,
                master              = self.master,
                value               = self.checkboxValue,
                label               = self.checkboxLabel,
                tooltip             = (
                        u"Process and send data whenever settings change."
                ),
        )
        OWGUI.setStopper(
                master              = self.master,
                sendButton          = sendButton,
                stopCheckbox        = autoSendCheckbox,
                changedFlag         = self.changedFlag,
                callback            = self.callback,
        )
        self.resetSettingsChangedFlag()

    def sendIf(self):
        """Send data if autoSend is on, else register setting change"""
        if self.sendIfPreCallback is not None:
            self.sendIfPreCallback()
        if self.master.autoSend:
            self.callback()
        else:
            setattr(self.master, self.changedFlag, True)
        if self.sendIfPostCallback is not None:
            self.sendIfPostCallback()

    def settingsChanged(self):
        """Notify setting change and send (if autoSend)"""
        if self.infoBoxAttribute is not None:
            infoBox = getattr(self.master, self.infoBoxAttribute)
            infoBox.settingsChanged()
        self.sendIf()

    def resetSettingsChangedFlag(self):
        """Set master's settings change flag to False"""
        setattr(self.master, self.changedFlag, False)


class AdvancedSettings(object):

    """A class encapsulating advanced settings operations in Textable"""

    def __init__(
            self,
            widget,
            master,
            callback,
            checkboxValue   = 'displayAdvancedSettings',
            basicWidgets    = None,
            advancedWidgets = None,
    ):
        """Initialize a new advanced settings instance"""
        self.widget         = widget
        self.master         = master
        self.callback       = callback
        self.checkboxValue  = checkboxValue
        if basicWidgets is None:
            basicWidgets = []
        self.basicWidgets = basicWidgets
        if advancedWidgets is None:
            advancedWidgets = []
        self.advancedWidgets = advancedWidgets

    def draw(self):
        """Draw the advanced settings checkbox on window"""
        OWGUI.separator(
                widget          = self.widget,
                height          = 1,
        )
        OWGUI.checkBox(
                widget          = self.widget,
                master          = self.master,
                value           = self.checkboxValue,
                label           = u'Advanced settings',
                callback        = self.callback,
                tooltip         = (
                        u"Toggle advanced settings on and off."
                ),
        )
        OWGUI.separator(
                widget          = self.widget,
                height          = 1,
        )

    def setVisible(self, bool):
        """Toggle between basic and advanced settings."""
        if bool:
            for widget in self.basicWidgets:
                widget.setVisible(not bool)
            for widget in self.advancedWidgets:
                widget.setVisible(bool)
        else:
            for widget in self.advancedWidgets:
                widget.setVisible(bool)
            for widget in self.basicWidgets:
                widget.setVisible(not bool)
        self.master.adjustSize()

    def basicWidgetsAppendSeparator(self, height=5):
        """Append a separator to the list of basic widgets."""
        self.basicWidgets.append(OWGUI.separator(
                widget  = self.widget,
                height  = height,
        ))
        
    def advancedWidgetsAppendSeparator(self, height=5):
        """Append a separator to the list of advanced widgets."""
        self.advancedWidgets.append(OWGUI.separator(
                widget  = self.widget,
                height  = height,
        ))

        
class InfoBox(object):

    """A class encapsulating info line management operations in Textable"""

    def __init__(
            self,
            widget,
            stringDataSent          = u'Data correctly sent to output.',
            stringNoDataSent        = u'No data sent to output yet.',
            stringSettingsChanged   = u'Settings were changed.',
            stringInputChanged      = u'Input has changed.',
            stringClickSend         = u"Please click 'Send' when ready.",
            statusHeader            = u'Status:\t',
            diagnosticHeader        = u'Diagnostic:\t',
    ):
        """Initialize a new InfoBox instance"""
        self.widget                 = widget
        self.stringDataSent         = stringDataSent
        self.stringNoDataSent       = stringNoDataSent
        self.stringSettingsChanged  = stringSettingsChanged
        self.stringInputChanged     = stringInputChanged
        self.stringClickSend        = stringClickSend
        self.statusHeader           = statusHeader
        self.diagnosticHeader       = diagnosticHeader

    def draw(self):
        """Draw the InfoBox on window"""
        box = OWGUI.widgetBox(
                widget      = self.widget,
                box         = u'Info',
                orientation = 'vertical',
                addSpace    = True,
        )
        self.line1 = OWGUI.widgetLabel(
                widget      = box,
                label       = u'',
        )
        self.line2 = OWGUI.widgetLabel(
                widget      = box,
                label       = u'',
        )
        OWGUI.separator(
                widget      = box,
                height      = 3,
        )
        OWGUI.rubber(widget=self.widget)
        self.initialMessage()

    def initialMessage(self):
        """Display initial message"""
        self.line1.setText(self.statusHeader + self.stringNoDataSent)
        self.line2.setText(u'\t' + self.stringClickSend)

    def noDataSent(self, message=u''):
        """Display error message (and 'no data sent' status)"""
        self.line1.setText(self.statusHeader + self.stringNoDataSent)
        if message:
            self.line2.setText(self.diagnosticHeader + message)
        else:
            self.line2.setText(u'')

    def dataSent(self, message=u''):
        """Display 'ok' message (and 'data sent' status)"""
        self.line1.setText(self.statusHeader + self.stringDataSent)
        if message:
            self.line2.setText(u'\t' + message)
        else:
            self.line2.setText(u'')

    def settingsChanged(self):
        """Display 'Settings changed' message"""
        self.line1.setText(self.statusHeader + self.stringSettingsChanged)
        self.line2.setText(u'\t' + self.stringClickSend)

    def inputChanged(self):
        """Display 'Input changed' message"""
        self.line1.setText(self.statusHeader + self.stringInputChanged)
        self.line2.setText(u'\t' + self.stringClickSend)

    def customMessage(self, status=u'', message=u''):
        """Display custom message"""
        if status:
            self.line1.setText(self.statusHeader + status)
        else:
            self.line1.setText(u'')
        self.line2.setText(message)


class BasicOptionsBox(object):

    """A class encapsulating the basic options box in Textable widgets"""

    def __new__(cls, widget, master, addSpace=False):
        """Initialize a new BasicOptionsBox instance"""
        basicOptionsBox = OWGUI.widgetBox(
                widget              = widget,
                box                 = u'Options',
                orientation         = 'vertical',
                addSpace            = addSpace,
        )
        OWGUI.lineEdit(
                widget              = basicOptionsBox,
                master              = master,
                value               = 'label',
                orientation         = 'horizontal',
                label               = u'Output segmentation label:',
                labelWidth          = 180,
                callback            = master.sendButton.settingsChanged,
                tooltip             = (
                        u"Label of the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = basicOptionsBox,
                height              = 3,
        )
        return basicOptionsBox


def pluralize(
        input_string,
        criterion,
        plural        = u's',
        singular      = u'',
):
    """Replace every '@p' in a string with a given form (u's' by default) if
    some criterion is larger than 1, and by another form (u'' by default)
    otherwise.
    """
    replacement = plural if criterion > 1 else singular
    return re.compile(r'@p').sub(replacement, input_string)

def updateMultipleInputs(
        itemList,
        newItem,
        newId           = None,
        removalCallback = None
    ):
    """Process input when the widget can take multiple ones"""
    ids = [x[0] for x in itemList]
    if not newItem: # remove
        if not ids.count(newId):
            return # no such item, removed before
        index = ids.index(newId)
        if removalCallback is not None:
            removalCallback(index)
        itemList.pop(index)
    else:
        if ids.count(newId): # update (already seen item from this source)
            index = ids.index(newId)
            itemList[index] = (newId, newItem)
        else: # add new
            itemList.append((newId, newItem))


def normalizeCarriageReturns(string):
    if os.name == 'nt':
        row_delimiter = u'\r\n'
    elif os.name == 'mac':
        row_delimiter = u'\r'
    else:
        row_delimiter = u'\n'
    return(string.replace('\n', row_delimiter))


def getPredefinedEncodings():
    """Return the list of predefined encodings"""
    return [
            u'ascii',
            u'iso-8859-1',
            u'iso-8859-15',
            u'utf-8',
            u'windows-1252',
            u'big5',
            u'big5hkscs',
            u'cp037',
            u'cp424',
            u'cp437',
            u'cp500',
            u'cp720',
            u'cp737',
            u'cp775',
            u'cp850',
            u'cp852',
            u'cp855',
            u'cp856',
            u'cp857',
            u'cp858',
            u'cp860',
            u'cp861',
            u'cp862',
            u'cp863',
            u'cp864',
            u'cp865',
            u'cp866',
            u'cp869',
            u'cp874',
            u'cp875',
            u'cp932',
            u'cp949',
            u'cp950',
            u'cp1006',
            u'cp1026',
            u'cp1140',
            u'cp1250',
            u'cp1251',
            u'cp1252',
            u'cp1253',
            u'cp1254',
            u'cp1255',
            u'cp1256',
            u'cp1257',
            u'cp1258',
            u'euc_jp',
            u'euc_jis_2004',
            u'euc_jisx0213',
            u'euc_kr',
            u'gb2312',
            u'gbk',
            u'gb18030',
            u'hz',
            u'iso2022_jp',
            u'iso2022_jp_1',
            u'iso2022_jp_2',
            u'iso2022_jp_2004',
            u'iso2022_jp_3',
            u'iso2022_jp_ext',
            u'iso2022_kr',
            u'latin_1',
            u'iso8859_2',
            u'iso8859_3',
            u'iso8859_4',
            u'iso8859_5',
            u'iso8859_6',
            u'iso8859_7',
            u'iso8859_8',
            u'iso8859_9',
            u'iso8859_10',
            u'iso8859_13',
            u'iso8859_14',
            u'iso8859_15',
            u'iso8859_16',
            u'johab',
            u'koi8_r',
            u'koi8_u',
            u'mac_cyrillic',
            u'mac_greek',
            u'mac_iceland',
            u'mac_latin2',
            u'mac_roman',
            u'mac_turkish',
            u'ptcp154',
            u'shift_jis',
            u'shift_jis_2004',
            u'shift_jisx0213',
            u'utf_32',
            u'utf_32_be',
            u'utf_32_le',
            u'utf_16',
            u'utf_16_be',
            u'utf_16_le',
            u'utf_7',
            u'utf_8',
            u'utf_8_sig'
]
    
    
