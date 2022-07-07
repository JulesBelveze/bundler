import argparse

import pandas as pd
from sentence_transformers import SentenceTransformer
from umap import UMAP


def parse_args():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, default="paraphrase-MiniLM-L6-v2")
    parser.add_argument("--input-file", type=str)
    parser.add_argument("--output-file", type=str)
    return parser.parse_args()


def run(args):
    # Load the universal sentence encoder
    model = SentenceTransformer(args["model_name"])

    # Load original dataset
    df = pd.read_csv(args["input_file"])
    sentences = df["text"]

    # Calculate embeddings
    X = model.encode(sentences)

    # Reduce the dimensions with UMAP
    umap = UMAP()
    X_tfm = umap.fit_transform(X)

    # Apply coordinates
    df["x"] = X_tfm[:, 0]
    df["y"] = X_tfm[:, 1]

    df.to_csv(args["output_file"], index=False)


if __name__ == "__main__":
    args = parse_args()
    run(vars(args))
