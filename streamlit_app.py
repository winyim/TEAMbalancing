import streamlit as st
import pandas as pd


def balance_teams(players, num_teams):
    opens = [player for player in players if player[2] == 'open']
    womans = [player for player in players if player[2] == 'woman']

    cutters = [player for player in players if player[3] == 'cutter']
    handlers = [player for player in players if player[3] == 'handler']
    hybrids = [player for player in players if player[3] == 'hybrid']

    opens.sort(key=lambda x: x[1], reverse=True)
    womans.sort(key=lambda x: x[1], reverse=True)
    cutters.sort(key=lambda x: x[1], reverse=True)
    handlers.sort(key=lambda x: x[1], reverse=True)
    hybrids.sort(key=lambda x: x[1], reverse=True)

    teams = [[] for _ in range(num_teams)]
    skill_sums = [0] * num_teams
    assigned_players = set()

    def assign_players(player_list):
        for player in player_list:
            if player not in assigned_players:
                team_index = skill_sums.index(min(skill_sums))
                teams[team_index].append(player)
                skill_sums[team_index] += player[1]
                assigned_players.add(player)

    assign_players(opens + womans)
    assign_players(cutters)
    assign_players(handlers)
    assign_players(hybrids)

    max_team_size = max(len(team) for team in teams)
    for team in teams:
        while len(team) < max_team_size:
            team.append(None)

    return teams


def calculate_avg_skill(teams):
    avg_skills = []
    for team in teams:
        skills = [player[1] for player in team if player and player[1] > 0]
        avg_skills.append(sum(skills) / len(skills) if skills else 0)
    return avg_skills


def generate_bracket(team_names):
    random.shuffle(team_names)
    bracket = []
    while len(team_names) > 1:
        round_matches = []
        for i in range(0, len(team_names), 2):
            if i + 1 < len(team_names):
                round_matches.append((team_names[i], team_names[i + 1]))
            else:
                round_matches.append((team_names[i], "BYE"))
        bracket.append(round_matches)
        team_names = [winner[0]
                      for winner in round_matches if winner[1] != "BYE"]
    return bracket


st.title("Balanced Mixed Teams For Ultimate")

st.markdown(
    '''This app creates balanced teams based on skill level and preferred role.''')
st.markdown(
    '''Input format: Name, Skill Level (integer), Gender (open/woman), Role (cutter/handler/hybrid).  
    Separate each field with a space''')

players_input = st.text_area("Enter player data:", height=500)
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
                if gender not in ['open', 'woman'] or role not in ['cutter', 'handler', 'hybrid']:
                    continue
                players.append((name.strip(), skill, gender, role))
            except ValueError:
                continue

num_teams = st.slider("Select number of teams",
                      min_value=2, max_value=15, value=2)
custom_names = st.checkbox("Customize team names")
team_names = []

if custom_names:
    for i in range(num_teams):
        team_names.append(st.text_input(
            f"Enter name for Team {i+1}", f"Team {i+1}"))
else:
    team_names = [f"Team {i+1}" for i in range(num_teams)]

if st.button("Balance Teams"):
    if len(players) < num_teams:
        st.error("Not enough players to form teams")
    else:
        teams = balance_teams(players, num_teams)
        avg_skill = calculate_avg_skill(teams)

        team_data = {team_names[i]: [
            player[0] if player else "Empty" for player in teams[i]] for i in range(num_teams)}
        avg_skill_data = {team_names[i]: [avg_skill[i]]
                          for i in range(num_teams)}

        team_data_open = {team_names[i]: [player[0] if player and player[2] ==
                                          'open' else "Empty" for player in teams[i]] for i in range(num_teams)}
        team_data_woman = {team_names[i]: [player[0] if player and player[2] ==
                                           'woman' else "Empty" for player in teams[i]] for i in range(num_teams)}

        df_teams = pd.DataFrame(team_data).dropna(
            how='all').reset_index(drop=True)
        df_avg_skill = pd.DataFrame(avg_skill_data)
        df_teams_open = pd.DataFrame(team_data_open).dropna(
            how='all').reset_index(drop=True)
        df_teams_woman = pd.DataFrame(team_data_woman).dropna(
            how='all').reset_index(drop=True)

        # Clean the DataFrames to remove any empty rows or columns
        df_teams_clean = df_teams.map(lambda x: x if x != "Empty" else None).dropna(how='all').dropna(
            axis=1, how='all').reset_index(drop=True).apply(lambda x: x.sort_values().values)
        df_teams_open_clean = df_teams_open.map(lambda x: x if x != "Empty" else None).dropna(
            how='all').dropna(axis=1, how='all').apply(lambda x: x.sort_values().values)
        df_teams_woman_clean = df_teams_woman.map(lambda x: x if x != "Empty" else None).dropna(
            how='all').dropna(axis=1, how='all').apply(lambda x: x.sort_values().values)

        st.write("Balanced Teams:")
        st.dataframe(df_teams_clean)
        st.write("Balanced Open Teams:")
        st.dataframe(df_teams_open_clean)
        st.write("Balanced Woman Teams:")
        st.dataframe(df_teams_woman_clean)
        st.write("Average Skill Level for Each Team:")
        st.dataframe(df_avg_skill)
