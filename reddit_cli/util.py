import json
import re
import subprocess
from urllib.parse import urlparse

POST_ID_PATTERN = re.compile(r"/comments/([a-z0-9]+)/?")
COMMENT_ID_PATTERN = re.compile(r"/comments/[a-z0-9]+/[^/]+/([a-z0-9]+)/?")


def extract_post_id(url: str) -> str:
    match = POST_ID_PATTERN.search(urlparse(url).path)
    if not match:
        raise ValueError("Could not extract post ID from URL")
    return match.group(1)


def extract_comment_id(url: str) -> str:
    match = COMMENT_ID_PATTERN.search(urlparse(url).path)
    if not match:
        raise ValueError("Could not extract comment ID from URL")
    return match.group(1)


def extract_image_urls(post: dict) -> list[str]:
    urls = []
    if post.get("is_video"):
        return urls
    direct = post.get("url") or ""
    if any(direct.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
        urls.append(direct)
    preview = post.get("preview") or {}
    for img in (preview.get("images") or []):
        source = img.get("source") or {}
        if source.get("url"):
            candidate = source["url"].replace("&amp;", "&")
            if candidate not in urls:
                urls.append(candidate)
    return urls


def fetch_post_data(post_id: str) -> dict:
    result = subprocess.run(
        ["rdt", "read", post_id, "--json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"rdt failed: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    if not data.get("ok"):
        raise RuntimeError(data.get("error", {}).get("message", "Unknown error"))
    return data


def parse_comment_tree(children: list) -> list[dict]:
    comments = []
    for child in children:
        if child["kind"] != "t1":
            continue
        data = child["data"]
        replies_data = data.get("replies") or {}
        nested = []
        if isinstance(replies_data, dict):
            replies_listing = replies_data.get("data") or {}
            nested = parse_comment_tree(replies_listing.get("children") or [])
        comments.append({
            "id": data["id"],
            "author": data["author"],
            "body": data["body"],
            "score": data["score"],
            "permalink": f"https://www.reddit.com{data['permalink']}",
            "created_utc": data["created_utc"],
            "replies": nested,
        })
    return comments
