def score_card_style(origial_score, score_rationale):
    return f"""
                <div style="
                    background:#f8f9fb;
                    border-radius:12px;
                    padding:20px 24px;
                    margin-bottom:16px;
                    border: 1px solid #e0e4ea;
                ">
                    <p style="font-weight:600; font-size:1rem; margin:0 0 6px 0;">Match Score</p>
                    <div style="display:flex; align-items:center; gap:16px;">
                        <span style="font-size:3rem; font-weight:800; color:#E07B54; line-height:1;">
                            {origial_score}<span style="font-size:1.5rem;">%</span>
                        </span>
                        <p style="margin:0; color:#444; font-size:0.9rem; line-height:1.5;">
                            {score_rationale}
                        </p>
                    </div>
                </div>
                """


def keyword_gaps_pill_style(gap):
    return f"""<span style="
                        display:inline-block;
                        background:#FFF8E7;
                        border:1px solid #F0D080;
                        border-radius:999px;
                        padding:4px 14px;
                        margin:4px;
                        font-size:0.85rem;
                        color:#333;
                    ">{gap}</span>"""


def suggestions_style(original, rewritten):
    return f"""
                        <div style="
                            background:#FFF5F5;
                            border-left: 4px solid #E07B54;
                            border-radius:6px;
                            padding:12px 16px;
                            margin-bottom:8px;
                            font-size:0.88rem;
                            color:#333;
                        ">
                            <strong>Before:</strong> {original}
                        </div>
                        <div style="
                            background:#F0FAF4;
                            border-left: 4px solid #2E8B57;
                            border-radius:6px;
                            padding:12px 16px;
                            margin-bottom:20px;
                            font-size:0.88rem;
                            color:#333;
                        ">
                            <strong>After:</strong> {rewritten}
                        </div>
                        """
