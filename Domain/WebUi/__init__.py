import datetime
from abc import abstractmethod
from random import randint
from typing import List, Any

from Domain.Validation.Values import Get
from Domain.functools.Format import format_name, js_format
from Domain.functools.List import without_None


class _grid_measure:
    main = None

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return self.main + str(self.val)


class MFuture:
    def __init__(self, key):
        self.key = key

    def set(self, val):
        return val


class MFunctionFuture(MFuture):
    def __init__(self, key, function, *pre_args, **pre_kwargs):
        super().__init__(key)
        self.function = function
        self.pre_args = pre_args
        self.pre_kwargs = pre_kwargs

    def set(self, *args, **kwargs):
        return self.function(*args, *self.pre_args, **kwargs, **self.pre_kwargs)


class MLambdaFuture(MFuture):
    def __init__(self, func):
        self.func = func

    def set(self):
        return self.func()


class offset(_grid_measure):
    main = "offset-"

    def __init__(self, val):
        if isinstance(val, _grid_measure):
            super().__init__(val.val)
            self.main += val.main
        else:
            raise NotImplementedError()


class s(_grid_measure):
    main = 's'


class m(_grid_measure):
    main = 'm'


class Grid:
    def __init__(self, *col):
        self._col = col

    def __set_monitor__(self, mobile):
        pass

    @property
    def col(self):
        if isinstance(self._col, _grid_measure):
            return str(self._col)
        elif isinstance(self._col, (tuple, list)):
            return ' '.join([str(i) for i in self._col])
        else:
            return ''

    def __str__(self):
        return self.col


class WebPage:
    main = """
<!DOCTYPE html>
<html lang="en">
<head>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Roboto+Mono" rel="stylesheet">
    <link rel="stylesheet" href="file/materialize{main_color}.css">
    <link rel="stylesheet" href="file/row_height_fix.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {style}
    {js_source}
</head>
<body style="font-family: 'Roboto Mono', monospace;">
{js_begin}
<header>
    {header}
</header>
{nav}
<main>
    <div class="{in_container}">
    {components}
    </div>
</main>
{footer}
<script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>  
{js}
{js_end}
<script> M.AutoInit(); </script>
</body>
</html>
"""

    def __init__(self, *components, header=None, nav=None, footer=None, title='Информационная панель преподавателя',
                 main_color='',
                 in_container=True):
        self.header = header
        self.nav = nav
        self.components: List[WebComponent] = [] if components is None else list(components)
        self.title = title
        self.footer = footer
        self.main_color = main_color
        self.in_container = in_container

    def insert(self, component, index=None):
        if isinstance(component, WebComponent):
            if index is None:
                self.components.append(component)
            else:
                self.components.insert(index, component)
        else:
            raise Exception()

    def show(self, main_color='', **future):
        def _set_future(obj):
            for item_name in dir(obj):
                item = getattr(obj, item_name)
                if isinstance(item, MFuture):
                    if isinstance(item, MLambdaFuture):
                        setattr(obj, item_name, item.set())
                    else:
                        setattr(obj, item_name, item.set(future.get(item.key)))
                    item = getattr(obj, item_name)
                if isinstance(item, WebComponent):
                    _set_future(item)
                if isinstance(item, (list, tuple)):
                    for sub_item in item:
                        _set_future(sub_item)

        if self.main_color is '':
            self.main_color = main_color

        if future is not None:
            _set_future(self)

        return self.main.format(
            title=self.title,
            header=self.header.__render__() if self.header is not None else '',
            nav=self.nav.__render__() if self.nav is not None else '',
            components=self._compile_components(),
            footer=self.footer if self.footer is not None else '',
            style=self._get_all('style'),
            js=self._get_all('js'),
            js_end=self._get_all('js_end'),
            js_source=self._get_all('js_source'),
            js_begin=self._get_all('js_begin'),
            main_color='-' + self.main_color if self.main_color != '' else '',
            in_container='container' if self.in_container else '')

    def _get_all(self, key):
        f = set()
        for item in without_None((*self.components, self.header, self.nav)):
            if isinstance(item, WebComponent):
                value = item.get(key)
                if isinstance(value, (str, int)):
                    f.add(value)
                elif isinstance(value, (set, list)):
                    f.update(value)
                else:
                    print(type(value), value)
            else:
                raise Exception(type(item), item)
        print(''.join(f))
        return ''.join(f)

    def _compile_components(self):
        return ''.join([component.__render__() for component in self.components])

    def __str__(self):
        return self.show()

    def __repr__(self):
        return self.show()


