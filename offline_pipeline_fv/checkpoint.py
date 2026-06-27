import json

from offline_pipeline.config import CHECKPOINT_FILE


class PipelineCheckpoint:

    def __init__(self):

        self.state = {
            "processed_cases": 0,
            "embedding_shards": 0,
            "last_case_id": None,
            "finished_chunking": False,
            "finished_embedding": False,
            "finished_faiss": False,
            "finished_metadata": False
        }

        self.load()

    def load(self):

        if CHECKPOINT_FILE.exists():

            with open(
                CHECKPOINT_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                self.state = json.load(f)

    def save(self):

        with open(
            CHECKPOINT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.state,
                f,
                indent=4
            )

    def update(self, **kwargs):

        self.state.update(kwargs)

        self.save()
