import csv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def maybe_update(kwargs, series):
    if kwargs is not None:
        # if kwargs aren't empty:
        kwargs.update(series.to_dict())
    else:
        # Otherwise kwargs are empty so assign full value
        kwargs = series.to_dict()
    return kwargs

def sanitize(x):
    """Turns a string x into a valid Python variable for dictionaries"""
    return x.lower().replace(' ', "_").replace("/", "_per_")


class Plate():
    merge_columns = ['well', 'row_letter', 'column_number']

    def __init__(self, data, plate, repeat, barcode, formula, measurement_date,
                 measured_height, inside_temperature_at_start,
                 inside_temperature_at_end, humidity_at_start, humidity_at_end,
                 ambient_temperature_at_start, ambient_temperature_at_end,
                 group, label, scanx, scany, measinfo, kinetics, result,
                 signal, flashes_per_time, meastime, plate_map=None,
                 control='DMSO', ignore_edge_rows=True, raw_cmap='RdYlGn',
                 computed_cmap="RdBu"):

            self.raw_data = data
            self.rawdata_tidy = self.tidify(self.raw_data, value='raw_values')
            self.plate = plate
            self.repeat = repeat
            self.barcode = barcode
            self.formula = formula
            self.measurement_date = measurement_date
            self.measured_height = measured_height
            self.inside_temperature_at_start = inside_temperature_at_start
            self.inside_temperature_at_end = inside_temperature_at_end
            self.humidity_at_start = humidity_at_start
            self.humidity_at_end = humidity_at_end
            self.ambient_temperature_at_start = ambient_temperature_at_start
            self.ambient_temperature_at_end = ambient_temperature_at_end
            self.group = group
            self.label = label
            self.scanx = scanx
            self.scany = scany
            self.measinfo = measinfo
            self.kinetics = kinetics
            self.result = result
            self.signal = signal
            self.flashes_per_time = flashes_per_time
            self.meastime = meastime

            # Get user-supplied attributes about the plate
            self.map = plate_map
            self.map_tidy = self.tidify(self.map, value='plate_map')
            self.control = control
            self.ignore_edge_rows = ignore_edge_rows

            # Save colormaps for plotting
            self.raw_cmap = raw_cmap
            self.computed_cmap = computed_cmap

            # Make tidy format of both plate measured values and map
            self.merge_plate_data_and_map()

            # Compute percent viability
            self.computed_data = 100 * self.raw_data / self.mean()
            self.computed_tidy = self.tidify(self.computed_data,
                                             'computed_values')

            # Add computed percent viability to tidy
            self.tidy = self.tidy.merge(self.computed_tidy,
                                        on=self.merge_columns)


    @staticmethod
    def tidify(data2d, value='value'):
        """Convert 2d raw_data matrix to tidy format, each row is 1 observation"""
        data2d.index.name = 'row_letter'
        data2d.columns.name = 'column_number'
        tidy = data2d.unstack().reset_index()
        tidy = tidy.rename(columns={0: value})
        tidy['well'] = tidy['row_letter'] + tidy['column_number']
        return tidy

    def merge_plate_data_and_map(self):

        self.tidy = self.map_tidy.merge(self.rawdata_tidy,
                                        on=self.merge_columns,
                                        suffixes=['_map', '_data'])



    def __repr__(self):
        return f"Plate measured at {self.measurement_date}"

    def plot(self, ax=None, raw=True):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        if raw:
            data = self.raw_data
            cmap = self.raw_cmap
        else:
            data = self.computed_data
            cmap = self.computed_cmap

        sns.heatmap(data, annot=self.map, fmt='', ax=ax, cmap=cmap)

    @property
    def _tidy(self):
        """Internal method for tidy raw_data that deals with edge effects"""
        if self.ignore_edge_rows:
            tidy = self.tidy.query(
                '(row_letter not in @self.edge_letters)')
        else:
            tidy = self.tidy
        return tidy

    @property
    def controls(self):
        return self._tidy.query('plate_map == @self.control')

    @property
    def edge_letters(self):
        return self.raw_data.index[0], self.raw_data.index[-1]

    def mean(self):
        return self.controls['raw_values'].mean()

    def stdev(self):
        return self.controls['raw_values'].std()

    def cv(self):
        return 100 * self.stdev() / self.mean()



def reader(path):
    with open(path, newline='') as csv_file:
        out = {}
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if len(row) != 0:
                # Filter out empty strings with 'if x'
                out[idx] = [x.strip() for x in row if x]
    return out

def parse(path, plate_map, nrow_per_plate=8, plot=True):
    lines = reader(path)
    plates = []

    plate_kwargs = None
    background_kwargs = None
    data = None
    for key, value in lines.items():

        # Get plate layout information
        if value[0] == 'Plate information':
            keys = map(sanitize, lines[key + 1])
            arguments = [x if x != 'N/A' else np.nan for x in lines[key + 2]]
            series = pd.Series(dict(zip(keys, arguments))).dropna()
            plate_kwargs = maybe_update(plate_kwargs, series)


        # Get ambient temperature, humidity, time information
        if value[0] == 'Background information':
            keys = map(sanitize, lines[key + 1])
            arguments = [x if x != 'N/A' else np.nan for x in lines[key + 2]]
            series = pd.Series(dict(zip(keys, arguments))).dropna()
            background_kwargs = maybe_update(background_kwargs, series)

        # Get the values measured on the plate into a Pandas dataframe
        if value[0].startswith("Calculated results"):
            # range starts at next row
            # nrow+2 for header
            d = [lines[key + i] if i > 1 else ['well'] + lines[key + 1] for i in
                 range(1, nrow_per_plate + 2)]
            data = pd.DataFrame(d)
            data.columns = data.iloc[0]
            data = data.set_index('well')
            data = data.drop('well', axis=0)

            # Force integer type
            data = data.astype(int)

        # This is the duplicate data (raw uncorrected?)
        if value[0].startswith("Results for"):
            # Have seen all the data, time to make Plate object
            plate_kwargs.update(background_kwargs)
            plate = Plate(data, plate_map=plate_map,
                                       control='DMSO', ignore_edge_rows=True,
                                       **plate_kwargs)
            plates.append(plate)

            # Reset values
            plate_kwargs = None
            background_kwargs = None
            data = None
            if plot:
                plate.plot()

    return plates

