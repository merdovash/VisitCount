import _md5
import random

import flask
from flask import render_template, request

from DataBase2 import Auth, Session, Discipline
from Domain.Aggregation import Weeks, Column, StudentAggregator, DisciplineAggregator
from Domain.Date import study_week
from Domain.Exception.Authentication import InvalidLoginException, InvalidPasswordException, AuthenticationException, \
    InvalidUidException
from Domain.WebUi import WebPage, MHeader, MCard, Grid, s, m, MLink, DataFrameColumnChart, \
    MRow, MFooter, MList, Col, offset, MText, DataFrameSmartTable2, CollapsibleBlock, Collapsible, \
    TabContainer, Tab, MForm, MTextInput, MButton, MSubmitButton
from Domain.functools.Format import format_name


def new_uid(session):
    """

    :return: new unique session id
    """
    number = (random.random() * 100000000000000000) % 13082761331670031
    value = _md5.md5(str(number).encode()).hexdigest()
    while session.query(Auth.uid).filter(Auth.uid == value).first():
        number = (random.random() * 100000000000000000) % 13082761331670031
        value = _md5.md5(str(number).encode()).hexdigest()
    return value


def is_mobile(user_agent: str):
    return any([target in user_agent.lower() for target in ('iphone', 'android', 'blackberry''')])


def login(func):
    def wrapper(*args, **kwargs):
        if request.method == 'POST':
            try:
                auth = Auth.log_in(login=request.form.get('login', None), password=request.form.get('password'))
                auth.uid = new_uid(auth.session)
                auth.session.commit()

                res = flask.make_response()
                res.set_cookie('uid', auth.uid)

                return func(*args, **kwargs, response=res, auth=auth)

            except AuthenticationException as e:
                try:
                    if 'uid' in request.cookies:
                        try:
                            auth = Auth.log_in_by_uid(request.cookies['uid'])
                            return func(*args, **kwargs, auth=auth, response=flask.make_response())
                        except InvalidUidException:
                            res = flask.make_response(flask.redirect('/cabinet'))
                            return res
                    else:
                        raise e

                except InvalidLoginException:
                    return WebPage(
                        MCard(
                            "Ошибка аутентификации",
                            "Вы указали невеврный логин",
                            MLink('/cabinet', text='Назад')
                        )
                    ).show()
                except InvalidPasswordException:
                    return WebPage(
                        MCard(
                            "Ошибка аутентифкации",
                            "Вы указали неверный пароль",
                            MLink('/cabinet', text='Назад')
                        )
                    ).show()
        elif request.method == 'GET':
            return func(*args, **kwargs)
    return wrapper


def admin_cabinet(auth):
    return WebPage(
        MRow(
            MCard(
                'Добро пожаловать',
                'Система предназанчена для мониторинга посещаемости. Ниже вы можете увидеть базовые представления.',
                grid=Grid(m(6), s(12))),
            MCard('В разработке',
                 'На данный момент система находится в разратоке - возможны перебои стабильности.',
                  grid=Grid(m(6), s(12)))),
        CollapsibleBlock(
            Collapsible(
                title='Посещения по неделям на всех ваших занятиях',
                body=DataFrameColumnChart(
                    Weeks.by_professor(auth.user),
                    x=Column.date,
                    y=Column.visit_rate,
                    title='Посещения в неделю, %',
                    xAxes_labelString='Неделя', yAxes_labelString='Посещения, %')
            ),
            Collapsible(
                title='Подробная информация по студентам',
                body=DataFrameSmartTable2(
                    StudentAggregator.by_professor(auth.user),
                    params={
                        'header': {
                            'filter': {
                                '1': {
                                    'type': 'select'
                                }
                            }
                        }
                    }
                ),
                icon='format_list_numbered'
            ),
            Collapsible(
                title='Подробная информация по дисциплинам',
                body=TabContainer(
                    Tab(
                        title='Общее',
                        body=DataFrameSmartTable2(
                            DisciplineAggregator.by_professor(auth.user),
                            params={
                                'header': {
                                    'filter': {
                                        '0': {
                                            'type': 'select'
                                        }
                                    }
                                }
                            }
                        )
                    ),
                    *(Tab(
                        title=disc.name,
                        body=DataFrameSmartTable2(
                            StudentAggregator.by_discipline(disc),
                            params={
                                'header': {
                                    'filter': {
                                        '1': {
                                            'type': 'select'
                                        }
                                    }
                                },
                                'table': {
                                    'style': 'highlight'
                                }
                            }
                        )
                    ) for disc in Discipline.of(auth.user))
                )
            )
        ),
        header=MHeader(
            ' СПбГУТ',
            MLink('#', format_name(auth.user, small=True)),
            MLink('#', f'Текущая неделя: {study_week()}'),
            MLink('/', 'Выход')),
        footer=MFooter(
            MRow(
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
    ).show()


def auth_form():
    return WebPage(
        MCard(
            title="Вход в информационную панель",
            body=MForm(
                elements=(
                    MRow(
                        MTextInput(
                            label="Логин",
                            placeholder="Логин",
                            name="login",
                        ),
                    ),
                    MRow(
                        MTextInput(
                            label="Пароль",
                            type="password",
                            name="password"
                        )
                    )),
                submit=MSubmitButton(
                    text="Вход"
                ),
                action="/cabinet",
                method="POST"
            ),
            grid=Grid(s(12), m(4))
        )
    ).show()


def init(app):
    @app.route('/cabinet', methods=['GET', 'POST'])
    @login
    def cabinet(auth=None, response=None):
        if request.method == 'GET':
            return auth_form()
        elif request.method == 'POST':
            response.set_data(admin_cabinet(auth))
            return response


    # @app.route('/panel', methods=['GET'])
    # @login
    # def panel(auth):


