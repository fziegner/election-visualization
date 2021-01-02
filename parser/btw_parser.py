import pandas as pd
import json
import re
import numbers
input = ""
output = ""
land_list = ["Schleswig-Holstein","Hamburg","Niedersachsen","Bremen","Nordrhein-Westfalen","Hessen","Rheinland-Pfalz","Baden-Württemberg",
            "Bayern","Saarland","Berlin","Brandenburg","Mecklenburg-Vorpommern","Sachsen","Sachsen-Anhalt","Thüringen","Bundesgebiet"]

test = []
with open(input, mode = "r", encoding="utf-8", errors="ignore") as f:
    conv =  []
    for line in f:
        if re.match("(\d)?(\d)?\d;", line):
            line = re.sub("\n","",line)
            test.append(line)
            split = line.split(";")
            print(split[1])
            if split[1] not in land_list: #filter Bundesland/Bundesgebiet results
                conv.append(split)


df = pd.DataFrame(conv)

with open(output, mode='w', encoding="utf-8") as feedsjson:
    content = []
    for index, row in df.iterrows():
        if(row[2] == "9"): #if Wahlkreis in Bayern (ID = 9) choose CSU
            union = row[37]
        else: #else choose CDU
            union = row[21]
        not_misc = [union,row[25],row[33],row[45],row[29],row[41]]

        try:
            not_misc[1] = int(row[25])
        except:
            not_misc[1] = 0
        try:
            not_misc[2] = int(row[33])
        except:
            not_misc[2] = 0
        try:
            not_misc[3] = int(row[45])
        except:
            not_misc[3] = 0
        try:
            not_misc[4] = int(row[29])
        except:
            not_misc[4] = 0
        try:
            not_misc[5] = int(row[41])
        except:
            not_misc[5] = 0

        misc = int(row[17]) - sum(int(votes) for votes in not_misc)
        entry = {"WKR_NR":row[0],"WKR_NAME":row[1],"eligible_voters":row[2],"union":union,"spd":row[25],"gruene":row[33],"afd":row[45],"linke":row[29],"fdp":row[41],"misc":str(misc)}
        content.append(entry)
    json.dump(content, feedsjson)
