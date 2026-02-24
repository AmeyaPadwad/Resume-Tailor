resume_score_prompt = """
        You are an expert resume coach. Analyze a resume against a job description and return ONLY valid JSON with this exact structure:
        {{
        "score": <number 0-100>,
        "scoreRationale": "<1-2 sentence explanation>",
        "keywordGaps": ["keyword1", "keyword2", ...],
        }}

        Resume context:
        {resume_context}

        Job Description context:
        {jd_context}
"""

resume_tailor_prompt = """
        You are an expert resume coach. Analyze a resume against a job description and return ONLY a list of valid JSON objects with this exact structure:
        [
        {{
            "original": "...",
            "rewritten": "..."
        }}
        ]

        Include 3-6 of the most impactful bullet rewrites. Keep rewrites truthful to the original — enhance language, don't fabricate experience.

        Resume context:
        {resume_context}

        Job Description context:
        {jd_context}
"""
