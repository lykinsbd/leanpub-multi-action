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


@click.group()
@click.option(
    "--leanpub-api-key",
    envvar="INPUT_LEANPUB-API-KEY",
    required=True,
    help="Leanpub API Key.",
)
@click.option(
    "--book-slug",
    envvar="INPUT_LEANPUB-BOOK-SLUG",
    required=True,
    help="Leanpub book slug (the URL path component).",
)
@click.pass_context
def main(ctx: click.Context, leanpub_api_key: str, book_slug: str) -> None:
    """Interact with Leanpub: preview, publish, or check job status."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = Leanpub(leanpub_api_key=leanpub_api_key)
    ctx.obj["book_slug"] = book_slug


@main.command()
@click.pass_context
def preview(ctx: click.Context) -> None:
    """Generate a preview of the book."""
    book_slug = ctx.obj["book_slug"]
    print(f"Generating a Preview of '{book_slug}'")
    resp, err = ctx.obj["client"].preview(book_slug=book_slug)
    sys.exit(_handle_response(resp, err, f"Preview job started at {datetime.datetime.now(datetime.UTC)}"))


@main.command()
@click.option("--email-readers", envvar="INPUT_EMAIL-READERS", is_flag=True, help="Email readers about the publish.")
@click.option("--release-notes", envvar="INPUT_RELEASE-NOTES", default=None, help="Release notes for the publish.")
@click.pass_context
def publish(ctx: click.Context, email_readers: bool, release_notes: str | None) -> None:
    """Publish the book."""
    book_slug = ctx.obj["book_slug"]
    print(f"Publishing '{book_slug}'")
    resp, err = ctx.obj["client"].publish(
        book_slug=book_slug,
        email_readers=email_readers,
        release_notes=release_notes,
    )
    sys.exit(_handle_response(resp, err, f"Publish job started at {datetime.datetime.now(datetime.UTC)}"))


@main.command(name="check-status")
@click.pass_context
def check_status(ctx: click.Context) -> None:
    """Check the job status of a preview or publish."""
    book_slug = ctx.obj["book_slug"]
    print(f"Checking status of '{book_slug}'")
    resp, err = ctx.obj["client"].check_status(book_slug=book_slug)
    if err is not None:
        print(err)
        sys.exit(1)
    if resp is not None and resp.status_code == 200:
        print(f"Status: {resp.json()}")
        sys.exit(0)
    print("Unknown error has occurred!")
    sys.exit(1)
