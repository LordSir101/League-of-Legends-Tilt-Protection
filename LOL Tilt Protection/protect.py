from riotwatcher import LolWatcher, ApiError
import psutil
import time

timeInterval = 10
timeBetweenGamesParam = 120
timeSinceLastGameParam = 120

name = input("Please enter your LOL username\n")
validated = False


# golbal variables
api_key = 'RGAPI-a1f6cfd6-fc02-4a2a-ad66-4018767e338f'
watcher = LolWatcher(api_key)
my_region = 'na1'

while(not validated):
    try:
        # summoner details
        me = watcher.summoner.by_name(my_region, name)
        validated = True
    except:
        name = input("Invalid username please try again")

#print(me)

print("\n---Ranked---\n")

ranked_stats = watcher.league.by_summoner(my_region, me['id'])
print(ranked_stats)

while(True):
    print("\n---Matches---\n")

    # useing a loop in case we hit a query limit
    # we will pause the program for 2 secs and try again
    while(True):
        try:
            # get details of most recent matches
            matches = watcher.match.matchlist_by_account(my_region, me['accountId'])
            break
        except:
            time.sleep(2)

    # last two matches played
    last_match = matches['matches'][0]
    second_last_match = matches['matches'][1]


    while(True):
        try:
            # get champion details of each match
            # this will get data for all players
            match_detail = watcher.match.by_id(my_region, last_match['gameId'])
            match_detail2 = watcher.match.by_id(my_region, second_last_match['gameId'])
            break
        except:
            time.sleep(2)

    # Find the difference between games in mins
    # Riot API has timestamps in milli
    timeDiff = int(last_match['timestamp']) - int(second_last_match['timestamp'])
    diffMins = timeDiff/1000/60

    # check if the last game played was more than 2 hours ago
    currTime = time.time()
    timeLastPlayed = (currTime - (int(last_match['timestamp'])/1000))/60

    if(timeLastPlayed > timeSinceLastGameParam):
        print("The last game played was more than 2 hours ago")
        time.sleep(timeInterval)
        continue

    # check if both the matches were ranked and were started within 2 hours of each other
    if(last_match['queue'] == 420 and second_last_match['queue'] == 420 and diffMins < timeBetweenGamesParam):
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


    else:
        print("The last two matches were not ranked or they were started 2 hours apart")

    # check matches every 5 seconds
    time.sleep(timeInterval)
