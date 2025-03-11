import streamlit as st
import pandas as pd

def balance_teams(players, num_teams):
    # Separate players by gender and role
    males = [player for player in players if player[2] == 'male']
    females = [player for player in players if player[2] == 'female']
    
    # Separate players by role
    cutters = [player for player in players if player[3] == 'cutter']
    handlers = [player for player in players if player[3] == 'handler']
    hybrids = [player for player in players if player[3] == 'hybrid']
    
    # Sort by skill (descending)
    males.sort(key=lambda x: x[1], reverse=True)
    females.sort(key=lambda x: x[1], reverse=True)
    cutters.sort(key=lambda x: x[1], reverse=True)
    handlers.sort(key=lambda x: x[1], reverse=True)
    hybrids.sort(key=lambda x: x[1], reverse=True)
    
    # Create empty teams
    teams = [[] for _ in range(num_teams)]
    skill_sums = [0] * num_teams  # Track the total skill for each team
    
    assigned_players = set()  # Set to track players that have been assigned to teams

    # Function to assign players to teams ensuring no duplicates
    def assign_players(player_list):
        for player in player_list:
            # Ensure the player isn't already assigned
            if player not in assigned_players:
                team_index = skill_sums.index(min(skill_sums))  # Find the team with the least skill sum
                teams[team_index].append(player)
                skill_sums[team_index] += player[1]  # Update the skill sum for the chosen team
                assigned_players.add(player)

    # Distribute males and females (already balanced by gender)
    assign_players(males + females)
    
    # Distribute cutters and handlers
    assign_players(cutters)
    assign_players(handlers)
    
    # Distribute hybrids evenly between cutter and handler
    # If there are more cutters, we assign hybrids as handlers, and vice versa
    hybrid_cutters = [player for player in hybrids if len(cutters) <= len(handlers)]
    hybrid_handlers = [player for player in hybrids if len(handlers) < len(cutters)]
    
    assign_players(hybrid_cutters)
    assign_players(hybrid_handlers)
    
    # Fill teams with None to ensure all teams have the same number of players
    max_team_size = max(len(team) for team in teams)
    for team in teams:
        while len(team) < max_team_size:
            team.append(None)
    
    return teams

def calculate_avg_skill(teams):
    """Calculate average skill for each team."""
    avg_skills = []
    for team in teams:
        skills = [player[1] for player in team if player and player[1] > 0]
        avg_skills.append(sum(skills) / len(skills) if skills else 0)
    return avg_skills

# Streamlit UI
st.title("Balanced Teams Generator")

# Player input
players_input = st.text_area("Enter players, their skill levels, gender, and role (space-delimited, e.g., John Doe 5 Male Cutter)", height=500)

# Parse input into list of players
players = []
if players_input:
    for line in players_input.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            name = " ".join(parts[:-3])
            try:
                skill = int(parts[-3])
                gender = parts[-2].lower()
                role = parts[-1].lower()
                if gender not in ['male', 'female']:
                    st.error(f"Invalid gender in input: {parts[-2]}. Must be 'male' or 'female'.")
                    continue
                if role not in ['cutter', 'handler', 'hybrid']:
                    st.error(f"Invalid role in input: {parts[-1]}. Must be 'cutter', 'handler', or 'hybrid'.")
                    continue
                players.append((name.strip(), skill, gender, role))
            except ValueError:
                st.error(f"Invalid skill value for player: {' '.join(parts)}. Skill must be an integer.")
        else:
            st.error(f"Invalid input format: {line}. Ensure the format is 'Name Skill Gender Role'.")

# Number of teams input
num_teams = st.slider("Select number of teams", min_value=2, max_value=10, value=2)

# Balance button
if st.button("Balance Teams"):
    if len(players) < num_teams:
        st.error("Not enough players to form teams")
    else:
        teams = balance_teams(players, num_teams)
        avg_skill = calculate_avg_skill(teams)
        
        # Create the team data with "Empty" values
        team_data = {f"Team {i+1}": [player[0] if player is not None else "Empty" for player in teams[i]] for i in range(num_teams)}
        
        # Ensure all teams have the same number of players, and add "Empty" where necessary
        max_team_size = max(len(team) for team in teams)
        for i in range(num_teams):
            while len(team_data[f"Team {i+1}"]) < max_team_size:
                team_data[f"Team {i+1}"].append("Empty")
        
        avg_skill_data = {f"Team {i+1}": [avg_skill[i]] for i in range(num_teams)}
        
        # Separate male and female players into different tables while maintaining None values
        team_data_male = {f"Team {i+1}": [player[0] if player and player[2] == 'male' else "Empty" for player in teams[i]] for i in range(num_teams)}
        team_data_female = {f"Team {i+1}": [player[0] if player and player[2] == 'female' else "Empty" for player in teams[i]] for i in range(num_teams)}
        
        # Create the DataFrames
        df_teams = pd.DataFrame(team_data)
        df_avg_skill = pd.DataFrame(avg_skill_data)
        df_teams_male = pd.DataFrame(team_data_male)
        df_teams_female = pd.DataFrame(team_data_female)
        
        # Clean the DataFrames to remove any empty rows or columns
        df_teams_clean = df_teams.applymap(lambda x: x if x != "Empty" else None).dropna(how='all').dropna(axis=1, how='all').reset_index(drop=True)
        df_teams_male_clean = df_teams_male.applymap(lambda x: x if x != "Empty" else None).dropna(how='all').dropna(axis=1, how='all')
        df_teams_female_clean = df_teams_female.applymap(lambda x: x if x != "Empty" else None).dropna(how='all').dropna(axis=1, how='all')
        
        # Display the results without "Empty" values
        st.write("Balanced Teams:")
        st.dataframe(df_teams_clean)
        st.write("Balanced Male Teams:")
        st.dataframe(df_teams_male_clean)
        st.write("Balanced Female Teams:")
        st.dataframe(df_teams_female_clean)
        st.write("Average Skill Level for Each Team:")
        st.dataframe(df_avg_skill)
