#=============================================================================
# Class LTTL.Segment, v0.13
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

from operator       import itemgetter
from itertools      import groupby

from Segmentation   import Segmentation

class Segment():

    """A class for representing components of a Segmentation."""
      
    def __init__(self, address, annotations=None):
        """Initialize a Segment instance"""
        if annotations is None: annotations = {}
        self.address        = address
        self.annotations    = annotations
        
    def get_content(self):
        """Stringify the content of a Segment"""
        address = self.address
        return Segmentation.data[address.str_index][address.start:address.end]

    def contains(self, other_segment):
        """Test if another segment is contained in this one"""
        address         = self.address
        other_address   = other_segment.address
        if address.str_index != other_address.str_index:
            return False
        if (address.start or 0) > (other_address.start or 0):
            return False
        if (
                (address.end or len(Segmentation.data[address.str_index]))
              < (other_address.end or len(
                        Segmentation.data[other_address.str_index]
                ))
        ):
            return False
        return True

    def contains_sequence(self, sequence):
        """Test if a sequence of segments is contained in this one"""
        address         = self.address
        other_addresses = [s.address for s in sequence]
        text_length     = len(Segmentation.data[address.str_index])
        for other_address in other_addresses:
            if address.str_index != other_address.str_index:
                return False
            if (address.start or 0) > (other_address.start or 0):
                return False
            if (
                    (address.end or text_length)
                  < (other_address.end or len(
                            Segmentation.data[other_address.str_index]
                    ))
            ):
                return False
        return True

    def equals(self, other_segment):
        """Test if another segment has the same address as this one"""
        address         = self.address
        other_address   = other_segment.address
        if address.str_index != other_address.str_index:
            return False
        text_length         = len(Segmentation.data[address.str_index])
        other_text_length   = len(Segmentation.data[other_address.str_index])
        if (
                (address.start or 0) == (other_address.start or 0)
            and
                    (address.end        or text_length)
                ==  (other_address.end  or other_text_length)
        ):
            return True
        else:
            return False

    def get_contained_segments(self, segmentation):
        """Return contained segments in another segmentation"""
        address     = self.address
        str_index   = address.str_index
        start       = address.start or 0
        text_length = len(Segmentation.data[address.str_index])
        end         = address.end or text_length
        data        = Segmentation.data
        return [
                s for s in segmentation
                        if  str_index   ==  s.address.str_index
                        and start       <= (s.address.start or 0)
                        and end         >= (
                                s.address.end
                             or len(data[s.address.str_index])
                        )
        ]

    def get_contained_segment_indices(self, segmentation):
        """Return contained segment indices in another segmentation"""
        address     = self.address
        str_index   = address.str_index
        start       = address.start or 0
        text_length = len(Segmentation.data[address.str_index])
        end         = address.end or text_length
        data        = Segmentation.data
        return [
                i for i in xrange(len(segmentation))
                        if  str_index ==  segmentation[i].address.str_index
                        and start     <= (segmentation[i].address.start or 0)
                        and end       >= (
                                segmentation[i].address.end
                             or len(data[segmentation[i].address.str_index])
                        )
        ]

    def get_contained_sequences(self, segmentation, length):
        """Return contained segment sequences in another segmentation"""
        address     = self.address
        str_index   = address.str_index
        start       = address.start or 0
        text_length = len(Segmentation.data[address.str_index])
        end         = address.end or text_length
        data        = Segmentation.data
        contained_indices = [
                i for i in xrange(len(segmentation))
                        if  str_index ==  segmentation[i].address.str_index
                        and start     <= (segmentation[i].address.start or 0)
                        and end       >= (
                                segmentation[i].address.end
                             or len(data[segmentation[i].address.str_index])
                        )
        ]
        contained_index_sequences = [
                map(itemgetter(1), g)
                        for k, g in groupby(
                                enumerate(contained_indices
                        ), lambda (i,x):i-x)
        ]
        fixed_length_sequences = []
        for contained_index_sequence in contained_index_sequences:
            fixed_length_sequences.extend([
                    segmentation[
                    contained_index_sequence[index]
                    :
                    contained_index_sequence[index] + length
                    ]
                            for index in xrange(
                                    len(contained_index_sequence) - length + 1
                            )
            ])
        return fixed_length_sequences

    def get_contained_sequence_indices(self, segmentation, length):
        """Return indices of first position of contained segment sequences
        in another segmentation
        """
        address     = self.address
        str_index   = address.str_index
        start       = address.start or 0
        text_length = len(Segmentation.data[address.str_index])
        end         = address.end or text_length
        data        = Segmentation.data
        contained_indices = [
                i for i in xrange(len(segmentation))
                        if  str_index ==  segmentation[i].address.str_index
                        and start     <= (segmentation[i].address.start or 0)
                        and end       >= (
                                segmentation[i].address.end
                             or len(data[segmentation[i].address.str_index])
                        )
        ]
        contained_index_sequences = [
                map(itemgetter(1), g)
                        for k, g in groupby(
                                enumerate(contained_indices
                        ), lambda (i,x):i-x)
        ]
        fixed_length_index_sequences = []
        for contained_index_sequence in contained_index_sequences:
            fixed_length_index_sequences.extend([
                    contained_index_sequence[index]
                            for index in xrange(
                                    len(contained_index_sequence) - length + 1
                            )
            ])
        return fixed_length_index_sequences



