import riotwatcher
from riotwatcher import LolWatcher, RiotWatcher, ApiError
import pandas as pd
import os
from datetime import timedelta

most_wanted_inter = "Neck"

#Neck,Anh,Sexten,Vladi

if most_wanted_inter == "Neck":
    puuid = '_J-2ueCR5fA3h616PW1x66e5FR0BNhm8WkA4w7QYA21u9rmD-Yddsmk4fBvfcERdV0qqEatf6KbYkA'
    my_region = 'euw1'
elif most_wanted_inter == "Anh":
    puuid = "PTv27XMdH5-GFvcnT4Num58PH1pSmZYBUyRQ5jzWPl61i3uheXzZew5zeIZW3k1COtRqWJkSV8vIOA"
    my_region = 'na1'
elif most_wanted_inter == "Sexten":
    puuid = 'xw7Jfg4Wq7GU4pcRQjx6oX56FOkrFpWGldQcGSSYoEIFYnrTw_uniupcosLL0qN5rMenShXnEmWxRA'
    my_region = 'euw1'
elif most_wanted_inter == "Vladi":
    puuid = 'qZ65dfrYt3l8bzYOydozor65qRb5VT9SYirQezHvbUM-lXHs9gqewu06IQIzK8sBS6QP0ItY8oZo7Q'
    my_region = 'euw1'

lol_watcher = LolWatcher('API Key') ##################################################API Key##################################################
me = lol_watcher.summoner.by_puuid(region = my_region, encrypted_puuid = puuid)
match_history = lol_watcher.match.matchlist_by_puuid(region = my_region, puuid = puuid, count = 100)


