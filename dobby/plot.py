import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .util import maybe_make_directory


def _plot_regression(means, regressed, plate_name, output_folder='.'):
    means.plot(legend=True)
    y = pd.Series(regressed.slope * means.index + regressed.intercept,
                  index=means.index,
                  name='Regression')
    y.plot(legend=True)

    # :.5 indicates 5 decimal places
    plt.title(f'$R^2$ = {regressed.rvalue:.5}')

    pdf = os.path.join(output_folder, 'regression',
                       f'{plate_name}_regression_lines.pdf')
    maybe_make_directory(pdf)
    plt.savefig(pdf)

    sys.stderr.write(f'{plate_name}: Wrote regression plot to {pdf}')
    return pdf


def heatmap(data, plate_name, datatype, output_folder):
    sns.heatmap(data)
    plt.title(f'{plate_name} {datatype}')
    pdf = os.path.join(output_folder, datatype,
                       f'{plate_name}_{datatype}_heatmap.pdf')
    maybe_make_directory(pdf)
    plt.savefig(pdf)
    sys.stderr.write(f'{plate_name}: Wrote {datatype} heatmap to {pdf}\n')
    return pdf