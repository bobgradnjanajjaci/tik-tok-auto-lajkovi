# like_rules.py

def calculate_target_likes(top_likes: int) -> int:
    # ako nema top komentara
    if top_likes <= 0:
        return 100

    # mali komentari
    if top_likes < 100:
        return 100

    # do 1k -> agresivnije
    if top_likes < 1000:
        return int(top_likes * 1.5)

    # 1k – 3k -> x1.3 (IZMIJENJENO)
    if top_likes < 3000:
        return int(top_likes * 1.3)

    # 3k – 8k -> +1000 (IZMIJENJENO)
    if top_likes < 8000:
        return top_likes + 1000

    # preko 8k -> preskoci (preskupo / sumnjivo)
    return 0
