"""Leanpub Actions for GitHub Actions Workflows."""

import datetime
import sys

import click

from leanpub_multi_action.leanpub import Leanpub


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
@click.option("--email_readers", envvar="INPUT_EMAIL-READERS", is_flag=True, help="Email readers about the new publish.")
@click.option("--release_notes", envvar="INPUT_RELEASE-NOTES", default=None, help="Release notes for the publish.")
@click.option("--check_status", is_flag=True, help="Check the job status of a Preview or Publish on Leanpub.")
def main(
    leanpub_api_key: str = None,
    book_slug: str = None,
    preview: bool = False,
    publish: bool = False,
    email_readers: bool = False,
    release_notes: str = None,
    check_status: bool = False,
) -> int:
    """Entrypoint into our script.

    Publish, Preview, or Check Status on an existing Publish/Preview job.

    Args:
        leanpub_api_key (bool): API Key for the Leanpub API.
            If not set, will error out.
        book_slug (bool): Unique book name from the leanpub URL of the book.
            i.e. the 'mybook' portion of https://leanpub.com/mybook
            If not set, will error out.
        check_status(bool): Check the job status of a Preview or Publish on Leanpub.

    Returns:
        int: exit_code as an integer to return to OS
    """
    exit_code = 0

    # Attempt to find API Key
    if not leanpub_api_key:
        exit_code = 1
        print("No Leanpub API Key Found!")
        return exit_code

    # Attempt to find Book Slug
    if not book_slug:
        exit_code = 1
        print("No Leanpub Book Slug Found!")
        return exit_code

    print("Leanpub API Key and Book Slug found")

    # We need to be doing one of the three possible actions
    if not publish and not preview and not check_status:
        exit_code = 1
        print("Must either Publish, Preview, or Check Status!")
        return exit_code

    err = None

    # Instantiate the Leanpub client
    leanpub = Leanpub(leanpub_api_key=leanpub_api_key)

    # Check if we are previewing
    if preview:
        print(f"Generating a Preview of '{book_slug}'")
        resp, err = leanpub.preview(book_slug=book_slug)
        if err is not None:
            print(err)
            exit_code = 1
        elif resp.status_code == 200:
            print(f"Preview job started at {datetime.datetime.utcnow()}")
        else:
            print("Unknown error has occurred!")
            exit_code = 1

    # Check if we are publishing
    if publish:
        print(f"Publishing '{book_slug}'")
        resp, err = leanpub.publish(book_slug=book_slug, email_readers=email_readers, release_notes=release_notes)
        if err is not None:
            print(err)
            exit_code = 1
        elif resp.status_code == 200:
            print(f"Publish job started at {datetime.datetime.utcnow()}")
        else:
            print("Unknown error has occurred!")
            exit_code = 1

    # Check if we are checking :lulz:
    if check_status:
        print(f"Checking status of '{book_slug}'")
        resp, err = leanpub.check_status(book_slug=book_slug)
        if err is not None:
            print(err)
            exit_code = 1
        elif resp.status_code == 200:
            status = resp.json()
            print(f"Status: {status}")
        else:
            print("Unknown error has occurred!")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
