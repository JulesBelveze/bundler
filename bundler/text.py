import numpy as np
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import Button, ColorBar, ColumnDataSource, DataTable, MultiChoice, RangeSlider, TableColumn, TextInput
from bokeh.plotting import figure

from .utils import LabelStudioClient, get_color_mapping, get_datatable_columns

ls_client = LabelStudioClient()


def label_filter(df, values, is_label_float):
    """"""
    if is_label_float:
        min_val, max_val = values
        return df[(df["color"] > min_val) & (df["color"] < max_val)]
    else:
        return df[df["color"].isin(values)]


def bulk_text(path):
    def bkapp(doc):
        df = pd.read_csv(path)

        highlighted_idx = []

        mapper, df = get_color_mapping(df)
        columns = [
            TableColumn(field=col, title=col) for col in get_datatable_columns(df)
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

        data_table = DataTable(source=source, columns=columns, width=800)
        source.data = df

        p = figure(title="", sizing_mode="scale_both",
                   tools=["lasso_select", "box_select", "pan", "box_zoom", "wheel_zoom", "reset"])
        p.toolbar.active_drag = None
        p.toolbar.active_inspect = None

        circle_kwargs = {"x": "x", "y": "y", "size": 1, "source": source_orig}
        if "color" in df.columns:
            circle_kwargs.update({"color": mapper})

            color_bar = ColorBar(color_mapper=mapper["transform"], width=8)
            p.add_layout(color_bar, "right")

        scatter = p.circle(**circle_kwargs)
        p.plot_width = 600
        p.plot_height = 600

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
                label_filter_widget = MultiChoice(title="label filters", options=df.color.unique().tolist())

            label_filter_widget.on_change("value", update_on_label_filter)
            controls = column(p, tab_name, label_filter_widget, tab_btn)
        else:
            controls = column(p, tab_name, tab_btn)

        return doc.add_root(
            row(controls, data_table)
        )

    return bkapp
