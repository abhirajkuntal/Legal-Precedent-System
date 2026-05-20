import json
import time
import ollama

class LegalCaseAnalyzer:

    def __init__(
        self,
        model_name="qwen2.5:7b"
    ):

        self.model_name = model_name

    def analyze_case(
        self,
        chunk_text

    ):

        prompt = f"""
You are an expert legal analyst.

Analyze the following legal case excerpt.

Extract:

1. legal_issue
2. holding
3. procedural_posture
4. reasoning

Return ONLY valid JSON.

Do not use markdown.
Do not explain.
Do not wrap in ```json.

Example:

{{
    "legal_issue":
        "Whether misuse of confidential information constitutes breach of fiduciary duty.",

    "holding":
        "The court held that misuse of confidential information may constitute a breach of fiduciary duty.",

    "procedural_posture":
        "Appeal from lower court dismissal.",

    "reasoning":
        "Employees owe fiduciary duties regarding confidential corporate information."
}}

Case excerpt:

{chunk_text[:1000]}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = (
            response["message"]["content"]
        )


        try:

            content = content.strip()

            if "```json" in content:

                content = (
                    content
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            start = content.find("{")
            end = content.rfind("}") + 1

            content = content[start:end]

            parsed = json.loads(content)

            return parsed

        except Exception:

            return {
                "legal_issue": "",
                "holding": "",
                "procedural_posture": "",
                "reasoning": ""
            }