class WebComponent:
    main: str = None

    @abstractmethod
    def __render__(self) -> str:
        raise NotImplementedError()

    def get(self, key) -> str:
        return getattr(self, key, '')

    def __str__(self):
        return self.__render__()

    def _instances_of(self, type) -> List[str]:
        l = []
        for name in dir(self):
            try:
                if isinstance(getattr(self, name), type):
                    l.append(name)
            except TypeError:
                pass
        return l

    def params(self):
        if hasattr(self, '_params'):
            return ' '.join([f'{key}="{value}"' for key, value in self._params.items()])
        else:
            return ''


class WebContainer(WebComponent):
    def __init__(self, *components):
        self.container = list(components)

    def get(self, key):
        f = [WebComponent.get(self, key)]
        for item in self._items():
            try:
                value = item.get(key)
                if isinstance(value, str):
                    f.append(value)
                elif isinstance(value, list):
                    f.extend(value)
            except TypeError:
                raise TypeError(f'must be str in get {repr(item)} on key={key}')
            except AttributeError:
                pass
        return f

    def _items(self):
        return [getattr(self, name)
                for name in dir(self) if not name.startswith('_') and isinstance(getattr(self, name), WebComponent)] + \
               self.container

    def add(self, item: WebComponent):
        self.container.append(item)
        return self


class Row(WebContainer):
    main = "<div class='row{is_flex}'>{components}</div>"

    def __render__(self) -> str:
        return self.main.format(
            components=''.join(map(str, self._items())),
            is_flex=' flex' if self.flex else '')

    def __init__(self, *components, flex=False):
        super().__init__(*components)
        self.flex = flex


class Col(WebContainer):
    main = """<div class="col {grid}{is_flex}">{components}</div>"""

    def __render__(self) -> str:
        return self.main.format(
            grid=self.grid.col,
            components=''.join(map(str, self.container)),
            is_flex=' flex' if self.flex else '')

    def __init__(self, *components, grid=None, flex=False):
        super().__init__(*components)

        self.flex = flex
        if isinstance(grid, Grid):
            self.grid = grid
        elif isinstance(grid, _grid_measure):
            self.grid = Grid(grid)
        elif all(map(lambda x: isinstance(x, _grid_measure), grid)):
            self.grid = Grid(*grid)
        elif grid is None:
            self.grid = Grid()
        else:
            raise Exception(f'grid can not be {grid}')


class MForm(WebContainer):
    def __render__(self) -> str:
        return self.main.format(
            items=self.items(),
            submit=self.submit,
            method=self.method,
            action=self.action
        )

    main = """
<form action="{action}" method="{method}">
{items}
{submit}
</form>
"""

    def __init__(self, submit, elements, method="POST", action="/"):
        super().__init__(*elements)
        self.submit = submit
        self.method = method
        self.action = action

    def items(self):
        return '\n'.join(str(i) for i in self.container)


class MTextInput(WebComponent):
    def __render__(self) -> str:
        return self.main.format(
            label=self.label,
            name=self.name,
            placeholder=self.placeholder,
            type=self.type,
            id=self.id
        )

    main = """
    <input placeholder="{placeholder}" name="{name}" id="{id}" type="{type}" class="validate">
    <label for="{id}">{label}</label>
"""

    def __init__(self, label, placeholder='', name=None, id=None, type='text'):
        if id is None:
            id = f'input{randint(1, 1000000)}'

        self.id = id
        self.name = name
        self.placeholder = placeholder
        self.label = label
        self.type = type


