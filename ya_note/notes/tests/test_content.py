from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем и регистрируем первого юзера и его заметку
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note_a = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        # Создаем и регистрируем второго юзера и его заметку
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note_b = Note.objects.create(
            title='Заголовок2',
            text='Текст2',
            author=cls.reader
        )
        cls.NOTES_IN_DATABASE = 1

    def test_context(self):
        """отдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context,
        в список заметок одного пользователя
        не попадают заметки другого пользователя"""
        url = reverse('notes:list')
        response = self.author_client.get(url)
        self.assertEqual(len(response.context['object_list']),
                         self.NOTES_IN_DATABASE)
        response = self.reader_client.get(url)
        self.assertEqual(len(response.context['object_list']),
                         self.NOTES_IN_DATABASE)

    def test_add_and_edit_has_form(self):
        # на страницы создания и редактирования заметки передаются формы
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_a.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
