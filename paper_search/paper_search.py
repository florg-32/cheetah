import itertools
import polars as pl
import sys
import os
import functools
import warnings
from tqdm import tqdm


def main():
    warnings.filterwarnings("ignore", message="Could not determine dtype")
    try: 
        os.mkdir("output")
    except:  # noqa: E722
        pass

    samples = [f"{sys.argv[1]}/" + p for p in os.listdir(sys.argv[1])]
    
    combined = functools.reduce(join, map(load_search, tqdm(samples)))
    combined.write_csv("output/combined.csv")

    samples.sort()
    samples = itertools.groupby(samples, lambda s: s.split('_')[0])

    for s in tqdm(samples):
        reduced = functools.reduce(join, map(load_search, s[1]))
        species = s[0].rsplit('/')[-1]
        reduced.write_csv(f"output/{species}.csv")



def join_reduce(files) -> pl.DataFrame:
    first = load_search(files[0])
    for f in map(load_search, files[1:]):
        first = join(first, f)
    return first


def join(left: pl.DataFrame, right=None) -> pl.DataFrame:
    if right is None:
        return left

    joined = left.join(right, on=pl.col("Title").str.to_lowercase().str.strip_chars('"'), how="full")
    return joined.select(
        [
            pl.coalesce(["Authors", "Authors_right"]),
            pl.coalesce(["Title", "Title_right"]),
            pl.coalesce(["DOI", "DOI_right"]),
            pl.coalesce(["Year", "Year_right"]),
            pl.concat_str(
                ["File", "File_right"],
                ignore_nulls=True,
                separator=",",
            ),
        ]
    )


def load_search(filename: str) -> pl.DataFrame:
    if filename.endswith(".csv"):
        df = load_scopus(filename)
    else:
        df = load_wos(filename)

    # dedup title
    df = df.with_columns(lowered=pl.col("Title").str.to_lowercase()).unique("lowered").drop("lowered")
    return df.with_columns(pl.lit(os.path.basename(filename)).alias("File"))


def load_scopus(filename: str) -> pl.DataFrame:
    df = pl.read_csv(filename)
    return df.select(["Authors", "Title", "DOI", "Year"])


def load_wos(filename: str) -> pl.DataFrame:
    df = pl.read_excel(filename, columns=["Authors", "Article Title", "DOI", "Publication Year"])
    return df.select(
        [
            "Authors",
            pl.col("Article Title").alias("Title"),
            "DOI",
            pl.col("Publication Year").alias("Year"),
        ]
    )


if __name__ == "__main__":
    main()