class MList(WebContainer):
    main = """
    <ul class="collection">
      {components}
    </ul>"""

    def __render__(self):
        def element(c: WebComponent):
            return """<li class="collection-item">{}</li>""".format(str(c))

        return self.main.format(components=''.join(map(element, self.container)))


class MText(WebComponent):
    main = """
    <span class="flow-text">{text}</span>
    """

    def __init__(self, text):
        self.text = text

    def __render__(self):
        return self.main.format(text=self.text)


class P(WebComponent):
    def __render__(self) -> str:
        return self.main.format(p=self.text,
                                params=self.params())

    main = """
    <p {params}>{p}</p>"""

    def __init__(self, text, **style):
        self.text = text
        self._style = style


class MImage(WebComponent):
    def __render__(self) -> str:
        return self.main.format(address=self.address)

    main = """<div class="material-placeholder">
<image class="responsive-img" src="{address}">
</div>"""

    def __init__(self, address):
        self.address = address


class Header(WebContainer):
    def __render__(self) -> str:
        return """
  <nav>
    <div class="nav-wrapper">
      <a href="#!" class="brand-logo offset-s1">{logo}</a>
      <a href="#" data-target="mobile-demo" class="sidenav-trigger"><i class="material-icons">menu</i></a>
      <ul class="right hide-on-med-and-down">
        {items}
      </ul>
    </div>
  </nav>

  <ul class="sidenav" id="mobile-demo">
    {items}
  </ul>""".format(
            items=self.items(),
            logo=self.logo)

    def __init__(self, logo, *links):
        super().__init__()
        self.logo = logo
        self.links = list(links)

    def items(self):
        return ''.join([f'<li>{link}</li>' for link in self.links])


class MLink(WebContainer):
    def __render__(self) -> str:
        return self.main.format(address=self.address, text=self.text, **self.kwargs)

    main = """<a class="{text_color}" href='{address}'>{text}</a>"""

    def __init__(self, address, text=None, **kwargs):
        super().__init__()
        self.address = address
        if text is None:
            self.text = ''
        elif isinstance(text, MText):
            self.text = text
        else:
            self.text = MText(text)

        self.text = address if text is None else text

        self.kwargs = dict()
        self.kwargs['text_color'] = kwargs.get('text_color', None) + '-text' if kwargs.get(
            'text_color') is not None else ''


class Card(WebContainer):
    def _apply_mobile(self, is_mobile):
        self.position.__set_monitor__(is_mobile)

    main = """
    {page_link}
    <div class="col {col_pos} cell">
      <div class="card {bg_color} darken-1">
        <div class="card-content {text_color}-text">
          <span class="card-title">{title}</span>
          {body}
        </div>
        <div class="card-action">
          {links}
        </div>
      </div>
    </div>"""

    def __init__(self, title, body, *links, bg_color='white', text_color='black',
                 grid=Grid(s(12)), page_link=None):
        super().__init__()
        self.title = title
        self.body = body
        self.links = list(links)
        self.bg_color = bg_color
        self.text_color = text_color
        self.position: Grid = grid
        self.page_link = page_link

    def __render__(self) -> str:
        return self.main.format(
            title=self.title,
            body=self.body,
            links=self._prepare_links(),
            bg_color=self.bg_color,
            text_color=self.text_color,
            col_pos=self.position.col,
            page_link=f'<a name="{self.page_link}"></a>' if self.page_link is not None else ''
        )

    def _prepare_links(self):
        return ''.join([link.__render__() for link in self.links])


