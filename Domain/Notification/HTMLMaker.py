from bs4 import BeautifulSoup
from Domain.MessageFormat import inflect
from Parser import Args


class HTMLMaker:
    def __init__(self, data):
        with open('Server/templates/default_email.html', 'r') as file:
            self.html = BeautifulSoup(file.read(), 'html.parser')

        self.content = self.html.find('div', id='content')
        self.footer = self.html.find('div', id='footer')
        self.header = self.html.find('div', id='header')
        self.signature = self.html.find('div', id='signature')

        self.add_to_header(data['greeting'])

        self.add_to_footer('Данное письмо рассылается автоматически. Отвечать на него не надо.')
        self.add_to_footer(f'Вопросы и предложения по работе {inflect(Args().system_name, {"gent"})} '
                           f'отправлять на адрес {Args().help_email}')
        self.add_to_signature(data['sign'])

    def add_content(self, text):
        p = self.html.new_tag('p')
        self.content.append(p)

        p.string = text

    def add_to_footer(self, text):
        p = self.html.new_tag('p')
        self.footer.append(p)
        p.string = text

    def add_to_signature(self, text):
        p = self.html.new_tag('p')
        self.signature.append(p)
        p.string = text

    def add_to_header(self, text):
        p = self.html.new_tag('p')
        self.header.append(p)
        p.string = text

    def __str__(self):
        return str(self.html)
