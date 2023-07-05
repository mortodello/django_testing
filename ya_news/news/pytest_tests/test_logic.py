from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, id_for_news):
    url = reverse('news:detail', args=id_for_news)
    form_data = {'text': 'Текст комментария'}
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, id_for_news, news, author):
    url = reverse('news:detail', args=id_for_news)
    form_data = {'text': 'Текст комментария'}
    response = author_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    assertRedirects(response, f'{url}#comments')
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == 'Текст комментария'
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, id_for_news):
    url = reverse('news:detail', args=id_for_news)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(id_for_comment,
                                   id_for_news, author_client):
    delete_url = reverse('news:delete', args=id_for_comment)
    news_url = reverse('news:detail', args=id_for_news)
    url_to_comments = news_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client,
                                                  id_for_comment):
    delete_url = reverse('news:delete', args=id_for_comment)
    response = admin_client.delete(delete_url)
    assert response.status_code, HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client,
                                 id_for_comment, id_for_news, comment):
    form_data = {'text': 'Обновленный комментарий'}
    edit_url = reverse('news:edit', args=id_for_comment)
    news_url = reverse('news:detail', args=id_for_news)
    url_to_comments = news_url + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'Обновленный комментарий'


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(admin_client,
                                                id_for_comment, comment):
    form_data = {'text': 'Обновленный комментарий'}
    edit_url = reverse('news:edit', args=id_for_comment)
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Comment Text'
