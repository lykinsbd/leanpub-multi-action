"""Unit tests for the Leanpub API client."""

import requests
import requests_mock as rm

from leanpub_multi_action.leanpub import Leanpub

API_KEY = "test-api-key"
SLUG = "mybook"


def _client():
    return Leanpub(leanpub_api_key=API_KEY)


class TestPreview:
    """Test the preview API call."""

    def test_success(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/preview.json", status_code=200)
            resp, err = client.preview(SLUG)
        assert err is None
        assert resp.status_code == 200
        assert resp.request.body == f'{{"api_key": "{API_KEY}"}}'.encode()

    def test_subset(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/preview/subset.json", status_code=200)
            resp, err = client.preview(SLUG, subset=True)
        assert err is None
        assert resp.status_code == 200
        assert "subset" in resp.request.url

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/preview.json", status_code=500)
            resp, err = client.preview(SLUG)
        assert resp is None
        assert isinstance(err, requests.RequestException)


class TestPreviewSingle:
    """Test the single file preview API call."""

    def test_success(self):
        client = _client()
        content = "# Chapter 1\n\nHello world."
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/preview/single.json", status_code=200)
            resp, err = client.preview_single(SLUG, content=content)
        assert err is None
        assert resp.status_code == 200
        assert resp.request.body == content.encode()
        assert f"api_key={API_KEY}" in resp.request.url

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/preview/single.json", status_code=500)
            resp, err = client.preview_single(SLUG, content="test")
        assert resp is None
        assert isinstance(err, requests.RequestException)


class TestPublish:
    """Test the publish API call."""

    def test_success(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/publish.json", status_code=200)
            resp, err = client.publish(SLUG)
        assert err is None
        assert resp.status_code == 200
        assert f"api_key={API_KEY}" in resp.request.body
        assert "publish%5Bemail_readers%5D=False" in resp.request.body

    def test_with_options(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/publish.json", status_code=200)
            resp, err = client.publish(SLUG, email_readers=True, release_notes="v2.0")
        assert err is None
        assert "publish%5Bemail_readers%5D=True" in resp.request.body
        assert "publish%5Brelease_notes%5D=v2.0" in resp.request.body

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.post(f"https://leanpub.com/{SLUG}/publish.json", status_code=403)
            resp, err = client.publish(SLUG)
        assert resp is None
        assert isinstance(err, requests.RequestException)


class TestBookSummary:
    """Test the book_summary API call."""

    def test_success(self):
        client = _client()
        with rm.Mocker() as m:
            m.get(
                f"https://leanpub.com/{SLUG}.json",
                json={"slug": SLUG, "title": "My Book", "total_copies_sold": 42},
                status_code=200,
            )
            resp, err = client.book_summary(SLUG)
        assert err is None
        assert resp.json()["slug"] == SLUG
        assert f"api_key={API_KEY}" in resp.request.url

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.get(f"https://leanpub.com/{SLUG}.json", status_code=404)
            resp, err = client.book_summary(SLUG)
        assert resp is None
        assert isinstance(err, requests.RequestException)


class TestCheckStatus:
    """Test the check_status API call."""

    def test_success(self):
        client = _client()
        with rm.Mocker() as m:
            m.get(
                f"https://leanpub.com/{SLUG}/job_status.json",
                json={"status": "working", "job_type": "GenerateBookJob#preview", "num": 5, "total": 28},
                status_code=200,
            )
            resp, err = client.check_status(SLUG)
        assert err is None
        assert resp.json()["status"] == "working"
        assert f"api_key={API_KEY}" in resp.request.url

    def test_no_job_running(self):
        client = _client()
        with rm.Mocker() as m:
            m.get(
                f"https://leanpub.com/{SLUG}/job_status.json",
                json={},
                status_code=200,
            )
            resp, err = client.check_status(SLUG)
        assert err is None
        assert resp.json() == {}

    def test_http_error(self):
        client = _client()
        with rm.Mocker() as m:
            m.get(f"https://leanpub.com/{SLUG}/job_status.json", status_code=404)
            resp, err = client.check_status(SLUG)
        assert resp is None
        assert isinstance(err, requests.RequestException)
