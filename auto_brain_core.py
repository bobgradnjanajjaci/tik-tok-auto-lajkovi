from comment_finder import find_target_comment
from like_rules import calculate_target_likes

def process_video(video_url: str):
    result = find_target_comment(video_url)

    if not result.get("found"):
        return {"status": "error", "message": "Komentar nije pronađen"}

    target = calculate_target_likes(result["top_likes"])
    if target == 0:
        return {"status": "skip", "message": "Top komentar prejak – ne šaljem"}

    my_likes = int(result.get("my_likes") or 0)
    to_send = max(0, target - my_likes)

    if to_send <= 0:
        return {"status": "ok", "message": "Dovoljno lajkova"}

    return {
        "status": "ok",
        "video_id": result["video_id"],
        "cid": result["my_cid"],
        "username": result["username"],
        "send_likes": to_send,
    }
