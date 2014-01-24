#=============================================================================
# Class LTTL.Input, v0.09
# Copyright 2012-2014 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the LTTL package v1.4
#
# LTTL v1.4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LTTL v1.4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LTTL v1.4. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

from Segment        import Segment
from Address        import Address
from Segmentation   import Segmentation

class Input(Segmentation):
                                                                                                     
    """A class for representing a segmentation storing data in LTTL"""
    
    def __init__(self, text=None, label=u'my_input'):
        """Initialize an Input instance"""
        Segmentation.data.append(None)
        str_index = len(Segmentation.data) - 1
        Segmentation.__init__(self, [Segment(Address(str_index))])
        self.update(text, label)

    def update(self, text=None, label=None):
        """Set text and label values associated with an Input"""
        Segmentation.data[self.segments[0].address.str_index] = text
        self.label = label
    
    def clear(self):
        """Reset text and label values associated with an Input to None"""
        self.update()

