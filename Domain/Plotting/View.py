import random
from collections import Callable

from bokeh.core.property.dataspec import value
from bokeh.embed import components
from bokeh.models import HoverTool, DatetimeTickFormatter, ColumnDataSource, Range
from bokeh.plotting import Figure, figure
from bokeh.resources import CDN
from bokeh.transform import dodge
from pandas import DataFrame

from Domain.Plotting import PlotInfo, src
from Domain.functools.format import js_format


class BokehPlot(PlotInfo):
    supported_plots = ['distribution']

    @classmethod
    def get_plotter(cls, name):
        if name == 'distribution':
            return cls.plot_line
        if name in ('bar_week',):
            return cls.plot_categorical_bar
        raise NotImplementedError(name)

    def plot_line(self, data, x, y, legend):
        plot = figure(tools='box_zoom,save,reset', x_axis_type='datetime', y_range=(0, 100), title=self.title,
                      sizing_mode='stretch_both',
                      x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label)

        colors = self.colors(len(data))
        for df, legend, color in zip(data, legend, colors):
            l = plot.line(x=df[x], y=df[y], legend=legend, color=color, name=legend, line_width=2)

        plot.xaxis.formatter = DatetimeTickFormatter(
            hours=["%d.%m.%Y"],
            days=["%d.%m.%Y"],
            months=["%d.%m.%Y"],
            years=["%d.%m.%Y"],
        )

        plot.add_tools(HoverTool(
            tooltips=[
                (self.x_axis_label, "@x{%F}"),
                (self.y_axis_label, "@y"),
                ('Имя', "$name")
            ],
            point_policy='follow_mouse',
            formatters={"x": "datetime"}
        ))

        return plot

    def plot_categorical_bar(self, data, x, y, legend):
        plot = figure(tools='box_zoom,save,reset', y_range=(0, 100), x_range=legend, title=self.title,
                      sizing_mode='stretch_both',
                      x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label)

        source = ColumnDataSource(data=data)
        count = data.shape[1]
        colors = self.colors(count)
        print(data)
        for i, name in enumerate(data.columns.values.tolist()):
            plot.vbar(x=dodge(x, 0.25 + 0.5 * (i / max((count - 1), 1)), range=plot.x_range), top=name,
                      width=max(0.6 / count, 0.1),
                      source=source,
                      color=colors[i], legend=value(name), name=name)
        plot.x_range.range_padding = 0.1
        plot.xgrid.grid_line_color = None

        plot.add_tools(HoverTool(
            tooltips=[
                (self.x_axis_label, "$index"),
                (self.y_axis_label, "@$name"),
                ('Имя', "$name")
            ],
            point_policy='follow_mouse',
            formatters={"x": "datetime"}
        ))

        return plot

    @classmethod
    def colors(cls, n):
        colors = [
            (255, 87, 51),
            (240, 98, 146),
            (186, 104, 200),
            (149, 117, 205),
            (63, 81, 181),
            (66, 165, 245),
            (0, 150, 136),
            (76, 175, 80),
            (124, 179, 66),
            (175, 180, 43),
            (255, 235, 59),
            (245, 124, 0),
            (244, 81, 30),
            (121, 85, 72),
        ]
        if n > len(colors):
            return [random.choice(colors)] * n
        return random.sample(colors, n)

    def widget(self):
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        widget = QWebEngineView()
        widget.setHtml(self.html)
        return widget

    def create(self) -> str:

        func: Callable[[DataFrame, str, str, str, str], None] = self.get_plotter(self.plot_type)

        plot = func(self, self.data, self.x, self.y, self.legend)

        plot.legend.click_policy = "hide"
        plot.legend.location = "bottom_right"
        plot.xaxis.axis_label_text_font_size = "16pt"
        plot.yaxis.axis_label_text_font_size = "16pt"

        script, div = components(plot, CDN, 'my plot')
        with open(src.template, 'r') as template:
            data = js_format(template.read(), div=div, script=script)
            self.html = data
            return data
