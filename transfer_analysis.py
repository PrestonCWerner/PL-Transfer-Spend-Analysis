import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

match_stats_df = pd.read_csv("./pl_match_stats_2014_2024.csv")
transfer_stats_df = pd.read_csv("./pl_transfers_2014_2024.csv")
wage_bill_stats_df = pd.read_csv("./pl_wage_bill_2014_2024.csv")

#Average Transfer Spend by Team
# Looking at the most $$$ spent on transfers completed between 2009 and 2021
# Man U tops Man City over the 12-year period!
pd.set_option('display.float_format', '{:.2f}'.format) 
incoming_transfers = transfer_stats_df[transfer_stats_df['Status'] == "In"]
team_name_agg = incoming_transfers.groupby(['Team', 'Season'], as_index = False).agg(transfers = ('Team', 'count'), sum_transfer_fee = ('Fee', 'sum'))

team_name_agg = team_name_agg.sort_values(by = 'sum_transfer_fee', ascending = False)
#display(team_name_agg)

match_stats_df['year'] = match_stats_df['date'].str.extract("^(\d{4})")
match_stats_dict = {}
#display(match_stats_df.head())

for team in match_stats_df['home_team_name']:
    match_stats_dict[team] = {}
    for season in match_stats_df['season'].unique():
        if (team == "team_name"):
            pass
        else:
            match_stats_dict[team][str(season)] = {'W': 0, 'L': 0, 'D': 0, 'GF': 0, 'GA': 0}



# Go through all results in the match stats df to assign wins, losses, draws, goals for, and goals against for all PL teams
for result in match_stats_df.itertuples():
    if (result.result == "H"):
        match_stats_dict[result.home_team_name][result.season]['W'] += 1
        match_stats_dict[result.away_team_name][result.season]['L'] += 1
        match_stats_dict[result.home_team_name][result.season]['GF'] += result.home_goals
        match_stats_dict[result.home_team_name][result.season]['GA'] += result.away_goals
        match_stats_dict[result.away_team_name][result.season]['GF'] += result.away_goals
        match_stats_dict[result.away_team_name][result.season]['GA'] += result.home_goals
    elif (result.result == "A"):
        match_stats_dict[result.home_team_name][result.season]['L'] += 1
        match_stats_dict[result.away_team_name][result.season]['W'] += 1
        match_stats_dict[result.home_team_name][result.season]['GF'] += result.home_goals
        match_stats_dict[result.home_team_name][result.season]['GA'] += result.away_goals
        match_stats_dict[result.away_team_name][result.season]['GF'] += result.away_goals
        match_stats_dict[result.away_team_name][result.season]['GA'] += result.home_goals
    else:
        match_stats_dict[result.home_team_name][result.season]['D'] += 1
        match_stats_dict[result.away_team_name][result.season]['D'] += 1
        match_stats_dict[result.home_team_name][result.season]['GF'] += result.home_goals
        match_stats_dict[result.home_team_name][result.season]['GA'] += result.away_goals
        match_stats_dict[result.away_team_name][result.season]['GF'] += result.away_goals
        match_stats_dict[result.away_team_name][result.season]['GA'] += result.home_goals

team_performance_df = pd.DataFrame(columns = ["team_name", "season", "W", "L", "D", "GF", "GA", "GD", "points", "place", "annual_wage_bill", "annual_transfer_spend"])

for key_name, value in match_stats_dict.items():
    for key_season, data in value.items():
        points = (data['W'] * 3) + data['D']
        gd = data['GF'] - data['GA']
        team_performance_df.loc[len(team_performance_df)] = [key_name, key_season, data['W'], data['L'], data['D'], data['GF'], data['GA'], gd, points, 0, 0, 0]

for season in team_performance_df['season']:
    temp_df = team_performance_df[team_performance_df['season'] == season].sort_values(by = "points", ascending = False)
    temp_df.reset_index(drop=True, inplace=True)
    for team in temp_df['team_name']:
        team_performance_df.loc[(team_performance_df['team_name'] == str(team)) & (team_performance_df['season'] == season), "place"] = temp_df[temp_df['team_name'] == str(team)].index + 1

# Drop data where teams were not in the PL that season
team_performance_df = team_performance_df[team_performance_df["points"] != 0]
team_performance_df.fillna(0, inplace=True)


for season in wage_bill_stats_df['Season']:
    season_df = wage_bill_stats_df[wage_bill_stats_df['Season'] == season]
    for team in season_df['Team']:
        team_performance_df.loc[(team_performance_df['team_name'] == str(team)) & (team_performance_df['season'] == season), "annual_wage_bill"] = wage_bill_stats_df.loc[(wage_bill_stats_df['Team'] == str(team)) & (wage_bill_stats_df['Season'] == season), "Annual Wages"].iloc[0]