def lastgame():   

    results = []

    last_game_id = []

    all_games = True

    if all_games:
        last_game_id.extend(match_history)
        
    else:  

        last_game_id.append(match_history[0])
    
    for match in last_game_id:

        timeline_data = lol_watcher.match.timeline_by_match(region = my_region, match_id = match)
        
        match_data = lol_watcher.match.by_id(region = my_region, match_id = match)

        player_index = match_data['metadata']['participants'].index(puuid)
        
        par_id = player_index + 1

        sr_game = match_data['info']['gameMode']

        if sr_game == 'CLASSIC':

            def get_damage_at_frame(timeline_data, frame_index, participant_id):
                
                try:

                    frame = timeline_data['info']['frames'][frame_index]
                    
                    participant_frame = frame['participantFrames'][str(participant_id)]
                    
                    damage_stats = {
                        'total_damage_to_champions': participant_frame.get('damageStats', {}).get('totalDamageDoneToChampions', 0),
                    }
                    
                    return damage_stats
                except IndexError:
                    return {'total_damage_to_champions': "N/A"}
            
            def get_damage_taken_at_frame(timeline_data, frame_index, participant_id):

                try:

                    frame = timeline_data['info']['frames'][frame_index]
                    
                    participant_frame = frame['participantFrames'][str(participant_id)]
                    
                    damage_taken_stats = {
                        'damage_taken': participant_frame.get('damageStats', {}).get('totalDamageTaken', 0),
                    }
                    
                    return damage_taken_stats
                except IndexError:
                    return {'damage_taken': "N/A"}
            
            def get_cs_at_frame(timeline_data, frame_index, participant_id):

                try:

                    frame = timeline_data['info']['frames'][frame_index]
                    
                    participant_frame = frame['participantFrames'][str(participant_id)]
                    
                    cs_stats = {
                    'total_minions_killed': participant_frame.get('minionsKilled', 0),
                    'neutral_minions_killed': participant_frame.get('jungleMinionsKilled', 0),
                    'total_cs': participant_frame.get('minionsKilled', 0) + participant_frame.get('jungleMinionsKilled', 0),
                    }
                
                    return cs_stats
                except IndexError:
                    return {'total_cs': "N/A"}
            
            def get_gold_at_frame(timeline_data, frame_index, participant_id):

                try:

                    frame = timeline_data['info']['frames'][frame_index]
                    
                    participant_frame = frame['participantFrames'][str(participant_id)]
                    
                    gold_stats = {
                    'gold': participant_frame.get('totalGold', 0),
                    }
                
                    return gold_stats
                except IndexError:
                    return {'gold': "N/A"}
            
            def get_xp_at_frame(timeline_data, frame_index, participant_id):

                try:

                    frame = timeline_data['info']['frames'][frame_index]
                    
                    participant_frame = frame['participantFrames'][str(participant_id)]
                    
                    xp_stats = {
                    'get_xp': participant_frame.get('xp', 0),
                    }
                
                    return xp_stats
                except IndexError:
                    return {'get_xp': "N/A"}

            game_duration = match_data['info']['gameDuration']

            gd_minutes = game_duration // 60
            gd_seconds = game_duration % 60

            game_time = f"{gd_minutes:02d}:{gd_seconds:02d}"

            kills = match_data['info']['participants'][player_index]['kills']
            deaths = match_data['info']['participants'][player_index]['deaths']
            assists = match_data['info']['participants'][player_index]['assists']

            KDA = (kills + assists) / deaths
            
            longest_life = match_data['info']['participants'][player_index]['longestTimeSpentLiving']
            
            gd_minutes = longest_life // 60
            gd_seconds = longest_life % 60

            longest_life_formated = f"{gd_minutes:02d}:{gd_seconds:02d}"

            did_win = match_data['info']['participants'][player_index]['win'] 

            if did_win:

                win = 'win'

            else:
        
                win = 'lost'

            #spreadsheet
        
            results.append({
            "Champion": match_data['info']['participants'][player_index]['championName'],
            "Result": win,
            "Length": game_time,
            "Kills": kills,
            "Deaths": deaths,
            "Assists": assists,
            "KDA": f"{KDA:.1f}",
            "Damage": match_data['info']['participants'][player_index]['totalDamageDealtToChampions'],
            "DPM": int(match_data['info']['participants'][player_index]['totalDamageDealtToChampions'] / (game_duration / 60)),
            "DMG@5": get_damage_at_frame(timeline_data = timeline_data, frame_index = 5, participant_id = par_id)['total_damage_to_champions'],
            "DMG@10": get_damage_at_frame(timeline_data = timeline_data, frame_index = 10, participant_id = par_id)['total_damage_to_champions'],
            "DMG@15": get_damage_at_frame(timeline_data = timeline_data, frame_index = 15, participant_id = par_id)['total_damage_to_champions'],
            "DMG@20": get_damage_at_frame(timeline_data = timeline_data, frame_index = 20, participant_id = par_id)['total_damage_to_champions'],
            "DMG@25": get_damage_at_frame(timeline_data = timeline_data, frame_index = 25, participant_id = par_id)['total_damage_to_champions'],
            "DMG@30": get_damage_at_frame(timeline_data = timeline_data, frame_index = 30, participant_id = par_id)['total_damage_to_champions'],
            "DMG Taken": match_data['info']['participants'][player_index]['totalDamageTaken'],
            "DMG Taken@5": get_damage_taken_at_frame(timeline_data = timeline_data, frame_index = 5, participant_id = par_id)['damage_taken'],
            "DMG Taken@10": get_damage_taken_at_frame(timeline_data = timeline_data, frame_index = 10, participant_id = par_id)['damage_taken'],
            "DMG Taken@15": get_damage_taken_at_frame(timeline_data = timeline_data, frame_index = 15, participant_id = par_id)['damage_taken'],
            "DMG Taken@20": get_damage_taken_at_frame(timeline_data = timeline_data, frame_index = 20, participant_id = par_id)['damage_taken'],
            "DMG Taken@25": get_damage_taken_at_frame(timeline_data = timeline_data, frame_index = 25, participant_id = par_id)['damage_taken'],
            "DMG Taken@30": get_damage_taken_at_frame(timeline_data = timeline_data, frame_index = 30, participant_id = par_id)['damage_taken'],
            "Turret Damage": match_data['info']['participants'][player_index]['damageDealtToTurrets'],
            "CS": match_data['info']['participants'][player_index]['totalMinionsKilled'],
            "CS/M": f"{match_data['info']['participants'][player_index]['totalMinionsKilled'] / (game_duration / 60):.1f}",
            "CS@5": get_cs_at_frame(timeline_data = timeline_data, frame_index = 5, participant_id = par_id)['total_cs'],
            "CS@10": get_cs_at_frame(timeline_data = timeline_data, frame_index = 10, participant_id = par_id)['total_cs'],
            "CS@15": get_cs_at_frame(timeline_data = timeline_data, frame_index = 15, participant_id = par_id)['total_cs'],
            "CS@20": get_cs_at_frame(timeline_data = timeline_data, frame_index = 20, participant_id = par_id)['total_cs'],
            "CS@25": get_cs_at_frame(timeline_data = timeline_data, frame_index = 25, participant_id = par_id)['total_cs'],
            "CS@30": get_cs_at_frame(timeline_data = timeline_data, frame_index = 30, participant_id = par_id)['total_cs'],
            "Total Gold": match_data['info']['participants'][player_index]['goldEarned'],
            "Gold@5": get_gold_at_frame(timeline_data = timeline_data, frame_index = 5, participant_id = par_id)['gold'],
            "Gold@10": get_gold_at_frame(timeline_data = timeline_data, frame_index = 10, participant_id = par_id)['gold'],
            "Gold@15": get_gold_at_frame(timeline_data = timeline_data, frame_index = 15, participant_id = par_id)['gold'],
            "Gold@20": get_gold_at_frame(timeline_data = timeline_data, frame_index = 20, participant_id = par_id)['gold'],
            "Gold@25": get_gold_at_frame(timeline_data = timeline_data, frame_index = 25, participant_id = par_id)['gold'],
            "Gold@30": get_gold_at_frame(timeline_data = timeline_data, frame_index = 30, participant_id = par_id)['gold'],
            "XP@5": get_xp_at_frame(timeline_data = timeline_data, frame_index = 5, participant_id = par_id)['get_xp'],
            "XP@10": get_xp_at_frame(timeline_data = timeline_data, frame_index = 10, participant_id = par_id)['get_xp'],
            "XP@15": get_xp_at_frame(timeline_data = timeline_data, frame_index = 15, participant_id = par_id)['get_xp'],
            "XP@20": get_xp_at_frame(timeline_data = timeline_data, frame_index = 20, participant_id = par_id)['get_xp'],
            "XP@25": get_xp_at_frame(timeline_data = timeline_data, frame_index = 25, participant_id = par_id)['get_xp'],
            "XP@30": get_xp_at_frame(timeline_data = timeline_data, frame_index = 30, participant_id = par_id)['get_xp'],
            "Vision": match_data['info']['participants'][player_index]['visionScore'],
            "Wards Placed": match_data['info']['participants'][player_index]['wardsPlaced'],
            "Wards Killed": match_data['info']['participants'][player_index]['wardsKilled'],
            "Longest Life": longest_life_formated,
            "FB": match_data['info']['participants'][player_index]['firstBloodKill'],
            "A Key": match_data['info']['participants'][player_index]['spell1Casts'],
            "S Key": match_data['info']['participants'][player_index]['spell2Casts'],
            "D Key": match_data['info']['participants'][player_index]['spell3Casts'],
            "F Key": match_data['info']['participants'][player_index]['spell4Casts'],
            "On My Way Ping": match_data['info']['participants'][player_index]['onMyWayPings'],
            "All In Ping": match_data['info']['participants'][player_index]['allInPings'],
            "Assist Me Ping": match_data['info']['participants'][player_index]['assistMePings'],
            "Enemy Missing Ping": match_data['info']['participants'][player_index]['enemyMissingPings'],
            "Enemy Vision Ping": match_data['info']['participants'][player_index]['enemyVisionPings'],
            "Get Back Ping": match_data['info']['participants'][player_index]['getBackPings'],
            "Need Vision Ping": match_data['info']['participants'][player_index]['needVisionPings'],
            "Push Ping": match_data['info']['participants'][player_index]['pushPings'],
            "Vision Cleared Ping": match_data['info']['participants'][player_index]['visionClearedPings'],
            "Hold Ping": match_data['info']['participants'][player_index]['holdPings'],
            })
           
            
        
        else:
            
            continue      
                
    df = pd.DataFrame(results)
    df.to_excel("output.xlsx", index=False)
    os.startfile(r"C:\Users\kiwis\Desktop\YEpTHIS IS FOR THE NEW PROJECT\output.xlsx")


lastgame()
