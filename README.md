<img src="lasso.svg" align="right" >

# bulk

Bulk is a quick developer tool to apply some bulk labels. Given a prepared dataset with 2d embeddings it can generate an interface that allows you to quickly add some bulk, albeit less precice, annotations.

![](screenshot.png)



# Install 

```
git clone https://github.com/JulesBelveze/bulk.git
```

## Disclaimer

The original tool from [koaning](https://github.com/koaning) can be found [here](https://github.com/koaning/bulk), but I forked the project and kept working on my fork as our use cases were different.

## Usage

To use bulk, you'll first need to prepare a csv file.

> **Note**
> The example below uses the [universal sentence encoder](https://tfhub.dev/google/universal-sentence-encoder/4) but you're
> totally free to use what-ever text embedding tool that you like.
> You may also enjoy [whatlies](https://koaning.github.io/whatlies/tutorial/scikit-learn/) or [sentence transformers](https://www.sbert.net/examples/applications/computing-embeddings/README.html). You will
> need to install these tools seperately.


```python
import pandas as pd
from umap import UMAP
from sentence_transformers import SentenceTransformer

# Load the universal sentence encoder
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Load original dataset
df = pd.read_csv("original.csv")

# Apply embeddings 
X = model.encode(df['text'])

# Reduce the dimensions with UMAP
umap = UMAP()
X_tfm = umap.fit_transform(X)

# Apply coordinates
df['x'] = X_tfm[:, 0]
df['y'] = X_tfm[:, 1]
df.to_csv("ready.csv")
```

You can now use this `ready.csv` file to apply some bulk labelling. 

```
python3 -m bulk text ready.csv
```

## Usecase 

The interface may help you label very quickly. It enables you to directly create tabs on Label Studio to either correct or create labels.
