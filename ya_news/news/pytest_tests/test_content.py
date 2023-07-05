import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(home_page_with_news):
    object_list = home_page_with_news.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(home_page_with_news):
    object_list = home_page_with_news.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(comment_set):
    assert comment_set[0].created < comment_set[1].created


@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
@pytest.mark.django_db
def test_form_for_different_users(id_for_news,
                                  parametrized_client, form_in_list):
    response = parametrized_client.get(reverse('news:detail',
                                               args=id_for_news))
    assert ('form' in response.context) is form_in_list
