"""
Class OWTextableInterchange
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

__version__ = '0.1.5'


from LTTL.Segment import Segment
from LTTL.Input import Input as LTTL_Input
from LTTL.Segmentation import Segmentation
from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    SendButton, InfoBox, pluralize
)

from Orange.widgets import gui, settings
from Orange.data import DiscreteVariable, StringVariable, Domain, Table
from Orange.widgets.widget import Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview

textMiningIsInstalled = True
try:
    from orangecontrib.text.corpus import Corpus
except ImportError:
    textMiningIsInstalled = False


class OWTextableInterchange(OWTextableBaseWidget):
    """Orange widget for converting between Textable and Text Mining formats"""

    name = "Interchange"
    description = "Convert Textable segmentation into Text Mining corpus" \
                  " and vice-versa"
    icon = "icons/interchange.svg"
    priority = 10003

    if textMiningIsInstalled:
        inputs = [
            ("Textable segmentation", Segmentation, "inputSegmentation"),
            ("Text Mining corpus", Corpus, "inputCorpus"),
        ]
        outputs = [
            ("Textable segmentation", Segmentation),
            ("Text Mining corpus", Corpus),
        ]
        class Inputs:
            segmentation = Input("Textable segmentation", Segmentation, 
                                 auto_summary=False)
            corpus = Input("Text Mining corpus", Corpus, auto_summary=False)
        class Outputs:
            segmentation = Output("Textable segmentation", Segmentation, 
                                  auto_summary=False)
            corpus = Output("Text Mining corpus", Corpus, auto_summary=False)

        settingsHandler = VersionedSettingsHandler(
            version=__version__.rsplit(".", 1)[0]
        )
        limitNumCategories = settings.Setting(True)
        maxNumCategories = settings.Setting(100)

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a Message widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.segmentation = None
        self.corpus = None
        self.segmentContent = 0
        self.createdInputs = list()
        self.infoBox = InfoBox(widget=self.controlArea)

        if not textMiningIsInstalled:
            self.infoBox.draw()
            self.infoBox.setText(
                "This widget serves to convert data between the "
                "Textable add-on format (segmentation) and the Text "
                "Mining add-on format (corpus). In order to use it, "
                "please install the Text Mining add-on (Orange3-Text).",
                "warning"
            )
            return
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI

        self.toCorpusOptionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Conversion to corpus',
            orientation='vertical',
        )

        self.maxNumCategoriesSpin = gui.spin(
            widget=self.toCorpusOptionsBox,
            master=self,
            value='maxNumCategories',
            label=u'Max values in discrete vars:',
            labelWidth=180,
            controlWidth=None,
            checked='limitNumCategories',
            minv=1,
            maxv=999,
            callback=self.sendButton.settingsChanged,
            checkCallback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Beyond the selected number of values, string variables will\n"
                u"be created in place of discrete variables."
            ),
        )

        self.toSegmentationOptionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Conversion to segmentation',
            orientation='vertical',
        )

        self.segmentContentCombo = gui.comboBox(
            widget=self.toSegmentationOptionsBox,
            master=self,
            value='segmentContent',
            orientation='horizontal',
            label=u'Use this as segment content:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The selected meta variable will be used as segment content."
            ),
        )
        self.segmentContentCombo.setMinimumWidth(120)

        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.setMinimumWidth(150)

        self.sendButton.sendIf()

    @Inputs.segmentation
    def inputSegmentation(self, segmentation):
        """Process incoming segmentation"""
        self.segmentation = segmentation
        self.infoBox.inputChanged()
        self.updateGUI()
        self.sendButton.sendIf()

    @Inputs.corpus
    def inputCorpus(self, corpus):
        """Process incoming corpus"""
        self.corpus = corpus
        self.segmentContent = 0
        self.infoBox.inputChanged()
        self.updateGUI()
        self.sendButton.sendIf()

    def sendData(self):
        """Convert input(s) and send output"""
        if not (self.segmentation or self.corpus):
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.sendNoneToOutputs()
            return

        msg_seg = msg_corpus = ""

        num_iterations = 0
        if self.corpus:
            num_iterations += len(self.corpus)
        if self.segmentation:
            num_iterations += len(self.segmentation)
        self.infoBox.setText(u"Processing, please wait...", "warning")
        self.controlArea.setDisabled(True)
        progressBar = ProgressBar(
            self,
            iterations=num_iterations
        )

        # Convert corpus to segmentation...
        if self.corpus:
            self.clearCreatedInputs()
            new_segments = list()
            text_feature = self.corpus.text_features[self.segmentContent]
            for row in self.corpus:
                content = row[text_feature].value
                if content == "":
                    continue
                new_input = LTTL_Input(row[text_feature].value)
                new_segment_annotations = dict()
                for attr in self.corpus.domain:
                    attr_str = str(row[attr])
                    if attr_str != "?":
                        new_segment_annotations[str(attr)] = attr_str
                for meta_attr in self.corpus.domain.metas:
                    meta_attr_str = str(row[meta_attr])
                    if (
                        meta_attr != text_feature and
                        meta_attr_str != "?"
                    ):
                        new_segment_annotations[str(meta_attr)] = meta_attr_str
                new_segments.append(
                    Segment(
                        new_input[0].str_index,
                        new_input[0].start,
                        new_input[0].end,
                        new_segment_annotations
                    )
                )
                self.createdInputs.append(new_input)
                progressBar.advance()
            new_segmentation = Segmentation(new_segments, self.captionTitle)
            msg_seg = u'%i segment@p sent to output.' % len(new_segmentation)
            msg_seg = pluralize(msg_seg, len(new_segmentation))
            if len(new_segmentation):
                self.Outputs.segmentation.send(new_segmentation)
            else:
                self.Outputs.segmentation.send(None)           
        else:
            self.Outputs.segmentation.send(None)

        # Convert segmentation to corpus...
        if self.segmentation:
            metas = list()
            attributes = list()
            meta_keys = list()
            attribute_keys = list()
            for key in self.segmentation.get_annotation_keys():
                possible_values = set()
                for segment in self.segmentation:
                    try:
                        possible_values.add(str(segment.annotations[key]))
                    except KeyError:
                        pass
                if (
                    self.limitNumCategories
                    and len(possible_values) > self.maxNumCategories
                ):
                    metas.append(StringVariable(key))
                    meta_keys.append(key)
                else:
                    attributes.append(
                        DiscreteVariable(key, values=list(possible_values))
                    )
                    attribute_keys.append(key)
            metas.append(StringVariable("textable_text"))
            domain = Domain(attributes, [], metas)
            rows = list()
            for segment in self.segmentation:
                row = [
                    str(segment.annotations.get(annotation_key, None))
                    for annotation_key in attribute_keys
                ]
                row.extend(
                    [
                        str(segment.annotations.get(annotation_key, None))
                        for annotation_key in meta_keys
                    ]
                )
                row.append(segment.get_content())
                rows.append(row)
                progressBar.advance
            table = Table(domain, rows)
            if textMiningIsInstalled:
                corpus = Corpus(
                    domain,
                    X=table.X,
                    metas=table.metas,
                    text_features=[metas[-1]]
                )
            msg_corpus = u'%i document@p' % len(self.segmentation)
            msg_corpus = pluralize(msg_corpus, len(self.segmentation))
            self.Outputs.corpus.send(corpus)
        else:
            self.Outputs.corpus.send(None)

        progressBar.finish()
        self.controlArea.setDisabled(False)

        if msg_seg or msg_corpus:
            message = msg_seg
            if msg_seg and msg_corpus:
                message += " and "
            message += msg_corpus
            message += " sent to output."
            self.infoBox.setText(message)

        self.sendButton.resetSettingsChangedFlag()

    def updateGUI(self):
        """Update GUI state"""
        self.toSegmentationOptionsBox.setDisabled(True)
        self.toCorpusOptionsBox.setDisabled(True)
        self.segmentContentCombo.clear()
        if self.corpus is not None:
            for feature in self.corpus.text_features:
                self.segmentContentCombo.addItem(str(feature))
            self.segmentContent = self.segmentContent
            self.toSegmentationOptionsBox.setDisabled(
                len(self.corpus.text_features) < 2
            )
        if self.segmentation is not None:
            self.toCorpusOptionsBox.setDisabled(False)

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.clearCreatedInputs()

    def clearCreatedInputs(self):
        for i in self.createdInputs:
            Segmentation.set_data(i[0].str_index, None)
        del self.createdInputs[:]


if __name__ == "__main__":
    WidgetPreview(OWTextableInterchange).run()