for season in team_performance_df['season']:
    temp_df = team_performance_df[team_performance_df['season'] == season]
    for team in temp_df['team_name']:
        team_performance_df.loc[(team_performance_df['team_name'] == str(team)) & (team_performance_df['season'] == season), "annual_transfer_spend"] = team_name_agg.loc[(team_name_agg['Team'] == str(team)) & (team_name_agg['Season'] == season), "sum_transfer_fee"].iloc[0]
    
    


#Convert annual wage bill to int
team_performance_df['annual_wage_bill'] = team_performance_df['annual_wage_bill'].str.replace(',', '', regex=False)
team_performance_df['annual_wage_bill'] = team_performance_df['annual_wage_bill'].astype(float)

#display(team_performance_df.sort_values(by = "annual_wage_bill", ascending = False).head())

team_performance_2014 = team_performance_df[team_performance_df['season'] == "2014/2015"].sort_values(by = "points", ascending = False)

team_performance_2023 = team_performance_df[team_performance_df['season'] == "2023/2024"].sort_values(by = "points", ascending = False)

team_transfer_expenditure_2014 = team_name_agg[team_name_agg['Season'] == "2014/2015"]
team_transfer_expenditure_2023 = team_name_agg[team_name_agg['Season'] == "2023/2024"]


average_annual_wage_bill_2014_2015 = team_performance_2014['annual_wage_bill'].mean()
average_annual_wage_bill_2023_2024 = team_performance_2023['annual_wage_bill'].mean()

print("Average wage bill 2014/2015: ", average_annual_wage_bill_2014_2015)
print("Average wage bill 2023/2024 (adjusted for inflation): ", average_annual_wage_bill_2023_2024 * .79)


print("Average transfer spend 2014/2015: ", team_transfer_expenditure_2014['sum_transfer_fee'].mean())
print("Average transfer spend 2023/2024 (adjusted for inflation)", team_transfer_expenditure_2023['sum_transfer_fee'].mean() *.79)

#Create Previous Season Transfer Spend column to show total transfer spend in the previous year
for season in team_performance_df['season']:
    prev_season = str(int(season.split('/')[0]) - 1) + '/' + str(int(season.split('/')[1]) - 1)
    temp_df = team_performance_df[team_performance_df['season'] == prev_season]
    if (season == "2014/2015"):
        temp_df = team_performance_df[team_performance_df['season'] == season]
        for team in temp_df['team_name']:
            team_performance_df.loc[(team_performance_df['team_name'] == str(team)) & (team_performance_df['season'] == season), "prev_annual_transfer_spend"] = 0
    else:
        for team in temp_df['team_name']:
            team_performance_df.loc[(team_performance_df['team_name'] == str(team)) & (team_performance_df['season'] == season), "prev_annual_transfer_spend"] = temp_df.loc[(temp_df['team_name'] == str(team)) & (temp_df['season'] == prev_season), "annual_transfer_spend"].iloc[0]

#display(team_performance_df.sort_values(by = "prev_annual_transfer_spend", ascending = False))

prev_transfer_spend = team_performance_df[team_performance_df['season'] != "2014/2015"]
prev_transfer_spend = prev_transfer_spend.dropna()

#display(prev_transfer_spend.sort_values(by = "prev_annual_transfer_spend", ascending = False))

#import lat/lon data for stadiums for cool data viz
geo_loc_df = pd.read_csv('./pl_stadiums_loc.csv')
for season in team_performance_df['season']:
	temp_df = team_performance_df[team_performance_df['season'] == season]
	for team in temp_df["team_name"]:
		latitude = geo_loc_df.loc[(geo_loc_df['Team'] == str(team)), "Latitude"]
		print(season)
		print(team)
		team_performance_df.loc[(team_performance_df['team_name'] == team) & (team_performance_df['season'] == season), "lat"] = geo_loc_df.loc[(geo_loc_df['Team'] == team), "Latitude"].iloc[0]
		team_performance_df.loc[(team_performance_df['team_name'] == team) & (team_performance_df['season'] == season), "lon"] = geo_loc_df.loc[(geo_loc_df['Team'] == team), "Longitude"].iloc[0]
		print(latitude)
		
