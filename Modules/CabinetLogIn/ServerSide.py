import _md5
import random

from flask import render_template
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFError
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from DataBase2 import Auth, Session, Discipline
from Domain.Aggregation import Weeks, Column, StudentAggregator, DisciplineAggregator
from Domain.Date import study_week
from Domain.WebUi import WebPage, Header, Card, Grid, s, m, MLink, DataFrameColumnChart, \
    Section, Row, Footer, MList, Col, offset, MText, DataFrameSmartTable2, CardReveal, CollapsibleBlock, Collapsible, \
    TabContainer, Tab
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


class ValidateLogin():
    def __call__(self, form, field):
        session = Session()
        return len(session.query(Auth.login).filter(Auth.login == field.data).all())


class ValidatePassword():
    def __call__(self, form, field):
        return len(
            Session().query(Auth).filter(Auth.login == form.login.data).filter(Auth.password == field.data).all())


class CabinetForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), ValidateLogin()])
    password = PasswordField('Пароль', validators=[DataRequired(), ValidatePassword()])

    submit_button = SubmitField('Вход')


def is_mobile(user_agent: str):
    return any([target in user_agent.lower() for target in ('iphone', 'android', 'blackberry''')])


def admin_cabinet(form: CabinetForm):
    session = Session()

    auth = session.query(Auth).filter(Auth.login == form.login.data).filter(Auth.password == form.password.data).first()

    return WebPage(
        Row(
            Card(
                'Добро пожаловать',
                'Система предназанчена для мониторинга посещаемости. Ниже вы можете увидеть базовые представления.',
                grid=Grid(m(6), s(12))),
            Card('В разработке',
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
        header=Header(
            ' СПбГУТ',
            MLink('#', format_name(auth.user, small=True)),
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
    ).show()


def init(app):
    @app.route('/cabinet', methods=['GET', 'POST'])
    def cabinet():
        try:
            form = CabinetForm()

            if form.validate_on_submit():
                return admin_cabinet(form)

            return render_template('login2.htm', form=form)
        except Exception as e:
            print(e)
            raise
            form = CabinetForm()
            render_template('login2.htm', form=form)
