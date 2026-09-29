# Baseball Scouting Analytics

A Python-based baseball analytics project that processes pitch-level data, stores it in a SQL database, and generates scouting insights for pitchers.

## Overview

This project was built to turn raw baseball tracking data into useful scouting information.

The pipeline:

1. Loads pitch-level and player data from CSV files
2. Cleans and validates the data using Pandas
3. Stores the cleaned data in SQLite
4. Joins pitch and player data using SQL
5. Calculates scouting metrics
6. Generates automated reports and visualizations
7. Performs probability-based analysis for decision-making

## Current Features

- Pitch usage percentage
- Average pitch velocity
- Whiff rate
- Zone percentage
- Data validation
- SQL joins between pitch and player data
- Automated scouting reports
- CSV report export
- Pitch usage visualizations
- Pitch type probability analysis
- Whiff probability analysis

## Technologies Used

- Python
- Pandas
- SQLite
- SQL
- Matplotlib

## Project Structure

```text
baseball-scouting-analytics/
│
├── baseball.py
├── probability.py
├── pitches.csv
├── players.csv
└── README.md