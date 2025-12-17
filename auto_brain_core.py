import time
from comment_finder import find_target_comment
from like_rules import calculate_target_likes


def process_video(video_url: str):
    try:
        result = find_target_comment(video_url)

        if not result.get("found"):
            return {"status": "error", "message": "Komentar nije pronađen"}

        target = calculate_target_likes(result["top_likes"])
        if target <= result["my_likes"]:
            return {"status": "ok", "message": "Dovoljno lajkova"}

        return {
            "status": "ok",
            "video_id": result["video_id"],
            "cid": result["my_cid"],
            "username": result["username"],
            "send_likes": target - result["my_likes"],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
