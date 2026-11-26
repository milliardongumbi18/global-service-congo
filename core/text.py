import re
import unicodedata


def normaliser(texte: str) -> str:
    """Prépare un texte pour la recherche : '  Électricité  Générale ' -> 'electricite generale'.

    Minuscules, accents retirés, espaces multiples réduits à un seul.
    Fonctionne de la même façon sur SQLite (local) et PostgreSQL (production).
    """
    sans_accents = unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", sans_accents).strip().lower()