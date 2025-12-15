from comment_finder import find_target_comment
from like_rules import calculate_target_likes
import requests

LIKE_APP_URL = "https://lajkovi-crtica-lajkovi.up.railway.app/"

def process_video(video_url: str) -> dict:
    result = find_target_comment(video_url)

    if not result.get("found"):
        return {"status": "error", "message": "Komentar nije pronađen"}

    top_likes = result["top_likes"]
    my_likes = result["my_likes"]
    username = result["username"]

    target = calculate_target_likes(top_likes)
    if target == 0:
        return {"status": "skip", "message": "Top komentar prevelik"}

    to_send = max(0, target - my_likes)
    if to_send <= 0:
        return {"status": "ok", "message": "Već ima dovoljno lajkova"}

    orders_line = f"{video_url} {username} {to_send}"
    payload = {"orders": orders_line}

    r = requests.post(LIKE_APP_URL, data=payload, timeout=25)

    return {
        "status": "sent",
        "likes_sent": to_send,
        "username": username,
        "response_snippet": r.text[:300]
    }
