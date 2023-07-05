from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Anonymus',
            'text': 'Anonymus text',
        }
        cls.AUTO_SLUG = 'anonymus'
        cls.NOTES_IN_DB = 0
        cls.CREATED_NOTES_IN_DB = 1

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTES_IN_DB)

    def test_auth_user_can_create_note(self):
        redirect_url = reverse('notes:success')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.CREATED_NOTES_IN_DB)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.AUTO_SLUG)
        # Заодно проверяем работу функции автозаполнения слага
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя - автора заметки.
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note_a = Note.objects.create(
            title='Заголовок',
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.NOTES_IN_DB = 1
        cls.NOTES_IN_DB_AFTER_DEL = 0
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # URL
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note_a.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note_a.slug,))
        cls.redirect_url = reverse('notes:success')
        # Формируем данные для POST-запроса по обновлению заметки.
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NEW_NOTE_TEXT
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTES_IN_DB_AFTER_DEL)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTES_IN_DB)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note_a.refresh_from_db()
        self.assertEqual(self.note_a.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_a.refresh_from_db()
        self.assertEqual(self.note_a.text, self.NOTE_TEXT)

    def test_unique_slug(self):
        # Создаем заметку с тем же слагом, что и в фикстурах
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTES_IN_DB)
