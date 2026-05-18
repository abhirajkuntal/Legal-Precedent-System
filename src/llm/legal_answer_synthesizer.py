import ollama


class LegalAnswerSynthesizer:

    def __init__(
        self,
        model_name="qwen2.5:7b"
    ):

        self.model_name = model_name

    def synthesize(
        self,
        query,
        results
    ):

        context = ""

        for i, result in enumerate(results):

            context += f"""
CASE {i+1}

TITLE:
{result['chunk'].case_title}

LEGAL ISSUE:
{result.get('legal_issue', '')}

HOLDING:
{result.get('holding', '')}

REASONING:
{result.get('reasoning', '')}

--------------------------------
"""

        prompt = f"""
You are an expert legal research assistant.

Using the retrieved cases below,
answer the legal query.

Provide:
1. concise legal answer
2. overall rule/principle
3. important nuances
4. trends across courts if visible

Legal query:
{query}

Cases:
{context}

Provide a professional legal synthesis.
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2
            }
        )

        return response[
            "message"
        ]["content"]
