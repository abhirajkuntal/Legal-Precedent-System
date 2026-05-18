from collections import Counter


class LegalAnswerGenerator:

    def __init__(self):

        pass

    def generate_answer(
        self,
        query,
        retrieved_results
    ):

        if not retrieved_results:

            return (
                "No relevant legal precedents found."
            )

        case_titles = []

        courts = []

        legal_issues = []

        holdings = []

        summaries = []

        for result in retrieved_results:

            chunk = result["chunk"]

            case_titles.append(
                chunk.case_title
            )

            courts.append(
                chunk.court
            )

            summary = result.get(
                "summary",
                ""
            )

            issue = result.get(
                "legal_issue",
                ""
            )

            holding = result.get(
                "holding",
                ""
            )

            if summary:
                summaries.append(summary)

            if issue:
                legal_issues.append(issue)

            if holding:
                holdings.append(holding)

        top_cases = (
            Counter(case_titles)
            .most_common(3)
        )

        top_courts = (
            Counter(courts)
            .most_common(3)
        )

        answer_parts = []

        answer_parts.append(
            f"LEGAL RESEARCH QUERY:\n{query}\n"
        )

        if legal_issues:

            answer_parts.append(
                "COMMON LEGAL ISSUES:\n"
            )

            for issue in legal_issues[:3]:

                answer_parts.append(
                    f"- {issue}"
                )

        if holdings:

            answer_parts.append(
                "\nKEY HOLDINGS:\n"
            )

            for holding in holdings[:3]:

                answer_parts.append(
                    f"- {holding}"
                )

        if summaries:

            answer_parts.append(
                "\nSUMMARY OF FINDINGS:\n"
            )

            for summary in summaries[:3]:

                answer_parts.append(
                    f"- {summary}"
                )

        answer_parts.append(
            "\nMOST RELEVANT CASES:\n"
        )

        for case, count in top_cases:

            answer_parts.append(
                f"- {case}"
            )

        answer_parts.append(
            "\nMOST RELEVANT COURTS:\n"
        )

        for court, count in top_courts:

            answer_parts.append(
                f"- {court}"
            )

        final_answer = "\n".join(
            answer_parts
        )

        return final_answer
