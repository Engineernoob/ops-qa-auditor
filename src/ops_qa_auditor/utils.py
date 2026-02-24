# src/ops_qa_auditor/utils.py
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ReadabilityStats:
    word_count: int
    sentence_count: int


_SENTENCE_SPLIT = re.compile(r"[.!?]+\s+")
_WORD = re.compile(r"\b[\w']+\b")


def normalize(text: str) -> str:
    """Normalize text for robust matching."""
    return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split()).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """Case-insensitive containment check on normalized text."""
    t = normalize(text).lower()
    p = normalize(phrase).lower()
    return p in t


def readability(text: str) -> ReadabilityStats:
    t = text.strip()
    words = _WORD.findall(t)
    # Rough sentence count; if no punctuation, treat as 1 sentence when there are words.
    sentences = _SENTENCE_SPLIT.split(t)
    sentence_count = sum(1 for s in sentences if s.strip())
    if sentence_count == 0 and len(words) > 0:
        sentence_count = 1
    return ReadabilityStats(word_count=len(words), sentence_count=sentence_count)