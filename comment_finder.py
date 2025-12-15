import re
import requests

# ✅ keywordi koje tražiš (mora biti lower-case)
KEYWORDS = ["encrypted money code"]

STATIC_BUFFER = 5
PERCENT_BUFFER = 0.20

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def expand_tiktok_url(url: str) -> str:
    """
    Pretvara short TikTok link (tiktok.com/t/...) u puni link (.../@user/video/ID).
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
        return r.url
    except Exception:
        return url


def extract_video_id(video_url: str) -> str | None:
    """
    Izvlači video ID iz punog TikTok URL-a.
    """
    match = re.search(r"/video/(\d+)", video_url)
    return match.group(1) if match else None


def fetch_comments(video_id: str, count: int = 50) -> list:
    """
    Pokušava povući komentare sa TikTok public endpointa.
    """
    url = "https://www.tiktok.com/api/comment/list/"
    params = {
        "aid": 1988,
        "count": count,
        "aweme_id": video_id
    }

    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if r.status_code != 200:
        return []

    try:
        return r.json().get("comments", [])
    except Exception:
        return []


def apply_buffer(likes: int) -> int:
    """
    Dodaje buffer jer TikTok UI često pokazuje više lajkova nego API.
    """
    dynamic = int(likes * PERCENT_BUFFER)
    return likes + max(STATIC_BUFFER, dynamic)


def find_target_comment(video_url: str) -> dict:
    """
    1) Expand short link (ako je short)
    2) Izvuci video_id
    3) Povuci komentare
    4) Nadji prvi komentar koji sadrži keyword
    5) Vrati cid + username + likes
    """
    video_url = expand_tiktok_url(video_url)

    video_id = extract_video_id(video_url)
    if not video_id:
        return {"found": False, "error": "Video ID nije pronađen (provjeri link)"}

    comments = fetch_comments(video_id)
    if not comments:
        return {"found": False, "error": "Nema komentara ili fetch nije uspio"}

    top_likes = 0
    my_comment = None

    for c in comments:
        likes = c.get("digg_count", 0)
        text = (c.get("text") or "").lower()

        if likes > top_likes:
            top_likes = likes

        if any(k in text for k in KEYWORDS):
            user = c.get("user", {}) or {}
            my_comment = {
                "cid": c.get("cid"),
                "likes": likes,
                "username": user.get("unique_id")
            }
            break

    if not my_comment or not my_comment.get("cid") or not my_comment.get("username"):
        return {"found": False, "error": "Keyword komentar nije pronađen"}

    return {
        "found": True,
        "video_id": video_id,
        "my_cid": my_comment["cid"],
        "my_likes": apply_buffer(my_comment["likes"]),
        "top_likes": top_likes,
        "username": my_comment["username"],
        "expanded_url": video_url  # korisno za debug
    }
