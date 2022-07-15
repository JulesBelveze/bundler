# How-to guide

<hr>

Both `embed.py` and `embed_spans.py` are scripts to generate a 2D representation of a sample (or a span) from your Label
Studio annotations.

First you need to install some extra dependencies:
```
pip3 install umap-learn transformers tqdm
```

You now need to export your annotations from your Label Studio project. Then the only thing you need to do is run:
```
python3 -m bundler.scripts.embed_spans --input-file=<LS_ANNOTATIONS> --output-file=embeddings.csv
```
