from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='a',
            author=cls.author
        )

    def test_pages_availability(self):
        """Главная страница доступна анонимному пользователю
        Страницы регистрации пользователей, входа в учётную запись
        и выхода из неё доступны всем пользователям"""
        urls = [
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        ]
        for name in urls:
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_detail_delete(self):
        """Страницы отдельной заметки, удаления и редактирования
        заметки доступны только автору заметки"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа"""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug)),
            ('notes:edit', (self.note.slug)),
            ('notes:delete', (self.note.slug)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_list_add_done(self):
        """Аутентифицированному пользователю доступна
        страница со списком заметок,
        страница успешного добавления заметки,
        страница добавления новой заметки"""
        urls = [
            'notes:list',
            'notes:add',
            'notes:success',
        ]
        for name in urls:
            self.client.force_login(self.author)
            with self.subTest(user=self.author, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
