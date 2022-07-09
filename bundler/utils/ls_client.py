import logging
import os
import pandas as pd
import requests as requests
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()


class LabelStudioAuthenticationError(Exception):
    pass


class LabelStudioError(Exception):
    pass


class LabelStudioClient(object):
    def __init__(self):

        try:
            self.token = os.environ["LS_TOKEN"]
        except KeyError:
            raise LabelStudioAuthenticationError("Authentication token missing.")

        try:
            self.url = os.environ["LS_ENDPOINT"]
        except KeyError:
            raise LabelStudioError("Label studio endpoint is missing.")

        self.headers = {"Authorization": f"Token {self.token}"}

    def create_tab(self, df: pd.DataFrame, name: str) -> None:
        """"""
        projects = defaultdict(list)
        for _, row in df.iterrows():
            projects[row.project].append(row.id)

        url = f"{self.url}/api/dm/views/"
        for project, ids in projects.items():
            query = {
                "data": {
                    "type": "list",
                    "target": "tasks",
                    "gridWidth": 4,
                    "columnsWidth": {},
                    "hiddenColumns": {
                        "explore": [
                            "tasks:inner_id",
                            "tasks:annotations_results",
                            "tasks:annotations_ids",
                            "tasks:predictions_score",
                            "tasks:predictions_model_versions",
                            "tasks:predictions_results",
                            "tasks:file_upload",
                            "tasks:created_at",
                            "tasks:updated_at",
                            "tasks:updated_by",
                            "tasks:avg_lead_time"
                        ],
                        "labeling": [
                            "tasks:id",
                            "tasks:inner_id",
                            "tasks:completed_at",
                            "tasks:cancelled_annotations",
                            "tasks:total_predictions",
                            "tasks:annotators",
                            "tasks:annotations_results",
                            "tasks:annotations_ids",
                            "tasks:predictions_score",
                            "tasks:predictions_model_versions",
                            "tasks:predictions_results",
                            "tasks:file_upload",
                            "tasks:created_at",
                            "tasks:updated_at",
                            "tasks:updated_by",
                            "tasks:avg_lead_time"
                        ]
                    },
                    "columnsDisplayType": {}
                },
                "project": project,
                "user": 5
            }
            if len(ids) <= 100:
                query["data"]["title"] = name
                query["data"]["filters"] = {
                    "conjunction": "or",
                    "items": [
                        {
                            "filter": "filter:tasks:id",
                            "operator": "equal",
                            "type": "Number",
                            "value": idx
                        } for idx in ids
                    ]

                }
                r = requests.post(url, json=query, headers=self.headers)
                try:
                    assert r.status_code == 201
                    logging.info(f"Tab {name} has been created.")
                except AssertionError:
                    logging.error(f"Upload aborted:\n{r.json()}")
            else:
                for i, offset in enumerate(range(0, len(ids), 100)):
                    batch = ids[offset: offset + 100]

                    query["data"]["title"] = f"{name} - {i}"
                    query["data"]["filters"] = {
                        "conjunction": "or",
                        "items": [
                            {
                                "filter": "filter:tasks:id",
                                "operator": "equal",
                                "type": "Number",
                                "value": idx
                            } for idx in batch
                        ]

                    }

                    r = requests.post(url, json=query, headers=self.headers)
                    try:
                        assert r.status_code == 201
                        logging.info(f"Tab {name} has been created.")
                    except AssertionError:
                        logging.error(f"Upload aborted:\n{r.json()}")
