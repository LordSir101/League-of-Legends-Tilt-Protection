from riotwatcher import LolWatcher, ApiError
import pandas as pd
import psutil

# TODO check date played of matches
# TODO handle cases where there are not ranked matches
# TODO loop and periodically check matches in the background

# golbal variables
api_key = 'KEY'
watcher = LolWatcher(api_key)
my_region = 'na1'

# summoner details
me = watcher.summoner.by_name(my_region, 'Fio')
#print(me)

print("\n---Ranked---\n")

ranked_stats = watcher.league.by_summoner(my_region, me['id'])
print(ranked_stats)

print("\n---Matches---\n")

# get details of most recent matches
matches = watcher.match.matchlist_by_account(my_region, me['accountId'])

last_match = []
second_last_match = []
matchesFound = 0

# last two matches played
for match in matches['matches']:
    # find ranked matches only (queue = 420)
    if(match['queue'] == 420 and matchesFound == 0):
        last_match = match
        matchesFound += 1

    elif(match['queue'] == 420 and matchesFound == 1):
        second_last_match = match
        break

# get champion details of each match
# this will get data for all players
match_detail = watcher.match.by_id(my_region, last_match['gameId'])
match_detail2 = watcher.match.by_id(my_region, second_last_match['gameId'])

losses = 0
matchData = []
matchData2 = []
# check if first game won
# loop through all players until we find the player we are seaching for
for row in match_detail['participants']:
    if(row['championId'] == last_match["champion"]):
        matchData = row
        if(not row['stats']["win"]):
            losses += 1

# check if second game won
for row in match_detail2['participants']:
    if(row['championId'] == second_last_match["champion"]):
        matchData2 = row
        if(not row['stats']["win"]):
            losses += 1

# if the player lost 2 ranked games in a row, they cannot play league anymore
if(losses == 2):
    print('Lost two games in a row')

    # close the league Client
    for process in psutil.process_iter():
        if process.name() == "LeagueClient.exe":
            process.kill()
else:
    print('You can keep playing')

print('\n')
print(matchData)
print('\n')
print(matchData2)
