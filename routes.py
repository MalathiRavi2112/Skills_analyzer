from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    ParseResumeRequest,
    ParseResumeResponse,
    AnalyzeGapRequest,
    AnalyzeGapResponse,
    ResumeSections,
    ExtractedSkill
)
from app.services.section_parser import parse_resume_sections
from app.services.extractor import extractor
from app.services.scorer import GapScorer
from app.utils.text_cleaner import clean_text

router = APIRouter()

@router.post(
    "/parse-resume",
    response_model=ParseResumeResponse,
    summary="Parse resume sections and extract technical/soft skills",
    status_code=status.HTTP_200_OK
)
async def parse_resume(payload: ParseResumeRequest):
    try:
        cleaned = clean_text(payload.text)
        if len(cleaned) < 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Resume content has insufficient readable characters."
            )

        # 1. Parse sections (skills, education, experience, projects, certifications)
        sections_dict = parse_resume_sections(cleaned)
        sections = ResumeSections(
            skills=sections_dict.get("skills", []),
            education=sections_dict.get("education", []),
            experience=sections_dict.get("experience", []),
            projects=sections_dict.get("projects", []),
            certifications=sections_dict.get("certifications", []),
        )

        # 2. Extract skills using spaCy PhraseMatcher & alias lookup
        raw_skills = extractor.extract_skills(cleaned)
        extracted_skills = [
            ExtractedSkill(
                name=s["name"],
                category=s["category"],
                confidence=s.get("confidence", 0.95)
            )
            for s in raw_skills
        ]

        return ParseResumeResponse(
            sections=sections,
            extractedSkills=extracted_skills
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing resume: {str(e)}"
        )

@router.post(
    "/analyze-gap",
    response_model=AnalyzeGapResponse,
    summary="Evaluate weighted skill gap analysis and compute multi-factor scores",
    status_code=status.HTTP_200_OK
)
async def analyze_gap(payload: AnalyzeGapRequest):
    try:
        target_skills_dicts = [s.model_dump() for s in payload.targetSkills]

        result = GapScorer.evaluate(
            job_title=payload.jobTitle,
            job_description=payload.jobDescription or "",
            resume_skills=payload.resumeSkills,
            target_skills=target_skills_dicts,
            resume_projects=payload.resumeProjects or [],
            resume_experience=payload.resumeExperience or [],
            resume_education=payload.resumeEducation or [],
            resume_text=payload.resumeText or ""
        )

        return AnalyzeGapResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating skill gap: {str(e)}"
        )

@router.post(
    "/extract-skills",
    summary="Direct skill extraction from arbitrary text snippet",
    status_code=status.HTTP_200_OK
)
async def extract_skills_endpoint(payload: ParseResumeRequest):
    try:
        skills = extractor.extract_skills(clean_text(payload.text))
        return {"skills": skills, "count": len(skills)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

