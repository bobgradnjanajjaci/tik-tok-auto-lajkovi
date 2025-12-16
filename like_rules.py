def calculate_target_likes(top_likes: int) -> int:
    """
    Vraća UKUPAN broj lajkova koji komentar treba da ima.
    Auto-brain će poslati razliku (target - trenutni).

    Pravila:
    - Minimum efekta: 250
    - Od 300+ radi po staroj logici
    - Ako je top komentar prejak, ne šaljemo ništa
    """

    # ⛔ Ako je top komentar prevelik – preskačemo
    if top_likes >= 10000:
        return 0

    # 🔒 FORSIRANI MINIMUM
    if top_likes < 200:
        return 250

    # ⬇️ OD OVDJE IDE TVOJA POSTOJEĆA LOGIKA (NIJE MIJENJANA)
    if top_likes < 1000:
        return int(top_likes * 1.4)

    elif top_likes < 3000:
        return int(top_likes * 1.8)

    elif top_likes < 8000:
        return top_likes + 1500

    else:
        return top_likes
