import argparse
import pandas as pd
import pingouin
import sklearn

BEHAVIORS_COHENS_KAPPA = [
    "approach speaker",
    "move away",
    "out of sight",
    "raise head - looking at speaker",
    "run away",
]

DURATIONS_ICC = [
    "latency to move away duration relative",
    "latency to look duration relative",
    "raise head - looking at speaker duration relative",
]


def main():
    parser = argparse.ArgumentParser(description="Calculate the cohens kappa score for behavior counts")
    parser.add_argument("left")
    parser.add_argument("right")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    left, right = load_data(args.left, args.right)

    # Calculate cohen kappa scores
    cohen_scores = {}
    for beh in BEHAVIORS_COHENS_KAPPA:
        col_left = left[beh].apply(lambda x: x > 0)
        col_right = right[beh].apply(lambda x: x > 0)
        cohen_scores[beh] = sklearn.metrics.cohen_kappa_score(col_left, col_right)

    # Calculate ICCs, but create a df that pingouin can work with
    concatenated = pd.concat([left, right], keys=["left", "right"], names=["rater"]).reset_index()
    icc_scores = {}
    for dur in DURATIONS_ICC:
        iccs = pingouin.intraclass_corr(concatenated, targets="uid", raters="rater", ratings=dur)
        icc_scores[dur] = iccs.iloc[1]["ICC"]  # pingouin calculates much more, take only ICC2

    # create dfs for export
    cohens_df = pd.DataFrame.from_dict(cohen_scores, orient="index", columns=["cohens kappa score"])
    icc_df = pd.DataFrame.from_dict(icc_scores, orient="index", columns=["ICC2"])
    result = pd.concat([cohens_df, icc_df])
    print(result)

    if args.output is not None:
        result.to_excel(args.output)


def load_data(left, right):
    left = pd.read_excel(left).set_index("uid")
    right = pd.read_excel(right).set_index("uid")

    common_observations = left.index.intersection(right.index)
    return (left.loc[common_observations], right.loc[common_observations])


if __name__ == "__main__":
    main()
