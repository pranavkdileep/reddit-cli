import subprocess
import json
import time
import sys
import threading

from reddit_cli.ai import createComment


MY_USERNAME = None


def get_username() -> str:
    global MY_USERNAME
    if MY_USERNAME:
        return MY_USERNAME
    result = subprocess.run(
        ["rdt", "whoami", "--json"],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        MY_USERNAME = data.get("data", {}).get("name", "")
    return MY_USERNAME


def get_new_posts(subreddit: str, minutes: int = 10) -> list[dict]:
    result = subprocess.run(
        ["rdt", "sub", subreddit, "-s", "new", "-n", "10", "--json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"[{subreddit}] rdt error: {result.stderr.strip()}")
        return []
    data = json.loads(result.stdout)
    children = data["data"]["data"]["children"]
    cutoff = time.time() - minutes * 60
    posts = []
    for child in children:
        post = child["data"]
        if post["created_utc"] >= cutoff:
            posts.append(post)
    return posts


def post_comment(post_id: str, text: str) -> bool:
    result = subprocess.run(
        ["rdt", "comment", post_id, text],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0:
        print(f"  Comment posted on {post_id}")
        return True
    print(f"  Failed on {post_id}: {result.stderr.strip()}")
    return False


def monitor(subreddit: str):
    username = get_username()
    print(f"[{subreddit}] Monitoring every 60s... (user: {username})")
    seen = set()
    while True:
        try:
            posts = get_new_posts(subreddit)
            new_posts = [p for p in posts if p["id"] not in seen]
            if new_posts:
                print(f"\n[{subreddit}] {len(new_posts)} new post(s)")
                for post in new_posts:
                    seen.add(post["id"])
                    title = post.get("title", "untitled")[:60]
                    print(f"  {post['id']}: {title}")
                    try:
                        url = f"https://www.reddit.com{post['permalink']}"
                        text = createComment(url)
                        print(f"  Generated: {text[:80]}...")
                        post_comment(post["id"], text)
                    except Exception as e:
                        print(f"  Error: {e}")
                    time.sleep(3)
            else:
                print(f"[{subreddit}] No new posts")
        except Exception as e:
            print(f"[{subreddit}] Error: {e}")
        time.sleep(60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python auto.py <subreddit1> <subreddit2> ...")
        sys.exit(1)
    subs = sys.argv[1:]
    print(f"Monitoring {len(subs)} communities: {', '.join(subs)}")
    threads = []
    for sub in subs:
        t = threading.Thread(target=monitor, args=(sub,), daemon=True)
        t.start()
        threads.append(t)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == "__main__":
    main()
