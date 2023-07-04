import json
from tabulate import tabulate
from termcolor import colored

# Set the value of detailed_version (True) for more info/to analyze more in depth, but might overwhelm your terminal
detailed_version = False

# Read the JSON file
with open('NA1_4698549616.json') as file:
    data = json.load(file)

# Extract the participant data
participants = data['info']['participants']

# Function to deduce the rank based on the metrics
def deduce_rank(participant):
    rank_score = 0
    metrics = participant['challenges']

    # Function to safely access metrics
    def get_metric(metrics, metric_name):
        return metrics.get(metric_name, 0)

    # Extracting additional metrics
    kda = get_metric(metrics, 'kda')
    takedowns = get_metric(metrics, 'takedowns')
    deaths = participant.get('deaths', 0)
    kills = participant.get('kills', 0)
    damagePerMinute = get_metric(metrics, 'damagePerMinute')
    damageTakenOnTeamPercentage = get_metric(metrics, 'damageTakenOnTeamPercentage')
    killParticipation = get_metric(metrics, 'killParticipation')
    turretTakedowns = get_metric(metrics, 'turretTakedowns')
    goldPerMinute = get_metric(metrics, 'goldPerMinute')
    healingAndShielding = get_metric(metrics, 'effectiveHealAndShielding')
    totalDamageDealtToChampions = participant.get('totalDamageDealtToChampions', 0)
    totalTimeCCDealt = participant.get('totalTimeCCDealt', 0)
    totalDamageTaken = participant.get('totalDamageTaken', 0)
    totalUnitsHealed = participant.get('totalUnitsHealed', 0)

    # Deduction based on the metrics
    if takedowns >= 40:
        rank_score += 2
    elif takedowns >= 30:
        rank_score += 1.5
    elif takedowns >= 20:
        rank_score += 1

    if deaths <= 3:
        rank_score += 2
    elif deaths <= 5:
        rank_score += 1.5
    elif deaths <= 7:
        rank_score += 1

    if kda >= 6:
        rank_score += 2
    elif kda >= 4:
        rank_score += 1.5
    elif kda >= 2:
        rank_score += 1

    if kills >= 15:
        rank_score += 2
    elif kills >= 10:
        rank_score += 1.5
    elif kills >= 5:
        rank_score += 1

    if damagePerMinute >= 2000:
        rank_score += 2
    elif damagePerMinute >= 1500:
        rank_score += 1.5
    elif damagePerMinute >= 1000:
        rank_score += 1

    if damageTakenOnTeamPercentage <= 0.1:
        rank_score += 2
    elif damageTakenOnTeamPercentage <= 0.15:
        rank_score += 1.5
    elif damageTakenOnTeamPercentage <= 0.2:
        rank_score += 1

    if killParticipation >= 0.8:
        rank_score += 2
    elif killParticipation >= 0.6:
        rank_score += 1.5
    elif killParticipation >= 0.4:
        rank_score += 1

    if goldPerMinute >= 800:
        rank_score += 0.5
    elif goldPerMinute >= 600:
        rank_score += 0.25

    if healingAndShielding >= 5000:
        rank_score += 1.5
    elif healingAndShielding >= 3000:
        rank_score += 1

    if totalDamageDealtToChampions >= 30000:
        rank_score += 1.5
    elif totalDamageDealtToChampions >= 20000:
        rank_score += 1

    if totalTimeCCDealt >= 1000:
        rank_score += 0.5

    if totalDamageTaken <= 20000:
        rank_score += 1
    elif totalDamageTaken <= 30000:
        rank_score += 0.5

    if totalUnitsHealed >= 10:
        rank_score += 0.5
    
    # Deduce the rank based on the rank score
    if rank_score >= 27:
        return 'S+'
    elif rank_score >= 24:
        return 'S'
    elif rank_score >= 21:
        return 'S-'
    elif rank_score >= 18:
        return 'A+'
    elif rank_score >= 15:
        return 'A'
    elif rank_score >= 12:
        return 'A-'
    elif rank_score >= 9:
        return 'B+'
    elif rank_score >= 6:
        return 'B'
    elif rank_score >= 3:
        return 'B-'
    elif rank_score >= 2.5:
        return 'C+'
    elif rank_score >= 2:
        return 'C'
    elif rank_score >= 1.5:
        return 'C-'
    elif rank_score >= 1:
        return 'D+'
    elif rank_score >= 0.5:
        return 'D'
    else:
        return 'D-'

