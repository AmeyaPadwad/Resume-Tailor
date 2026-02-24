resume_score_prompt = """
        You are an expert resume coach. Analyze a resume against a job description.
        You must respond with ONLY a valid JSON object. No introduction, no explanation, no markdown, no text before or after the JSON.
        
        Structure of response:
        {{
        "score": <number 0-100>,
        "scoreRationale": "<1-2 sentence explanation>",
        "keywordGaps": ["keyword1", "keyword2", ...],
        "visaSponsorship": "<True or False>"
        }}
        
        For the visaSponsorship variable, mark it as False if the job description explicitly mentions no visa sponsorship, otherwise True.

        Resume context:
        {resume_context}

        Job Description context:
        {jd_context}
"""

resume_tailor_prompt = """
        You are an expert resume coach. Analyze a resume against a job description.

        You must respond with ONLY a valid JSON object array. No introduction, no explanation, no markdown, no text before or after the JSON.
        
        Structure of response:
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
