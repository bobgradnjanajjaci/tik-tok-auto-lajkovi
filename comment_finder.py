import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

SIGNATURE_TOKENS = [
    "encrypted",
    "money",
    "code",
    "ethan",
    "rothwell",
]

EXACT_TITLE = "encrypted money code by ethan rothwell"

POWER_PHRASES = [
    "changed my life",
    "it changed my life",
    "change your life",
    "you need this book",
    "need right now",
    "game changer",
    "another level",
    "hidden information",
    "not random",
    "plot twist",
    "page 13",
]

STATIC_BUFFER = 5
PERCENT_BUFFER = 0.20


def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def expand_url(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        return r.url
    except Exception:
        return url


def extract_video_id(url: str):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None


def fetch_comments(video_id: str):
    comments = []
    cursor = 0

    for _ in range(8):  # ⬅️ povećano na 400 komentara
        params = {
            "aid": 1988,
            "count": 50,
            "cursor": cursor,
            "aweme_id": video_id,
        }

        try:
            r = requests.get(
                "https://www.tiktok.com/api/comment/list/",
                headers=HEADERS,
                params=params,
                timeout=10
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


def score_comment(text_norm: str) -> int:
    score = 0

    # 🥇 EXACT TITLE – NE MOŽE PROMAŠITI
    if EXACT_TITLE in text_norm:
        score += 300

    token_hits = sum(1 for t in SIGNATURE_TOKENS if t in text_norm)

    # 🔹 3/5 tokena ali mora imati encrypted + money
    if token_hits >= 3 and "encrypted" in text_norm and "money" in text_norm:
        score += 120 + token_hits * 15

    # 🔹 stari strong case
    if token_hits >= 4:
        score += 150 + token_hits * 20

    for p in POWER_PHRASES:
        if p in text_norm:
            score += 25

    return score


def apply_buffer(likes: int) -> int:
    return likes + max(STATIC_BUFFER, int(likes * PERCENT_BUFFER))


def find_target_comment(video_url: str) -> dict:
    video_url = expand_url(video_url)
    video_id = extract_video_id(video_url)

    if not video_id:
        return {"found": False}

    comments = fetch_comments(video_id)
    if not comments:
        return {"found": False}

    best = None
    best_score = 0
    top_likes = 0

    fallback_candidates = []

    for c in comments:
        text = c.get("text") or ""
        likes = int(c.get("digg_count") or 0)
        text_norm = normalize(text)

        top_likes = max(top_likes, likes)
        score = score_comment(text_norm)

        if "encrypted money code" in text_norm:
            fallback_candidates.append((likes, c))

        if score > 0:
            if (
                not best
                or score > best_score
                or (score == best_score and likes > best["likes"])
            ):
                best = {
                    "cid": c.get("cid"),
                    "likes": likes,
                    "username": c.get("user", {}).get("unique_id"),
                    "text": text,
                }
                best_score = score

    # 🔥 LAST RESORT FALLBACK
    if not best and fallback_candidates:
        likes, c = max(fallback_candidates, key=lambda x: x[0])
        best = {
            "cid": c.get("cid"),
            "likes": likes,
            "username": c.get("user", {}).get("unique_id"),
            "text": c.get("text"),
        }

    if not best:
        return {"found": False}

    return {
        "found": True,
        "video_id": video_id,
        "my_cid": best["cid"],
        "my_likes": apply_buffer(best["likes"]),
        "top_likes": top_likes,
        "username": best["username"],
        "matched_text": best["text"],
        "confidence_score": best_score,
    }
