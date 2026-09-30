import re
import time
from typing import Dict, Optional, Any


class EdgeRefiner:
    def __init__(self, is_enabled: bool = False, default_style: str = "clean_verbatim"):
        self.is_enabled = is_enabled
        self.default_style = default_style
        self.filler_words = [
            r"\bumm*\b",
            r"\buhh*\b",
            r"\bahh*\b",
            r"\byou know\b",
            r"\blike\b",
            r"\bi mean\b",
            r"\bactually\b",
            r"\bbasically\b",
            r"\bsort of\b",
            r"\bkind of\b",
        ]
        self.filler_pattern = re.compile("|".join(self.filler_words), re.IGNORECASE)

    def set_enabled(self, enabled: bool):
        self.is_enabled = enabled

    def clean_verbatim(self, text: str) -> str:
        if not text:
            return ""

        cleaned = self.filler_pattern.sub("", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        word_to_num = {
            "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
            "fifteen": "15", "twenty": "20", "thirty": "30", "forty": "40",
            "fifty": "50", "hundred": "100", "thousand": "1000"
        }
        for w, n in word_to_num.items():
            cleaned = re.sub(rf"\b{w}\s+dollars?\b", rf"${n}", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(rf"\b{w}\s+percent\b", rf"{n}%", cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r"\b(\d+)\s+dollars?\b", r"$\1", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b(\d+)\s+percent\b", r"\1%", cleaned, flags=re.IGNORECASE)

        if cleaned and not cleaned[0].isupper():
            cleaned = cleaned[0].upper() + cleaned[1:]

        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."

        return cleaned

    def executive_email(self, text: str) -> str:
        cleaned = self.clean_verbatim(text)
        if not cleaned:
            return ""

        first_sentence = cleaned.split(".")[0].strip()
        words = first_sentence.split()[:6]
        subject_candidate = " ".join(words)

        return (
            f"Subject: Update: {subject_candidate}\n\n"
            f"Hi Team,\n\n"
            f"{cleaned}\n\n"
            f"Please let me know if you have any questions.\n\n"
            f"Best regards,\n"
            f"Sent via SnapFlow AI on Snapdragon HP OmniBook"
        )

    def action_items(self, text: str) -> str:
        cleaned = self.clean_verbatim(text)
        if not cleaned:
            return ""

        clauses = re.split(r"[.;,]\s+(?:and\s+)?", cleaned)
        items = []
        for c in clauses:
            c = c.strip()
            if len(c) > 5:
                if not c[0].isupper():
                    c = c[0].upper() + c[1:]
                items.append(f"- [ ] {c}")

        if not items:
            items.append(f"- [ ] {cleaned}")

        return "### Action Items & Decisions:\n" + "\n".join(items)

    def code_docstring(self, text: str) -> str:
        cleaned = self.clean_verbatim(text)
        if not cleaned:
            return ""

        return (
            f'"""\n'
            f'{cleaned}\n\n'
            f'Parameters:\n'
            f'    None (Auto-extracted from voice context)\n\n'
            f'Returns:\n'
            f'    Formatted output stream for edge pipeline\n'
            f'"""'
        )

    def refine(self, text: str, style: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        if not text:
            return {"original": "", "refined": "", "style": style or self.default_style, "latency_ms": 0.0}

        should_refine = force or self.is_enabled or (style is not None and style != "raw")
        if not should_refine:
            return {"original": text, "refined": text, "style": "raw", "latency_ms": 0.0}

        t_start = time.perf_counter()
        target_style = style or self.default_style

        if target_style == "executive_email":
            refined = self.executive_email(text)
        elif target_style == "action_items":
            refined = self.action_items(text)
        elif target_style == "code_docstring":
            refined = self.code_docstring(text)
        else:
            target_style = "clean_verbatim"
            refined = self.clean_verbatim(text)

        t_end = time.perf_counter()
        latency_ms = round((t_end - t_start) * 1000.0, 2)

        return {
            "original": text,
            "refined": refined,
            "style": target_style,
            "latency_ms": latency_ms,
        }
