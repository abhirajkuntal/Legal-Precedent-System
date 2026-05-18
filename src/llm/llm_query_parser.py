import json

import ollama


class LLMQueryParser:

    def __init__(
        self,
        model_name="qwen2.5:7b"
    ):

        self.model_name = model_name

    def parse_query(
        self,
        query
    ):

        prompt = f"""
You are a legal query parser.

Extract the following fields from the legal search query:

- semantic_query
- court
- jurisdiction
- judge
- category

Return ONLY valid JSON.

If a field is missing, return null.

Example:

{{
    "semantic_query": "fiduciary duty breach",
    "court": "Delaware Court of Chancery",
    "jurisdiction": "Delaware",
    "judge": "Jacobs",
    "category": "Corporate Law"
}}

Legal query:
{query}
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

            parsed = json.loads(content)

            return parsed

        except Exception:

            return {
                "semantic_query": query,
                "court": None,
                "jurisdiction": None,
                "judge": None,
                "category": None
            }
