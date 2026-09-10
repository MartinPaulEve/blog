"""A minimal Bluesky (ATProto XRPC) client for posting thought threads."""

from datetime import UTC, datetime

import requests

from .text import find_links

BASE_URL = "https://bsky.social"


class BlueskyError(RuntimeError):
    """An XRPC request that the PDS rejected."""


def _checked(response) -> dict:
    if 200 <= response.status_code < 300:
        return response.json()
    raise BlueskyError(f"HTTP {response.status_code}: {response.text[:300]}")


class BlueskyClient:
    """Posts app.bsky.feed.post records with an app password.

    ``login()`` opens the session; ``post_thread`` publishes segments as
    a reply chain, with link facets on every segment, images embedded on
    the first, and an external link-preview card on the first when there
    are no images.
    """

    def __init__(
        self,
        identifier: str,
        password: str,
        base_url: str = BASE_URL,
        session=None,
        now=None,
    ):
        self.identifier = identifier
        self.base_url = base_url.rstrip("/")
        self._password = password
        self._session = session if session is not None else requests.Session()
        self._now = now or (lambda: datetime.now(UTC))
        self.did = None
        self._jwt = None

    def _headers(self, content_type: str | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self._jwt}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def login(self) -> str:
        """Create the session; return (and remember) the account DID."""
        data = _checked(
            self._session.post(
                f"{self.base_url}/xrpc/com.atproto.server.createSession",
                json={"identifier": self.identifier, "password": self._password},
            )
        )
        self.did = data["did"]
        self._jwt = data["accessJwt"]
        return self.did

    def upload_blob(self, data: bytes, mime: str) -> dict:
        """Upload bytes; return the blob object for embedding."""
        response = _checked(
            self._session.post(
                f"{self.base_url}/xrpc/com.atproto.repo.uploadBlob",
                data=data,
                headers=self._headers(mime),
            )
        )
        return response["blob"]

    def _embed(self, images, card) -> dict | None:
        if images:
            return {
                "$type": "app.bsky.embed.images",
                "images": [
                    {
                        "image": self.upload_blob(i["data"], i["mime"]),
                        "alt": i.get("alt", ""),
                    }
                    for i in images[:4]
                ],
            }
        if card:
            external = {
                "uri": card["uri"],
                "title": card.get("title") or card["uri"],
                "description": card.get("description") or "",
            }
            if card.get("thumb_data"):
                external["thumb"] = self.upload_blob(
                    card["thumb_data"], card.get("thumb_mime", "image/jpeg")
                )
            return {"$type": "app.bsky.embed.external", "external": external}
        return None

    def post_thread(
        self,
        segments: list[str],
        images: list[dict] | None = None,
        card: dict | None = None,
    ) -> list[str]:
        """Publish segments as a thread; return the bsky.app post URLs.

        ``images`` is ``[{"data", "mime", "alt"}]`` (at most four),
        embedded on the first post. ``card`` is a link-preview dict from
        linkcard.fetch_card, embedded on the first post when no images
        are attached.
        """
        if self._jwt is None:
            self.login()
        embed = self._embed(images, card)

        urls = []
        root_ref = parent_ref = None
        for index, segment in enumerate(segments):
            record = {
                "$type": "app.bsky.feed.post",
                "text": segment,
                "createdAt": self._now()
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
            }
            facets = [
                {
                    "index": {
                        "byteStart": link["byte_start"],
                        "byteEnd": link["byte_end"],
                    },
                    "features": [
                        {
                            "$type": "app.bsky.richtext.facet#link",
                            "uri": link["url"],
                        }
                    ],
                }
                for link in find_links(segment)
            ]
            if facets:
                record["facets"] = facets
            if index == 0 and embed:
                record["embed"] = embed
            if parent_ref:
                record["reply"] = {"root": root_ref, "parent": parent_ref}

            response = _checked(
                self._session.post(
                    f"{self.base_url}/xrpc/com.atproto.repo.createRecord",
                    json={
                        "repo": self.did,
                        "collection": "app.bsky.feed.post",
                        "record": record,
                    },
                    headers=self._headers(),
                )
            )
            ref = {"uri": response["uri"], "cid": response["cid"]}
            root_ref = root_ref or ref
            parent_ref = ref
            rkey = response["uri"].rsplit("/", 1)[-1]
            urls.append(
                f"https://bsky.app/profile/{self.identifier}/post/{rkey}"
            )
        return urls