# Define color ranges for different columns
color_ranges = {
    'KDA': [(6, 'green'), (4, 'yellow'), (0, 'blue')],
    'Takedowns': [(40, 'green'), (30, 'yellow'), (20, 'blue')],
    'Deaths': [(3, 'green'), (5, 'yellow'), (7, 'blue')],
    'Damage Taken Percentage': [(0.1, 'green'), (0.15, 'yellow'), (0.2, 'blue')],
    'Kill Participation': [(0.8, 'green'), (0.6, 'yellow'), (0.4, 'blue')],
    'Gold Per Minute': [(800, 'green'), (600, 'yellow'), (500, 'blue')],
    'Healing and Shielding': [(5000, 'green'), (3000, 'yellow')],
    'Total Damage Dealt to Champions': [(30000, 'green'), (20000, 'yellow'), (9000, 'blue')],
    'Damage Per Minute': [(1500, 'green'), (1000, 'yellow'), (500, 'blue')],
    'Total Time CC Dealt': [(1000, 'green')],
    'Total Damage Taken': [(20000, 'green'), (30000, 'yellow')],
    'Total Units Healed': [(10, 'green')],
    'Estimated Rank': [('S+', 'green'), ('S', 'green'), ('S-', 'green'),
                      ('A+', 'yellow'), ('A', 'yellow'), ('A-', 'yellow'),
                      ('B+', 'yellow'), ('B', 'blue'), ('B-', 'blue'),
                      ('C+', 'blue'), ('C', 'blue'), ('C-', 'blue'),
                      ('D+', 'blue'), ('D', 'blue'), ('D-', 'blue')]
}

# Display the data in a tabular format
print("\n")
if detailed_version:
    headers = ["Summoner Name", "Champion Name", "KDA", "Takedowns", "Deaths", "Kills",
               "Damage Taken Percentage", "Kill Participation", "Turret Takedowns",
               "Gold Per Minute", "Damage Per Minute", "Healing and Shielding",
               "Total Damage Dealt to Champions", "Total Time CC Dealt",
               "Total Damage Taken", "Total Units Healed", "Estimated Rank"]
else:
    headers = ["Summoner Name", "Champion Name", "KDA", "Kill Participation",
               "Gold Per Minute", "Damage Per Minute",
               "Total Damage Dealt to Champions", "Estimated Rank"]

table_data = []
for participant in participants:
    # Extract relevant data based on the value of detailed_version
    summoner_name = participant['summonerName']
    champion_name = participant['championName']
    kda = participant['challenges'].get('kda', 0)
    kill_participation = participant['challenges'].get('killParticipation', 0)
    gold_per_minute = participant['challenges'].get('goldPerMinute', 0)
    damage_per_minute = participant['challenges'].get('damagePerMinute', 0)
    total_damage_dealt = participant.get('totalDamageDealtToChampions', 0)
    estimated_rank = deduce_rank(participant)

    if detailed_version:
        takedowns = participant['challenges'].get('takedowns', 0)
        deaths = participant.get('deaths', 0)
        kills = participant.get('kills', 0)
        damage_taken_percentage = participant['challenges'].get('damageTakenOnTeamPercentage', 0)
        turret_takedowns = participant['challenges'].get('turretTakedowns', 0)
        healing_and_shielding = participant['challenges'].get('effectiveHealAndShielding', 0)
        total_time_cc_dealt = participant.get('totalTimeCCDealt', 0)
        total_damage_taken = participant.get('totalDamageTaken', 0)
        total_units_healed = participant.get('totalUnitsHealed', 0)

        table_row = [summoner_name, champion_name, kda, takedowns, deaths, kills,
                     damage_taken_percentage, kill_participation, turret_takedowns,
                     gold_per_minute, damage_per_minute, healing_and_shielding,
                     total_damage_dealt, total_time_cc_dealt, total_damage_taken,
                     total_units_healed, estimated_rank]
    else:
        table_row = [summoner_name, champion_name, kda, kill_participation,
                     gold_per_minute, damage_per_minute, total_damage_dealt,
                     estimated_rank]

    # Color the values based on the color ranges
    colored_row = []
    for i, value in enumerate(table_row):
        header = headers[i]
        if header == 'Estimated Rank':
            color_range = color_ranges[header]
            for rank, color in color_range:
                if value == rank:
                    colored_value = colored(value, color)
                    break
            else:
                # If no rank matches, use the default color for the column
                colored_value = colored(str(value))
        elif header in color_ranges:
            color_range = color_ranges[header]
            for threshold, color in color_range:
                if value >= threshold:
                    colored_value = colored(value, color)
                    break
            else:
                # If no threshold matches, use the default color for the column
                colored_value = colored(str(value))
        else:
            colored_value = value
        colored_row.append(colored_value)

    table_data.append(colored_row)

table = tabulate(table_data, headers, tablefmt="pipe")
print(table)
print("\n")
