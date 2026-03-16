"""Unit tests for the CLI."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from leanpub_multi_action.cli import main

API_KEY = "test-api-key"
SLUG = "mybook"


def _invoke(*args):
    return CliRunner().invoke(main, list(args))


class TestValidation:
    def test_no_api_key(self):
        result = _invoke("--book_slug", SLUG, "--preview")
        assert result.exit_code == 0  # click exit code
        assert "No Leanpub API Key Found!" in result.output

    def test_no_book_slug(self):
        result = _invoke("--leanpub_api_key", API_KEY, "--preview")
        assert "No Leanpub Book Slug Found!" in result.output

    def test_no_action(self):
        result = _invoke("--leanpub_api_key", API_KEY, "--book_slug", SLUG)
        assert "Must either Publish, Preview, or Check Status!" in result.output


class TestPreviewCLI:
    @patch("leanpub_multi_action.cli.Leanpub")
    def test_success(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.preview.return_value = (mock_resp, None)
        result = _invoke("--leanpub_api_key", API_KEY, "--book_slug", SLUG, "--preview")
        assert "Preview job started" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_error(self, mock_cls):
        mock_cls.return_value.preview.return_value = (None, Exception("fail"))
        result = _invoke("--leanpub_api_key", API_KEY, "--book_slug", SLUG, "--preview")
        assert "fail" in result.output


class TestPublishCLI:
    @patch("leanpub_multi_action.cli.Leanpub")
    def test_success(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.publish.return_value = (mock_resp, None)
        result = _invoke("--leanpub_api_key", API_KEY, "--book_slug", SLUG, "--publish")
        assert "Publish job started" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_error(self, mock_cls):
        mock_cls.return_value.publish.return_value = (None, Exception("denied"))
        result = _invoke("--leanpub_api_key", API_KEY, "--book_slug", SLUG, "--publish")
        assert "denied" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_with_options(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.publish.return_value = (mock_resp, None)
        result = _invoke(
            "--leanpub_api_key", API_KEY, "--book_slug", SLUG,
            "--publish", "--email_readers", "--release_notes", "v2",
        )
        mock_cls.return_value.publish.assert_called_once_with(
            book_slug=SLUG, email_readers=True, release_notes="v2"
        )
        assert "Publish job started" in result.output


class TestCheckStatusCLI:
    @patch("leanpub_multi_action.cli.Leanpub")
    def test_success(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"status": "complete"}
        mock_cls.return_value.check_status.return_value = (mock_resp, None)
        result = _invoke("--leanpub_api_key", API_KEY, "--book_slug", SLUG, "--check_status")
        assert "complete" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_error(self, mock_cls):
        mock_cls.return_value.check_status.return_value = (None, Exception("timeout"))
        result = _invoke("--leanpub_api_key", API_KEY, "--book_slug", SLUG, "--check_status")
        assert "timeout" in result.output
