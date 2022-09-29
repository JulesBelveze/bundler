import numpy as np
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, TextInput, DataTable, TableColumn, ColorBar, MultiChoice
from bokeh.plotting import figure

from .utils import get_color_mapping, LabelStudioClient, get_datatable_columns

ls_client = LabelStudioClient()


def bulk_text(path):
    def bkapp(doc):
        df = pd.read_csv(path)
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

            if label_filters.value:
                source.data = subset[subset['color'].isin(label_filters.value)]
            else:
                source.data = subset

        def save():
            """Callback used to save highlighted data points"""
            global highlighted_idx
            subset = df.iloc[highlighted_idx]

            if label_filters.value:
                subset = subset[subset['color'].isin(label_filters.value)]

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

        df['color'] = df['color'].astype(str) #MultiChoice works only with Strings

        label_filters = MultiChoice(title= 'label filters', options=df.color.unique().tolist())

        controls = column(p, tab_name, label_filters, tab_btn)
        return doc.add_root(
            row(controls, data_table)
        )

    return bkapp
