import re

from .rules import DEFAULT_UNITS, DIAGNOSES, INDICATOR_ALIASES, SYMPTOMS


DURATION_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?|半|一|二|两|三|四|五|六|七|八|九|十)"
    r"\s*(?P<unit>小时|天|日|周|星期|月|年)"
)

NUMBER_PATTERN = r"[-+]?\d+(?:\.\d+)?"
UNIT_PATTERN = r"(?:℃|°C|度|mmHg|mg/L|ng/mL|mmol/L|g/L|10\^9/L|10\^12/L|%|次/分|bpm|U/L)?"


def unique_by_key(items: list[dict], key: str) -> list[dict]:
    seen = set()
    result = []
    for item in items:
        marker = item.get(key)
        if marker not in seen:
            seen.add(marker)
            result.append(item)
    return result


def extract_durations(text: str) -> list[dict]:
    durations = []
    for match in DURATION_PATTERN.finditer(text):
        value = match.group("value")
        unit = match.group("unit")
        if unit == "日":
            unit = "天"
        if unit == "星期":
            unit = "周"
        durations.append({"text": match.group(0), "value": value, "unit": unit})
    return durations


def extract_symptoms(text: str, sentences: list[str]) -> list[dict]:
    symptoms = []
    for symptom in sorted(SYMPTOMS, key=len, reverse=True):
        for sentence in sentences:
            if symptom in sentence:
                negated = bool(re.search(rf"(无|未见|否认).{{0,4}}{re.escape(symptom)}", sentence))
                duration = None
                duration_match = DURATION_PATTERN.search(sentence)
                if duration_match:
                    duration = duration_match.group(0)
                symptoms.append(
                    {
                        "name": symptom,
                        "negated": negated,
                        "duration": duration,
                        "source": sentence,
                    }
                )
                break
    return unique_by_key(symptoms, "name")


def build_indicator_patterns() -> list[tuple[str, str, re.Pattern]]:
    patterns = []
    for standard_name, aliases in INDICATOR_ALIASES.items():
        for alias in aliases:
            escaped = re.escape(alias)
            pattern = re.compile(
                rf"(?P<name>{escaped})\s*"
                rf"(?:为|是|:|：|=|约|达|升至|降至)?\s*"
                rf"(?P<value>{NUMBER_PATTERN}(?:\s*/\s*{NUMBER_PATTERN})?)\s*"
                rf"(?P<unit>{UNIT_PATTERN})",
                re.IGNORECASE,
            )
            patterns.append((standard_name, alias, pattern))
    return patterns


INDICATOR_PATTERNS = build_indicator_patterns()


def normalize_unit(indicator_name: str, raw_unit: str) -> tuple[str, bool]:
    unit = (raw_unit or "").strip()
    if unit in ["°C", "度"]:
        return "℃", False
    if unit == "bpm":
        return "次/分", False
    if unit:
        return unit, False
    return DEFAULT_UNITS.get(indicator_name, ""), True


def extract_indicators(text: str) -> list[dict]:
    indicators = []
    occupied = set()

    for standard_name, alias, pattern in INDICATOR_PATTERNS:
        for match in pattern.finditer(text):
            span = match.span()
            if span in occupied:
                continue
            occupied.add(span)

            value = re.sub(r"\s+", "", match.group("value"))
            unit, auto_completed = normalize_unit(standard_name, match.group("unit"))

            indicators.append(
                {
                    "name": standard_name,
                    "alias": alias,
                    "value": value,
                    "unit": unit,
                    "unit_auto_completed": auto_completed,
                    "source": match.group(0),
                }
            )

    return indicators


def extract_diagnoses(text: str, sentences: list[str]) -> list[dict]:
    diagnoses = []
    diagnosis_prefix = re.compile(r"(诊断|考虑|提示|印象|符合|拟诊)[:：为]?\s*([^。；;，,]+)")

    for sentence in sentences:
        prefix_match = diagnosis_prefix.search(sentence)
        if prefix_match:
            candidate = prefix_match.group(2).strip()
            for diagnosis in DIAGNOSES:
                if diagnosis in candidate:
                    diagnoses.append(
                        {
                            "name": diagnosis,
                            "source": sentence,
                            "confidence": "high",
                        }
                    )

        for diagnosis in DIAGNOSES:
            if diagnosis in sentence and not any(item["name"] == diagnosis for item in diagnoses):
                diagnoses.append(
                    {
                        "name": diagnosis,
                        "source": sentence,
                        "confidence": "medium",
                    }
                )

    return unique_by_key(diagnoses, "name")


def extract_information(text: str, sentences: list[str]) -> dict:
    return {
        "symptoms": extract_symptoms(text, sentences),
        "durations": extract_durations(text),
        "indicators": extract_indicators(text),
        "diagnoses": extract_diagnoses(text, sentences),
    }
