import pandas as pd
import json
import re

input = "btw17_kerg.csv"
land_list = ["Schleswig-Holstein","Hamburg","Niedersachsen","Bremen","Nordrhein-Westfalen","Hessen","Rheinland-Pfalz","Baden-Württemberg",
            "Bayern","Saarland","Berlin","Brandenburg","Mecklenburg-Vorpommern","Sachsen","Sachsen-Anhalt","Thüringen","Bundesgebiet"]

test = []
with open(input, mode = "r", encoding="utf-8") as f:
    conv =  []
    for line in f:
        if re.match("(\d)?(\d)?\d;", line):
            line = re.sub("\n","",line)
            test.append(line)
            split = line.split(";")
            if split[1] not in land_list: #filter Bundesland/Bundesgebiet results
                conv.append(split)

df = pd.DataFrame(conv)

with open("results.json", mode='w', encoding="utf-8") as feedsjson:
    content = []
    for index, row in df.iterrows():
        if(row[2] == "9"): #if Wahlkreis in Bayern (ID = 9) choose CSU
            union = row[37]
        else: #else choose CDU
            union = row[21]
        not_misc = [union,row[25],row[33],row[45],row[29],row[41]]
        misc = int(row[17]) - sum(int(votes) for votes in not_misc)
        entry = {"WKR_NR":row[0],"WKR_NAME":row[1],"eligible_voters":row[2],"union":union,"spd":row[25],"gruene":row[33],"afd":row[45],"linke":row[29],"fdp":row[41],"misc":str(misc)}
        content.append(entry)
    json.dump(content, feedsjson)
