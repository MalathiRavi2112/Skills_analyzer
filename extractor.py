import json
import os
from typing import List, Dict, Tuple
import spacy
from spacy.matcher import PhraseMatcher
from app.core.config import settings

class SkillExtractor:
    def __init__(self):
        self.nlp = None
        self.matcher = None
        self.alias_to_canonical: Dict[str, str] = {}
        self.skill_categories: Dict[str, str] = {}
        self._load_nlp_and_skills()

    def _load_nlp_and_skills(self):
        # 1. Load spaCy model (fall back to blank en if model package not installed)
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
        except Exception:
            self.nlp = spacy.blank("en")

        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # 2. Load skills dictionary
        skills_path = settings.SKILLS_DATA_PATH
        if not os.path.exists(skills_path):
            skills_path = os.path.join(os.getcwd(), "data", "skills_master.json")

        if os.path.exists(skills_path):
            with open(skills_path, "r", encoding="utf-8") as f:
                skills_data = json.load(f)
        else:
            skills_data = []

        patterns_dict: Dict[str, List] = {}

        for item in skills_data:
            canonical = item.get("canonical")
            category = item.get("category", "Tools & Methodologies")
            aliases = item.get("aliases", [])

            self.skill_categories[canonical] = category

            # Map both canonical and aliases
            all_terms = set([canonical] + aliases)
            for term in all_terms:
                clean_term = term.strip().lower()
                self.alias_to_canonical[clean_term] = canonical
                doc = self.nlp.make_doc(clean_term)
                if canonical not in patterns_dict:
                    patterns_dict[canonical] = []
                patterns_dict[canonical].append(doc)

        for canonical, patterns in patterns_dict.items():
            self.matcher.add(canonical, patterns)

    def extract_skills(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts skills from text using spaCy PhraseMatcher.
        Maps matched phrases back to canonical skill names and categories.
        """
        if not text:
            return []

        doc = self.nlp(text[:50000]) # Cap to 50k chars for fast processing
        matches = self.matcher(doc)

        extracted = {}

        for match_id, start, end in matches:
            rule_id = self.nlp.vocab.strings[match_id] # canonical name
            span_text = doc[start:end].text.strip().lower()

            canonical_name = self.alias_to_canonical.get(span_text, rule_id)
            category = self.skill_categories.get(canonical_name, "Tools & Methodologies")

            if canonical_name not in extracted:
                extracted[canonical_name] = {
                    "name": canonical_name,
                    "category": category,
                    "confidence": 0.95
                }

        # Secondary heuristic regex pass for C++, C#, .NET, CI/CD which sometimes tokenize unusually
        raw_lower = text.lower()
        special_cases = [
            ("c++", "C++", "Programming Languages"),
            ("c#", "C#", "Programming Languages"),
            (".net", "C#", "Programming Languages"),
            ("ci/cd", "CI/CD", "Cloud & DevOps"),
            ("k8s", "Kubernetes", "Cloud & DevOps"),
            ("js", "JavaScript", "Programming Languages"),
            ("ts", "TypeScript", "Programming Languages"),
        ]
        for token, canon, cat in special_cases:
            if canon not in extracted:
                # check boundary
                if f" {token} " in f" {raw_lower} " or f"({token})" in raw_lower or f"/{token}" in raw_lower:
                    extracted[canon] = {
                        "name": canon,
                        "category": cat,
                        "confidence": 0.90
                    }

        return list(extracted.values())

# Singleton instance
extractor = SkillExtractor()

