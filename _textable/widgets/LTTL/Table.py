#=============================================================================
# Module LTTL.Table, v0.14
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
# Provides classes:
# - Table
# - Crosstab(Table)
# - PivotCrosstab(Crosstab)
# - FlatCrosstab(Crosstab)
# - WeightedFlatCrosstab(Crosstab)
# - IntPivotCrosstab(PivotCrosstab)
# - IntWeightedFlatCrosstab(WeightedFlatCrosstab)
#=============================================================================

from __future__     import division

from Utils          import tuple_to_simple_dict_transpose

import Orange
import numpy as np

import os, math


class Table(object):

    """Base class for tables in LTTL."""

    def __init__(
            self,
            row_ids,
            col_ids,
            values,
            header_row      = None,
            header_col      = None,
            col_type        = None,
            class_col_id    = None,
            missing         = None,
            cached_row_id   = None,
    ):
        """Initialize a Table."""
        if header_row is None:
            header_row = {
                'id':   u'__col__',
                'type': u'',
            }
        elif 'id' not in header_row:
            header_row['id'] = u'__col__'
        if header_col is None:
            header_col = {
                'id':   u'__row__',
                'type': u'',
            }
        elif 'id' not in header_col:
            header_col['id'] = u'__row__'
        if col_type is None:
            col_type = {}
        self.row_ids        = row_ids
        self.col_ids        = col_ids
        self.values         = values
        self.header_row     = header_row
        self.header_col     = header_col
        self.col_type       = col_type
        self.class_col_id   = class_col_id
        self.missing        = missing
        self.cached_row_id  = cached_row_id

    def to_string(
            self,
            output_orange_headers   = False,
            col_delimiter           = '\t',
    ):
        """Display the table"""
        if os.name == 'nt':                                                   # refactor?
            row_delimiter = u'\r\n'
        elif os.name == 'mac':
            row_delimiter = u'\r'
        else:
            row_delimiter = u'\n'
        output_string  = self.header_col['id'] + col_delimiter
        if isinstance(self.col_ids[0], (int, long)):
            str_col_ids = [str(i) for i in self.col_ids]
        else:
            str_col_ids = self.col_ids
        output_string += col_delimiter.join(str_col_ids)
        if output_orange_headers:
            output_string += u'%s%s%s' % (
                    row_delimiter,
                    self.header_col.get('type', u''),
                    col_delimiter,
            )
            col_type_list  = [self.col_type.get(x, u'') for x in self.col_ids]
            output_string += col_delimiter.join(col_type_list)
            output_string += row_delimiter + col_delimiter
            for col_id in self.col_ids:
                if col_id == self.class_col_id:
                    output_string += u'class'
                output_string += col_delimiter
            output_string = output_string[:-1]
        missing = u''
        if self.missing is not None:
            missing = unicode(self.missing)
        row_strings = (u'%s%s%s%s' % (
                row_delimiter,
                row_id,
                col_delimiter,
                col_delimiter.join([
                        unicode(self.values.get((row_id, col_id), missing))
                                for col_id in self.col_ids
                ])
        ) for row_id in self.row_ids)
        return output_string + ''.join(row_strings)


    def to_orange_table(
            self,
            encoding        = 'iso-8859-15',
    ):
        """Create an Orange table.

        NB1: Columns without a col_type will be set to 'string' by default.

        NB2: Orange does not seem to support unicode well, hence this method
        is at risk to mangle non-ASCII data for the time being.
        """
        import Orange
        features = []
        ordered_cols = [self.header_col['id']]
        ordered_cols.extend(
                [x for x in self.col_ids if x != self.class_col_id]
        )
        if self.class_col_id:
            ordered_cols.append(self.class_col_id)
        for col_id in ordered_cols:
            if isinstance(col_id, (int, long)):
                str_col_id = str(col_id)
            else:
                str_col_id = col_id
            encoded_col_id = str_col_id.encode(
                    encoding,
                    errors='xmlcharrefreplace',
            )
            col_type = None
            if col_id == self.header_col['id']:
                col_type = self.header_col['type']
            else:
                col_type = self.col_type.get(col_id, u'string')
            if col_type == u'string':
                features.append(Orange.feature.String(encoded_col_id))
            elif col_type == u'continuous':
                features.append(Orange.feature.Continuous(encoded_col_id))
            elif col_type == u'discrete':
                values = []
                if col_id == self.header_col['id']:
                    for row_id in self.row_ids:
                        value = row_id.encode(
                                encoding,
                                errors='xmlcharrefreplace',
                        )
                        if value not in values:
                            values.append(value)
                else:
                    for row_id in self.row_ids:
                        if self.values.has_key((row_id, col_id)):
                            value = unicode(self.values[(row_id, col_id)])
                            value = value.encode(
                                    encoding,
                                    errors='xmlcharrefreplace',
                            )
                            if value not in values:
                                values.append(value)
                feature = Orange.feature.Discrete(
                        name   = encoded_col_id,
                        values = Orange.core.StringList(values),
                )
                features.append(feature)
        if self.class_col_id:
            has_class = True
        else:
            has_class = False
        domain = Orange.data.Domain(features, has_class)
        orange_table = Orange.data.Table(domain)
        missing = u'?'
        if self.missing is not None:
            missing = unicode(self.missing)
        for row_id in self.row_ids:
            row_data = []
            for col_id in ordered_cols:
                if col_id == self.header_col['id']:
                    value = row_id
                else:
                    value = self.values.get((row_id, col_id), missing)
                if value:
                    value = unicode(value).encode(
                            encoding,
                            errors='xmlcharrefreplace',
                    )
                row_data.append(value)
            orange_table.append(row_data)
        return orange_table


    def to_sorted(self, row={}, col={}):
        """Return a sorted copy of the table

        Args are dicts with keys 'key_id' (id of col/row to be used
        as sorting key, None by default) and 'reverse' (False by default).
        """
        new_row_ids = []
        new_col_ids = []
        if row.get('key_id', None) is not None:
            if row['key_id'] == self.header_col['id']:
                new_row_ids.extend(sorted(
                        self.row_ids,
                        reverse=row.get('reverse', False)
                ))
            else:
                values = [
                        self.values.get(
                                (row_id, row['key_id']),
                                self.missing
                        )
                                for row_id in self.row_ids
                ]
                pairs = zip(values, self.row_ids)
                new_row_ids.extend([
                        x[1] for x in sorted(
                                zip(values, self.row_ids),
                                reverse=row.get('reverse', False)
                        )
                ])
        else:
            new_row_ids.extend(self.row_ids)
        if col.get('key_id', None) is not None:
            if col.get('key_id', None) == self.header_row['id']:
                new_col_ids.extend(sorted(
                        self.col_ids,
                        reverse=col.get('reverse', False)
                ))
            else:
                values = [
                        self.values.get(
                                (col['key_id'], col_id),
                                self.missing
                        )
                                for col_id in self.col_ids
                ]
                pairs = zip(values, self.col_ids)
                new_col_ids.extend([
                        x[1] for x in sorted(
                                zip(values, self.col_ids),
                                reverse=col.get('reverse', False)
                        )
                ])
        else:
            new_col_ids.extend(self.col_ids)
        creator = None
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
        return(creator(
                new_row_ids,
                new_col_ids,
                dict(self.values),
                dict(self.header_row),
                dict(self.header_col),
                dict(self.col_type),
                self.class_col_id,
                self.missing,
                self.cached_row_id,
        ))
        
    def deepcopy(self):
        """Deep copy a table"""
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
        return(creator(
                self.row_ids[:],
                self.col_ids[:],
                self.values.copy(),
                self.header_row.copy(),
                self.header_col.copy(),
                self.col_type.copy(),
                self.class_col_id,
                self.missing,
                self.cached_row_id,           
        ))



