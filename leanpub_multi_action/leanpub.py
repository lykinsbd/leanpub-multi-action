"""Leanpub API Client and Helpers.

API Docs: https://leanpub.com/help/api
API URL: https://leanpub.com/
"""

from typing import Optional, Tuple

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
        """
        super().__init__(**kwargs)
        self.leanpub_api_key = leanpub_api_key
        self.leanpub_url = "https://leanpub.com/"

    def preview(self, book_slug: str) -> Tuple[Optional[requests.Response], Optional[requests.RequestException]]:
        """Request a Preview be built of the book_slug provided.

        Args:
            book_slug (str): book_slug to generate a Preview of
        """
        url = f"{self.leanpub_url}{book_slug}/preview.json"
        payload = {"api_key": self.leanpub_api_key}
        try:
            resp = self.post(url=url, json=payload)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None

    def publish(
        self,
        book_slug: str,
        email_readers: bool = False,
        release_notes: Optional[str] = None,
    ) -> Tuple[Optional[requests.Response], Optional[requests.RequestException]]:
        """Publish the book_slug provided.

        Args:
            book_slug (str): book_slug to publish
            email_readers (bool): Whether to email readers about the new version
            release_notes (str): Optional release notes for this publish
        """
        url = f"{self.leanpub_url}{book_slug}/publish.json"
        payload = {"api_key": self.leanpub_api_key, "publish[email_readers]": email_readers}
        if release_notes:
            payload["publish[release_notes]"] = release_notes
        try:
            resp = self.post(url=url, data=payload)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None

    def check_status(self, book_slug: str) -> Tuple[Optional[requests.Response], Optional[requests.RequestException]]:
        """Check the job status of a Preview or Publish for the book_slug provided.

        Args:
            book_slug (str): book_slug to check status of
        """
        url = f"{self.leanpub_url}{book_slug}/book_status.json"
        params = {"api_key": self.leanpub_api_key}
        try:
            resp = self.get(url=url, params=params)
            resp.raise_for_status()
        except requests.RequestException as exception:
            return None, exception

        return resp, None
