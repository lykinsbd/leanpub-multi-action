"""Leanpub Actions for GitHub Actions Workflows."""

import datetime
import sys

import click
import requests

from leanpub_multi_action.leanpub import Leanpub


def _handle_response(
    resp: requests.Response | None,
    err: requests.RequestException | None,
    success_msg: str,
) -> int:
    """Handle a Leanpub API response and return an exit code.

    Args:
        resp: The API response, if successful.
        err: The exception, if the request failed.
        success_msg: Message to print on success.

    Returns:
        Exit code: 0 for success, 1 for failure.

    """
    if err is not None:
        print(err)
        return 1
    if resp is not None and resp.status_code == 200:
        print(success_msg)
        return 0
    print("Unknown error has occurred!")
    return 1


@click.command()
@click.option(
    "--leanpub_api_key",
    envvar="INPUT_LEANPUB-API-KEY",
    help="Leanpub API Key. Will also look for 'INPUT_LEANPUB-API-KEY' environment variable.",
)
@click.option(
    "--book_slug",
    envvar="INPUT_LEANPUB-BOOK-SLUG",
    help=(
        "Book Slug is the unique book name on Leanpub.com (i.e. the 'mybook' portion of https://leanpub.com/mybook)."
        "Will also look for 'INPUT_LEANPUB-BOOK-SLUG' environment variable."
    ),
)
@click.option("--preview", envvar="INPUT_PREVIEW", is_flag=True, help="Preview a book on Leanpub.")
@click.option("--publish", envvar="INPUT_PUBLISH", is_flag=True, help="Publish a book on Leanpub.")
@click.option(
    "--email_readers",
    envvar="INPUT_EMAIL-READERS",
    is_flag=True,
    help="Email readers about the new publish.",
)
@click.option(
    "--release_notes",
    envvar="INPUT_RELEASE-NOTES",
    default=None,
    help="Release notes for the publish.",
)
@click.option(
    "--check_status",
    envvar="INPUT_CHECK-STATUS",
    is_flag=True,
    help="Check the job status of a Preview or Publish on Leanpub.",
)
def main(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    leanpub_api_key: str | None = None,
    book_slug: str | None = None,
    preview: bool = False,
    publish: bool = False,
    email_readers: bool = False,
    release_notes: str | None = None,
    check_status: bool = False,
) -> None:
    """Entrypoint into our script.

    Publish, Preview, or Check Status on an existing Publish/Preview job.

    See #61 for planned refactor to Click subcommands.

    Args:
        leanpub_api_key (str): API Key for the Leanpub API.
            If not set, will error out.
        book_slug (str): Unique book name from the leanpub URL of the book.
            i.e. the 'mybook' portion of https://leanpub.com/mybook
            If not set, will error out.
        preview (bool): Preview a book on Leanpub.
        publish (bool): Publish a book on Leanpub.
        email_readers (bool): Email readers about the new publish.
        release_notes (str): Release notes for the publish.
        check_status (bool): Check the job status of a Preview or Publish on Leanpub.

    Returns:
        int: exit_code as an integer to return to OS

    """
    if not leanpub_api_key:
        print("No Leanpub API Key Found!")
        sys.exit(1)

    if not book_slug:
        print("No Leanpub Book Slug Found!")
        sys.exit(1)

    print("Leanpub API Key and Book Slug found")

    if not publish and not preview and not check_status:
        print("Must either Publish, Preview, or Check Status!")
        sys.exit(1)

    leanpub = Leanpub(leanpub_api_key=leanpub_api_key)
    exit_code = 0

    if preview:
        print(f"Generating a Preview of '{book_slug}'")
        resp, err = leanpub.preview(book_slug=book_slug)
        exit_code = _handle_response(resp, err, f"Preview job started at {datetime.datetime.utcnow()}")

    if publish:
        print(f"Publishing '{book_slug}'")
        resp, err = leanpub.publish(book_slug=book_slug, email_readers=email_readers, release_notes=release_notes)
        exit_code = _handle_response(resp, err, f"Publish job started at {datetime.datetime.utcnow()}")

    if check_status:
        print(f"Checking status of '{book_slug}'")
        resp, err = leanpub.check_status(book_slug=book_slug)
        if err is not None:
            print(err)
            exit_code = 1
        elif resp is not None and resp.status_code == 200:
            print(f"Status: {resp.json()}")
        else:
            print("Unknown error has occurred!")
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
