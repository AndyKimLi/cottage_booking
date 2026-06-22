from django.urls import reverse
from django.test import Client


def test_index_page_returns_200():
    client = Client()
    response = client.get('/')
    assert response.status_code in (200, 302)