class SideNav(WebComponent):
    def __render__(self) -> str:
        return self.main.format(
            bg=self._background(),
            user_image=self._user_image(),
            user_name=self.user_name,
            user_contact=self.user_contact
        )

    style = """
    <style type='text/css'>
    header, main, footer {
      padding-left: 300px;
    }

    @media only screen and (max-width : 992px) {
      header, main, footer {
        padding-left: 0;
      }
    }
    </style>
    """

    main = """
    
     <ul id="slide-out" class="sidenav sidenav-fixed">
        <li><div class="user-view">
            <div class="background" style="background-image:('{bg}');"><a href='#'></a></div>
            <a href="#user"><img class="circle" src="{user_image}"></a>
            <a href="#name"><span class="white-text name">{user_name}</span></a>
            <a href="#email"><span class="white-text email">{user_contact}</span></a>
        </div>
    </li>
    <li>
        <a href="#!"><i class="material-icons">cloud</i>First Link With Icon</a>
    </li>
    <li>
        <a href="#!">Second Link</a>
    </li>
    <li>
        <div class="divider"></div>
    </li>
    <li>
        <a class="subheader">Subheader</a>
    </li>
    <li
        ><a class="waves-effect" href="#!">Third Link With Waves</a>
    </li>
  </ul>
  <a href="#" data-target="slide-out" class="sidenav-trigger show-on-large"><i class="material-icons">menu</i></a>"""

    def __init__(self, bg, user, user_image=None):
        self.bg = bg
        self.user_image = user_image
        self.user_name = format_name(user)
        self.user_contact = Get.email(user)

    def _background(self):
        if isinstance(self.bg, MImage):
            return self.bg.address
        elif self.bg is None:
            return ""
        else:
            raise NotImplementedError()

    def _user_image(self):
        if self.user_image is not None:
            return self.user_image.address
        else:
            return ""


class DataFrameTable(WebComponent):
    main = """{table}
<script>
$('#{table_id}').dynatable();
</script> 
"""

    def __render__(self) -> str:
        return self.main.format(
            table=self.df.to_html(table_id=self.id),
            table_id=self.id
        )

    def __init__(self, df, id='data_frame_table'):
        self.df = df
        self.id = id


class Section(WebContainer):
    def __render__(self) -> str:
        return self.main.format(title=self.title, body=self.body)

    main = """
<div class="divider"></div>
  <div class="section">
    <h5>{title}</h5>
    {body}
</div>"""

    def __init__(self, title='', body: Any = ''):
        super().__init__()
        self.title = title
        self.body = body


class DataFrameColumnChart(WebComponent):
    main = """
    <div class='convas-container' height=100% width=100%">
        <canvas id="{id}" ></canvas>
    </div>
    """

    js_source = "<script src='file/Chart.js'></script>"

    @property
    def js_end(self):
        return js_format("""<script>
Chart.defaults.global.defaultColor = 'rgba(255,128,0,0.4)'        

function beforePrintHandler () {
    for (var id in Chart.instances) {
        Chart.instances[id].resize()
    }
}
var ctx = document.getElementById("{id}");
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: {x_values},
        datasets: [{
            label: '{title}',
            data: {y_values},
            borderWidth: 1,
            backgroundColor: '{color}'
        }]
    },
    options: {
        scales: {
            xAxes: [{
                ticks: {
                    beginAtZero:true
                },
                scaleLabel: {
                    display: true,
                    labelString: '{xAxes_labelString}'
                }
            }],
            yAxes: [{
                display: true,
                ticks: {
                    beginAtZero: true,
                    steps: 10,
                    stepValue: 10,
                    max: 100
                },
                scaleLabel: {
                    display: true,
                    labelString: '{yAxes_labelString}'
                }
            }]
        }
    }
});
</script>""",
                         title=self.title,
                         x_values=self.x_values(),
                         y_values=self.y_values(),
                         id=self.id,
                         color=self.color,
                         **self.kwargs)

    def __render__(self) -> str:
        return self.main.format(id=self.id)

    def __init__(self, df, x='x', y='y',
                 label_font_color='#000',
                 title='Chart',
                 id='chartContainer' + str(randint(0, 1000000)),
                 color='rgba(255,128,0,0.75)',
                 **kwargs):
        self.df = df
        self.title = title
        self.label_font_color = label_font_color
        self.x, self.y = x, y
        self.id = id
        self.color = color
        self.kwargs = dict()
        self.kwargs['yAxes_labelString'] = kwargs.get('yAxes_labelString', '')
        self.kwargs['xAxes_labelString'] = kwargs.get('xAxes_labelString', '')

    def x_values(self):
        return '[{}]'.format(
            ','.join([str(i) for i in self.df[self.x]])
        )

    def y_values(self):
        return '[{}]'.format(
            ','.join([str(i) for i in self.df[self.y]])
        )


