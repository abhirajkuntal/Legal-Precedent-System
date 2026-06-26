from src.schemas.case_metadata import CaseMetadata


class CaseMetadataBuilder:

    def build(self, cases):

        metadata = {}

        for case in cases:

            metadata[case.case_id] = CaseMetadata(
                case_id=case.case_id,
                title=case.title,
                court=case.court,
                jurisdiction=case.jurisdiction,
                judges=case.judges,
                head_matter=case.head_matter,
                opinion_text=case.opinion_text,
                pagerank=case.pagerank
            )

        return metadata
