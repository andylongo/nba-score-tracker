import json
from datetime import datetime
import os
import re
import requests
import pytz
import winsound
import time
import threading
from bs4 import BeautifulSoup

class SportsScoreTracker:
    def __init__(self):
        """Initialize the score tracker."""
        self.scores_file = 'scores.json'
        self.scores = self.load_scores()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.nba_halftime_averages = {}  # Cache for NBA halftime averages
        self.nba_second_half_averages = {}  # Cache for NBA second half averages
        self.last_averages_update = None
        # ANSI escape codes for text formatting
        self.BOLD = '\033[1m'
        self.END = '\033[0m'
        
        # NBA team name mappings (ESPN names to teamrankings.com city names)
        self.nba_team_mappings = {
            'Hawks': 'Atlanta',
            'Celtics': 'Boston',
            'Nets': 'Brooklyn',
            'Hornets': 'Charlotte',
            'Bulls': 'Chicago',
            'Cavaliers': 'Cleveland',
            'Mavericks': 'Dallas',
            'Nuggets': 'Denver',
            'Pistons': 'Detroit',
            'Warriors': 'Golden State',
            'Rockets': 'Houston',
            'Pacers': 'Indiana',
            'Clippers': 'LA Clippers',
            'Lakers': 'LA Lakers',
            'Grizzlies': 'Memphis',
            'Heat': 'Miami',
            'Bucks': 'Milwaukee',
            'Timberwolves': 'Minnesota',
            'Pelicans': 'New Orleans',
            'Knicks': 'New York',
            'Thunder': 'Okla City',
            'Magic': 'Orlando',
            '76ers': 'Philadelphia',
            'Suns': 'Phoenix',
            'Trail Blazers': 'Portland',
            'Kings': 'Sacramento',
            'Spurs': 'San Antonio',
            'Raptors': 'Toronto',
            'Jazz': 'Utah',
            'Wizards': 'Washington'
        }
        self.update_nba_halftime_averages()  # Initial fetch of averages

    def update_nba_halftime_averages(self):
        """Fetch NBA team halftime scoring averages from teamrankings.com"""
        try:
            print("Fetching NBA halftime averages...")
            url = "https://www.teamrankings.com/nba/stat/1st-half-points-per-game"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find any table with the tr-table class
            table = soup.find('table', {'class': 'tr-table'})
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:  # Make sure we have enough columns
                        team_name = cols[1].text.strip()
                        try:
                            avg_score = float(cols[2].text.strip())
                            self.nba_halftime_averages[team_name] = avg_score
                            print(f"Added {team_name}: {avg_score}")
                        except ValueError as e:
                            print(f"Error parsing score for {team_name}: {e}")
                
                self.last_averages_update = datetime.now()
                print(f"Updated NBA halftime averages. Found {len(self.nba_halftime_averages)} teams.")
                
                # Debug: print all team names in our averages
                print("\nTeam names in averages:")
                for team in sorted(self.nba_halftime_averages.keys()):
                    print(f"  {team}")
            else:
                print("Error: Could not find stats table")
                print("Available tables:", [t.get('class', ['no-class']) for t in soup.find_all('table')])
        except Exception as e:
            print(f"Error updating NBA halftime averages: {str(e)}")
            if 'response' in locals():
                print(f"Response status: {response.status_code}")
                print(f"Response content: {response.text[:500]}...")  # Print first 500 chars

        try:
            print("Fetching NBA second half averages...")
            url = "https://www.teamrankings.com/nba/stat/2nd-half-points-per-game"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find any table with the tr-table class
            table = soup.find('table', {'class': 'tr-table'})
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:  # Make sure we have enough columns
                        team_name = cols[1].text.strip()
                        try:
                            avg_score = float(cols[2].text.strip())
                            self.nba_second_half_averages[team_name] = avg_score
                            print(f"Added {team_name}: {avg_score}")
                        except ValueError as e:
                            print(f"Error parsing score for {team_name}: {e}")
                
                print(f"Updated NBA second half averages. Found {len(self.nba_second_half_averages)} teams.")
                
                # Debug: print all team names in our averages
                print("\nTeam names in averages:")
                for team in sorted(self.nba_second_half_averages.keys()):
                    print(f"  {team}")
            else:
                print("Error: Could not find stats table")
                print("Available tables:", [t.get('class', ['no-class']) for t in soup.find_all('table')])
        except Exception as e:
            print(f"Error updating NBA second half averages: {str(e)}")
            if 'response' in locals():
                print(f"Response status: {response.status_code}")
                print(f"Response content: {response.text[:500]}...")  # Print first 500 chars

    def get_team_stats(self, team_id, second_half=False):
        """Get team's average halftime score."""
        try:
            # Update averages once per hour
            if (not self.last_averages_update or 
                (datetime.now() - self.last_averages_update).total_seconds() > 3600):
                self.update_nba_halftime_averages()
            
            # Get team name from ESPN data
            team_name = None
            
            # First try to find by team ID mapping
            team_id_mappings = {
                '1': 'Hawks',
                '2': 'Celtics',
                '3': 'Nets',
                '4': 'Hornets',
                '5': 'Bulls',
                '6': 'Cavaliers',
                '7': 'Mavericks',
                '8': 'Nuggets',
                '9': 'Pistons',
                '10': 'Warriors',
                '11': 'Rockets',
                '12': 'Pacers',
                '13': 'Clippers',
                '14': 'Lakers',
                '15': 'Grizzlies',
                '16': 'Heat',
                '17': 'Bucks',
                '18': 'Timberwolves',
                '19': 'Pelicans',
                '20': 'Knicks',
                '21': 'Thunder',
                '22': 'Magic',
                '23': '76ers',
                '24': 'Suns',
                '25': 'Trail Blazers',
                '26': 'Kings',
                '27': 'Spurs',
                '28': 'Raptors',
                '29': 'Jazz',
                '30': 'Wizards'
            }
            
            # Try to get team name from ID first
            if team_id in team_id_mappings:
                team_name = self.nba_team_mappings[team_id_mappings[team_id]]
            else:
                # Fallback to searching by name
                for key in self.nba_team_mappings.keys():
                    if key.lower() in team_id.lower():
                        team_name = self.nba_team_mappings[key]
                        break
            
            if not team_name:
                print(f"Could not find mapping for team ID: {team_id}")
                return None
            
            # Try to find the team in our averages
            if second_half:
                if team_name in self.nba_second_half_averages:
                    return self.nba_second_half_averages[team_name]
            else:
                if team_name in self.nba_halftime_averages:
                    return self.nba_halftime_averages[team_name]
                
            print(f"Could not find stats for team: {team_name}")
            return None
        except Exception as e:
            print(f"Error getting team stats: {str(e)}")
            return None

    def analyze_performance(self, current_score, avg_score_per_game):
        """Compare current score with average scoring."""
        if not avg_score_per_game:
            return "⚪"  # Grey circle for no data

        current_score = float(current_score)
        expected_score = float(avg_score_per_game)
        diff_percentage = ((current_score - expected_score) / expected_score) * 100
        
        if diff_percentage >= 5:
            return "🔥"  # Fire for hot
        elif diff_percentage <= -5:
            return "❄️"  # Snowflake for cold
        return "➖"  # Dash for average

    def get_halftime_score(self, competitor):
        """Get the halftime score for a team."""
        try:
            if 'linescores' in competitor and len(competitor['linescores']) >= 2:
                return sum(float(score.get('value', 0)) for score in competitor['linescores'][:2])
        except Exception as e:
            print(f"Error getting halftime score: {str(e)}")
        return None

    def monitor_scores(self):
        """Continuously monitor NBA halftime scores."""
        print("\nMonitoring NBA Halftime Scores...")
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        
        while True:
            try:
                try:
                    response = requests.get('https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard')
                    data = response.json()

                    if 'events' in data:
                        # Filter games that have reached at least halftime
                        live_games = []
                        completed_games = []
                        
                        for event in data['events']:
                            if ('competitions' in event and len(event['competitions']) > 0 and
                                'competitors' in event['competitions'][0] and
                                len(event['competitions'][0]['competitors']) >= 2):
                                
                                home_team = event['competitions'][0]['competitors'][0]
                                away_team = event['competitions'][0]['competitors'][1]
                                
                                # Get halftime scores
                                home_halftime = self.get_halftime_score(home_team)
                                away_halftime = self.get_halftime_score(away_team)
                                
                                if home_halftime is not None and away_halftime is not None:
                                    game_info = {
                                        'event': event,
                                        'home_team': home_team,
                                        'away_team': away_team,
                                        'home_halftime': home_halftime,
                                        'away_halftime': away_halftime
                                    }
                                    
                                    if event['status']['type']['state'] == 'post':
                                        completed_games.append(game_info)
                                    else:
                                        live_games.append(game_info)
                        
                        games_found = False
                        
                        # Display live games first
                        if live_games:
                            print("\nNBA Live Games (Halftime Scores):")
                            print("-" * 50)
                            games_found = True
                            
                            for game in live_games:
                                event = game['event']
                                home_team = game['home_team']
                                away_team = game['away_team']
                                
                                # Get performance analysis for both teams
                                home_stats = self.get_team_stats(home_team['team']['id'])
                                away_stats = self.get_team_stats(away_team['team']['id'])
                                home_perf = self.analyze_performance(game['home_halftime'], home_stats)
                                away_perf = self.analyze_performance(game['away_halftime'], away_stats)
                                
                                game_status = event['status']['type']['detail']
                                game_line = f"{away_team['team']['name']} {game['away_halftime']} {away_perf} @ {home_team['team']['name']} {game['home_halftime']} {home_perf} - {game_status}"
                                
                                # Highlight if both teams are hot or both are cold
                                if (home_perf == "🔥" and away_perf == "🔥") or (home_perf == "❄️" and away_perf == "❄️"):
                                    game_line = f"{self.BOLD}{game_line}{self.END}"
                                
                                print(game_line)
                        
                        # Then display completed games
                        if completed_games:
                            if live_games:  # Add extra line between sections if we have both
                                print("")
                            print("\nCompleted Games (Halftime Scores):")
                            print("-" * 50)
                            games_found = True
                            
                            for game in completed_games:
                                event = game['event']
                                home_team = game['home_team']
                                away_team = game['away_team']
                                
                                # For completed games, show both halftime and second half performance
                                home_final = float(home_team.get('score', 0))
                                away_final = float(away_team.get('score', 0))
                                home_halftime = float(game['home_halftime'])
                                away_halftime = float(game['away_halftime'])
                                
                                # Calculate second half scores
                                home_second_half = home_final - home_halftime
                                away_second_half = away_final - away_halftime
                                
                                # Get performance for both halves
                                home_first_perf = self.analyze_performance(
                                    home_halftime, 
                                    self.get_team_stats(home_team['team']['id'])
                                )
                                away_first_perf = self.analyze_performance(
                                    away_halftime, 
                                    self.get_team_stats(away_team['team']['id'])
                                )
                                home_second_perf = self.analyze_performance(
                                    home_second_half, 
                                    self.get_team_stats(home_team['team']['id'], second_half=True)
                                )
                                away_second_perf = self.analyze_performance(
                                    away_second_half, 
                                    self.get_team_stats(away_team['team']['id'], second_half=True)
                                )
                                
                                game_line = (
                                    f"{away_team['team']['name']} {away_halftime}/{away_second_half} "
                                    f"{away_first_perf}/{away_second_perf} @ "
                                    f"{home_team['team']['name']} {home_halftime}/{home_second_half} "
                                    f"{home_first_perf}/{home_second_perf} - FINAL"
                                )
                                
                                # Highlight if both teams are hot or both are cold in either half
                                if ((home_first_perf == "🔥" and away_first_perf == "🔥") or 
                                    (home_first_perf == "❄️" and away_first_perf == "❄️") or
                                    (home_second_perf == "🔥" and away_second_perf == "🔥") or 
                                    (home_second_perf == "❄️" and away_second_perf == "❄️")):
                                    game_line = f"{self.BOLD}{game_line}{self.END}"
                                
                                print(game_line)
                            
                        if not games_found:
                            print("\nNo NBA games with halftime scores available")
                    
                except Exception as e:
                    print(f"Error fetching NBA scores: {str(e)}")
                
                print("\nPress Ctrl+C to exit")
                print(f"\nLast updated: {datetime.now().strftime('%I:%M:%S %p')}")
                time.sleep(30)  # Wait 30 seconds before next update
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen for next update
                
            except KeyboardInterrupt:
                print("\nStopping score monitoring...")
                break

    def load_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

if __name__ == "__main__":
    tracker = SportsScoreTracker()
    tracker.monitor_scores()