class Footer(WebContainer):
    def __render__(self) -> str:
        return self.main.format(components=''.join(map(str, self._items())),
                                copyright=self._copyright,
                                copyright_links=self._copyright_links)

    main = """
    <footer class="page-footer">
        {components}
        <div class="footer-copyright">
        <div class="container">
        {copyright}
        {copyright_links}
        </div>
      </div>
    </footer>"""

    def __init__(self, *components, **kwargs):
        super().__init__(*components)

        self._copyright = kwargs.get('copyright', '')
        self._copyright_links = kwargs.get('copyright_links', '')


class DataFrameSmartTable2(WebComponent):
    def __render__(self) -> str:
        return self.main.format(id=self.id)

    main = """
    <div id='{id}'></div>
    """

    js_begin = """<script src='file/table.js'></script>"""

    @property
    def js_end(self):
        return js_format("""<script>
    init_table('{id}', {data}, {params});
    </script>""",
                         id=self.id,
                         data=self.data(),
                         params=self.params)

    def __init__(self, df, id=None, params='{}'):
        if id is None:
            id = 'smart_table' + str(randint(0, 100000))
        self.df = df
        self.id = id
        self.params = params

    def data(self):
        d = {}

        df_dict = self.df.to_dict('split')
        for i, col in enumerate(df_dict['columns']):
            d[col] = list(map(lambda x: x[i], df_dict['data']))

        return d


class CardReveal(WebContainer):
    def __render__(self) -> str:
        return self.main.format(title=self.title,
                                img=self.img,
                                body=self.body,
                                links=''.join([str(l) for l in self.links]))

    main = """
    <div class="card">
    <div class="card-image waves-effect waves-block waves-light">
      <img class="activator" src="{img}">
    </div>
    <div class="card-content">
      <span class="card-title activator grey-text text-darken-4">{title}<i class="material-icons 
      right">more_vert</i></span>
      <p>{links}</p>
    </div>
    <div class="card-reveal">
      <span class="card-title grey-text text-darken-4">{title}<i class="material-icons right">close</i></span>
      {body}
    </div>
  </div>
    """

    def __init__(self, title, body, links, img=''):
        super().__init__(*links)
        self.title = title
        self.body = body
        self.links = links
        self.img = img


class MButton(WebContainer):
    def __render__(self) -> str:
        return self.main.format(text=self.text,
                                img_before=self.img_before,
                                img_after=self.img_after,
                                params=self.params())

    main = """
    <a class="waves-effect waves-light btn" {params}>{img_before}{text}{img_after}</a>"""

    def __init__(self, text, img_before='', img_after='', **params):
        super().__init__()

        self.text = text
        self.img_before = img_before
        self.img_after = img_after
        self._params = params

        params.get('href')


class MSubmitButton(WebComponent):
    def __render__(self) -> str:
        return self.main.format(
            text=self.text,
            icon_before=self.icon_before,
            icon_after=self.icon_after
        )

    main = """
<button class="btn waves-effect waves-light" type="submit" name="action">
{icon_before}
{text}
{icon_after}
</button>"""

    def __init__(self, text, icon_before='', icon_after=''):
        self.text = text
        self.icon_before = icon_before
        self.icon_after = icon_after


class CollapsibleBlock(WebContainer):
    def __render__(self) -> str:
        return self.main.format(body=''.join([str(c) for c in self.container]))

    main = """
    <ul class="collapsible">
    {body}
    </ul>
    """

    js_end = """<script>
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.collapsible');
    var instances = M.Collapsible.init(elems, {});
});
</script>"""

    def __init__(self, *items):
        super().__init__(*items)


