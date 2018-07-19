
# coding: utf-8

# In[4]:


import pandas as pd
from collections import deque
from pprint import pprint


# In[5]:


plays = pd.read_csv('../data/play_by_play.txt', delimiter = "\t")
lineup = pd.read_csv('../data/lineup.txt', delimiter = "\t").sort_values(['Game_id', 'Period', 'Team_id'], 
                                                                         ascending = [True, True, True])
plays = plays.sort_values(['Game_id', 'Period', 'PC_Time', 'WC_Time', 'Event_Num'], 
                 axis = 0, ascending = [True, True, False, True, True]).drop(['Team_id_type', 'Option2', 'Option3'], axis = 1)
game_ids = plays['Game_id'].unique().tolist()


# In[6]:



bigList = []
for g in range(50):
    team1players = {}
    team2players = {}

    t1Active = []
    t2Active = []


    t1Active2=[]
    t1Active3=[]
    t1Active4=[]
    t1Active5=[]

    t2Active2=[]
    t2Active3=[]
    t2Active4=[]
    t2Active5=[]

    team1 = ''
    team2 = ''
  

    lineup0 = lineup[lineup.Game_id == game_ids[g]].reset_index()
    df = plays[plays.Game_id == game_ids[g]]

    for i, row in lineup0.iterrows(): #0-9, 10-19, 20-29, 30-39 , 40-49
#         print(t1Active)
#         print(t2Active)
#         print
#         print(event)
        if i < 10:
            if i < 5:
                team1 = row["Team_id"]

                team1players[row['Person_id']] = 0
                t1Active.append(row['Person_id'])

            else:
                team2 = row["Team_id"]

                team2players[row['Person_id']] = 0
                t2Active.append(row['Person_id'])


        elif 10 <= i <= 19:
            if (i < 15):          
                team1players[row['Person_id']] = 0
                t1Active2.append(row['Person_id'])  

            else:
                team2players[row['Person_id']] = 0
                t2Active2.append(row['Person_id'])


        elif 20<= i<=29:
            if (i<25):
                team1players[row['Person_id']] = 0
                t1Active3.append(row['Person_id'])  

            else:
                team2players[row['Person_id']] = 0
                t2Active3.append(row['Person_id'])


        elif 30<=i<=39:
            if (i<35):
                team1players[row['Person_id']] = 0
                t1Active4.append(row['Person_id'])  

            else:
                team2players[row['Person_id']] = 0
                t2Active4.append(row['Person_id'])


        elif 40<=i<=49:
            if (i<45):
                team1players[row['Person_id']] = 0
                t1Active5.append(row['Person_id'])  


            else:
                team2players[row['Person_id']] = 0
                t2Active5.append(row['Person_id'])


    subsInFoul = deque()
    flag = False

    for i, event in df.iterrows():

        event_type = event['Event_Msg_Type']

        #1-made shot, 2-missed shot, 3-free throw, 4-rebound, 5-turnover, 6-foul, 7-violation, 8-substitution, 
        #9-Timeout, 10-Jump Ball, 11-Ejection, 12-Start Period, 13-End Period

        #12 - pick out our lineups

        if event_type==12:
            #pop off all the subs 
            flag = False
            while len(subsInFoul) != 0:

                sub = subsInFoul.popleft()
    #            print(sub)
                if sub[0] in team1players:
                    t1Active.remove(sub[0])
                    t1Active.append(sub[1])
                    if sub[1] not in team1players:
                        team1players[sub[1]] = 0


                else:
                    t2Active.remove(sub[0])
                    t2Active.append(sub[1])
                    if sub[1] not in team2players:
                        team2players[sub[1]] = 0


            #put in quarter start lineup        
            period = event['Period']
            if (period == 2):
                t1Active = t1Active2
                t2Active = t2Active2
            elif (period == 3):
                t1Active = t1Active3
                t2Active = t2Active3
            elif (period==4):
                t1Active=t1Active4
                t2Active=t2Active4
            elif (period==5):
                t1Active=t1Active5
                t2Active=t2Active5



        #6-foul happened
        if event_type == 6:
            flag = True
            #True - free throw could happen 

        #substitution
        if event_type == 8: 
            person1 = event['Person1']
            person2 = event['Person2']
    #        print(person1, person2, event['Team_id'])    
            if not flag: #if free throw is definitely not happening, substitute 

                if person1 in team1players:
                    t1Active.remove(person1)
                    t1Active.append(person2)
                    if person2 not in team1players:
                        team1players[person2] = 0 #add them to the dictionary


                else:
                    t2Active.remove(person1)
                    t2Active.append(person2)
                    if person2 not in team2players:
                        team2players[person2] = 0


            else: #free throw might be happening, add them to the queue

                subsInFoul.append( (person1, person2))

        if (flag == True) and (event_type == 1 or event_type == 2 or event_type == 4 or event_type == 5 or event_type == 7 
                               or event_type==10 or event_type==13):
            #there was a foul, play went on for sure (made/missed shot, rebound, turnover, violation, jump ball, end of quarter (technical foul glitch too strong))
            #foul did not result in free throws
            flag = False
            #do all the substitutions 

            while len(subsInFoul) != 0:


                sub = subsInFoul.popleft()
    #            print(sub)
                if sub[0] in team1players:
                    t1Active.remove(sub[0])
                    t1Active.append(sub[1])
                    if sub[1] not in team1players:
                        team1players[sub[1]] = 0

                else:
                    t2Active.remove(sub[0])
                    t2Active.append(sub[1])
                    if sub[1] not in team2players:
                        team2players[sub[1]] = 0


        #now we have the real active lineup

        #compute plus minus

        if (flag == False) and (event_type==1): 

            person1 = event['Person1']
            person2 = event['Person2']

            if (person1 in team1players):

                for i in t1Active:
                    team1players[i] += event['Option1']

                for i in t2Active:
                    team2players[i] -= event['Option1']  

            else:
                for i in t1Active:
                    team1players[i] -= event['Option1']
                for i in t2Active:
                    team2players[i] += event['Option1']          

        if (event_type==3):


            person1 = event['Person1']
            person2 = event['Person2']

            if (person1 in team1players):   
                for i in t1Active:
                    team1players[i] += event['Option1']
                for i in t2Active:
                    team2players[i] -= event['Option1']  

            else:
                for i in t1Active:
                    team1players[i] -= event['Option1']
                for i in t2Active:
                    team2players[i] += event['Option1']



    #    print("\n")
    a1 = [(k, team1players[k]) for k in sorted(team1players, key=team1players.get, reverse=True)]
    a2 = [(k, team2players[k]) for k in sorted(team2players, key=team2players.get, reverse=True)]
    for i,j in a1:
        bigList.append( ( game_ids[g],i,j))
    for i,j in a2:
        bigList.append( (game_ids[g],i,j))

    
#Your_Team_Name_Q1_BBALL.csv
ans = pd.DataFrame(bigList, columns = ['Game_ID', 'Player_ID', 'Player_Plus/Minus'])
ans.to_csv("Organic_Bike_Q1_BBALL.csv")

