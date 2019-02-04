from flask import request

from Domain.WebUi import *


def _page() -> WebPage:
    return WebPage(
        MRow(
            MCard(
                'Добро пожаловать',
                'На данном сайте представлены проектные работы, разрабатываемые студентами университета. Здесь вы '
                'сможете узнать краткую информацию о каждом из проектов, а так же перейти на их веб-сайты. ',
                grid=Grid(s(12), m(6)),
                bg_color='white',
                text_color='black'
            )
        ),
        Section(
            title='Список проектов',
            body=CollapsibleBlock(
                Collapsible(
                    title='Автоматизированная система сбора, хранения и рассылки информации о посещениях занятий '
                          'обучающимися',
                    body=MRow(
                        P('Система предназанчена для контроля посещений занятий студентами. Основой проекта '
                          'является автоматизированная рассылка оповещений о пропусках занятий студентами. '
                          'Автоматизация сбора достигается путем использования смарт-карт и специального ПО с '
                          'RFID-считывателем.'),
                        P('Автор: Щекочихин В.П.'),
                        P('Научный руководитель: Евстигнеев В.А.'),
                        MRow(MButton(href='/visit', text='Перейти к проекту'))
                    ),

                ),
                Collapsible(
                    title="Программа проверки наличия ссылок на источники в теле работы",
                    body=MRow(
                        P('Программа позволяет проанализировать работу (курсовую работу, курсовой проект, '
                          'дипломную работу, реферат и т.д.) на предмет наличия ссылок в теле работы на указанные в '
                          'спсике литератур'
                          'источники '),
                        P('Автор: Кухарь А. Щекочихин В.'),
                        P('Руководитель: Филиппов Ф.В.'),
                        MRow(MButton(href='/source_checker', text='Перейти к проекту'))
                    )
                )
            )
        ),
        header=MHeader(
            logo='Проекты студентов СПбГУТ'
        ),
        footer=MFooter(
            copyright='СПбГУТ, 2019'
        )
    )


def init(app):
    @app.route("/", methods=['GET'])
    def index():
        """

        :return: index.html
        """
        if request.method == "GET":
            return _page().show()
