"""Unit tests for the Leanpub API client."""

import requests
import requests_mock as rm

from leanpub_multi_action.leanpub import Leanpub

API_KEY = "test-api-key"
SLUG = "mybook"


def _client():
    return Leanpub(leanpub_api_key=API_KEY)


class TestPreview:
    def test_success(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/preview.json", status_code=200)
            resp, err = client.preview(SLUG)
        assert err is None
        assert resp.status_code == 200

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/preview.json", status_code=500)
            resp, err = client.preview(SLUG)
        assert resp is None
        assert isinstance(err, requests.RequestException)


class TestPublish:
    def test_success(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/publish.json", status_code=200)
            resp, err = client.publish(SLUG)
        assert err is None
        assert resp.status_code == 200

    def test_with_options(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/publish.json", status_code=200)
            resp, err = client.publish(SLUG, email_readers=True, release_notes="v2.0")
        assert err is None
        body = resp.request.body
        assert "publish%5Bemail_readers%5D=True" in body
        assert "publish%5Brelease_notes%5D=v2.0" in body

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/publish.json", status_code=403)
            resp, err = client.publish(SLUG)
        assert resp is None
        assert isinstance(err, requests.RequestException)


class TestCheckStatus:
    def test_success(self):
        client = _client()
        with rm.Mocker() as m:
            m.get(f"https://leanpub.com/{SLUG}/book_status.json", json={"status": "working"}, status_code=200)
            resp, err = client.check_status(SLUG)
        assert err is None
        assert resp.json() == {"status": "working"}

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.get(f"https://leanpub.com/{SLUG}/book_status.json", status_code=404)
            resp, err = client.check_status(SLUG)
        assert resp is None
        assert isinstance(err, requests.RequestException)