class Collapsible(WebContainer):
    def __render__(self) -> str:
        return self.main.format(title=self.tittle,
                                body=self.body,
                                icon=self.icon)

    main = """
    <li>
      <div class="collapsible-header"><i class="material-icons">expand_more</i><i 
      class="material-icons">{icon}</i>{title}</div>
      <div class="collapsible-body"><span>{body}</span></div>
    </li>
    """

    def __init__(self, body, title='', icon='bar_chart'):
        super().__init__()
        self.tittle = title
        self.body = body
        self.icon = icon


class TabContainer(WebContainer):
    main = """
    <div class="row">
    <div class="col s12">
      <ul class="tabs">
        {titles}
      </ul>
    </div>
    {bodies}
  </div>
    """

    js_end = """
<script>
var instance = M.Tabs.init(document.querySelector('.tabs'), {});
</script>"""

    def __render__(self) -> str:
        return self.main.format(
            titles=self.titels(),
            bodies=self.bodies()
        )

    def __init__(self, *tabs, id=None):
        super().__init__(*tabs)

        if id is None:
            id = f's{randint(0, 100000000)}'
        self.id = id

    def titels(self):
        return ''.join(f'<li class="tab col {self.id}">{t.title()}</li>' for t in self.container)

    def bodies(self):
        return ''.join(f'<div id="{t.id}" class="col s12">{t.body()}</div>' for t in self.container)


class Tab(WebContainer):
    def __init__(self, title, body, id=None):
        super().__init__(body)
        if id is None:
            id = f'tab_item{randint(1, 1000000)}'

        self.id = id

        if isinstance(title, MLink):
            self._title = title
        elif isinstance(title, (int, str)):
            self._title = MLink(address=f'#{id}', text=title)

        self._body = body

    def title(self):
        return self._title

    def body(self):
        print(self._body)
        return self._body


if __name__ == '__main__':
    from DataBase2 import Session, Professor
    from Domain.Aggregation import Weeks, Column
    from Domain.Date import study_week

    from matplotlib import pyplot as plt

    professor = Session().query(Professor).all()[0]


    def speed_test():
        start = datetime.datetime.now()
        d = WebPage(
            Row(
                Card(
                    'Добро пожаловать',
                    'Система предназанчена для мониторинга посещаемости. Ниже вы можете увидеть базовые представления.',
                    grid=Grid(m(6), s(12))),
                Card('В разработке',
                     'На данный момент система находится в разратоке - возможны перебои стабильности.',
                     grid=Grid(m(6), s(12)))),
            Section(
                title='Посещения по неделям на всех ваших занятиях',
                body=DataFrameColumnChart(
                    Weeks.by_professor(professor),
                    x=Column.date,
                    y=Column.visit_rate,
                    title='Посещения в неделю, %',
                    xAxes_labelString='Неделя', yAxes_labelString='Посещения, %')),
            header=Header(
                'СПбГУТ',
                MLink('#', format_name(professor, small=True)),
                MLink('#', f'Текущая неделя: {study_week()}'),
                MLink('/', 'Выход')),
            footer=Footer(
                Row(
                    Col(
                        MList(
                            MLink(address='#', text='1'),
                            MLink(address='#', text='2'),
                        ),
                        grid=Grid(s(6), offset(s(6)))
                    )
                ),
                copyright=MText('(c) СПбГУТ 2018г')
            )
        )
        generated = datetime.datetime.now()
        d.show()
        futured = datetime.datetime.now()
        del d
        return (generated - start).microseconds, (futured - generated).microseconds


    d = []
    for t in range(100):
        d.append(speed_test())

    plt.plot(range(len(d)), list(map(lambda x: int(x[0]), d)))
    plt.plot(range(len(d)), list(map(lambda x: int(x[1]), d)))

    plt.show()
