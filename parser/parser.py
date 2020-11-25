import pandas as pd
import json
import re

input = "14111-01-03-4.csv"
with open(input, encoding='cp1252') as f:
    conv =  []
    for line in f:
        if(re.match("\d\d.\d\d.\d\d\d\d;\d", line)):
            line = re.sub("\n","",line)
            split = line.split(";")
            if len(split[1]) == 5 or str(split[1]) in ["02","04","11"]:
                conv.append(split)

dict = {"01":"Schleswig-Holstein",
        "02":"Hamburg",
        "03":"Niedersachsen",
        "04":"Bremen",
        "05":"Nordrhein-Westfalen",
        "06":"Hessen",
        "07":"Rheinland-Pfalz",
        "08":"Baden-Württemberg",
        "09":"Bayern",
        "10":"Saarland",
        "11":"Berlin",
        "12":"Brandenburg",
        "13":"Mecklenburg-Vorpommern",
        "14":"Sachsen",
        "15":"Sachsen-Anhalt",
        "16":"Thüringen"}

df = pd.DataFrame(conv)

with open("results.json", mode='w', encoding="utf-8") as feedsjson:
    list = []
    for index, row in df.iterrows():
        land_id = row[1][0:2]
        entry = {'date':row[0],'bundesland':dict[land_id],"name":row[2].strip().split(",")[0],"eligible_voters":row[3],"turnout":row[4],"voters":row[5],"cdu_csu":row[6],"spd":row[7],"gruene":row[8],"fdp":row[9],"linke":row[10],"afp":row[11],"misc":row[12]}
        list.append(entry)
    json.dump(list, feedsjson)
