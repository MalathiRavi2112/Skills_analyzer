from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ParseResumeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Raw text of the resume")

class ExtractedSkill(BaseModel):
    name: str
    category: str
    confidence: float = 1.0

class ResumeSections(BaseModel):
    skills: List[str] = []
    education: List[str] = []
    experience: List[str] = []
    projects: List[str] = []
    certifications: List[str] = []

class ParseResumeResponse(BaseModel):
    sections: ResumeSections
    extractedSkills: List[ExtractedSkill]

class TargetSkill(BaseModel):
    name: str
    category: Optional[str] = "General"
    demandFrequency: Optional[float] = 70.0

class AnalyzeGapRequest(BaseModel):
    jobTitle: str
    jobDescription: Optional[str] = ""
    resumeSkills: List[str]
    targetSkills: List[TargetSkill]
    resumeProjects: Optional[List[str]] = []
    resumeExperience: Optional[List[str]] = []
    resumeEducation: Optional[List[str]] = []
    resumeText: Optional[str] = ""

class SkillItem(BaseModel):
    name: str
    category: str
    demandFrequency: float
    priority: Optional[str] = "Medium"

class ScoreBreakdown(BaseModel):
    overall: int
    skillMatchScore: int
    projectRelevanceScore: int
    experienceRelevanceScore: int
    resumeQualityScore: int

class RadarMetric(BaseModel):
    category: str
    resumeScore: int
    marketBenchmark: int

class AnalyzeGapResponse(BaseModel):
    matchedSkills: List[SkillItem]
    missingSkills: List[SkillItem]
    extraSkills: List[str]
    scores: ScoreBreakdown
    categoryLabel: str
    summary: str
    radarMetrics: List[RadarMetric]

