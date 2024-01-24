from itertools import zip_longest
from typing import Any, Iterable, Iterator

import numpy as np
from bokeh.layouts import column, row
from bokeh.models import Button, ColorBar, ColumnDataSource, DataTable, MultiChoice, RangeSlider, TableColumn, \
    TextInput, HTMLTemplateFormatter
from bokeh.plotting import figure

from bundler.utils.ls_client import LabelStudioClient
from bundler.utils.utils import get_datatable_columns, label_filter, read_file

ls_client = LabelStudioClient()


def grouper(iterable: Iterable, n: int, *, incomplete: str = "fill", fillvalue: Any = None) -> Iterator:
    """
    Collect data into non-overlapping fixed-length chunks or blocks

    Args:
        iterable (Iterable): The iterable to be grouped.
        n (int): Desired length of chunks or blocks.
        incomplete (str): Strategy to handle incomplete chunks: "fill", "strict", or "ignore".
        fillvalue (Any): The value to fill in for missing values if incomplete is "fill". Default is None.

    Returns:
        Iterator: An iterator producing tuples of elements from the iterable. The length of these
            tuples is determined by `n`, and the behavior of incomplete chunks is determined by the
            `incomplete` argument.
    """
    args = [iter(iterable)] * n
    if incomplete == "fill":
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == "strict":
        return zip(*args, strict=True)
    if incomplete == "ignore":
        return zip(*args)
    else:
        raise ValueError("Expected fill, strict, or ignore")


def bulk_images(path):
    """
    Returns a Bokeh application function to visualize images and data from a CSV file.

    Args:
        path (str): The file system path to the CSV file containing image paths and accompanying data.

    Returns:
        function: A Bokeh application function that can be used to serve an interactive data table
            and image viewer.

    The application lets the user select data points (images) and optionally filter by a 'color'
    column using widgets. The filtered or selected data can be saved in a new tab within a Bokeh server.
    """

    def bkapp(doc):
        """
        The Bokeh application function that creates interactive data and image visualization.

        Parameters:
            doc: The Bokeh document to which elements can be added.

        This inner function sets up the layout and interactive callbacks of the Bokeh application.
        """
        mapper, df = read_file(path)

        # Indices of the selected/highlighted images
        highlighted_idx = []

        columns = [
                      TableColumn(
                          field="image",
                          title="image",
                          formatter=HTMLTemplateFormatter(template="<%=image%>"),
                      )
                  ] + [
                      TableColumn(field=col, title=col) for col in get_datatable_columns(df) if col != "image"
                  ]

        is_label_float = str(df["color"].dtype).startswith("float") if mapper is not None else None

        def update(attr, old, new):
            """Callback used for plot update when lasso selecting"""
            global highlighted_idx
            subset = df.iloc[new]
            highlighted_idx = new
            subset = subset.iloc[np.random.permutation(len(subset))]

            if mapper is not None and label_filter_widget.value:
                subset = label_filter(subset, label_filter_widget.value, is_label_float)

            source.data = subset

        def update_on_label_filter(attr, old, new):
            """Callback used for plot update when changing label filter"""
            global highlighted_idx
            subset = df.iloc[highlighted_idx]
            subset = subset.iloc[np.random.permutation(len(subset))]

            if mapper is not None and new:
                subset = label_filter(subset, new, is_label_float)

            source.data = subset

        def save():
            """Callback used to save highlighted data points"""
            global highlighted_idx
            subset = df.iloc[highlighted_idx]

            if mapper is not None and label_filter_widget.value:
                subset = label_filter(subset, label_filter_widget.value, is_label_float)

            ls_client.create_tab(subset, tab_name.value)

        source = ColumnDataSource(data=dict())
        source_orig = ColumnDataSource(data=df)

        data_table = DataTable(
            source=source,
            columns=columns,
            row_height=100
        )
        source.data = df[:20]

        p = figure(
            title="",
            sizing_mode="scale_both",
            tools=["lasso_select", "box_select", "pan", "box_zoom", "wheel_zoom", "reset"]
        )
        p.toolbar.active_drag = None
        p.toolbar.active_inspect = None

        circle_kwargs = {
            "x": "x",
            "y": "y",
            "size": 1,
            "source": source_orig
        }
        if "color" in df.columns:
            circle_kwargs.update({"color": mapper})
            color_bar = ColorBar(color_mapper=mapper["transform"], width=8)
            p.add_layout(color_bar, "right")

        scatter = p.circle(**circle_kwargs)
        p.plot_width = 800
        p.plot_height = 800

        scatter.data_source.selected.on_change("indices", update)

        tab_name = TextInput(value="", title="Tab name:")
        tab_btn = Button(label="Create tab")
        tab_btn.on_click(save)

        if mapper is not None:
            # adding filtering widget if 'color' column exists
            if is_label_float:
                min_val = df["color"].min()
                max_val = df["color"].max()
                label_filter_widget = RangeSlider(title="label filters", start=min_val, end=max_val,
                                                  value=(min_val, max_val), step=0.01)
            else:
                df["color"] = df["color"].astype(str)  # MultiChoice works only with Strings
                label_filter_widget = MultiChoice(
                    title="label filters",
                    options=df.color.unique().tolist()
                )

            label_filter_widget.on_change("value", update_on_label_filter)
            controls = column(p, tab_name, label_filter_widget, tab_btn)
        else:
            controls = column(p, tab_name, tab_btn)

        return doc.add_root(
            row(controls, data_table)
        )

    return bkapp
