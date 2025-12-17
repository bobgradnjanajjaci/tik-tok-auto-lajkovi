import time
import requests
from comment_finder import find_target_comment
from like_rules import calculate_target_likes

LIKE_APP_URL = "https://lajkovi-crtica-lajkovi.up.railway.app/"

def process_video(video_url: str) -> dict:
    result = find_target_comment(video_url)

    if not result.get("found"):
        time.sleep(2)
        result = find_target_comment(video_url)

    if not result.get("found"):
        return {"status": "error", "message": "Komentar nije pronađen"}

    target = calculate_target_likes(result["top_likes"])
    to_send = max(0, target - result["my_likes"])

    if to_send <= 0:
        return {"status": "skip", "message": "Dovoljno lajkova"}

    payload = {
        "orders": f"{video_url} {result['username']} {to_send}"
    }

    r = requests.post(LIKE_APP_URL, data=payload, timeout=20)

    return {
        "status": "sent",
        "likes": to_send,
        "username": result["username"],
        "response": r.text[:200]
    }
