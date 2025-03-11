import streamlit as st
import pandas as pd

def balance_teams(players, num_teams):
    # Separate players by gender
    males = [player for player in players if player[2].lower() == 'male']
    females = [player for player in players if player[2].lower() == 'female']
    
    # Sort by skill (descending)
    males.sort(key=lambda player: player[1], reverse=True)
    females.sort(key=lambda player: player[1], reverse=True)

    # Create empty teams
    teams_male = [[] for _ in range(num_teams)]
    teams_female = [[] for _ in range(num_teams)]
    teams_combined = [[] for _ in range(num_teams)]  # For calculating avg skill

    # Balanced round-robin distribution function
    def balanced_distribution(players, teams):
        while players:
            for i in range(num_teams):
                if players:
                    teams[i].append(players.pop(0))
            for i in reversed(range(num_teams)):
                if players:
                    teams[i].append(players.pop(0))

    # Distribute players using balanced distribution
    balanced_distribution(males, teams_male)
    balanced_distribution(females, teams_female)
    
    # Combine male and female teams for overall team calculation
    for i in range(num_teams):
        teams_combined[i] = teams_male[i] + teams_female[i]

    return teams_male, teams_female, teams_combined

def calculate_avg_skill(teams):
    """Calculate average skill for each team, ignoring players with skill level 0."""
    avg_skills = []
    for team in teams:
        team_skills = [player[1] for player in team if player and player[1] > 0]
        avg_skills.append(sum(team_skills) / len(team_skills) if team_skills else 0)
    return avg_skills

# Streamlit UI
st.title("Balanced Teams Generator with Gender")

# Player input
players_input = st.text_area("Enter players, their skill levels, and gender (space-delimited, e.g., John Doe 5 Male)")

# Parse input into list of players
players = []
if players_input:
    for line in players_input.splitlines():
        parts = line.split()
        
        # Check if the line has at least 3 parts: Name, Skill, Gender
        if len(parts) >= 3:
            name = " ".join(parts[:-2])  # Join all but the last two parts as name
            try:
                skill = int(parts[-2])       # Second-to-last part is skill
                gender = parts[-1].lower()   # Last part is gender (convert to lowercase)

                if gender not in ['male', 'female']:
                    st.error(f"Invalid gender in input: {parts[-1]}. Must be 'male' or 'female'.")
                    continue
                
                players.append((name.strip(), skill, gender))
            except ValueError:
                st.error(f"Invalid skill value for player: {' '.join(parts)}. Skill must be an integer.")
        else:
            st.error(f"Invalid input format: {line}. Ensure the format is 'Name Skill Gender'.")

# Number of teams input
num_teams = st.slider("Select number of teams", min_value=2, max_value=10, value=2)

# Balance button
if st.button("Balance Teams"):
    if len(players) < num_teams:
        st.error("Not enough players to form teams")
    else:
        # Balance teams based on skill distribution
        teams_male, teams_female, teams_combined = balance_teams(players, num_teams)

        # Create dictionaries to hold team names separately for males and females
        team_data_male = {f"Team {i+1}": [player[0] for player in team] for i, team in enumerate(teams_male)}
        team_data_female = {f"Team {i+1}": [player[0] for player in team] for i, team in enumerate(teams_female)}

        # Calculate average skill for each team (combined genders)
        avg_skill_combined = calculate_avg_skill(teams_combined)

        # Find the max number of players in any team
        max_team_size_male = max(len(team) for team in teams_male)
        max_team_size_female = max(len(team) for team in teams_female)

        # Pad teams with None to make all teams the same length
        for i in range(num_teams):
            while len(team_data_male[f"Team {i+1}"]) < max_team_size_male:
                team_data_male[f"Team {i+1}"].append(None)
            while len(team_data_female[f"Team {i+1}"]) < max_team_size_female:
                team_data_female[f"Team {i+1}"].append(None)

        # Prepare the average skill data for display (combined genders)
        avg_skill_data = {f"Team {i+1}": [avg_skill_combined[i]] for i in range(num_teams)}

        # Create DataFrames for males, females, and average skill
        df_male = pd.DataFrame(team_data_male)
        df_female = pd.DataFrame(team_data_female)
        df_avg_skill = pd.DataFrame(avg_skill_data)

        # Display the male teams table
        st.write("Balanced Male Teams:")
        st.dataframe(df_male)

        # Display the female teams table
        st.write("Balanced Female Teams:")
        st.dataframe(df_female)

        # Display the average skill table (combined genders)
        st.write("Average Skill Level for Each Team (Combined Genders):")
        st.dataframe(df_avg_skill)
