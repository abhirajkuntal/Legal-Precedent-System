from sumy.parsers.plaintext import (
    PlaintextParser
)

from sumy.nlp.tokenizers import (
    Tokenizer
)

from sumy.summarizers.lsa import (
    LsaSummarizer
)


class LegalSummarizer:

    def __init__(self):

        self.summarizer = LsaSummarizer()

    def summarize(
        self,
        text,
        sentence_count=3
    ):

        if not text.strip():
            return ""

        parser = PlaintextParser.from_string(
            text,
            Tokenizer("english")
        )

        summary = self.summarizer(
            parser.document,
            sentence_count
        )

        return " ".join(
            str(sentence)
            for sentence in summary
        )
