# comment_finder.py
import re
import requests

KEYWORDS = ["encrypted money code"]

STATIC_BUFFER = 5
PERCENT_BUFFER = 0.20

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def extract_video_id(video_url: str) -> str | None:
    match = re.search(r"/video/(\d+)", video_url)
    return match.group(1) if match else None


def fetch_comments(video_id: str, count: int = 50) -> list:
    url = "https://www.tiktok.com/api/comment/list/"
    params = {
        "aid": 1988,
        "count": count,
        "aweme_id": video_id
    }

    r = requests.get(url, headers=HEADERS, params=params, timeout=10)
    if r.status_code != 200:
        return []

    return r.json().get("comments", [])


def apply_buffer(likes: int) -> int:
    dynamic = int(likes * PERCENT_BUFFER)
    return likes + max(STATIC_BUFFER, dynamic)


def find_target_comment(video_url: str) -> dict:
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"found": False, "error": "Video ID nije pronađen"}

    comments = fetch_comments(video_id)
    if not comments:
        return {"found": False, "error": "Nema komentara ili fetch nije uspio"}

    top_likes = 0
    my_comment = None

    for c in comments:
        likes = c.get("digg_count", 0)
        text = c.get("text", "").lower()

        if likes > top_likes:
            top_likes = likes

        if any(k in text for k in KEYWORDS):
            user = c.get("user", {})
            my_comment = {
                "cid": c.get("cid"),
                "likes": likes,
                "username": user.get("unique_id")
            }
            break  # ⬅️ BITNO: uzmi PRVI tačan komentar

    if not my_comment or not my_comment["username"]:
        return {"found": False, "error": "Keyword komentar nije pronađen"}

    return {
        "found": True,
        "video_id": video_id,
        "my_cid": my_comment["cid"],
        "my_likes": apply_buffer(my_comment["likes"]),
        "top_likes": top_likes,
        "username": my_comment["username"]
    }
