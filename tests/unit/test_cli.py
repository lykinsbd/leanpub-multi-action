"""Unit tests for the CLI."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from leanpub_multi_action.cli import main

API_KEY = "test-api-key"
SLUG = "mybook"


def _invoke(*args):
    return CliRunner().invoke(main, list(args))


def _base(*args):
    """Prepend common options and return full arg list."""
    return ("--leanpub-api-key", API_KEY, "--book-slug", SLUG, *args)


class TestValidation:
    """Test input validation guards."""

    def test_no_api_key(self):
        result = _invoke("--book-slug", SLUG, "preview")
        assert result.exit_code == 2
        assert "Missing option '--leanpub-api-key'" in result.output

    def test_no_book_slug(self):
        result = _invoke("--leanpub-api-key", API_KEY, "preview")
        assert result.exit_code == 2
        assert "Missing option '--book-slug'" in result.output

    def test_no_subcommand(self):
        result = _invoke("--leanpub-api-key", API_KEY, "--book-slug", SLUG)
        assert result.exit_code == 2
        assert "Missing command" in result.output


class TestPreviewCLI:
    """Test the preview action path."""

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_success(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.preview.return_value = (mock_resp, None)
        result = _invoke(*_base("preview"))
        mock_cls.return_value.preview.assert_called_once_with(book_slug=SLUG, subset=False)
        assert result.exit_code == 0
        assert "Preview job started" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_subset(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.preview.return_value = (mock_resp, None)
        result = _invoke(*_base("preview", "--subset"))
        mock_cls.return_value.preview.assert_called_once_with(book_slug=SLUG, subset=True)
        assert result.exit_code == 0
        assert "Subset Preview job started" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_single_file(self, mock_cls, tmp_path):
        md_file = tmp_path / "chapter.md"
        md_file.write_text("# Test\n\nContent.")
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.preview_single.return_value = (mock_resp, None)
        result = _invoke(*_base("preview", "--single-file", str(md_file)))
        mock_cls.return_value.preview_single.assert_called_once_with(
            book_slug=SLUG,
            content="# Test\n\nContent.",
        )
        assert result.exit_code == 0
        assert "Single file preview job started" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_error(self, mock_cls):
        mock_cls.return_value.preview.return_value = (None, Exception("fail"))
        result = _invoke(*_base("preview"))
        assert result.exit_code == 1
        assert "fail" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_unknown_error(self, mock_cls):
        mock_resp = MagicMock(status_code=500)
        mock_cls.return_value.preview.return_value = (mock_resp, None)
        result = _invoke(*_base("preview"))
        assert result.exit_code == 1
        assert "Unknown error has occurred!" in result.output


class TestPublishCLI:
    """Test the publish action path."""

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_success(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.publish.return_value = (mock_resp, None)
        result = _invoke(*_base("publish"))
        assert result.exit_code == 0
        assert "Publish job started" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_error(self, mock_cls):
        mock_cls.return_value.publish.return_value = (None, Exception("denied"))
        result = _invoke(*_base("publish"))
        assert result.exit_code == 1
        assert "denied" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_unknown_error(self, mock_cls):
        mock_resp = MagicMock(status_code=403)
        mock_cls.return_value.publish.return_value = (mock_resp, None)
        result = _invoke(*_base("publish"))
        assert result.exit_code == 1
        assert "Unknown error has occurred!" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_with_options(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_cls.return_value.publish.return_value = (mock_resp, None)
        result = _invoke(*_base("publish", "--email-readers", "--release-notes", "v2"))
        mock_cls.return_value.publish.assert_called_once_with(
            book_slug=SLUG,
            email_readers=True,
            release_notes="v2",
        )
        assert result.exit_code == 0
        assert "Publish job started" in result.output


class TestCheckStatusCLI:
    """Test the check_status action path."""

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_success(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"status": "working", "job_type": "GenerateBookJob#preview"}
        mock_cls.return_value.check_status.return_value = (mock_resp, None)
        result = _invoke(*_base("check-status"))
        assert result.exit_code == 0
        assert "working" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_no_job_running(self, mock_cls):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {}
        mock_cls.return_value.check_status.return_value = (mock_resp, None)
        result = _invoke(*_base("check-status"))
        assert result.exit_code == 0

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_error(self, mock_cls):
        mock_cls.return_value.check_status.return_value = (None, Exception("timeout"))
        result = _invoke(*_base("check-status"))
        assert result.exit_code == 1
        assert "timeout" in result.output

    @patch("leanpub_multi_action.cli.Leanpub")
    def test_unknown_error(self, mock_cls):
        mock_resp = MagicMock(status_code=500)
        mock_cls.return_value.check_status.return_value = (mock_resp, None)
        result = _invoke(*_base("check-status"))
        assert result.exit_code == 1
        assert "Unknown error has occurred!" in result.output
