import numpy as np
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, TextInput, DataTable, TableColumn, ColorBar, MultiChoice, RangeSlider
from bokeh.plotting import figure

from .utils import get_color_mapping, LabelStudioClient, get_datatable_columns

ls_client = LabelStudioClient()

def float_label_filter(df, values):
    min_val = values[0]
    max_val = values[1]

    return df[(df['color'] > min_val) & (df['color'] < max_val)]

def default_label_filter(df, values):
    return df[df['color'].isin(values)]

def bulk_text(path):
    def bkapp(doc):
        df = pd.read_csv(path)
        LABEL_IS_FLOAT = df['color'].dtype == np.float64
        highlighted_idx = []

        mapper, df = get_color_mapping(df)
        columns = [
            TableColumn(field=col, title=col) for col in get_datatable_columns(df)
        ]

        def update(attr, old, new):
            """Callback used for plot update when lasso selecting"""
            global highlighted_idx
            subset = df.iloc[new]
            highlighted_idx = new
            subset = subset.iloc[np.random.permutation(len(subset))]

            if label_filter_widget.value:
                subset = filter_func(subset, label_filter_widget.value)

            source.data = subset

        def update_on_label_filter(attr, old, new):
            """Callback used for plot update when changing label filter"""
            global highlighted_idx
            subset = df.iloc[highlighted_idx]
            subset = subset.iloc[np.random.permutation(len(subset))]

            if new:
                subset = filter_func(subset, new)

            source.data = subset

        def save():
            """Callback used to save highlighted data points"""
            global highlighted_idx
            subset = df.iloc[highlighted_idx]

            if label_filter_widget.value:
                subset = filter_func(subset, label_filter_widget.value)

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

            color_bar = ColorBar(color_mapper=mapper['transform'], width=8)
            p.add_layout(color_bar, 'right')

        scatter = p.circle(**circle_kwargs)
        p.plot_width = 600
        p.plot_height = 600

        scatter.data_source.selected.on_change('indices', update)

        tab_name = TextInput(value="", title="Tab name:")
        tab_btn = Button(label="Create tab")
        tab_btn.on_click(save)

        if LABEL_IS_FLOAT:
            min_val = df['color'].min()
            max_val = df['color'].max()
            label_filter_widget = RangeSlider(title='label filters', start=min_val, end=max_val, value=(min_val, max_val), step=0.01)

            filter_func = float_label_filter
        else:
            df['color'] = df['color'].astype(str)  # MultiChoice works only with Strings
            label_filter_widget = MultiChoice(title='label filters', options=df.color.unique().tolist())

            filter_func = default_label_filter

        label_filter_widget.on_change('value', update_on_label_filter)

        controls = column(p, tab_name, label_filter_widget, tab_btn)
        return doc.add_root(
            row(controls, data_table)
        )

    return bkapp