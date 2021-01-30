import json
import re

import pandas as pd

input_csv = "../Datasets/Wahlergebnisse/btw09_kerg.csv"
output_json = "../Datasets/Wahlergebnisse/btw09_results.json"
land_list = ["Schleswig-Holstein", "Hamburg", "Niedersachsen", "Bremen", "Nordrhein-Westfalen", "Hessen",
             "Rheinland-Pfalz", "Baden-Württemberg", "Bayern", "Saarland", "Berlin", "Brandenburg",
             "Mecklenburg-Vorpommern", "Sachsen", "Sachsen-Anhalt", "Thüringen", "Bundesgebiet"]

# Indices = CSU, CDU, SPD, Gruene, AfD, Linke, FDP
indices_dict = {"btw17": [37, 21, 25, 33, 45, 29, 41], "btw13": [41, 21, 25, 37, 105, 33, 29],
                "btw09": [41, 25, 21, 37, 99999, 33, 29], "btw05": [29, 25, 21, 33, 99999, 41, 37],
                "btw02": [14, 12, 10, 16, 99999, 20, 18], "btw98": [14, 12, 10, 16, 99999, 20, 18]}
year = input_csv.split("/")[-1].split("_")[0]

enc = "utf-8" if year in ["btw17", "btw13", "btw09"] else "cp1252"
with open(input_csv, mode="r", encoding=enc, errors="ignore") as f:
    conv = []
    for line in f:
        if re.match(r"(\d)?(\d)?\d;", line):
            line = re.sub("\n", "", line)
            split = line.split(";")
            if split[1] not in land_list:  # filter Bundesland/Bundesgebiet results
                conv.append(split)

df = pd.DataFrame(conv)

with open(output_json, mode='w', encoding="utf-8") as f:
    content = []
    for _, row in df.iterrows():
        not_misc = []
        for ind in indices_dict[year]:
            try:
                not_misc.append(int(row[ind]))
            except (ValueError, KeyError):
                not_misc.append(0)

        total_votes = row[9] if year == "btw17" else row[17] if year in ["btw13", "btw09", "btw05"] else row[8]
        misc = int(total_votes) - sum(int(votes) for votes in not_misc)
        entry = {"WKR_NR": row[0],
                 "WKR_NAME": row[1],
                 "eligible_voters": row[5] if year == "btw17" else row[3],
                 "total_votes": total_votes,
                 "union": str(not_misc[0]) if row[2] in ["9", "909"] else str(not_misc[1]),
                 "spd": str(not_misc[2]),
                 "gruene": str(not_misc[3]),
                 "afd": str(not_misc[4]),
                 "linke": str(not_misc[5]),
                 "fdp": str(not_misc[6]),
                 "misc": str(misc)}
        content.append(entry)

    json.dump(content, f)
