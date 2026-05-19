import re

from .rules import COLLOQUIAL_TERMS, CORRECTIONS, FILLER_WORDS


def clean_invalid_chars(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9.%℃°/：:，,。；;、\-\+\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def replace_terms(text: str, mapping: dict[str, str]) -> str:
    for wrong, right in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(wrong, right)
    return text


def remove_fillers(text: str) -> str:
    for word in sorted(FILLER_WORDS, key=len, reverse=True):
        text = text.replace(word, "")
    return text


def remove_duplicate_words(text: str) -> str:
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"([\u4e00-\u9fa5]{2,6})\1+", r"\1", text)
    return text


def normalize_punctuation(text: str) -> str:
    text = text.replace("；", "。").replace(";", "。")
    text = text.replace(",", "，").replace(":", "：")
    text = re.sub(r"[，、]\s*", "，", text)
    text = re.sub(r"。+", "。", text)
    return text.strip(" ，。")


def preprocess_text(text: str) -> dict:
    cleaned = clean_invalid_chars(text)
    corrected = replace_terms(cleaned, CORRECTIONS)
    no_fillers = remove_fillers(corrected)
    deduplicated = remove_duplicate_words(no_fillers)
    standardized = replace_terms(deduplicated, COLLOQUIAL_TERMS)
    normalized = normalize_punctuation(standardized)

    return {
        "original": text,
        "cleaned": cleaned,
        "corrected": corrected,
        "standardized": normalized,
    }
