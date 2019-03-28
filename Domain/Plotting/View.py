import random
from collections import Callable

from bokeh.embed import components
from bokeh.models import HoverTool, DatetimeTickFormatter
from bokeh.plotting import Figure, figure
from bokeh.resources import CDN
from pandas import DataFrame

from Domain.Plotting import PlotInfo, src
from Domain.functools.format import js_format


class BokehPlot(PlotInfo):
    supported_plots = ['distribution']

    @classmethod
    def get_plotter(cls, name):
        if name == 'distribution':
            return cls.plot_line
        raise NotImplementedError(name)

    @classmethod
    def plot_line(cls, plot: Figure, data, x, y, legend, color):
        return plot.line(x=data[x], y=data[y],
                         legend=legend, name=legend,
                         line_color=color, line_width=2)

    @classmethod
    def colors(cls, n):
        ret = []
        r = int(random.random() * 256)
        g = int(random.random() * 256)
        b = int(random.random() * 256)
        step = 256 / n
        for i in range(n):
            r += step*(n-1)
            g += step*(n-1)
            b += step*(n-1)
            r = int(r) % 256
            g = int(g) % 256
            b = int(b) % 256
            ret.append((r,g,b))
        return ret

    def widget(self):
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        widget = QWebEngineView()
        widget.setHtml(self.html)
        return widget

    def create(self) -> str:
        import locale
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        plot = figure(tools='box_zoom,save,reset', x_axis_type='datetime', y_range=(0, 100), title=self.title,
                      sizing_mode='stretch_both',
                      x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label)

        func: Callable[[Figure, DataFrame, str, str, str, str], None] = self.get_plotter(self.plot_type)
        colors = self.colors(len(self.data))
        for df, legend, color in zip(self.data, self.legend, colors):
            l = func(plot=plot, data=df, x=self.x, y=self.y, legend=legend, color=color)

        plot.xaxis.formatter = DatetimeTickFormatter(
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )
        plot.add_tools(HoverTool(
            tooltips=[
                (self.y_axis_label, "@x{%F}"),
                (self.y_axis_label, "@y"),
                ('Имя', "$name")
            ],
            point_policy='follow_mouse',
            formatters={"x": "datetime"}
        ))

        plot.legend.click_policy = "hide"
        plot.legend.location = "bottom_right"
        plot.xaxis.axis_label_text_font_size = "16pt"
        plot.yaxis.axis_label_text_font_size = "16pt"

        script, div = components(plot, CDN, 'my plot')
        with open(src.template, 'r') as template:
            data = js_format(template.read(), div=div, script=script)
            self.html = data
            return data
