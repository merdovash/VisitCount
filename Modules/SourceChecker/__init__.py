from Domain.WebUi import WebPage, MHeader, MFooter, MRow, MCard, MLink, Grid, m, s


def init(app):
    @app.route('/source_checker')
    def checker():
        return WebPage(
            MRow(
                MCard(
                    "Проверка наличия ссылок в тексте",
                    "Программа проверяет наличие ссылок в теле работы на указнные источники в списке источников.",
                    MLink('file/Checker.exe', "Скачать"),
                    grid=Grid(s(12), m(6))
                )
            ),
            header=MHeader(
                'Анализ работ',
                MLink('/', "К списку проектов")
            ),
            footer=MFooter(
                copyright='СПбГУТ, 2019'
            ),
            in_container=True
        ).show()