class Crosstab(Table):

    """Base class for crosstabs in LTTL."""

    @staticmethod
    def get_unique_items(seq):
        """Get list of unique items in sequence (in original order)
        (adapted from http://www.peterbe.com/plog/uniqifiers-benchmark)
        """
        seen    = {}
        result  = []
        for item in seq:
            if item in seen: continue
            seen[item] = 1
            result.append(item)
        return result


class PivotCrosstab(Crosstab):

    """A class for storing crosstabs in 'pivot' format in LTTL."""

    def to_transposed(self):
        """Return a transposed copy of the crosstab"""
        new_col_ids = list(self.row_ids)
        return(PivotCrosstab(
                list(self.col_ids),
                new_col_ids,
                dict([
                        (tuple(reversed(key)), count)
                                for key, count in self.values.items()
                ]),
                dict(self.header_col),
                dict(self.header_row),
                dict([(col_id, u'continuous') for col_id in new_col_ids]),
                None,
                self.missing,
                self.cached_row_id,
        ))

    def to_weighted_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'weighted and flat' format"""
        new_header_col = {
            'id':   u'__id__',
            'type': u'string',
        }
        new_col_ids = [self.header_row.get('id', u'__column__')]
        num_row_ids  = len(self.row_ids)
        if num_row_ids > 1:
            new_col_ids.append(self.header_col.get('id', u'__row__'))
            new_cached_row_id = None
            second_col_id = new_col_ids[1]
        else:
            new_cached_row_id = self.row_ids[0]
        new_col_type = dict([(col_id, u'discrete') for col_id in new_col_ids])
        row_counter  = 1
        new_values   = {}
        new_row_ids  = []
        get_count    = self.values.get
        first_col_id = new_col_ids[0]
        for row_id in self.row_ids:
            for col_id in self.col_ids:
                count = get_count((row_id, col_id), 0)
                if count == 0:
                    continue
                new_row_id = unicode(row_counter)
                new_row_ids.append(new_row_id)
                new_values[(new_row_id, first_col_id)] = col_id
                if num_row_ids > 1:
                    new_values[(new_row_id, second_col_id)] = row_id
                new_values[(new_row_id, u'__weight__')] = count
                row_counter += 1
            if progress_callback:
                progress_callback()
        new_col_ids.append(u'__weight__')
        new_col_type[u'__weight__'] = u'continuous'
        return(WeightedFlatCrosstab(
                new_row_ids,
                new_col_ids,
                new_values,
                {},
                new_header_col,
                new_col_type,
                None,
                self.missing,
                new_cached_row_id,
        ))
    
    def to_numpy(self):
        """Return a numpy array with the numeric variables of the table"""
        if isinstance(self, IntPivotCrosstab):
            np_type = np.dtype(np.int32)
        elif isinstance(self, PivotCrosstab):
            np_type = np.dtype(np.float32)
        if self.missing == None:
            base_table = self.deepcopy()
            base_table.missing = 0
        else:
            base_table = self
        orange_table = base_table.to_orange_table()
        contigency_table = Orange.data.preprocess.RemoveDiscrete(orange_table)
        return contigency_table.to_numpy()[0].astype(np_type)
        
    @classmethod
    def from_numpy(
        cls,
        row_ids,
        col_ids,
        np_array,
        header_row      = None,
        header_col      = None,
        col_type        = None,
        class_col_id    = None,
        missing         = None,
        cached_row_id   = None,
    ):
        """Return an (Int)PivotCrosstab based on a numpy array."""
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
            header_row,
            header_col,
            col_type,
            class_col_id,
            missing,
            cached_row_id,
        )
        
        
        
class IntPivotCrosstab(PivotCrosstab):

    """A class for storing crosstabs in 'pivot' format in LTTL, with integer
    values.
    """

    def to_transposed(self):
        """Return a transposed copy of the crosstab"""
        transposed = super(IntPivotCrosstab, self).to_transposed()
        transposed.__class__ = IntPivotCrosstab
        return transposed

    def to_normalized(self, mode='rows', type='l1', progress_callback=None):
        """Return a sorted copy of the crosstab"""
        new_values = {}
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
            row_ids   = self.row_ids
            col_ids   = self.col_ids
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
            row_ids   = self.row_ids
            col_ids   = self.col_ids
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
                    idf = math.log(len(row_ids)/df)
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
        return(table_class(
                list(self.row_ids),
                list(self.col_ids),
                new_values,
                dict(self.header_row),
                dict(self.header_col),
                dict(self.col_type),
                None,
                self.missing,
                self.cached_row_id,
        ))

    def to_document_frequency(self, progress_callback=None):
        """Return a table with document frequencies based on the crosstab"""
        context_type = u'__document_frequency__';
        document_freq = dict()
        for col_id in self.col_ids:
            unit_profile = tuple_to_simple_dict_transpose(
                    self.values,
                    col_id
            )
            document_freq[(context_type, col_id)] = len(unit_profile)
            if progress_callback:
                progress_callback()
        return(IntPivotCrosstab(
                [context_type],
                self.col_ids[:],
                document_freq,
                {
                    'id':   u'__unit__',
                    'type': u'string',
                },
                {
                    'id':   u'__context__',
                    'type': u'string',
                },
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
        freq_table   = Orange.data.preprocess.RemoveDiscrete(orange_table)
        freq         = freq_table.to_numpy()[0]
        if self.header_col['type'] == 'continuous':
            freq = freq[::,1::]
        total_freq = freq.sum()
        sum_col    = freq.sum(axis=0)
        sum_row    = freq.sum(axis=1)
        exchange     = np.dot(
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
            col_id1 = unicode(col_ids[col_id_idx1])
            values.update(dict(
                    (
                            (col_id1, unicode(col_ids[i])),
                            output_matrix[col_id_idx1, i]
                    )
                            for i in xrange(len(col_ids))
            ))
            if progress_callback:
                progress_callback()
        return(PivotCrosstab(
                self.col_ids[:],
                self.col_ids[:],
                values,
                {},
                {
                    'id':   u'__unit__',
                    'type': u'string',
                },
                self.col_type.copy(),
        ))

    def to_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'flat' format"""
        new_header_col = {
            'id':   u'__id__',
            'type': u'string',
        }
        new_col_ids = [self.header_row.get('id', u'__column__')]
        num_row_ids  = len(self.row_ids)
        if num_row_ids > 1:
            new_col_ids.append(self.header_col.get('id', u'__row__'))
            new_cached_row_id = None
            second_col_id = new_col_ids[1]
        else:
            new_cached_row_id = self.row_ids[0]
        new_col_type = dict([(col_id, u'discrete') for col_id in new_col_ids])
        row_counter  = 1
        new_values   = {}
        new_row_ids  = []
        get_count    = self.values.get
        first_col_id = new_col_ids[0]
        for row_id in self.row_ids:
            for col_id in self.col_ids:
                count = get_count((row_id, col_id), 0)
                for i in xrange(count):
                    new_row_id = unicode(row_counter)
                    new_row_ids.append(new_row_id)
                    new_values[(new_row_id, first_col_id)] = col_id
                    if num_row_ids > 1:
                        new_values[(new_row_id, second_col_id)] = row_id
                    row_counter += 1
            if progress_callback:
                progress_callback()
        return(FlatCrosstab(
                new_row_ids,
                new_col_ids,
                new_values,
                {},
                new_header_col,
                new_col_type,
                None,
                self.missing,
                new_cached_row_id,
        ))

    def to_weighted_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'weighted and flat' format with
        integer values
        """
        weighted_flat = super(IntPivotCrosstab, self).to_weighted_flat(
            progress_callback = progress_callback
        )
        weighted_flat.__class__ = IntWeightedFlatCrosstab
        return weighted_flat


class FlatCrosstab(Crosstab):

    """A class for storing crosstabs in 'flat' format in LTTL."""

    def to_pivot(self, progress_callback=None):
        """Return a copy of the crosstab in 'pivot' format"""
        new_header_row_id = self.col_ids[0]
        new_header_row = {
            'id':   new_header_row_id,
            'type': u'discrete',
        }
        new_header_col = {'type': u'discrete'}
        new_col_ids = Crosstab.get_unique_items(
                [
                        self.values[(row_id, new_header_row_id)]
                                for row_id in self.row_ids
                ]
        )
        new_row_ids = []
        new_values  = {}
        if len(self.col_ids) > 1:
            new_header_col['id'] = self.col_ids[1]
            new_header_col_id = new_header_col['id']
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
            if self.cached_row_id is not None:
                cached_row_id = self.cached_row_id
            else:
                cached_row_id = u'__data__'
            new_row_ids.append(cached_row_id)
            for row_id in self.row_ids:
                pair = (
                        cached_row_id,
                        self.values[row_id, new_header_row_id],
                )
                new_values[pair] = new_values.get(pair, 0) + 1
                if progress_callback:
                    progress_callback()
        return(IntPivotCrosstab(
                new_row_ids,
                new_col_ids,
                new_values,
                new_header_row,
                new_header_col,
                dict([(col_id, u'continuous') for col_id in new_col_ids]),
                None,
                self.missing,
                self.cached_row_id,
        ))

    def to_weighted_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'weighted and flat' format"""
        new_col_ids = list(self.col_ids)
        new_col_type = dict(self.col_type)
        row_counter  = 1
        new_values   = {}
        new_row_ids  = []
        if len(self.col_ids) > 1:
            first_col_id  = self.col_ids[0]
            second_col_id = self.col_ids[1]
            row_id_for_pair = {}
            for row_id in self.row_ids:
                first_col_value  = self.values[row_id, first_col_id]
                second_col_value = self.values[row_id, second_col_id]
                pair = (first_col_value, second_col_value)
                if pair in row_id_for_pair.keys():
                    known_pair_row_id = row_id_for_pair[pair]
                    new_values[(known_pair_row_id, u'__weight__')] \
                            = new_values[(known_pair_row_id, u'__weight__')]+1
                else:
                    new_row_id = unicode(row_counter)
                    new_row_ids.append(new_row_id)
                    row_id_for_pair[pair] = new_row_id
                    new_values[(new_row_id, first_col_id)] = first_col_value
                    new_values[(new_row_id, second_col_id)] = second_col_value
                    new_values[(new_row_id, u'__weight__')] = 1
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        else:
            col_id  = self.col_ids[0]
            row_id_for_value = {}
            for row_id in self.row_ids:
                col_value = self.values[row_id, col_id]
                if col_value in row_id_for_value.keys():
                    known_value_row_id = row_id_for_value[col_value]
                    new_values[(known_value_row_id, u'__weight__')] \
                            = new_values[(known_value_row_id, u'__weight__')]+1
                else:
                    new_row_id = unicode(row_counter)
                    new_row_ids.append(new_row_id)
                    row_id_for_value[col_value] = new_row_id
                    new_values[(new_row_id, col_id)] = col_value
                    new_values[(new_row_id, u'__weight__')] = 1
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        new_col_ids.append(u'__weight__')
        new_col_type[u'__weight__'] = u'continuous'
        return(IntWeightedFlatCrosstab(
                new_row_ids,
                new_col_ids,
                new_values,
                self.header_row,
                self.header_col,
                new_col_type,
                None,
                self.missing,
                self.cached_row_id,
        ))


