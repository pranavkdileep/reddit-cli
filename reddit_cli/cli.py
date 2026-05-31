import subprocess
import sys

from reddit_cli.ai import createComment, createReply
from reddit_cli.util import extract_post_id, extract_comment_id, fetch_post_data, extract_image_urls


def view_post(url: str):
    try:
        post_id = extract_post_id(url)
    except ValueError as e:
        print(f"Error : {e}")
        return
    try:
        raw = fetch_post_data(post_id)
    except Exception as e:
        print(f"Error: {e}")
        return
    data = raw.get("data")
    if not data:
        print("Post not fund")
        return
    post_data = data["post"]
    comments = data.get("comments", [])
    print("\n" + "=" * 60)
    print(f"Title: {post_data['title']}")
    print(f"Author: u/{post_data['author']} | Score: {post_data['score']} | Comments: {post_data['num_comments']}")
    print("-" * 60)
    body = post_data.get("selftext", "")
    if body:
        print(body[:500])
    imgs = extract_image_urls(post_data)
    if imgs:
        print(f"\nImages: {len(imgs)}")
        for img in imgs[:3]:
            print(f"  {img}")
    print("\nComments:")
    for c in comments[:5]:
        print(f"  u/{c['author']}: {c['body'][:120]}")
    print("=" * 60)


def post_comment(url: str, text: str):
    try:
        post_id = extract_post_id(url)
    except ValueError as e:
        print(f"Error: {e}")
        return False
    result = subprocess.run(
        ["rdt", "comment", post_id, text],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0:
        print("Comment posted!")
        return True
    print(f"Failed: {result.stderr.strip()}")
    return False


def reply_comment(url: str, text: str):
    try:
        comment_id = extract_comment_id(url)
    except ValueError as e:
        print(f"Error: {e}")
        return False
    result = subprocess.run(
        ["rdt", "comment", f"t1_{comment_id}", text],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0:
        print("Reply posted!")
        return True
    print(f"Failed: {result.stderr.strip()}")
    return False


def ai_comment():
    url = input("Post URL: ").strip()
    while True:
        print("Generating AI comment...")
        try:
            text = createComment(url)
        except Exception as e:
            print(f"Error: {e}")
            return
        print("\n--- Generated Comment ---")
        print(text)
        print("-------------------------")
        choice = input("\n[Enter] to post | [r] regenerate | [q] back: ").strip().lower()
        if choice == "r":
            continue
        elif choice == "q":
            return
        else:
            if post_comment(url, text):
                return


def ai_reply():
    url = input("Comment URL: ").strip()
    while True:
        print("Generating AI reply...")
        try:
            text = createReply(url)
        except Exception as e:
            print(f"Error: {e}")
            return
        print("\n--- Generated Reply ---")
        print(text)
        print("-----------------------")
        choice = input("\n[Enter] to post | [r] regenerate | [q] back: ").strip().lower()
        if choice == "r":
            continue
        elif choice == "q":
            return
        else:
            if reply_comment(url, text):
                return


def main():
    while True:
        print("\n" + "=" * 40)
        print("  Reddit CLI")
        print("=" * 40)
        print("  1. AI Comment")
        print("  2. AI Reply")
        print("  3. View Post")
        print("  4. Post Comment (manual)")
        print("  5. Reply to Comment (manual)")
        print("  6. Exit")
        print("=" * 40)
        choice = input("Select: ").strip()
        if choice == "1":
            ai_comment()
        elif choice == "2":
            ai_reply()
        elif choice == "3":
            url = input("Post URL: ").strip()
            view_post(url)
        elif choice == "4":
            url = input("Post URL: ").strip()
            text = input("Comment text: ").strip()
            post_comment(url, text)
        elif choice == "5":
            url = input("Comment URL: ").strip()
            text = input("Reply text: ").strip()
            reply_comment(url, text)
        elif choice == "6":
            print("Bye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
