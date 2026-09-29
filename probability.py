import pandas as pd
import sqlite3


def pitch_type_probabilities(data):
    probs = (
        data["pitch_type"]
        .value_counts(normalize=True)
        .reset_index()
    )

    probs.columns = ["pitch_type", "probability"]

    probs["probability"] = (
        probs["probability"] * 100
    ).round(1)

    return probs


def whiff_probabilities(data):
    data = data.copy()

    data["whiff"] = (
        data["result"]
        .str.lower()
        .eq("swinging strike")
    )

    report = (
        data
        .groupby("pitch_type")
        .agg(
            total_pitches=("pitch_type", "size"),
            whiffs=("whiff", "sum")
        )
        .reset_index()
    )

    report["whiff_probability"] = (
        report["whiffs"]
        / report["total_pitches"]
        * 100
    ).round(1)

    return report


if __name__ == "__main__":

    conn = sqlite3.connect("baseball.db")

    data = pd.read_sql_query("""
    SELECT
        p.pitch_id,
        pl.name AS pitcher_name,
        p.pitch_type,
        p.result,
        p.velocity,
        p.zone
    FROM pitches p
    JOIN players pl
        ON p.pitcher_id = pl.player_id
    """, conn)

    print("\nPITCH TYPE PROBABILITIES")
    print(pitch_type_probabilities(data))

    print("\nWHIFF PROBABILITIES")
    print(whiff_probabilities(data))