from unittest import TestCase

from Domain.Loader.GroupLoader.GroupLoader import GroupWordReader


class TestGroupLoader(TestCase):
    def test_group_file_test1_docx(self):
        gr = GroupWordReader('../Domain/Loader/GroupLoader/test1.docx')
        self.assertEqual('ИСТ-511', gr.get_group_name())
        self.assertEqual([
            gr.student('фывыфвы', 'фвыф', 'в'),
            gr.student('фыв', 'фыв', 'фывф'),
            gr.student('фывфывфыв', 'аываыва')
        ],
            gr.get_students_list())

    def test_group_name_file_text2_docx(self):
        gr = GroupWordReader('../Domain/Loader/GroupLoader/test2.docx')
        self.assertEqual('ИСТ-511', gr.get_group_name())
        self.assertEqual([
            gr.student('фывыфвы', 'фвыф', 'в'),
            gr.student('фыв', 'фыв', 'фывф'),
            gr.student('фывфывфыв', 'аываыва')
        ],
            gr.get_students_list())

    def test_group_name_file_text3_docx(self):
        gr = GroupWordReader('../Domain/Loader/GroupLoader/test3.docx')
        self.assertEqual('ИСТ-511', gr.get_group_name())
        self.assertEqual([
            gr.student('Авыаыв', 'авыа', 'ыва'),
            gr.student('Авыа', 'ввыа', 'ыва'),
            gr.student('Вы', 'аывааыва', 'ыва'),
            gr.student('Ываываваы', 'ыва', 'ы')
        ],
            gr.get_students_list())
