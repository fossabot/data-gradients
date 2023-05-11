import dataclasses
from typing import Mapping, Optional, Tuple, Union

import pandas as pd

__all__ = ["CommonPlotOptions", "BarPlotOptions", "Hist2DPlotOptions", "PlotRenderer"]


@dataclasses.dataclass
class CommonPlotOptions:
    title: str


@dataclasses.dataclass
class BarPlotOptions(CommonPlotOptions):
    """
    Contains a set of options for displaying a bar plot

    Parameters:
    - x_label_key: A key for x-axis values
    - x_label_name: A title for x-axis
    - y_label_key: An optional key for y-axis (If None, bar plot will use count of x-axis values)
    - y_label_name: A title for y-axis
    - width: Width of the bars
    - bins: Generic bin parameter that can be the name of a reference rule, the number of bins, or the breaks of the bins.
    - x_ticks_rotation: X-ticks rotation (Helps to make more compact plots)
    - y_ticks_rotation: Y-ticks rotation
    - labels_key: If you want to display multiple classes on same plot use this property to indicate column
    - labels_palette: Setting this allows you to control the colors of the bars of each label: { "train": "royalblue", "val": "red", "test": "limegreen" }
    - log_scale: If True, y-axis will be displayed in log scale
    - tight_layout: If True enables more compact layout of the plot
    - figsize: Size of the figure

    """

    x_label_key: str
    x_label_name: str
    y_label_key: Optional[str]
    y_label_name: str

    width: float = 0.8
    bins: Optional[int] = None

    x_ticks_rotation: Optional[int] = 45
    y_ticks_rotation: Optional[int] = 0

    labels_key: Optional[str] = None
    labels_name: Optional[str] = None
    labels_palette: Optional[Mapping] = None

    log_scale: Union[bool, str] = "auto"
    tight_layout: bool = False
    figsize: Optional[Tuple[int, int]] = (10, 6)


@dataclasses.dataclass
class Hist2DPlotOptions(CommonPlotOptions):
    """
    Contains a set of options for displaying a bivariative histogram plot.

    Parameters:
    - x_label_key: A key for x-axis values
    - x_label_name: A title for x-axis
    - y_label_key: An optional key for y-axis (If None, bar plot will use count of x-axis values)
    - y_label_name: A title for y-axis
    - bins: Generic bin parameter that can be the name of a reference rule, the number of bins, or the breaks of the bins.
    - kde: If True, will display a kernel density estimate
    - individual_plots_key: If not None, will create a separate plot for each unique value of this column
    - individual_plots_max_cols: Sets the maximum number of columns to plot in the individual plots
    - labels_key: If you want to display multiple classes on same plot use this property to indicate column
    - labels_palette: Setting this allows you to control the colors of the bars of each label: { "train": "royalblue", "val": "red", "test": "limegreen" }
    - tight_layout: If True enables more compact layout of the plot
    - figsize: Size of the figure

    """

    x_label_key: str
    x_label_name: str

    y_label_key: str
    y_label_name: str

    bins: Optional[int] = None
    kde: bool = False

    individual_plots_key: str = None
    individual_plots_max_cols: int = None

    labels_key: Optional[str] = None
    labels_name: Optional[str] = None
    labels_palette: Optional[Mapping] = None

    tight_layout: bool = False
    figsize: Optional[Tuple[int, int]] = (10, 6)

    x_ticks_rotation: Optional[int] = 45
    y_ticks_rotation: Optional[int] = 0


@dataclasses.dataclass
class ScatterPlotOptions(CommonPlotOptions):
    """
    Contains a set of options for displaying a bivariative histogram plot.

    Parameters:
    - x_label_key: A key for x-axis values
    - x_label_name: A title for x-axis
    - y_label_key: An optional key for y-axis (If None, bar plot will use count of x-axis values)
    - y_label_name: A title for y-axis
    - bins: Generic bin parameter that can be the name of a reference rule, the number of bins, or the breaks of the bins.
    - kde: If True, will display a kernel density estimate
    - individual_plots_key: If not None, will create a separate plot for each unique value of this column
    - individual_plots_max_cols: Sets the maximum number of columns to plot in the individual plots
    - labels_key: If you want to display multiple classes on same plot use this property to indicate column
    - labels_palette: Setting this allows you to control the colors of the bars of each label: { "train": "royalblue", "val": "red", "test": "limegreen" }
    - tight_layout: If True enables more compact layout of the plot
    - figsize: Size of the figure

    """

    x_label_key: str
    x_label_name: str

    y_label_key: str
    y_label_name: str

    individual_plots_key: str = None
    individual_plots_max_cols: int = None

    labels_key: Optional[str] = None
    labels_name: Optional[str] = None
    labels_palette: Optional[Mapping] = None

    tight_layout: bool = False
    figsize: Optional[Tuple[int, int]] = (10, 6)


class PlotRenderer:
    def render_with_options(self, df: pd.DataFrame, options):
        raise NotImplementedError()
