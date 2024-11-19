# NBA Score Tracker

Real-time NBA score tracking system that monitors halftime and second-half performance.

## Features

- Live score updates every 30 seconds from ESPN API
- Performance indicators for both halftime and second-half scores
- Comparison against team averages from teamrankings.com
- Visual indicators for hot/cold performance (🔥/❄️)
- Bold highlighting for games where both teams are performing similarly

## Requirements

- Python 3.x
- Required packages:
  - requests
  - beautifulsoup4
  - datetime

## Installation

1. Clone this repository
2. Install required packages:
```bash
pip install requests beautifulsoup4
```

## Usage

Run the script:
```bash
python sports_scores.py
```

The program will display:
- Live games with current scores and performance
- Completed games with both halftime and second-half performance
- Performance indicators:
  - 🔥 Hot: Scoring 5% or more above average
  - ❄️ Cold: Scoring 5% or more below average
  - ➖ Average: Within ±5% of average
  - ⚪ No data available

## Data Sources

- Live scores: ESPN API
- Team averages: teamrankings.com
