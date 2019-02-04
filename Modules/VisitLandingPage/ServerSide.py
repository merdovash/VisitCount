from flask import request

from Domain.WebUi import *


def init(app):
    @app.route('/visit', methods=['GET'])
    def visit_landing_page():
        return WebPage(
            Section(
                title='',
                body=MRow(
                    Col(
                        MImage(address='file/landing_chart_r.png'),
                        grid=Grid(s(12), m(6))
                    ),
                    MCard(
                        'Автоматизируйте учет посещений',
                        MList(
                            'Откажитесь от записей на бумажку',
                            'Студенты отмечаются самостоятельно',
                            'Формирование отчетов',
                            'Рассылка оповещений'
                        ),
                        grid=Grid(s(12), m(6))
                    )
                )
            ),
            Section(
                'Больше никаких бумажных носителей',
                body=MRow(
                    MCard(
                        'Система полностью автоматизирована',
                        'Используйте специальное ПО для ведения учета. Не важно сколько у вас компьютеров, '
                        'централизованная система позаботится о том, чтобы на всех устройствах была актуальная '
                        'информация.',
                        grid=Grid(s(12), m(6))
                    ),
                    Col(
                        MImage(address='file/landing_soft_r.png'),
                        grid=Grid(s(12), m(6))
                    )
                )
            ),
            Section(
                'Больше никаких лишних действий',
                body=MRow(
                    Col(
                        MImage(address='file/landing_rfid.png'),
                        grid=Grid(s(12), m(6))
                    ),
                    MCard('Студенты отмечаются сами',
                         'Благодаря технологии RFID процес ведения учета сокращается до нажатия одной кнопки. '
                         'Студенты отмечаются в системе через специальное устройство и личную smart-карту.',
                          grid=Grid(s(12), m(6)))
                )
            ),
            Section(
                'Формирование отчётов',
                body=MRow(
                    MCard(
                        'Автоматическая генерация отчетов',
                        'Система позволяет не только визуализировать данные, но и рассылать готовые отчеты по '
                        'электронной почте. Такая функция подойдет для отчетности перед кафедрами, деканатами и '
                        'специализированными отделами.',
                        grid=Grid(s(12), m(6))),
                    Col(
                        MImage(address='file/landing_report.png'),
                        grid=Grid(s(12), m(6))
                    )

                )
            ),
            Section(
                'Рассылка оповещений',
                body=MRow(
                    Col(
                        MImage(address='file/landing_notification.png'),
                        grid=Grid(s(12), m(6))
                    ),
                    MCard('Автоматическое оповещение о пробелмах с посещаемостью',
                         'Как один из встреных инструментов повышения посещаемости система автоматически оповещает '
                         'студента и/или родителей о проблемах с посещаемостью.',
                          grid=Grid(s(12), m(6)))

                )
            ),
            MRow(
                MCard(
                    title='Контакты',
                    body=P('email: vladschekochikhin@gmail.com'),
                    grid=Grid(s(12), m(6)),
                    page_link='contact'
                )
            ),
            header=MHeader(
                'Система ведения учета',
                MLink(address='#contact', text='Контакты'),
                MLink(address='/cabinet', text='Личный кабинет'),
                MLink(address='/', text='Другие проекты')
            ),
            footer=MFooter(copyright='СПбГУТб 2018')
        ).show()