#Update dollar amounts to adjust for inflation since 2014
inflation_mult_dict = {}
inflation_mult_dict['2014/2015'] = 1
inflation_mult_dict['2015/2016'] = 1
inflation_mult_dict['2016/2017'] = 1
inflation_mult_dict['2017/2018'] = 1.02
inflation_mult_dict['2018/2019'] = 1.04
inflation_mult_dict['2019/2020'] = 1.05
inflation_mult_dict['2020/2021'] = 1.06
inflation_mult_dict['2021/2022'] = 1.09
inflation_mult_dict['2022/2023'] = 1.19
inflation_mult_dict['2023/2024'] = 1.27

for season in team_performance_df['season'].unique():
   temp_df = team_performance_df[team_performance_df['season'] == season]
   print(season)
   for team in temp_df['team_name']:
        print(team)
        print("Multiplied: ", inflation_mult_dict[season])
        print("Old amount: ", team_performance_df.loc[(team_performance_df['team_name'] == team) & (team_performance_df['season'] == season), "annual_wage_bill"].iloc[0])
        team_performance_df.loc[(team_performance_df['team_name'] == team) & (team_performance_df['season'] == season), "annual_wage_bill"] = team_performance_df.loc[(team_performance_df['team_name'] == team) & (team_performance_df['season'] == season), "annual_wage_bill"].iloc[0] / inflation_mult_dict[season]
        print("New amount: ", team_performance_df.loc[(team_performance_df['team_name'] == team) & (team_performance_df['season'] == season), "annual_wage_bill"].iloc[0])

#Export CSVs for data viz
team_performance_df.to_csv('team_data_by_season.csv', index=False)
prev_transfer_spend.to_csv('team_data_prev_transfer.csv', index = False)
print("Exported CSVs!")

#Determine correlation between prior year transfer spend and current season success
slope_prev_transfer, intercept_prev_transfer = np.polyfit(prev_transfer_spend['prev_annual_transfer_spend'], prev_transfer_spend['points'], 1)
prev_transfer_spend['points_predicted'] = slope_prev_transfer * prev_transfer_spend['prev_annual_transfer_spend'] + intercept_prev_transfer
r_squared_prev_transfer = r2_score(prev_transfer_spend['points'], prev_transfer_spend['points_predicted'])
print(f"R-squared for points dependency on previous year transfer spend: {r_squared_prev_transfer}")

slope_prev_transfer_place, intercept_prev_transfer_place = np.polyfit(prev_transfer_spend['prev_annual_transfer_spend'], prev_transfer_spend['place'], 1)
prev_transfer_spend['place_predicted'] = slope_prev_transfer_place * prev_transfer_spend['prev_annual_transfer_spend'] + intercept_prev_transfer_place
r_squared_prev_transfer_place = r2_score(prev_transfer_spend['place'], prev_transfer_spend['place_predicted'])
print(f"R-squared for place dependency on previous year transfer spend: {r_squared_prev_transfer_place}")


# Calculate predicted values (example using linear regression)
slope, intercept = np.polyfit(team_performance_df['annual_wage_bill'], team_performance_df['points'], 1)
team_performance_df['points_predicted'] = slope * team_performance_df['annual_wage_bill'] + intercept

slope_place, intercept_place = np.polyfit(team_performance_df['annual_wage_bill'], team_performance_df['place'], 1)
team_performance_df['place_predicted'] = slope_place * team_performance_df['annual_wage_bill'] + intercept_place

# Calculate R-squared
r_squared = r2_score(team_performance_df['points'], team_performance_df['points_predicted'])
r_squared_place = r2_score(team_performance_df['place'], team_performance_df['place_predicted'])
print(f"R-squared for points dependency on annual wage bill: {r_squared}")
print(f"R-squared for place dependency on annual wage bill: {r_squared_place}")

#Same steps for transfer spend
slope_transfer, intercept_transfer = np.polyfit(team_performance_df['annual_transfer_spend'], team_performance_df['points'], 1)
team_performance_df['points_predicted_transfer'] = slope_transfer * team_performance_df['annual_transfer_spend'] + intercept_transfer
r_squared_transfer = r2_score(team_performance_df['points'], team_performance_df['points_predicted_transfer'])
print(f"R-squared for points dependency on annual transfer spend: {r_squared_transfer}")

slope_transfer_place, intercept_transfer_place = np.polyfit(team_performance_df['annual_transfer_spend'], team_performance_df['place'], 1)
team_performance_df['place_predicted_transfer'] = slope_transfer_place * team_performance_df['annual_transfer_spend'] + intercept_transfer_place
r_squared_transfer_place = r2_score(team_performance_df['place'], team_performance_df['place_predicted_transfer'])
print(f"R-squared for place dependency on annual transfer spend: {r_squared_transfer_place}")

