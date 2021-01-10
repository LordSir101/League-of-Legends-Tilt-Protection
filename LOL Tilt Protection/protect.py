from riotwatcher import LolWatcher, ApiError
import psutil
import time

name = input("Please enter your LOL username\n")

while(True):
    # golbal variables
    api_key = 'RGAPI-d15ae015-04bb-4cb8-b3db-cb41c91077bb'
    watcher = LolWatcher(api_key)
    my_region = 'na1'

    # summoner details
    me = watcher.summoner.by_name(my_region, name)
    #print(me)

    print("\n---Ranked---\n")

    ranked_stats = watcher.league.by_summoner(my_region, me['id'])
    print(ranked_stats)

    print("\n---Matches---\n")

    # get details of most recent matches
    matches = watcher.match.matchlist_by_account(my_region, me['accountId'])

    # last two matches played
    last_match = matches['matches'][0]
    second_last_match = matches['matches'][1]

    # get champion details of each match
    # this will get data for all players
    match_detail = watcher.match.by_id(my_region, last_match['gameId'])
    match_detail2 = watcher.match.by_id(my_region, second_last_match['gameId'])

    # Find the difference between games in mins
    # Riot API has timestamps in milli
    timeDiff = int(last_match['timestamp']) - int(second_last_match['timestamp'])
    diffMins = timeDiff/1000/60

    # check if both the matches were ranked and were started within 2 hours of each other
    if(last_match['queue'] == 420 and second_last_match['queue'] == 420 and diffMins < 120):
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
        print("The last two matches were not ranked")

    # check matches every 5 seconds
    time.sleep(5)
