from typing import List, Dict, Any, Tuple
from app.services.similarity import similarity_engine
from app.utils.text_cleaner import extract_metrics_count

class GapScorer:
    """
    Weighted 4-factor scoring engine:
    - 50% Skill Match (weighted by market demand frequency)
    - 20% Project Relevance (semantic similarity via sentence-transformers)
    - 15% Experience / Internship Relevance
    - 15% Resume Quality (quantified metrics, clear structure, formatting)
    """

    @classmethod
    def evaluate(
        cls,
        job_title: str,
        job_description: str,
        resume_skills: List[str],
        target_skills: List[Dict[str, Any]],
        resume_projects: List[str],
        resume_experience: List[str],
        resume_education: List[str],
        resume_text: str
    ) -> Dict[str, Any]:
        resume_skills_lower = set(s.strip().lower() for s in resume_skills)

        matched_skills = []
        missing_skills = []

        total_target_demand_weight = 0.0
        matched_demand_weight = 0.0

        for t_skill in target_skills:
            name = t_skill.get("name", "")
            category = t_skill.get("category", "General")
            demand = float(t_skill.get("demandFrequency", 70.0))

            total_target_demand_weight += demand

            if name.lower() in resume_skills_lower:
                matched_skills.append({
                    "name": name,
                    "category": category,
                    "demandFrequency": demand,
                })
                matched_demand_weight += demand
            else:
                priority = "High" if demand >= 65 else ("Medium" if demand >= 45 else "Low")
                missing_skills.append({
                    "name": name,
                    "category": category,
                    "demandFrequency": demand,
                    "priority": priority
                })

        # Extra skills present in resume but not in primary target requirements
        target_names_lower = set(t.get("name", "").lower() for t in target_skills)
        extra_skills = [s for s in resume_skills if s.lower() not in target_names_lower]

        # 1. 50% Skill Match (Weighted by demand frequency)
        if total_target_demand_weight > 0:
            skill_match_ratio = matched_demand_weight / total_target_demand_weight
        else:
            skill_match_ratio = 0.50
        skill_match_score = min(100, int(round(skill_match_ratio * 100)))

        # 2. 20% Project Relevance (Semantic similarity with job title & description)
        target_context = f"{job_title}. {job_description}".strip()
        project_similarity = similarity_engine.compute_similarity(resume_projects, target_context)
        # If no explicit projects section found, use overall resume text
        if not resume_projects or len(resume_projects) == 0:
            project_similarity = similarity_engine.compute_similarity([resume_text[:2000]], target_context) * 0.85
        project_relevance_score = min(100, int(round(project_similarity * 100)))

        # 3. 15% Experience / Internship Relevance
        exp_similarity = similarity_engine.compute_similarity(resume_experience, target_context)
        if not resume_experience or len(resume_experience) == 0:
            exp_similarity = similarity_engine.compute_similarity([resume_text[:3000]], target_context) * 0.80
        experience_relevance_score = min(100, int(round(exp_similarity * 100)))

        # 4. 15% Resume Quality (Quantified achievements, section clarity, length)
        metrics_count = extract_metrics_count(resume_text)
        has_projects = len(resume_projects) > 0
        has_experience = len(resume_experience) > 0
        has_education = len(resume_education) > 0

        quality_points = 40 # Base
        quality_points += min(30, metrics_count * 6) # Up to 30 pts for 5+ metrics
        if has_projects: quality_points += 10
        if has_experience: quality_points += 10
        if has_education: quality_points += 10
        resume_quality_score = min(100, quality_points)

        # Weighted calculation
        overall_score = int(round(
            (skill_match_score * 0.50) +
            (project_relevance_score * 0.20) +
            (experience_relevance_score * 0.15) +
            (resume_quality_score * 0.15)
        ))
        overall_score = max(0, min(100, overall_score))

        # Category label assignment
        if overall_score >= 75:
            category_label = "Job-Ready"
        elif overall_score >= 50:
            category_label = "Intermediate"
        else:
            category_label = "Beginner"

        # AI-style analytical summary
        top_missing_str = ", ".join([m["name"] for m in missing_skills[:3]])
        if not top_missing_str:
            top_missing_str = "advanced niche frameworks"

        summary = (
            f"Your profile demonstrates a strong foundation with an overall score of {overall_score}/100 "
            f"({category_label}). You matched {len(matched_skills)} of {len(target_skills)} primary market skills "
            f"yielding a {skill_match_score}% weighted skill alignment. To maximize recruiter callbacks for '{job_title}', "
            f"focus on closing critical high-demand gaps in: {top_missing_str}."
        )

        # Radar Category Metrics
        radar_metrics = cls._calculate_radar(matched_skills, missing_skills, skill_match_score)

        return {
            "matchedSkills": matched_skills,
            "missingSkills": missing_skills,
            "extraSkills": extra_skills,
            "scores": {
                "overall": overall_score,
                "skillMatchScore": skill_match_score,
                "projectRelevanceScore": project_relevance_score,
                "experienceRelevanceScore": experience_relevance_score,
                "resumeQualityScore": resume_quality_score,
            },
            "categoryLabel": category_label,
            "summary": summary,
            "radarMetrics": radar_metrics,
        }

    @staticmethod
    def _calculate_radar(matched: List[Dict], missing: List[Dict], base_skill_score: int) -> List[Dict[str, Any]]:
        categories = [
            "Programming Languages",
            "Web Frameworks",
            "Databases",
            "Cloud & DevOps",
            "Soft Skills"
        ]
        radar = []
        for cat in categories:
            cat_matched = sum(1 for m in matched if m.get("category") == cat)
            cat_missing = sum(1 for m in missing if m.get("category") == cat)
            total = cat_matched + cat_missing
            if total > 0:
                score = int(round((cat_matched / total) * 100))
            else:
                score = max(35, min(90, base_skill_score + 5))
            radar.append({
                "category": cat,
                "resumeScore": score,
                "marketBenchmark": 80
            })
        return radar

