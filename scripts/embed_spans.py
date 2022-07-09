import argparse
import json
import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from transformers import LukeTokenizer, LukeModel
from typing import Dict, List
from umap import UMAP

model_name = "studio-ousia/luke-base"
tokenizer = LukeTokenizer.from_pretrained(model_name)
model = LukeModel.from_pretrained(model_name)
model.eval()


def parse_args():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str)
    parser.add_argument("--output-file", type=str)
    return parser.parse_args()


def get_entities_embeddings(task: Dict) -> List[Dict]:
    """Retrieves entity embedding"""
    # This part is designed to handle span annotation from Label Studio.
    # However, it can be changed according to your data structure.
    text = task["data"]["text"]
    annotations = task["annotations"][0]["result"]

    entity_spans = []
    for entity in annotations:
        entity_spans.append((entity["value"]["start"], entity["value"]["end"]))

    if len(entity_spans) == 0:
        return []

    # Tokenizing and feeding the model
    encoding = tokenizer(text, entity_spans=entity_spans, add_prefix_space=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**encoding)
    entity_last_hidden_state = outputs.entity_last_hidden_state
    entity_last_hidden_state = entity_last_hidden_state.squeeze(0).tolist()

    embeddings = []
    for entity, embed in zip(annotations, entity_last_hidden_state):
        embeddings.append({
            "embedding": embed,
            "color": entity["value"]["labels"][0],
            "text": entity["value"]["text"],
            "entity_id": entity["id"],
            "sample_id": task["id"]
        })
    return embeddings


def run(args):
    with open(args["input_file"], "r") as reader:
        data = json.load(reader)

    all_embeddings = []
    for elt in tqdm(data, total=len(data)):
        try:
            all_embeddings.extend(get_entities_embeddings(elt))
        except Exception as e:
            import ipdb
            ipdb.set_trace()

    X = np.array([entity["embedding"] for entity in all_embeddings])
    umap = UMAP()
    X_tfm = umap.fit_transform(X)

    df = pd.DataFrame.from_records(all_embeddings, exclude=["embedding"])
    df["x"] = X_tfm[:, 0]
    df["y"] = X_tfm[:, 1]

    df.to_csv(args["output_file"], index=False)


if __name__ == "__main__":
    args = parse_args()
    run(vars(args))
