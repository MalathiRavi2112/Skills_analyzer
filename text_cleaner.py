import re

def clean_text(text: str) -> str:
    """Normalizes whitespace, removes control characters, and standardizes punctuation."""
    if not text:
        return ""
    # Replace non-breaking spaces and line feed variants
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\xa0', ' ')
    # Consolidate multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove sequences of more than 2 blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_metrics_count(text: str) -> int:
    """Finds count of quantified achievements (e.g. 25%, $1.2M, 50k, 10x, 15+)."""
    if not text:
        return 0
    patterns = [
        r'\b\d+(?:\.\d+)?%',                    # percentages (e.g., 40%, 12.5%)
        r'\$\d+(?:,\d+)*(?:\.\d+)?[kKmMbB]?',   # money (e.g., $50k, $1.2M)
        r'\b\d+\+?\s*(?:users|clients|projects|commits|stars|nodes|requests|rps|tps|ms|seconds)',
        r'\b(?:increased|reduced|improved|saved|optimized|scaled|accelerated)\b[^\n.]{1,40}\b\d+',
    ]
    total_matches = 0
    for p in patterns:
        total_matches += len(re.findall(p, text, re.IGNORECASE))
    return total_matches

