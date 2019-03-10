from bs4 import BeautifulSoup
from Parser import server_args
from Domain.functools.Format import inflect


class HTMLMaker:
    def __init__(self):
        with open('Server/templates/default_email.html', 'r') as file:
            self.html = BeautifulSoup(file.read(), 'html.parser')

        self.content = self.html.find('div', id='content')
        self.footer = self.html.find('div', id='footer')
        self.header = self.html.find('div', id='header')

        self.add_to_footer('Данное письмо рассылается автоматически. Отвечать на него не надо.')
        self.add_to_footer(f'Вопросы и предложения по работе {inflect(server_args.system_name, {"gent"})} '
                           f'отправлять на адрес {server_args.help_email}')

    def add_content(self, text):
        p = self.html.new_tag('p')
        self.content.append(p)

        p.string = text

    def add_to_footer(self, text):
        p = self.html.new_tag('p')
        self.footer.append(p)
        p.string = text

    def add_to_header(self, text):
        p = self.html.new_tag('p')
        self.header.append(p)
        p.string = text

    def __str__(self):
        return str(self.html)
