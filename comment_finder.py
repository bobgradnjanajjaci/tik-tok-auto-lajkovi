import re
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

REQUIRED_WORDS = ["encrypted", "money"]

REQUEST_TIMEOUT = 8
MAX_PAGES = 4
RETRY_COUNT = 2
RETRY_DELAY = 8


def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def expand_url(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        return r.url
    except Exception:
        return url


def extract_video_id(url: str):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None


def fetch_comments(video_id: str):
    comments = []
    cursor = 0

    for _ in range(MAX_PAGES):
        try:
            r = requests.get(
                "https://www.tiktok.com/api/comment/list/",
                headers=HEADERS,
                params={
                    "aid": 1988,
                    "count": 50,
                    "cursor": cursor,
                    "aweme_id": video_id,
                },
                timeout=REQUEST_TIMEOUT,
            )

            if r.status_code != 200:
                break

            data = r.json()
            batch = data.get("comments") or []
            comments.extend(batch)

            if not data.get("has_more"):
                break

            cursor = int(data.get("cursor") or 0)

        except Exception:
            break

    return comments


def pick_best_comment(comments):
    best = None
    top_likes = 0

    for c in comments:
        try:
            text = c.get("text") or ""
            likes = int(c.get("digg_count") or 0)
            text_norm = normalize(text)

            top_likes = max(top_likes, likes)

            if not all(w in text_norm for w in REQUIRED_WORDS):
                continue

            if not best or likes > best["likes"]:
                best = {
                    "cid": c.get("cid"),
                    "likes": likes,
                    "username": c.get("user", {}).get("unique_id"),
                    "text": text,
                }
        except Exception:
            continue

    return best, top_likes


def find_target_comment(video_url: str) -> dict:
    video_url = expand_url(video_url)
    video_id = extract_video_id(video_url)

    if not video_id:
        return {"found": False, "reason": "no_video_id"}

    for attempt in range(RETRY_COUNT):
        comments = fetch_comments(video_id)

        if comments:
            best, top_likes = pick_best_comment(comments)

            if best:
                return {
                    "found": True,
                    "video_id": video_id,
                    "my_cid": best["cid"],
                    "my_likes": best["likes"],
                    "top_likes": top_likes,
                    "username": best["username"],
                    "matched_text": best["text"],
                    "attempt": attempt + 1,
                }

        time.sleep(RETRY_DELAY)

    return {"found": False, "reason": "no_match"}
