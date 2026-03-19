"""Leanpub API Client and Helpers.

API Docs: https://leanpub.com/help/api
API URL: https://leanpub.com/
"""

import requests


class Leanpub(requests.Session):
    """Leanpub API Client object.

    Based upon the requests.session object, so all underlying requests methods available.

    Requires a Leanpub API Key to be instantiated.
    """

    def __init__(self, leanpub_api_key: str, **kwargs: dict) -> None:
        """Instantiate a Leanpub client.

        Args:
            leanpub_api_key (str): A valid Leanpub API Key
            **kwargs (dict): Additional keyword arguments passed to requests.Session.

        """
        super().__init__(**kwargs)
        self.leanpub_api_key = leanpub_api_key
        self.leanpub_url = "https://leanpub.com/"

    def preview(
        self,
        book_slug: str,
        subset: bool = False,
    ) -> tuple[requests.Response | None, requests.RequestException | None]:
        """Request a Preview be built of the book_slug provided.

        Args:
            book_slug (str): book_slug to generate a Preview of
            subset (bool): If True, preview only the Subset.txt files

        """
        path = f"{book_slug}/preview/subset.json" if subset else f"{book_slug}/preview.json"
        url = f"{self.leanpub_url}{path}"
        payload = {"api_key": self.leanpub_api_key}
        try:
            resp = self.post(url=url, json=payload)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None

    def preview_single(
        self,
        book_slug: str,
        content: str,
    ) -> tuple[requests.Response | None, requests.RequestException | None]:
        """Preview a single file of Markdown content.

        Args:
            book_slug (str): book_slug to generate a Preview for
            content (str): Markdown content to preview

        """
        url = f"{self.leanpub_url}{book_slug}/preview/single.json"
        params = {"api_key": self.leanpub_api_key}
        headers = {"Content-Type": "text/plain"}
        try:
            resp = self.post(url=url, params=params, data=content.encode(), headers=headers)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None

    def publish(
        self,
        book_slug: str,
        email_readers: bool = False,
        release_notes: str | None = None,
    ) -> tuple[requests.Response | None, requests.RequestException | None]:
        """Publish the book_slug provided.

        Args:
            book_slug (str): book_slug to publish
            email_readers (bool): Whether to email readers about the new version
            release_notes (str): Optional release notes for this publish

        """
        url = f"{self.leanpub_url}{book_slug}/publish.json"
        payload = {
            "api_key": self.leanpub_api_key,
            "publish[email_readers]": email_readers,
        }
        if release_notes:
            payload["publish[release_notes]"] = release_notes
        try:
            resp = self.post(url=url, data=payload)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None

    def book_summary(self, book_slug: str) -> tuple[requests.Response | None, requests.RequestException | None]:
        """Get the summary/metadata for the book_slug provided.

        Args:
            book_slug (str): book_slug to get summary of

        """
        url = f"{self.leanpub_url}{book_slug}.json"
        params = {"api_key": self.leanpub_api_key}
        try:
            resp = self.get(url=url, params=params)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None

    def check_status(self, book_slug: str) -> tuple[requests.Response | None, requests.RequestException | None]:
        """Check the job status of a Preview or Publish for the book_slug provided.

        Args:
            book_slug (str): book_slug to check status of

        """
        url = f"{self.leanpub_url}{book_slug}/job_status.json"
        params = {"api_key": self.leanpub_api_key}
        try:
            resp = self.get(url=url, params=params)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None
