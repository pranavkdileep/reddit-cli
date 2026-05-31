from reddit_cli.llm_client import COMMENT_SYSTEM_PROMPT, generate
from reddit_cli.util import extract_post_id, extract_comment_id, extract_image_urls, fetch_post_data


def createComment(post_url: str, style: str = "casual") -> str:
    post_id = extract_post_id(post_url)
    raw = fetch_post_data(post_id)
    data = raw.get("data")
    if not data:
        raise RuntimeError("Post not fond")
    post_data = data["post"]
    title = post_data["title"]
    body = post_data.get("selftext", "")[:500]

    imgs = extract_image_urls(post_data)
    prompt = f"Post title: {title}\nPost body: {body}\n\nWrite a {style} comment on this post."
    return generate(COMMENT_SYSTEM_PROMPT, prompt, imgs[:3] if imgs else None)


def createReply(comment_url: str, style: str = "casual") -> str:
    comment_id = extract_comment_id(comment_url)
    post_id = extract_post_id(comment_url)
    raw = fetch_post_data(post_id)
    data = raw.get("data")
    if not data:
        raise RuntimeError("Post not found")
    post_data = data["post"]
    title = post_data["title"]
    comments = data.get("comments", [])

    def _find_comment(comments, target_id):
        for c in comments:
            if c["id"] == target_id:
                return c["body"]
            replies = c.get("replies") or []
            if isinstance(replies, list):
                found = _find_comment(replies, target_id)
                if found:
                    return found
        return None

    comment_body = _find_comment(comments, comment_id) or ""

    imgs = extract_image_urls(post_data)
    prompt = f"Post title: {title}\nComment: {comment_body}\n\nWrite a {style} reply to this comment."
    return generate(COMMENT_SYSTEM_PROMPT, prompt, imgs[:3] if imgs else None)
