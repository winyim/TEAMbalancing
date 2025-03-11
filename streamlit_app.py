import streamlit as st
import pandas as pd

def balance_teams(players, num_teams):
    # Separate players by gender and role
    opens = [player for player in players if player[2] == 'open']
    womans = [player for player in players if player[2] == 'woman']
    
    # Separate players by role
    cutters = [player for player in players if player[3] == 'cutter']
    handlers = [player for player in players if player[3] == 'handler']
    hybrids = [player for player in players if player[3] == 'hybrid']
    
    # Sort by skill (descending)
    opens.sort(key=lambda x: x[1], reverse=True)
    womans.sort(key=lambda x: x[1], reverse=True)
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

    # Distribute opens and womans (already balanced by gender)
    assign_players(opens + womans)
    
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

st.title("Balanced Mixed Teams For Ultimate")

welcome = st.markdown('''This app will take a list of players and attempt to make balanced evenly distributed teams taking into account skill level and preferred role.
                      ''')
info = st.markdown('''Information needed (best to copy and paste from spreadsheet):  
        player full name, their skill level (any integer), gender designation (open or woman), and role (cutter, handler or hybrid)''')

players_input = st.text_area('''Enter information in a space-delimited format where every line is a different individual  
                             (eg. John Doe 5 open cutter)''', height=500)

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
                if gender not in ['open', 'woman']:
                    st.error(f"Invalid gender in input: {parts[-2]}. Must be 'open' or 'woman'.")
                    continue
                if role not in ['cutter', 'handler', 'hybrid']:
                    st.error(f"Invalid role in input: {parts[-1]}. Must be 'cutter', 'handler', or 'hybrid'.")
                    continue
                players.append((name.strip(), skill, gender, role))
            except ValueError:
                st.error(f"Invalid skill value for player: {' '.join(parts)}. Skill must be an integer.")
        else:
            st.error(f"Invalid input format: {line}. Ensure the format is 'FirstName LastName Skill Gender Role'.")

# Number of teams input
num_teams = st.slider("Select number of teams", min_value=2, max_value=15, value=2)

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
        
        # Separate open and woman players into different tables while maintaining None values
        team_data_open = {f"Team {i+1}": [player[0] if player and player[2] == 'open' else "Empty" for player in teams[i]] for i in range(num_teams)}
        team_data_woman = {f"Team {i+1}": [player[0] if player and player[2] == 'woman' else "Empty" for player in teams[i]] for i in range(num_teams)}
        
        # Create the DataFrames
        df_teams = pd.DataFrame(team_data)
        df_avg_skill = pd.DataFrame(avg_skill_data)
        df_teams_open = pd.DataFrame(team_data_open)
        df_teams_woman = pd.DataFrame(team_data_woman)
        
        # Clean the DataFrames to remove any empty rows or columns
        df_teams_clean = df_teams.map(lambda x: x if x != "Empty" else None).dropna(how='all').dropna(axis=1, how='all').reset_index(drop=True).apply(lambda x: x.sort_values().values)
        df_teams_open_clean = df_teams_open.map(lambda x: x if x != "Empty" else None).dropna(how='all').dropna(axis=1, how='all').apply(lambda x: x.sort_values().values)
        df_teams_woman_clean = df_teams_woman.map(lambda x: x if x != "Empty" else None).dropna(how='all').dropna(axis=1, how='all').apply(lambda x: x.sort_values().values)
        
        # Display the results without "Empty" values
        st.write("Balanced Teams:")
        st.dataframe(df_teams_clean)
        st.write("Balanced open Teams:")
        st.dataframe(df_teams_open_clean)
        st.write("Balanced woman Teams:")
        st.dataframe(df_teams_woman_clean)
        st.write("Average Skill Level for Each Team:")
        st.dataframe(df_avg_skill)
