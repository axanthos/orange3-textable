"""
Module LTTL.Table, v0.15
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the LTTL package v1.6

LTTL v1.6 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LTTL v1.6 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LTTL v1.6. If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
Provides classes:
- Table
- Crosstab(Table)
- PivotCrosstab(Crosstab)
- FlatCrosstab(Crosstab)
- WeightedFlatCrosstab(Crosstab)
- IntPivotCrosstab(PivotCrosstab)
- IntWeightedFlatCrosstab(WeightedFlatCrosstab)
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from .Utils import tuple_to_simple_dict_transpose

import numpy as np

import os
import math
import sys

from builtins import str as text
from future.utils import iteritems
from past.builtins import xrange


class Table(object):
    """Base class for tables in LTTL."""

    # TODO: modify client code (signature change: header_row/col).
    def __init__(
            self,
            row_ids,
            col_ids,
            values,
            header_row_id='__col__',    # formerly header_row['id']
            header_row_type='string',   # formerly header_row['type']
            header_col_id='__row__',    # formerly header_col['id']
            header_col_type='string',   # formerly header_col['type']
            col_type=None,
            class_col_id=None,
            missing=None,
            _cached_row_id=None,
    ):
        """Initialize a Table.

        :param row_ids: list of items (usually strings) used as row ids

        :param col_ids: list of items (usually strings) used as col ids

        :param values: dictionary containing storing values of the table's
        cells; keys are (row_id, col_id) tuples.

        :param header_row_id: id of header row (default '__col__')

        :param header_row_type: a string indicating the type of header row
        (default 'string', other possible values 'continuous' and 'discrete')

        :param header_col_id: id of header col (default '__row__')

        :param header_col_type: a string indicating the type of header col
        (default 'string', other possible values 'continuous' and 'discrete')

        :param col_type: a dictionary where keys are col_ids and value are the
        corresponding types ('string', 'continuous' or 'discrete')

        :param class_col_id: id of the col that indicates the class associated
        with each row, if any (default None).

        :param missing: value assigned to missing values (default None)

        :param _cached_row_id: not for use by client code.
        """

        if col_type is None:
            col_type = dict()

        self.row_ids = row_ids
        self.col_ids = col_ids
        self.values = values
        self.header_row_id = header_row_id
        self.header_row_type = header_row_type
        self.header_col_id = header_col_id
        self.header_col_type = header_col_type
        self.col_type = col_type
        self.class_col_id = class_col_id
        self.missing = missing
        self._cached_row_id = _cached_row_id

    # TODO: test.
    def to_string(
            self,
            output_orange_headers=False,
            col_delimiter='\t',
            row_delimiter=None,
    ):
        """Return a string representation of the table.

        :param output_orange_headers: a boolean indicating whether orange 2
        table headers should be added to the string representation (default
        False).

        :param col_delimiter: the unicode string that will be inserted between
        successive columns (default '\t')

        :param row_delimiter: the unicode string that will be inserted between
        successive rows (default '\r\n' on windows, '\n' elsewhere)

        :return: stringified table
        """

        # Select default row delimiter depending on OS...
        if row_delimiter is None:
            if os.name == 'nt':
                row_delimiter = '\r\n'
            else:
                row_delimiter = '\n'

        # Start with header col id.
        output_string = self.header_col_id + col_delimiter

        # Convert col headers to unicode strings and output...
        output_string += col_delimiter.join(text(i) for i in self.col_ids)

        # Add Orange 2 table headers if needed...
        if output_orange_headers:
            output_string += '%s%s%s' % (
                row_delimiter,
                self.header_col_type,
                col_delimiter,
            )
            col_type_list = [self.col_type.get(x, '') for x in self.col_ids]
            output_string += col_delimiter.join(col_type_list)
            output_string += row_delimiter + col_delimiter
            for col_id in self.col_ids:
                if col_id == self.class_col_id:
                    output_string += 'class'
                output_string += col_delimiter
            output_string = output_string[:-1]

        # Default (empty) string for missing values...
        if self.missing is None:
            missing = ''
        else:
            missing = text(self.missing)

        # Format row strings...
        row_strings = (
            '%s%s%s%s' % (
                row_delimiter,
                row_id,
                col_delimiter,
                col_delimiter.join(
                    [
                        text(self.values.get((row_id, col_id), missing))
                        for col_id in self.col_ids
                    ]
                )
            )
            for row_id in self.row_ids
        )

        # Concatenate into a single string and output it.
        return output_string + ''.join(row_strings)

    # Method to_orange_table() is defined differently for Python 2 and 3.
    if sys.version_info >= 3:

        # TODO: Implement and test.
        def to_orange_table(self, encoding='iso-8859-15'):
            """Create an Orange 3 table."""
            raise NotImplementedError('method not implemented yet!')

        # TODO: test.
        def to_orange_table(self, encoding='iso-8859-15'):
            """Create an Orange 2 table.

            :param encoding: a string indicating the encoding of strings in
            the Orange 2 table

            :return: an Orange 2 table

            NB:
            - Columns without a col_type will be set to 'string' by default.
            - Orange 2 does not support unicode well, so this method is
              likely to mangle non-ASCII data.
            """

            import Orange   # This can raise an ImportError.

            # Initialize list of features.
            features = list()

            # Get ordered list of col headers (with class col at the end)...
            ordered_cols = [self.header_col_id]
            ordered_cols.extend(
                [x for x in self.col_ids if x != self.class_col_id]
            )
            if self.class_col_id:
                ordered_cols.append(self.class_col_id)

            # For each col header...
            for col_id in ordered_cols:

                # Convert it to string and encode as specified...
                str_col_id = text(col_id)
                encoded_col_id = str_col_id.encode(
                    encoding,
                    errors='xmlcharrefreplace',
                )

                # Select col type for this col and create Orange feature...
                if col_id == self.header_col_id:
                    col_type = self.header_col_type
                else:
                    col_type = self.col_type.get(col_id, 'string')
                if col_type == 'string':
                    features.append(Orange.feature.String(encoded_col_id))
                elif col_type == 'continuous':
                    features.append(Orange.feature.Continuous(encoded_col_id))
                elif col_type == 'discrete':
                    values = list()
                    if col_id == self.header_col_id:
                        for row_id in self.row_ids:
                            value = row_id.encode(
                                encoding,
                                errors='xmlcharrefreplace',
                            )
                            if value not in values:
                                values.append(value)
                    else:
                        for row_id in self.row_ids:
                            if (row_id, col_id) in self.values:
                                value = text(self.values[(row_id, col_id)])
                                value = value.encode(
                                    encoding,
                                    errors='xmlcharrefreplace',
                                )
                                if value not in values:
                                    values.append(value)
                    feature = Orange.feature.Discrete(
                        name=encoded_col_id,
                        values=Orange.core.StringList(values),
                    )
                    features.append(feature)

            # Create Orange 2 domain and table based on features...
            domain = Orange.data.Domain(features, self.class_col_id)
            orange_table = Orange.data.Table(domain)

            # Default string for missing values...
            if self.missing is None:
                missing = '?'
            if self.missing is not None:
                missing = text(self.missing)

            # Store values in each row...
            for row_id in self.row_ids:
                row_data = list()
                for col_id in ordered_cols:
                    if col_id == self.header_col_id:
                        value = row_id
                    else:
                        value = self.values.get((row_id, col_id), missing)
                    if value:
                        value = text(value).encode(
                            encoding,
                            errors='xmlcharrefreplace',
                        )
                    row_data.append(value)
                orange_table.append(row_data)

            return orange_table

    # TODO: modify client code to match signature change (key_id etc).
    # TODO: test.
    def to_sorted(
            self,
            key_col_id=None,      # formerly row['key_id']
            reverse_rows=False,   # formerly row['reverse']
            key_row_id=None,      # formerly col['key_id']
            reverse_cols=False,   # formerly col['reverse']
    ):
        """Return a sorted copy of the table

        :param key_col_id: id of col to be used as key for sorting rows (default
        None means don't sort cols)

        :param reverse_rows: boolean indicating whether rows should be sorted
        in reverse order (default False); has no effect is key_col_id is None.

        :param key_row_id: id of row to be used as key for sorting cols (default
        None means don't sort cols)

        :param reverse_cols: boolean indicating whether cols should be sorted
        in reverse order (default False); has no effect is key_row_id is None.

        :return: a sorted copy of the table.
        """

        # Initializations...
        new_row_ids = list()
        new_col_ids = list()

        # If a col id was specified as key for sorting rows...
        if key_col_id is not None:

            # If it is header col id, sort rows by id...
            if key_col_id == self.header_col_id:
                new_row_ids.extend(sorted(self.row_ids, reverse=reverse_rows))

            # Otherwise sort rows by selected col...
            else:
                values = [
                    self.values.get((row_id, key_col_id), self.missing)
                    for row_id in self.row_ids
                ]
                new_row_ids.extend(
                    [
                        x[1] for x in sorted(
                            zip(values, self.row_ids),
                            reverse=reverse_rows
                        )
                    ]
                )
        # Else if no col id was specified for sorting rows, copy them directly.
        else:
            new_row_ids = self.row_ids[:]

        # If a row id was specified as key for sorting cols...
        if key_row_id is not None:

            # If it is header row id, sort cols by id...
            if key_row_id == self.header_row_id:
                new_col_ids.extend(sorted(self.col_ids, reverse=reverse_cols))

            # Otherwise sort cols by selected row...
            else:
                values = [
                    self.values.get((key_row_id, col_id), self.missing)
                    for col_id in self.col_ids
                ]
                new_col_ids.extend(
                    [
                        x[1] for x in sorted(
                            zip(values, self.col_ids),
                            reverse=reverse_cols
                        )
                    ]
                )
        # Else if no row id was specified for sorting cols, copy them directly.
        else:
            new_col_ids = self.col_ids[:]

        # Get original table's creator and use it to create new table...
        if isinstance(self, IntPivotCrosstab):
            creator = IntPivotCrosstab
        elif isinstance(self, PivotCrosstab):
            creator = PivotCrosstab
        elif isinstance(self, FlatCrosstab):
            creator = FlatCrosstab
        elif isinstance(self, IntWeightedFlatCrosstab):
            creator = IntWeightedFlatCrosstab
        elif isinstance(self, WeightedFlatCrosstab):
            creator = WeightedFlatCrosstab
        else:
            creator = Table
        return creator(
            new_row_ids,
            new_col_ids,
            self.values.copy(),
            self.header_row_id,
            self.header_row_type,
            self.header_col_id,
            self.header_col_type,
            self.col_type.copy(),
            self.class_col_id,
            self.missing,
            self._cached_row_id,
        )

    # Todo: test.
    def deepcopy(self):
        """Deep copy a table"""

        # Get original table's creator and use it to create copy...
        if isinstance(self, IntPivotCrosstab):
            creator = IntPivotCrosstab
        elif isinstance(self, PivotCrosstab):
            creator = PivotCrosstab
        elif isinstance(self, FlatCrosstab):
            creator = FlatCrosstab
        elif isinstance(self, IntWeightedFlatCrosstab):
            creator = IntWeightedFlatCrosstab
        elif isinstance(self, WeightedFlatCrosstab):
            creator = WeightedFlatCrosstab
        else:
            creator = Table
        return creator(
            self.row_ids[:],
            self.col_ids[:],
            self.values.copy(),
            self.header_row_id,
            self.header_row_type,
            self.header_col_id,
            self.header_col_type,
            self.col_type.copy(),
            self.class_col_id,
            self.missing,
            self._cached_row_id,
        )


class Crosstab(Table):
    """Base class for crosstabs (i.e. contingency tables)."""

    # TODO: test.
    @staticmethod
    def get_unique_items(seq):
        """Get list of unique items in sequence (in original order)

        (Adapted from http://www.peterbe.com/plog/uniqifiers-benchmark)

        :param seq: the iterable from which unique items should be extracted

        :return: a list of unique items in input iterable
        """
        seen = dict()
        result = list()
        for item in seq:
            if item in seen:
                continue
            seen[item] = 1
            result.append(item)
        return result


class PivotCrosstab(Crosstab):
    """A class for storing crosstabs in 'pivot' format.

    Example:
               --------+-------+
               | unit1 | unit2 |
    +----------+-------+-------+
    | context1 |   1   |   3   |
    +----------+-------+-------+
    | context2 |   4   |   2   |
    +----------+-------+-------+
    """

    # TODO: test.
    def to_transposed(self):
        """Return a transposed copy of the crosstab"""
        new_col_ids = self.row_ids[:]
        return PivotCrosstab(
            self.col_ids[:],
            new_col_ids,
            dict(
                (tuple(reversed(key)), count)
                for key, count in iteritems(self.values)
            ),
            self.header_col_id,
            self.header_col_type,
            self.header_row_id,
            self.header_row_type,
            dict([(col_id, 'continuous') for col_id in new_col_ids]),
            None,
            self.missing,
            self.header_col_id,    # TODO: check this (was self._cached_row_id).
        )

    # TODO: test.
    def to_weighted_flat(self, progress_callback=None):
        """Convert the crosstab in 'weighted and flat' format

        :param progress_callback: callback for monitoring progress ticks (number
        of rows in table)

        :return: a copy of the table in WeightedFlatCrosstab format
        """

        # Initialize col ids and types for the converted table...
        new_header_col_id = '__id__'
        new_header_col_type = 'continuous'  # TODO: check (was string)
        new_col_ids = self.header_row_id or '__column__'
        num_row_ids = len(self.row_ids)
        if num_row_ids > 1:
            second_col_id = self.header_col_id or '__row__'
            new_cached_row_id = None
            new_col_ids.append(second_col_id)
        else:
            new_cached_row_id = self.header_col_id  # TODO: check (was self.row_ids[0]
        new_col_type = dict((col_id, 'discrete') for col_id in new_col_ids)
        new_col_ids.append('__weight__')
        new_col_type['__weight__'] = 'continuous'

        # Prepare values dict and row ids for converted table...
        row_counter = 1
        new_values = dict()
        new_row_ids = list()
        get_count = self.values.get
        first_col_id = new_col_ids[0]
        for row_id in self.row_ids:
            for col_id in self.col_ids:
                count = get_count((row_id, col_id), 0)
                if count == 0:
                    continue
                # new_row_id = text(row_counter)
                new_row_id = row_counter    # TODO: check (was previous line)
                new_row_ids.append(new_row_id)
                new_values[(new_row_id, first_col_id)] = col_id
                if num_row_ids > 1:
                    new_values[(new_row_id, second_col_id)] = row_id
                new_values[(new_row_id, '__weight__')] = count
                row_counter += 1
            if progress_callback:
                progress_callback()

        return WeightedFlatCrosstab(
            new_row_ids,
            new_col_ids,
            new_values,
            header_col_id=new_header_col_id,
            header_col_type=new_header_col_type,
            col_type=new_col_type,
            class_col_id=None,
            missing=self.missing,
            _cached_row_id=new_cached_row_id,
        )

    # TODO: test.
    def to_numpy(self):
        """Return a numpy array with the content of a crosstab"""

        # Set numpy table type based on the crosstab's type...
        if isinstance(self, IntPivotCrosstab):
            np_type = np.dtype(np.int32)
        elif isinstance(self, PivotCrosstab):
            np_type = np.dtype(np.float32)

        # Initialize numpy table...
        np_table = np.empty([len(self.row_ids), len(self.row_ids)], np_type)
        np_table.fill(self.missing or 0)

        # Fill and return numpy table...
        for row_idx in xrange(len(self.row_ids)):
            for col_idx in xrange(len(self.col_ids)):
                try:
                    np_table[row_idx][col_idx] =    \
                      self.values[self.row_ids[row_idx]][self.col_ids[col_idx]]
                except KeyError:
                    pass
        return np_table

    # TODO: test.
    @classmethod
    def from_numpy(
            cls,
            row_ids,
            col_ids,
            np_array,
            header_row_id='__col__',
            header_row_type='string',
            header_col_id='__row__',
            header_col_type='string',
            col_type=None,
            class_col_id=None,
            missing=None,
            _cached_row_id=None,
    ):
        """Return an (Int)PivotCrosstab based on a numpy array.

        :param row_ids: list of items (usually strings) used as row ids

        :param col_ids: list of items (usually strings) used as col ids

        :param np_array: numpy array containing the values to be stored in the
        table; the ordering of rows and column is assumed to match the ordering
        of row ids and col ids.

        :param header_row_id: id of header row (default '__col__')

        :param header_row_type: a string indicating the type of header row
        (default 'string', other possible values 'continuous' and 'discrete')

        :param header_col_id: id of header col (default '__row__')

        :param header_col_type: a string indicating the type of header col
        (default 'string', other possible values 'continuous' and 'discrete')

        :param col_type: a dictionary where keys are col_ids and value are the
        corresponding types ('string', 'continuous' or 'discrete')

        :param class_col_id: id of the col that indicates the class associated
        with each row, if any (default None).

        :param missing: value assigned to missing values (default None)

        :param _cached_row_id: not for use by client code.

        :return: a PivotCrosstab or IntPivotCrosstab with the data from the
        input numpy array.
        """
        table_values = dict()
        for i, row in enumerate(np_array):
            for j, value in enumerate(row):
                table_values[(row_ids[i], col_ids[j])] = value
        if cls == IntPivotCrosstab:
            if not issubclass(np_array.dtype.type, np.integer):
                raise ValueError(
                    'Cannot cast non-integer numpy array to IntPivotCrosstab.'
                )
        return cls(
            row_ids,
            col_ids,
            table_values,
            header_row_id,
            header_row_type,
            header_col_id,
            header_col_type,
            col_type,
            class_col_id,
            missing,
            _cached_row_id,
        )


class IntPivotCrosstab(PivotCrosstab):
    """A class for storing crosstabs in 'pivot' format, with integer values."""

    def to_transposed(self):
        """Return a transposed copy of the crosstab"""
        transposed = super(IntPivotCrosstab, self).to_transposed()
        transposed.__class__ = IntPivotCrosstab
        return transposed

    def to_normalized(self, mode='rows', type='l1', progress_callback=None):
        """Return a normalized copy of the crosstab (where normalization is
        defined in a rather liberal way, cf. details below.

        :param mode: a string indicating the kind of normalization desired;
        possible values are
        - 'rows': row normalization
        - 'columns': column normalization
        - 'table': normalize with regard to entire table sum
        - 'presence/absence': set non-zero values to 1
        - 'quotients': compute independence quotients under independence
        - 'TF-IDF': term frequency - inverse document frequency transform

        :param type: either 'l1' (default) or 'l2'; applicable only in mode
        'rows', 'columns' and 'table'

        :param progress_callback: callback for monitoring progress ticks; number
        of ticks depends on mode:
        - 'rows': number of rows
        - 'columns': number of columns
        - 'table': not applicable
        - 'presence/absence': number of rows times number of columns
        - 'quotients': number of columns times (number of rows + 1)
        - 'TF-IDF': number of columns

        :return: normalized copy of crosstab
        """
        new_values = dict()
        denominator = 0
        if mode == 'rows':
            table_class = PivotCrosstab
            col_ids = self.col_ids
            for row_id in self.row_ids:
                row_values = [
                    self.values.get((row_id, col_id), 0)
                    for col_id in col_ids
                    ]
                if type == 'l1':
                    denominator = sum(row_values)
                elif type == 'l2':
                    denominator = math.sqrt(sum([v * v for v in row_values]))
                if denominator > 0:
                    new_values.update(zip(
                        [(row_id, col_id) for col_id in col_ids],
                        [v / denominator for v in row_values]
                    ))
                else:
                    new_values.update(zip(
                        [(row_id, col_id) for col_id in col_ids],
                        [0 for v in row_values]
                    ))
                if progress_callback:
                    progress_callback()
        elif mode == 'columns':
            table_class = PivotCrosstab
            row_ids = self.row_ids
            for col_id in self.col_ids:
                col_values = [
                    self.values.get((row_id, col_id), 0)
                    for row_id in row_ids
                    ]
                if type == 'l1':
                    denominator = sum(col_values)
                elif type == 'l2':
                    denominator = math.sqrt(sum([v * v for v in col_values]))
                if denominator > 0:
                    new_values.update(zip(
                        [(row_id, col_id) for row_id in row_ids],
                        [v / denominator for v in col_values]
                    ))
                else:
                    new_values.update(zip(
                        [(row_id, col_id) for row_id in row_ids],
                        [0 for v in col_values]
                    ))
                if progress_callback:
                    progress_callback()
        elif mode == 'table':
            table_class = PivotCrosstab
            values = reduce(list.__add__, [
                [
                    self.values.get((row_id, col_id), 0)
                    for row_id in self.row_ids
                    ]
                for col_id in self.col_ids
                ])
            if type == 'l1':
                denominator = sum(values)
            elif type == 'l2':
                denominator = math.sqrt(sum([v * v for v in values]))
            if denominator > 0:
                new_values.update(zip(
                    reduce(list.__add__, [
                        [(row_id, col_id) for row_id in self.row_ids]
                        for col_id in self.col_ids
                        ]),
                    [v / denominator for v in values]
                ))
            else:
                new_values.update(zip(
                    reduce(list.__add__, [
                        [(row_id, col_id) for row_id in self.row_ids]
                        for col_id in self.col_ids
                        ]),
                    [0 for v in values]
                ))
        elif mode == 'presence/absence':
            table_class = IntPivotCrosstab
            row_ids = self.row_ids
            col_ids = self.col_ids
            for col_id in col_ids:
                for row_id in row_ids:
                    try:
                        value = self.values[(row_id, col_id)]
                        new_values[(row_id, col_id)] = 1 if value > 0 else 0
                    except KeyError:
                        pass
                    if progress_callback:
                        progress_callback()
        elif mode == 'quotients':
            table_class = PivotCrosstab
            row_ids = self.row_ids
            col_ids = self.col_ids
            col_total = list()
            for col_id in col_ids:
                col_values = [
                    self.values.get((row_id, col_id), 0)
                    for row_id in row_ids
                    ]
                col_total.append(sum(col_values))
                if progress_callback:
                    progress_callback()
            total = sum(col_total)
            for row_id in row_ids:
                row_values = [
                    self.values.get((row_id, col_id), 0)
                    for col_id in col_ids
                    ]
                row_total = sum(row_values)
                for col_idx in xrange(len(col_ids)):
                    freq_under_indep = row_total * col_total[col_idx]
                    if freq_under_indep > 0:
                        new_values[(row_id, col_ids[col_idx])] = (
                            (row_values[col_idx] * total)
                            /
                            freq_under_indep
                        )
                    if progress_callback:
                        progress_callback()
        elif mode == 'TF-IDF':
            table_class = PivotCrosstab
            row_ids = self.row_ids
            for col_id in self.col_ids:
                col_values = [
                    self.values.get((row_id, col_id), 0)
                    for row_id in row_ids
                    ]
                col_occurrences = [1 for v in col_values if v > 0]
                df = sum(col_occurrences)
                if df > 0:
                    idf = math.log(len(row_ids) / df)
                    new_values.update(zip(
                        [(row_id, col_id) for row_id in row_ids],
                        [v * idf for v in col_values]
                    ))
                else:
                    new_values.update(zip(
                        [(row_id, col_id) for row_id in row_ids],
                        [0 for v in col_values]
                    ))
                if progress_callback:
                    progress_callback()
        return (table_class(
            list(self.row_ids),
            list(self.col_ids),
            new_values,
            self.header_row_id,
            self.header_row_type,
            self.header_col_id,
            self.header_col_type,
            dict(self.col_type),
            None,
            self.missing,
            self._cached_row_id,
        ))

    def to_document_frequency(self, progress_callback=None):
        """Return a table with document frequencies based on the crosstab"""
        context_type = '__document_frequency__'
        document_freq = dict()
        for col_id in self.col_ids:
            unit_profile = tuple_to_simple_dict_transpose(
                self.values,
                col_id
            )
            document_freq[(context_type, col_id)] = len(unit_profile)
            if progress_callback:
                progress_callback()
        return (IntPivotCrosstab(
            [context_type],
            self.col_ids[:],
            document_freq,
            '__unit__',
            'string',
            '__context__',
            'string',
            self.col_type.copy(),
            None,
            0,
            None,
        ))

    def to_association_matrix(self, bias='none', progress_callback=None):
        """Return a table with Markov associativities between columns
        (cf. Bavaud & Xanthos 2005, Deneulin et al. 2014)
        """
        orange_table = self.to_orange_table('utf8')
        # freq_table = Orange.data.preprocess.RemoveDiscrete(orange_table)
        # freq = freq_table.to_numpy()[0]
        freq = self.to_numpy()[0]   # TODO: check (was previous 2 lines)
        if self.header_col_type == 'continuous':
            freq = freq[::, 1::]
        total_freq = freq.sum()
        sum_col = freq.sum(axis=0)
        sum_row = freq.sum(axis=1)
        exchange = np.dot(
            np.transpose(freq),
            np.dot(
                np.diag(1 / sum_row),
                freq
            )
        ) / total_freq
        if bias == 'frequent':
            output_matrix = exchange
        elif bias == 'none':
            sqrt_pi_inv = np.diag(1 / np.sqrt(sum_col / total_freq))
            output_matrix = np.dot(sqrt_pi_inv, np.dot(exchange, sqrt_pi_inv))
        else:
            pi_inv = np.diag(1 / (sum_col / total_freq))
            output_matrix = np.dot(pi_inv, np.dot(exchange, pi_inv))
        col_ids = self.col_ids
        values = dict()
        for col_id_idx1 in xrange(len(col_ids)):
            col_id1 = text(col_ids[col_id_idx1])
            values.update(dict(
                (
                    (col_id1, text(col_ids[i])),
                    output_matrix[col_id_idx1, i]
                )
                for i in xrange(len(col_ids))
            ))
            if progress_callback:
                progress_callback()
        return (PivotCrosstab(
            self.col_ids[:],
            self.col_ids[:],
            values,
            header_col_id='__unit__',
            header_col_type='string',
            col_type=self.col_type.copy(),
        ))

    def to_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'flat' format"""
        new_header_col_id = '__id__'
        new_header_col_type = 'string'
        new_col_ids = [self.header_row_id or '__column__']
        num_row_ids = len(self.row_ids)
        if num_row_ids > 1:
            new_col_ids.append(self.header_col_id or '__row__')
            new_cached_row_id = None
            second_col_id = new_col_ids[1]
        else:
            new_cached_row_id = self.row_ids[0]
        new_col_type = dict([(col_id, 'discrete') for col_id in new_col_ids])
        row_counter = 1
        new_values = dict()
        new_row_ids = list()
        get_count = self.values.get
        first_col_id = new_col_ids[0]
        for row_id in self.row_ids:
            for col_id in self.col_ids:
                count = get_count((row_id, col_id), 0)
                for i in xrange(count):
                    new_row_id = text(row_counter)
                    new_row_ids.append(new_row_id)
                    new_values[(new_row_id, first_col_id)] = col_id
                    if num_row_ids > 1:
                        new_values[(new_row_id, second_col_id)] = row_id
                    row_counter += 1
            if progress_callback:
                progress_callback()
        return (FlatCrosstab(
            new_row_ids,
            new_col_ids,
            new_values,
            header_col_id=new_header_col_id,
            header_col_type=new_header_col_type,
            col_type=new_col_type,
            class_col_id=None,
            missing=self.missing,
            _cached_row_id=new_cached_row_id,
        ))

    def to_weighted_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'weighted and flat' format with
        integer values
        """
        weighted_flat = super(IntPivotCrosstab, self).to_weighted_flat(
            progress_callback=progress_callback
        )
        weighted_flat.__class__ = IntWeightedFlatCrosstab
        return weighted_flat


class FlatCrosstab(Crosstab):
    """A class for storing crosstabs in 'flat' format in LTTL.

    Example:
    +----------+-------+
    | context  | unit  |
    +==========+=======+
    | context1 | unit1 |
    +----------+-------+
    | context1 | unit2 |
    +----------+-------+
    | context1 | unit2 |
    +----------+-------+
    | context1 | unit2 |
    +----------+-------+
    | context2 | unit1 |
    +----------+-------+
    | context2 | unit1 |
    +----------+-------+
    | context2 | unit1 |
    +----------+-------+
    | context2 | unit1 |
    +----------+-------+
    | context2 | unit2 |
    +----------+-------+
    | context2 | unit2 |
    +----------+-------+
    """

    def to_pivot(self, progress_callback=None):
        """Return a copy of the crosstab in 'pivot' format"""
        new_header_row_id = self.col_ids[0]
        new_header_row_type = 'discrete'
        new_header_col_id = '__row__'
        new_header_col_type = 'discrete'
        new_col_ids = Crosstab.get_unique_items(
            [
                self.values[(row_id, new_header_row_id)]
                for row_id in self.row_ids
            ]
        )
        new_row_ids = list()
        new_values = dict()
        if len(self.col_ids) > 1:
            new_header_col_id = self.col_ids[1]
            new_row_ids.extend(Crosstab.get_unique_items(
                [
                    self.values[(row_id, new_header_col_id)]
                    for row_id in self.row_ids
                ]
            ))
            for row_id in self.row_ids:
                pair = (
                    self.values[row_id, new_header_col_id],
                    self.values[row_id, new_header_row_id],
                )
                new_values[pair] = new_values.get(pair, 0) + 1
                if progress_callback:
                    progress_callback()
        else:
            if self._cached_row_id is not None:
                cached_row_id = self._cached_row_id
            else:
                cached_row_id = '__data__'
            new_row_ids.append(cached_row_id)
            for row_id in self.row_ids:
                pair = (
                    cached_row_id,
                    self.values[row_id, new_header_row_id],
                )
                new_values[pair] = new_values.get(pair, 0) + 1
                if progress_callback:
                    progress_callback()
        return (IntPivotCrosstab(
            new_row_ids,
            new_col_ids,
            new_values,
            new_header_row_id,
            new_header_row_type,
            new_header_col_id,
            new_header_col_type,
            dict([(col_id, 'continuous') for col_id in new_col_ids]),
            None,
            self.missing,
            self._cached_row_id,
        ))

    def to_weighted_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'weighted and flat' format"""
        new_col_ids = list(self.col_ids)
        new_col_type = dict(self.col_type)
        row_counter = 1
        new_values = dict()
        new_row_ids = list()
        if len(self.col_ids) > 1:
            first_col_id = self.col_ids[0]
            second_col_id = self.col_ids[1]
            row_id_for_pair = dict()
            for row_id in self.row_ids:
                first_col_value = self.values[row_id, first_col_id]
                second_col_value = self.values[row_id, second_col_id]
                pair = (first_col_value, second_col_value)
                if pair in row_id_for_pair.keys():
                    known_pair_row_id = row_id_for_pair[pair]
                    new_values[(known_pair_row_id, '__weight__')] += 1
                else:
                    new_row_id = text(row_counter)
                    new_row_ids.append(new_row_id)
                    row_id_for_pair[pair] = new_row_id
                    new_values[(new_row_id, first_col_id)] = first_col_value
                    new_values[(new_row_id, second_col_id)] = second_col_value
                    new_values[(new_row_id, '__weight__')] = 1
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        else:
            col_id = self.col_ids[0]
            row_id_for_value = dict()
            for row_id in self.row_ids:
                col_value = self.values[row_id, col_id]
                if col_value in row_id_for_value.keys():
                    known_value_row_id = row_id_for_value[col_value]
                    new_values[(known_value_row_id, '__weight__')] += 1
                else:
                    new_row_id = text(row_counter)
                    new_row_ids.append(new_row_id)
                    row_id_for_value[col_value] = new_row_id
                    new_values[(new_row_id, col_id)] = col_value
                    new_values[(new_row_id, '__weight__')] = 1
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        new_col_ids.append('__weight__')
        new_col_type['__weight__'] = 'continuous'
        return (IntWeightedFlatCrosstab(
            new_row_ids,
            new_col_ids,
            new_values,
            self.header_row_id,
            self.header_row_type,
            self.header_col_id,
            self.header_col_type,
            new_col_type,
            None,
            self.missing,
            self._cached_row_id,
        ))


class WeightedFlatCrosstab(Crosstab):
    """A class for storing crosstabs in 'weighted and flat' format.

    Example:
    +----------+-------+-------+
    | context  | unit  | count |
    +==========+=======+=======+
    | context1 | unit1 |   1   |
    +----------+-------+-------+
    | context1 | unit2 |   3   |
    +----------+-------+-------+
    | context2 | unit1 |   4   |
    +----------+-------+-------+
    | context2 | unit2 |   2   |
    +----------+-------+-------+
    """

    def to_pivot(self, progress_callback=None):
        """Return a copy of the crosstab in 'pivot' format"""
        new_header_row_id = self.col_ids[0]
        new_header_row_type = 'discrete'
        new_header_col_id = '__row__'
        new_header_col_type = 'discrete'
        new_col_ids = Crosstab.get_unique_items(
            [
                self.values[(row_id, new_header_row_id)]
                for row_id in self.row_ids
            ]
        )
        new_row_ids = list()
        new_values = dict()
        if len(self.col_ids) > 2:
            new_header_col_id = self.col_ids[1]
            new_row_ids.extend(Crosstab.get_unique_items(
                [
                    self.values[(row_id, new_header_col_id)]
                    for row_id in self.row_ids
                ]
            ))
            for row_id in self.row_ids:
                pair = (
                    self.values[row_id, new_header_col_id],
                    self.values[row_id, new_header_row_id],
                )
                new_values[pair] = self.values[row_id, '__weight__']
                if progress_callback:
                    progress_callback()
        else:
            if self._cached_row_id is not None:
                cached_row_id = self._cached_row_id
            else:
                cached_row_id = '__data__'
            new_row_ids.append(cached_row_id)
            for row_id in self.row_ids:
                pair = (
                    cached_row_id,
                    self.values[row_id, new_header_row_id],
                )
                new_values[pair] = self.values[row_id, '__weight__']
                if progress_callback:
                    progress_callback()
        return (PivotCrosstab(
            new_row_ids,
            new_col_ids,
            new_values,
            new_header_row_id,
            new_header_row_type,
            new_header_col_id,
            new_header_col_type,
            dict([(col_id, 'continuous') for col_id in new_col_ids]),
            None,
            self.missing,
        ))


class IntWeightedFlatCrosstab(WeightedFlatCrosstab):
    """A class for storing crosstabs in 'weighted and flat' format in LTTL,
    where weights are integer values.
    """

    def to_pivot(self, progress_callback=None):
        """Return a copy of the crosstab in 'pivot' format, with int values"""
        pivot = super(IntWeightedFlatCrosstab, self).to_pivot(
            progress_callback=progress_callback
        )
        pivot.__class__ = IntPivotCrosstab
        return pivot

    def to_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'flat' format"""
        new_col_ids = list([c for c in self.col_ids if c != '__weight__'])
        new_col_type = dict(self.col_type)
        del new_col_type['__weight__']
        row_counter = 1
        new_values = dict()
        new_row_ids = list()
        if len(self.col_ids) > 1:
            first_col_id = self.col_ids[0]
            second_col_id = self.col_ids[1]
            for row_id in self.row_ids:
                count = self.values[(row_id, '__weight__')]
                first_col_value = self.values[row_id, first_col_id]
                second_col_value = self.values[row_id, second_col_id]
                for i in xrange(count):
                    new_row_id = text(row_counter)
                    new_row_ids.append(new_row_id)
                    new_values[(new_row_id, first_col_id)] = first_col_value
                    new_values[(new_row_id, second_col_id)] = second_col_value
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        else:
            col_id = self.col_ids[0]
            for row_id in self.row_ids:
                count = self.values[(row_id, '__weight__')]
                col_value = self.values[row_id, col_id]
                for i in xrange(count):
                    new_row_id = text(row_counter)
                    new_row_ids.append(new_row_id)
                    new_values[(new_row_id, col_id)] = col_value
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        return (FlatCrosstab(
            new_row_ids,
            new_col_ids,
            new_values,
            self.header_row_id,
            self.header_row_type,
            self.header_col_id,
            self.header_col_type,
            new_col_type,
            None,
            self.missing,
            self._cached_row_id,
        ))
