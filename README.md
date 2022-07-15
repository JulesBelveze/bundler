<img src="figures/icon.png" width="25%" align="right"/>

# bundler

Bundler is a tool to help you gain insights from your dataset. Given 2D embeddings you can use the UI to either spot
wrong annotations or simply label samples per batch.

![](figures/screenshot.png)

# Install

You first need to clone the repo:

```
git clone https://github.com/JulesBelveze/bundler.git
```

Then download and install the package dependencies using [poetry](https://python-poetry.org/docs/):

```
python3 -m venv .venv/bundler
source .venv/bundler/bin/active
pip3 install --upgrade pip
poetry install
```

<details>
  <summary>To install poetry</summary>

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
```

</details>


## Disclaimer

The original tool from [koaning](https://github.com/koaning) can be found [here](https://github.com/koaning/bulk), but I
forked the project and kept working on a duplicate as our use cases were different.


## Usecase

The interface may help you label very quickly. It enables you to directly create tabs
on [Label Studio](https://labelstud.io/) to either correct or create labels.

As you might have noticed the tool was developed to handle textual data. However, it should be easily extendable to any
other data type.


## Usage

To use `bundler`, you first need to prepare your dataset to be mapped into a 2D embedding space.
You can find a couple of scripts under the `scripts/` folder on how to retrieve such coordinates.

Once your dataset is ready you can now open the UI and start exploring your data by running:

```
python3 -m bundler text [MY_FILE]
```

Note that one of the main feature of `bundler` is to be able to create tabs directly in Label Studio. However, to do so
you need to authenticate and specify the project of interest. To do so run the following before running `bundler`:
```
export LS_TOKEN=<YOUR_LS_TOKEN>
export LS_ENDPOINT=<ENDPOINT_OF_YOUR_LS>
```

