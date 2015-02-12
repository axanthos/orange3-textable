#=============================================================================
# Class LTTL.Address, v0.05
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

class Address():

    """A class for storing the address of a segment in LTTL."""
      
    def __init__(self, str_index, start=None, end=None):
        """Initialize an Address instance"""
        self.str_index  = str_index
        self.start      = start
        self.end        = end

