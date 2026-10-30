import re
from typing import Dict, List

SECTION_HEADERS = {
    "skills": [
        r"skills", r"technical skills", r"skills & tools", r"core competencies",
        r"technologies", r"tech stack", r"proficiencies", r"programming skills"
    ],
    "experience": [
        r"experience", r"work experience", r"professional experience",
        r"employment history", r"work history", r"internships", r"experience & internships"
    ],
    "projects": [
        r"projects", r"personal projects", r"academic projects",
        r"technical projects", r"key projects", r"portfolio projects"
    ],
    "education": [
        r"education", r"academic background", r"academic history",
        r"qualifications", r"degrees", r"educational background"
    ],
    "certifications": [
        r"certifications", r"certificates", r"licenses & certifications",
        r"accreditations", r"courses & certifications"
    ]
}

def parse_resume_sections(text: str) -> Dict[str, List[str]]:
    """
    Parses resume text into distinct sections by matching header patterns.
    Returns a dictionary of section names mapped to list of line items or paragraphs.
    """
    lines = text.split('\n')
    detected_sections: Dict[str, List[str]] = {
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": []
    }

    current_section = None
    buffer: List[str] = []

    # Build regex mapping for headers
    header_patterns = []
    for section_name, patterns in SECTION_HEADERS.items():
        combined = r'^(?:[#\-\*•\s]*)?\b(?:' + '|'.join(patterns) + r')\b(?::)?\s*$'
        header_patterns.append((section_name, re.compile(combined, re.IGNORECASE)))

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        # Check if line matches a section header
        matched_section = None
        for sec_name, pattern in header_patterns:
            if pattern.match(cleaned_line) or (len(cleaned_line.split()) <= 4 and any(re.search(rf'\b{p}\b', cleaned_line, re.IGNORECASE) for p in SECTION_HEADERS[sec_name])):
                # Check line length constraint to prevent catching ordinary sentences
                if len(cleaned_line) < 40:
                    matched_section = sec_name
                    break

        if matched_section:
            if current_section and buffer:
                detected_sections[current_section].extend(buffer)
                buffer = []
            current_section = matched_section
        else:
            if current_section:
                buffer.append(cleaned_line)

    if current_section and buffer:
        detected_sections[current_section].extend(buffer)

    # Fallback heuristic: If sections like skills or experience are empty, attempt keyword scan
    if not detected_sections["skills"]:
        for line in lines:
            if any(term in line.lower() for term in ["python", "javascript", "react", "sql", "java", "c++", "aws", "docker"]):
                detected_sections["skills"].append(line.strip())

    return detected_sections

