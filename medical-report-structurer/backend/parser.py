from .extractor import extract_information
from .preprocess import preprocess_text
from .tokenizer import split_sentences, tokenize_text


def parse_medical_report(text: str) -> dict:
    preprocessing = preprocess_text(text)
    standardized_text = preprocessing["standardized"]
    sentences = split_sentences(standardized_text)
    tokenized = tokenize_text(sentences)
    extracted = extract_information(standardized_text, sentences)

    return {
        "preprocessing": preprocessing,
        "sentences": sentences,
        "tokenized": tokenized,
        "extracted": extracted,
    }
