def clean_query(query: str) -> str:
    value = query.lower()
    for char in ['"', "'", ".", ",", "?", "!", "\n"]:
        value = value.replace(char, "")
    return " ".join(value.split()[:6]).strip()
