"""Key category of a single typed character. Only the category is kept, never the character."""

SENTENCE_PUNCT = set(".,")
PUNCT = set(";:'\"!?-_=+()[]{}<>/\\|`~@#$%^&*")


def char_category(ch):
    """Category of one character, using Python's Unicode predicates (str.isalpha, str.isdigit)."""
    if ch.isalpha():
        return "alphabetic"
    if ch.isdigit():
        return "numeric"
    if ch == " ":
        return "space"
    if ch == "\n":
        return "enter"
    if ch == "\t":
        return "tab"
    if ch in SENTENCE_PUNCT:
        return "sentence_punctuation"
    if ch in PUNCT:
        return "punctuation"
    return "other"