class WeightedFlatCrosstab(Crosstab):

    """A class for storing crosstabs in 'weighted and flat' format in LTTL."""

    def to_pivot(self, progress_callback=None):
        """Return a copy of the crosstab in 'pivot' format"""
        new_header_row_id = self.col_ids[0]
        new_header_row = {
            'id':   new_header_row_id,
            'type': u'discrete',
        }
        new_header_col = {'type': u'discrete'}
        new_col_ids = Crosstab.get_unique_items(
                [
                        self.values[(row_id, new_header_row_id)]
                                for row_id in self.row_ids
                ]
        )
        new_row_ids = []
        new_values  = {}
        if len(self.col_ids) > 2:
            new_header_col['id'] = self.col_ids[1]
            new_header_col_id = new_header_col['id']
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
                new_values[pair] = self.values[row_id, u'__weight__']
                if progress_callback:
                    progress_callback()
        else:
            if self.cached_row_id is not None:
                cached_row_id = self.cached_row_id
            else:
                cached_row_id = u'__data__'
            new_row_ids.append(cached_row_id)
            for row_id in self.row_ids:
                pair = (
                        cached_row_id,
                        self.values[row_id, new_header_row_id],
                )
                new_values[pair] = self.values[row_id, u'__weight__']
                if progress_callback:
                    progress_callback()
        return(PivotCrosstab(
                new_row_ids,
                new_col_ids,
                new_values,
                new_header_row,
                new_header_col,
                dict([(col_id, u'continuous') for col_id in new_col_ids]),
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
            progress_callback = progress_callback
        )
        pivot.__class__ = IntPivotCrosstab
        return pivot

    def to_flat(self, progress_callback=None):
        """Return a copy of the crosstab in 'flat' format"""
        new_col_ids = list([c for c in self.col_ids if c != u'__weight__'])
        new_col_type = dict(self.col_type)
        del new_col_type[u'__weight__']
        row_counter  = 1
        new_values   = {}
        new_row_ids  = []
        if len(self.col_ids) > 1:
            first_col_id  = self.col_ids[0]
            second_col_id = self.col_ids[1]
            for row_id in self.row_ids:
                count = self.values[(row_id, u'__weight__')]
                first_col_value  = self.values[row_id, first_col_id]
                second_col_value = self.values[row_id, second_col_id]
                for i in xrange(count):
                    new_row_id = unicode(row_counter)
                    new_row_ids.append(new_row_id)
                    new_values[(new_row_id, first_col_id)]  = first_col_value
                    new_values[(new_row_id, second_col_id)] = second_col_value
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        else:
            col_id  = self.col_ids[0]
            for row_id in self.row_ids:
                count = self.values[(row_id, u'__weight__')]
                col_value  = self.values[row_id, col_id]
                for i in xrange(count):
                    new_row_id = unicode(row_counter)
                    new_row_ids.append(new_row_id)
                    new_values[(new_row_id, col_id)]  = col_value
                    row_counter += 1
                if progress_callback:
                    progress_callback()
        return(FlatCrosstab(
                new_row_ids,
                new_col_ids,
                new_values,
                self.header_row,
                self.header_col,
                new_col_type,
                None,
                self.missing,
                self.cached_row_id,
        ))

