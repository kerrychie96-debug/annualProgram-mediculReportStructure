import re

import jieba

from .rules import MEDICAL_TERMS


for term in MEDICAL_TERMS:
    jieba.add_word(term, freq=200000, tag="med")


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"[。！？!?；;\n]+", text)
    sentences = []
    for part in parts:
        for item in re.split(r"(?<=[\u4e00-\u9fa5])，(?=[\u4e00-\u9fa5])", part):
            item = item.strip(" ，")
            if item:
                sentences.append(item)
    return sentences


def tokenize_sentence(sentence: str) -> list[str]:
    return [word for word in jieba.lcut(sentence, HMM=True) if word.strip()]


def tokenize_text(sentences: list[str]) -> list[dict]:
    return [{"sentence": sentence, "tokens": tokenize_sentence(sentence)} for sentence in sentences]
