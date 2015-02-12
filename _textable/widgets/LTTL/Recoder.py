#=============================================================================
# Class LTTL.Recoder, v0.05
# Copyright 2012-2015 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the LTTL package v1.5
#
# LTTL v1.5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LTTL v1.5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LTTL v1.5. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

import unicodedata, re

from Segmentation   import Segmentation
from Segment        import Segment
from Address        import Address
from Input          import Input


class Recoder(object):
                                                                                                     
    """A class for recoding text data in LTTL.

    Attr substitutions is a list of tuples, where each tuple has a compiled
    regex as first element and a replacement string as second element.
    Replacement strings may contain backreferences in the form of an ampersand
    (&) immediately followed by a digit referring to the group to be captured
    (the form &+digit, which is not standard in Python, is used here for
    consistency with LTTL.Segmenter.tokenize()).
    
    Attr case is either None, 'lower', or 'upper'.
    """
    
    def __init__(
            self,
            substitutions   = None,
            case            = None,
            remove_accents  = False,
    ):
        """Initialize an Recoder instance"""
        if substitutions is None:
            substitutions   = []
        self.substitutions  = substitutions
        self.case           = case
        self.remove_accents = remove_accents

    def apply(
            self,
            segmentation,
            mode                = 'custom',
            label               = 'my_recoded_data',
            copy_annotations    = True,
            progress_callback   = None,
    ):
        """Apply the recoding associated with this recoder.
        
        Depending on the mode, either apply custom recoding (mode='custom')
        based on substitutions or standard preprocessing (mode='standard').

        Raise a ValueError exception if input segmentation is overlapping.
        Otherwise if input segmentation is Input, recode it and create and
        return a new Input. Otherwise take each segment in
        turn, recode it, create a new Input for each modified segment (if
        any), and return a new segmentation.
        """
        if not segmentation.is_non_overlapping():
            raise(ValueError(
                    u'Cannot apply recoder to overlapping segmentation.'
            ))
        if mode == 'standard':
            recoding_callback = self._apply_preprocessing
        else:
            recoding_callback = self._apply_substitutions
        if isinstance(segmentation, Input):
            original_text   = segmentation[0].get_content()
            recoded_text    = recoding_callback(
                    original_text,
                    progress_callback,
            )
            if recoded_text != original_text:
                new_input = Input()
                new_input.update(recoded_text, label)
                if copy_annotations:
                    new_input[0].annotations.update(
                            segmentation[0].annotations
                    )
                return(new_input)
            else:
                new_segment = Segment(Address(
                        str_index   = segmentation[0].address.str_index,
                        start       = segmentation[0].address.start,
                        end         = segmentation[0].address.end,
                ))
                if copy_annotations:
                    new_segment.annotations.update(
                            segmentation[0].annotations
                    )
                return(Segmentation([new_segment], label))
        else:
            segments = []
            for segment in segmentation:
                original_text   = segment.get_content()
                recoded_text    = recoding_callback(
                        original_text,
                        progress_callback,
                )
                if recoded_text != original_text:
                    new_input = Input()
                    new_input.update(recoded_text, new_input.label)
                    if copy_annotations:
                        new_input[0].annotations = segment.annotations.copy()
                    segments.append(new_input[0])
                else:
                    new_segment = Segment(Address(
                            str_index   = segment.address.str_index,
                            start       = segment.address.start,
                            end         = segment.address.end,
                    ))
                    if copy_annotations:
                        new_segment.annotations.update(segment.annotations)
                    segments.append(new_segment)
            return(Segmentation(segments, label))

    def _apply_substitutions(self, text, progress_callback=None):
        """Apply substitutions to text"""
        backref = re.compile(r'&(?=[0-9]+)')
        recoded_text = text
        for substitution in self.substitutions:
            repl_string = backref.sub(r'\\', substitution[1])
            recoded_text = substitution[0].sub(repl_string, recoded_text)
            if progress_callback:
                progress_callback()
        return(recoded_text)
        
    def _apply_preprocessing(self, text, progress_callback=None):
        """Apply preprocessing to text

        Accent removal functionality taken from:
        http://stackoverflow.com/questions/517923/
        what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
        """
        recoded_text  = text
        if self.remove_accents:
            recoded_text = ''.join(
                    (c for c in unicodedata.normalize('NFD', recoded_text)
                            if unicodedata.category(c) != 'Mn')
            )
        if self.case == 'lower':
            recoded_text = recoded_text.lower()
        elif self.case == 'upper':
            recoded_text = recoded_text.upper()
        if progress_callback:
            progress_callback()
        return(recoded_text)


