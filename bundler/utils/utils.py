import base64
import io
import logging
from typing import Tuple, Optional, List

import bokeh.transform
import numpy as np
import pandas as pd
from PIL import Image
from bokeh.palettes import Magma256, magma
from bokeh.transform import linear_cmap, factor_cmap
from tqdm import tqdm

logger = logging.getLogger(__name__)


def label_filter(df: pd.DataFrame, values: List[float], is_label_float: bool):
    """
    Filters a DataFrame based on a color label, using either a range or a set of discrete values.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        values (List[float]): A list containing either two float values defining the range to filter by
                              if `is_label_float` is True, or a list of discrete values to filter by if
                              `is_label_float` is False.
        is_label_float (bool): A flag indicating whether the label is a float (True) to filter using a range
                               or not (False) to filter using discrete values.

    Returns:
        pd.DataFrame: A filtered DataFrame where the 'color' column values satisfy the specified conditions.
    """

    if is_label_float:
        min_val, max_val = values
        return df[(df["color"] > min_val) & (df["color"] < max_val)]
    else:
        return df[df["color"].isin(values)]


def get_color_mapping(df: pd.DataFrame) -> Tuple[Optional[bokeh.transform.transform], pd.DataFrame]:
    """
    Determines the appropriate color mapping for a DataFrame column and generates a color mapper.

    Args:
        df (pd.DataFrame): The DataFrame containing the 'color' column that needs a color mapping.

    Returns:
        Tuple[Optional[bokeh.transform.transform], pd.DataFrame]: A tuple where the first element is a color
            mapper (either a factor_cmap for categorical data or a linear_cmap for numerical data, or None if the
            'color' column is missing) and the second element is the DataFrame with potentially modified 'color'
            column to ensure compatibility with the color mapper.
    """

    if "color" not in df.columns:
        return None, df

    color_datatype = str(df["color"].dtype)
    if color_datatype == "object":
        df["color"] = df["color"].apply(
            lambda x: str(x) if not (type(x) == float and np.isnan(x)) else x
        )
        all_values = list(df["color"].dropna().unique())
        palette = magma(len(all_values))
        mapper = factor_cmap(
            field_name="color",
            palette=palette,
            factors=all_values,
            nan_color="grey"
        )
    elif color_datatype.startswith("float") or color_datatype.startswith("int"):
        all_values = df["color"].dropna().values
        mapper = linear_cmap(
            field_name="color",
            palette=Magma256,
            low=all_values.min(),
            high=all_values.max(),
            nan_color="grey"
        )
    else:
        raise TypeError(
            f"We currently only support the following type for 'color' column: 'int*', 'float*', 'object'. "
            f"Got {color_datatype}."
        )
    return mapper, df


def get_datatable_columns(df: pd.DataFrame) -> List[str]:
    """
    Generates a list of DataFrame column names filtered to exclude certain columns.

    Args:
        df (pd.DataFrame): The DataFrame from which to filter out specific columns.

    Returns:
        List[str]: A list of column names
    """

    columns = df.columns
    filtered_columns = []
    for c in columns:
        if c in ["x", "y", "path"] or c.startswith("Unnamed"):
            continue
        filtered_columns.append(c)
    return filtered_columns


def encode_image(path: str) -> str:
    """
    Encodes an image from a file or a URL into an HTML image tag with Base64 encoding.

    Args:
        path (str): The file system path or URL of the image to encode.

    Returns:
        str: An HTML image tag as a string with the image content encoded in Base64 if the path points to a
             file system resource, or an image tag with a URL source if the path is an HTTP URL.
    """

    if type(path) == str and path.startswith("http"):
        return f'<img style="object-fit: scale-down;" width="100%" height="100%" src="{path}">'
    else:
        try:
            with open(path, "rb") as image_file:
                img = Image.open(image_file)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=10)
                enc_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f'<img style="object-fit: scale-down;" width="100%" height="100%" src="data:image/jpeg;base64,{enc_str}">'
        except FileNotFoundError:
            logger.error(f"Could not find image {path}")
            return f'<img style="object-fit: scale-down;" width="100%" height="100%" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wYAAtMBwVI8FXgAAAAASUVORK5CYII=">'


def read_file(path: str, do_encoding: bool = True) \
        -> Tuple[bokeh.transform.transform, pd.DataFrame]:
    """
    Reads a CSV file into a DataFrame, assigns a color mapping, and conditionally encodes related images.

    Args:
        path (str): The file path to the CSV file to be read.
        do_encoding (bool, optional): Whether to encode associated images into the DataFrame. Defaults to True.

    Returns:
        Tuple[bokeh.transform.transform, pd.DataFrame]: A tuple where the first element is a color mapper generated
            by get_color_mapping, and the second element is the DataFrame with the CSV data and optionally with an
            additional 'image' column containing encoded image tags.
    """
    df = pd.read_csv(path)
    mapper, df = get_color_mapping(df)

    if do_encoding:
        thumbnail_paths = []
        for p in tqdm(df["path"], total=len(df["path"]), desc="Encoding Images"):
            thumbnail_paths.append(encode_image(p))
        df["image"] = thumbnail_paths

    return mapper, df
