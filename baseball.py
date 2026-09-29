import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from probability import (
    pitch_type_probabilities,
    whiff_probabilities
)

pitches = pd.read_csv("pitches.csv")
players = pd.read_csv("players.csv")

pitches.columns = pitches.columns.str.lower().str.strip()

pitches["pitch_type"] = (
    pitches["pitch_type"]
    .str.strip()
    .str.lower()
)

pitches["result"] = (
    pitches["result"]
    .str.strip()
    .str.lower()
)

print(pitches.head())

#Before generating reports, I added checks for duplicate pitch IDs,
#missing player identifiers, impossible values like unrealistic velocity readings,
#and unexpected categorical values.
#The goal was to prevent bad source data from silently affecting the scouting report.

def validate_data(df):

    if df["pitch_id"].duplicated().any():
        raise ValueError("Duplicate pitch IDs found.")

    if df["pitcher_id"].isna().any():
        raise ValueError("Missing pitcher IDs.")

    if not df["velocity"].between(50, 110).all():
        print("Warning: unusual velocity detected.")

    valid_pitch_types = {
        "fastball",
        "slider",
        "changeup",
        "curveball"
    }

    invalid = ~df["pitch_type"].isin(valid_pitch_types)

    if invalid.any():
        print("Unknown pitch type detected:")
        print(df.loc[invalid, "pitch_type"].unique())


validate_data(pitches)

import sqlite3

conn = sqlite3.connect("baseball.db")

pitches.to_sql(
    "pitches",
    conn,
    if_exists="replace",
    index=False
)

players.to_sql(
    "players",
    conn,
    if_exists="replace",
    index=False
)

query = """
SELECT
    p.pitch_id,
    pl.name AS pitcher_name,
    pl.throws,
    p.pitch_type,
    p.result,
    p.velocity,
    p.zone
FROM pitches p
JOIN players pl
    ON p.pitcher_id = pl.player_id
"""

data = pd.read_sql_query(query, conn)

print(data)

#pitch usage

pitch_usage = (
    data
    .groupby(["pitcher_name", "pitch_type"])
    .size()
    .reset_index(name="pitch_count")
)

total_pitches = (
    data
    .groupby("pitcher_name")
    .size()
    .reset_index(name="total_pitches")
)

pitch_usage = pitch_usage.merge(
    total_pitches,
    on="pitcher_name"
)

pitch_usage["usage_percent"] = (
    pitch_usage["pitch_count"]
    / pitch_usage["total_pitches"]
    * 100
)

print(pitch_usage)

#whiff rate
swing_results = [
    "swinging strike",
    "foul",
    "in play"
]

data["swing"] = (
    data["result"]
    .str.lower()
    .isin(swing_results)
)

data["whiff"] = (
    data["result"]
    .str.lower()
    .eq("swinging strike")
)
whiff_report = (
    data
    .groupby(["pitcher_name", "pitch_type"])
    .agg(
        swings=("swing", "sum"),
        whiffs=("whiff", "sum")
    )
    .reset_index()
)

whiff_report["whiff_rate"] = (
    whiff_report["whiffs"]
    .div(whiff_report["swings"])
    .fillna(0)
    * 100

)

print(whiff_report)

#average velocity

velocity_report = (
    data
    .groupby(["pitcher_name", "pitch_type"])
    ["velocity"]
    .mean()
    .reset_index()
)

velocity_report["velocity"] = (
    velocity_report["velocity"].round(1)
)

print(velocity_report)

#zone tendencies

data["in_zone"] = data["zone"].between(1, 9)

zone_report = (
    data
    .groupby(["pitcher_name", "pitch_type"])
    ["in_zone"]
    .mean()
    .reset_index()
)

zone_report["zone_percent"] = (
    zone_report["in_zone"] * 100
)

print(zone_report)

#combine

report = (
    pitch_usage
    .merge(
        whiff_report,
        on=["pitcher_name", "pitch_type"]
    )
    .merge(
        velocity_report,
        on=["pitcher_name", "pitch_type"]
    )
    .merge(
        zone_report[
            ["pitcher_name", "pitch_type", "zone_percent"]
        ],
        on=["pitcher_name", "pitch_type"]
    )
)

report["usage_percent"] = report["usage_percent"].round(1)
report["whiff_rate"] = report["whiff_rate"].round(1)
report["zone_percent"] = report["zone_percent"].round(1)

report = report[
    [
        "pitcher_name",
        "pitch_type",
        "pitch_count",
        "usage_percent",
        "velocity",
        "whiff_rate",
        "zone_percent"
    ]
]

print(report)

report.to_csv("scouting_report.csv", index=False)

print("\nScouting report saved to scouting_report.csv")

#automate

def generate_pitcher_report(pitcher):

    pitcher_report = report[
        report["pitcher_name"] == pitcher
    ]

    print("\nSCOUTING REPORT")
    print("-------------------------")
    print(pitcher_report.to_string(index=False))


generate_pitcher_report("John Smith")

john = report[
    report["pitcher_name"] == "John Smith"
]

plt.bar(
    john["pitch_type"],
    john["usage_percent"]
)

plt.title("John Smith Pitch Usage")
plt.xlabel("Pitch Type")
plt.ylabel("Usage Percentage")

plt.show()

print("\nPITCH TYPE PROBABILITIES")
print(
    pitch_type_probabilities(
        data,
        strikes=2,
        batter_side="L"
    )
)

print("\nWHIFF PROBABILITIES")
print(
    whiff_probabilities(data)
)