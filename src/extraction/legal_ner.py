import re
import spacy


class LegalNER:

    def __init__(self):

        self.nlp = spacy.load(
            "en_core_web_sm"
        )

    def extract_judges(
        self,
        text
    ):

        patterns = [
            r"Justice[\s,]+([A-Z][A-Za-z]+)",
            r"Judge[\s,]+([A-Z][A-Za-z]+)",
            r"Chief Justice[\s,]+([A-Z][A-Za-z]+)"
        ]

        judges = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            judges.extend(matches)

        return list(set(judges))

    def extract_courts(
        self,
        text
    ):

        patterns = [
            r"Supreme Court of [A-Za-z]+",
            r"Court of Chancery",
            r"Commonwealth Court of [A-Za-z]+",
            r"District Court",
            r"Court of Appeals",
            r"Superior Court"
        ]

        courts = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            courts.extend(matches)

        return list(set(courts))

    def extract_statutes(
        self,
        text
    ):

        patterns = [
            r"\d+\s+[A-Za-z\.]+\s+§\s*\d+",
            r"Section\s+\d+",
            r"\d+\s+Del\.\s+C\.\s+§\s*\d+"
        ]

        statutes = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            statutes.extend(matches)

        return list(set(statutes))

    def extract_entities(
        self,
        text
    ):

        doc = self.nlp(text)

        entities = {
            "persons": [],
            "organizations": [],
            "dates": [],
            "laws": [],
            "courts": [],
            "judges": []
        }

        for ent in doc.ents:

            if ent.label_ == "PERSON":

                entities["persons"].append(
                    ent.text
                )

            elif ent.label_ == "ORG":

                entities["organizations"].append(
                    ent.text
                )

            elif ent.label_ == "DATE":

                entities["dates"].append(
                    ent.text
                )

            elif ent.label_ == "LAW":

                entities["laws"].append(
                    ent.text
                )

        entities["judges"] = (
            self.extract_judges(text)
        )

        entities["courts"] = (
            self.extract_courts(text)
        )

        entities["laws"].extend(
            self.extract_statutes(text)
        )

        return {
            key: list(set(value))
            for key, value in entities.items()
        }
