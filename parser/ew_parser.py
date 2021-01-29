import json
import re

import pandas as pd

input_csv = "../Datasets/Wahlergebnisse/ew14_kerg.csv"
output_json = "../Datasets/Wahlergebnisse/ew14_results.json"
land_list = ["Schleswig-Holstein", "Hamburg", "Niedersachsen", "Bremen", "Nordrhein-Westfalen", "Hessen",
             "Rheinland-Pfalz", "Baden-Württemberg", "Bayern", "Saarland", "Berlin", "Brandenburg",
             "Mecklenburg-Vorpommern", "Sachsen", "Sachsen-Anhalt", "Thüringen", "Bundesgebiet"]


# Indices = CSU, CDU, SPD, Gruene, AfD, Linke, FDP
indices_dict = {"ew19": [21, 11, 13, 15, 19, 17, 23], "ew14": [21, 11, 13, 15, 51, 19, 17],
                "ew09": [17, 11, 13, 15, 99999, 19, 21], "ew04": [8, 6, 7, 9, 99999, 10, 11]}
year = input_csv.split("/")[-1].split("_")[0]

enc = "utf-8" if year != "ew04" else "cp1252"
with open(input_csv, mode="r", encoding=enc, errors="ignore") as f:
    conv = []
    for line in f:
        if re.match(r"\d\d\d\d(\d)?;|\d\d \d \d\d;", line):
            line = re.sub("\n", "", line)
            split = line.split(";")
            if split[1] not in land_list:  # filter Bundesland/Bundesgebiet results
                conv.append(split)

df = pd.DataFrame(conv)

with open(output_json, mode='w', encoding="utf-8") as feedsjson:
    content = []
    for index, row in df.iterrows():
        not_misc = []
        for ind in indices_dict[year]:
            try:
                not_misc.append(int(row[ind]))
            except (ValueError, KeyError):
                not_misc.append(0)

        misc = int(row[9]) - sum(int(votes) for votes in not_misc) if year != "ew04" else int(row[5]) - sum(int(votes) for votes in not_misc)
        entry = {"WKR_NR": row[0],
                 "WKR_NAME": row[1],
                 "eligible_voters": row[3] if year != "ew04" else row[2],
                 "total_votes": row[9] if year != "ew04" else row[5],
                 "union": str(not_misc[0]) if row[2] == "9" else str(not_misc[1]) if year != "ew04" else str(not_misc[0]) if row[0].startswith("09") else str(not_misc[1]),
                 "spd": str(not_misc[2]),
                 "gruene": str(not_misc[3]),
                 "afd": str(not_misc[4]),
                 "linke": str(not_misc[5]),
                 "fdp": str(not_misc[6]),
                 "misc": str(misc)}
        content.append(entry)

    json.dump(content, feedsjson)
