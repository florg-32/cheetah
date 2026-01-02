import pandas as pd
import os
import argparse

AGGREGATED_EVENTS_PATH = "aggregated events 60sec.xlsx"
OBSERVER_METADATA_PATH = "playback_plan_BORIS_blind_coding.xlsx"

POST_PLAYBACK_DURATIONS_PATH = "playback_plan_BORIS_looking_durations.xlsx"
STIMULUS_DATA_PATH = "playback_plan_filled_out.xlsx"


def main():
    parser = argparse.ArgumentParser(description="Combine annotation exports with playback plan and metadata")
    parser.add_argument("general_metadata", help=f"path to the folder containing {POST_PLAYBACK_DURATIONS_PATH} and {STIMULUS_DATA_PATH}")
    parser.add_argument("observer_data", help=f"path to the individual observers {AGGREGATED_EVENTS_PATH} and {OBSERVER_METADATA_PATH}")
    parser.add_argument("-o", "--output", help="output file", default="merged.xlsx")
    args = parser.parse_args()

    aggregated_events_path = os.path.join(args.observer_data, AGGREGATED_EVENTS_PATH)
    post_playback_path = os.path.join(args.general_metadata, POST_PLAYBACK_DURATIONS_PATH)
    stimulus_data_path = os.path.join(args.general_metadata, STIMULUS_DATA_PATH)
    observer_metadata_path = os.path.join(args.observer_data, OBSERVER_METADATA_PATH)

    aggregated_events = pd.read_excel(aggregated_events_path)
    aggregated_events = aggregated_events.pipe(with_uid).pipe(remove_events_without_subject)

    post_playback_durations = pd.read_excel(post_playback_path)
    post_playback_durations = extract_post_playback_durations(post_playback_durations)

    duration_columns = ["latency to look", "latency to move away", "raise head - looking at speaker", "out of sight"]
    behavior_durations = accumulate_behavior_durations_with_post_playback_time(
        aggregated_events, post_playback_durations, duration_columns
    )
    behavior_counts = count_behaviors(aggregated_events)

    stimulus_data = pd.read_excel(stimulus_data_path)
    stimulus_data = extract_stimulus_data(stimulus_data)

    metadata = pd.read_excel(observer_metadata_path)
    metadata = extract_metadata(metadata)

    result = (
        behavior_counts.join(behavior_durations)
        .join(stimulus_data, validate="1:m")
        .join(metadata["unspecific"], validate="1:m")
        .join(metadata["focal_specific"], validate="1:1")
    )
    print(result)
    result.to_excel(args.output)


def with_uid(df: pd.DataFrame) -> pd.DataFrame:
    df["uid"] = df["Observation id"].str.cat(df["Subject"], sep="-")
    return df


def remove_events_without_subject(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["Subject"] != "No focal subject"]


def extract_post_playback_durations(df: pd.DataFrame) -> pd.DataFrame:
    focals = [
        ("coding duration f1 60sec", "Focal 1"),
        ("coding duration f2 60sec", "Focal 2"),
        ("coding duration f3 60sec", "Focal 3"),
    ]

    result = []
    for _, row in df.iterrows():
        for col, label in focals:
            value = str(row[col]).strip()
            if not value or value == "/":
                continue
            duration = float(value.replace(",", "."))
            result.append({"uid": f"{row['Observation id']}-{label}", "post playback duration": duration})

    return pd.DataFrame(result).set_index("uid")


# Sum up the behavior durations
def accumulate_behavior_durations_with_post_playback_time(
    behaviors: pd.DataFrame, post_playback_durations: pd.DataFrame, duration_columns
) -> pd.DataFrame:
    interesting_behaviors = behaviors[behaviors["Behavior"].isin(duration_columns)]

    # Create columns for each unique behavior, taking the sum of durations for each behavior per uid
    behavior_durations = interesting_behaviors.pivot_table(
        index=["uid", "Observation id"], columns="Behavior", aggfunc="sum", values="Duration (s)", fill_value=0.0
    )

    # Combine it with the coding durations and calculate the relative durations
    behavior_durations = behavior_durations.join(post_playback_durations)
    for col in duration_columns:
        behavior_durations[f"{col} duration relative"] = (
            behavior_durations[col] / behavior_durations["post playback duration"]
        )
        behavior_durations.rename(columns={col: f"{col} duration absolute"}, inplace=True)

    return behavior_durations


# Count the behaviors
def count_behaviors(df: pd.DataFrame) -> pd.DataFrame:
    # Create columns for each unique behavior, then keep the number merged behaviors for each uid (size)
    return df.pivot_table(index=["uid", "Observation id"], columns="Behavior", aggfunc="size", fill_value=0)


def extract_stimulus_data(df: pd.DataFrame) -> pd.DataFrame:
    # First we need to recreate the observation id from the experiment number and date columns
    padded_experiment_number = df["experiment number"].astype(str).str.zfill(2)
    df["Observation id"] = padded_experiment_number.str.cat(df["date"].dt.strftime("%d.%m.%Y"), sep="_")

    df.set_index("Observation id", inplace=True)
    return df[["stim. cat.", "stimulus"]]


def extract_metadata(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    # These need to be merged onto all observations
    unspecific_columns = [
        "experiment number",
        "date",
        "time",
        "location (latitude)",
        "location (longitude)",
        "groupsize category",
        "other species present",
        "group comp.",
        "habitat",
        "group 30sec-looking",
        "group 30sec-moving",
        "species",
        "temp",
        "wind",
        "dist. to speaker",
        "car side",
    ]

    # This function will extract the relevant columns for subject n
    def focal_specific(df, n):
        translation = {f"focal {n}": "sex", f"f{n} move of": "move of distance"}
        df = df[translation.keys()]
        df = df.rename(columns=translation)
        df = df[df["sex"] != "/"]
        df = df.dropna()
        df["Subject"] = f"Focal {n}"
        return df

    # Create a single table with the extracted specifics for focals 1 to 3 (the end of range is exclusive)
    df.set_index("Observation id", inplace=True)
    focal_metadata = pd.concat([focal_specific(df, n) for n in range(1, 4)]).reset_index()
    focal_metadata["uid"] = focal_metadata["Observation id"].str.cat(focal_metadata["Subject"], sep="-")

    return {"unspecific": df[unspecific_columns], "focal_specific": focal_metadata.set_index("uid")}


if __name__ == "__main__":
    main()
