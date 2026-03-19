"""Leanpub Actions for GitHub Actions Workflows."""

import datetime
import pathlib
import sys
import time

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
@click.option("--subset", envvar="INPUT_SUBSET", is_flag=True, help="Preview only the Subset.txt files.")
@click.option(
    "--single-file",
    envvar="INPUT_SINGLE-FILE",
    type=click.Path(exists=True),
    default=None,
    help="Path to a Markdown file to preview.",
)
@click.pass_context
def preview(ctx: click.Context, subset: bool, single_file: str | None) -> None:
    """Generate a preview of the book."""
    book_slug = ctx.obj["book_slug"]
    client = ctx.obj["client"]
    now = datetime.datetime.now(datetime.UTC)

    if single_file:
        content = pathlib.Path(single_file).read_text(encoding="utf-8")
        print(f"Generating a Single File Preview of '{book_slug}' from '{single_file}'")
        resp, err = client.preview_single(book_slug=book_slug, content=content)
        sys.exit(_handle_response(resp, err, f"Single file preview job started at {now}"))

    kind = "Subset Preview" if subset else "Preview"
    print(f"Generating a {kind} of '{book_slug}'")
    resp, err = client.preview(book_slug=book_slug, subset=subset)
    sys.exit(_handle_response(resp, err, f"{kind} job started at {now}"))


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


@main.command(name="book-summary")
@click.pass_context
def book_summary(ctx: click.Context) -> None:
    """Get the book summary and metadata."""
    book_slug = ctx.obj["book_slug"]
    print(f"Getting summary for '{book_slug}'")
    resp, err = ctx.obj["client"].book_summary(book_slug=book_slug)
    if err is not None:
        print(err)
        sys.exit(1)
    if resp is not None and resp.status_code == 200:
        print(resp.json())
        sys.exit(0)
    print("Unknown error has occurred!")
    sys.exit(1)


@main.command(name="book-exists")
@click.pass_context
def book_exists(ctx: click.Context) -> None:
    """Check if a book exists and get its state."""
    book_slug = ctx.obj["book_slug"]
    print(f"Checking if '{book_slug}' exists")
    resp, err = ctx.obj["client"].book_exists(book_slug=book_slug)
    if err is not None:
        print(err)
        sys.exit(1)
    if resp is not None and resp.status_code == 200:
        print(resp.json())
        sys.exit(0)
    print("Unknown error has occurred!")
    sys.exit(1)


@main.command()
@click.pass_context
def unpublish(ctx: click.Context) -> None:
    """Unpublish the book."""
    book_slug = ctx.obj["book_slug"]
    print(f"Unpublishing '{book_slug}'")
    resp, err = ctx.obj["client"].unpublish(book_slug=book_slug)
    sys.exit(_handle_response(resp, err, f"Unpublish completed at {datetime.datetime.now(datetime.UTC)}"))


@main.command(name="check-status")
@click.option("--wait", is_flag=True, default=False, envvar="INPUT_WAIT", help="Poll until job completes.")
@click.option("--poll-interval", default=5, type=int, envvar="INPUT_POLL_INTERVAL", help="Seconds between polls.")
@click.option("--timeout", default=120, type=int, envvar="INPUT_TIMEOUT", help="Max seconds to wait.")
@click.pass_context
def check_status(ctx: click.Context, wait: bool, poll_interval: int, timeout: int) -> None:
    """Check the job status of a preview or publish."""
    book_slug = ctx.obj["book_slug"]
    client = ctx.obj["client"]
    print(f"Checking status of '{book_slug}'")

    if not wait:
        resp, err = client.check_status(book_slug=book_slug)
        if err is not None:
            print(err)
            sys.exit(1)
        if resp is not None and resp.status_code == 200:
            print(f"Status: {resp.json()}")
            sys.exit(0)
        print("Unknown error has occurred!")
        sys.exit(1)

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        resp, err = client.check_status(book_slug=book_slug)
        if err is not None:
            print(err)
            sys.exit(1)
        if resp is not None and resp.json() == {}:
            print("Job complete.")
            sys.exit(0)
        print(f"Status: {resp.json()}")
        time.sleep(poll_interval)
    print(f"Timeout after {timeout}s")
    sys.exit(1)
