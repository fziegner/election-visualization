import os
import json
import geojson
from difflib import SequenceMatcher

from Levenshtein import distance

FILE_PATH_GEOJSON = "../Datasets/Wahlkreise_geojson/EW2014GeometrieWahlkreise.geojson"
FILE_PATH_RESULTS = "../Datasets/Wahlergebnisse/ew14_results.json"

OUTPUT_PATH = "../Datasets/Combined/ew_2014.geojson"

MODE = OUTPUT_PATH.split("/")[-1].split("_")[0]
YEAR = int(OUTPUT_PATH.split("_")[1][:4])
print(YEAR)

land_dict = {
    "01": "Schleswig-Holstein",
    "02": "Hamburg",
    "03": "Niedersachsen",
    "04": "Bremen",
    "05": "Nordrhein-Westfalen",
    "06": "Hessen",
    "07": "Rheinland-Pfalz",
    "08": "Baden-Württemberg",
    "09": "Bayern",
    "10": "Saarland",
    "11": "Berlin",
    "12": "Brandenburg",
    "13": "Mecklenburg-Vorpommern",
    "14": "Sachsen",
    "15": "Sachsen-Anhalt",
    "16": "Thüringen"
}


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

with open(FILE_PATH_GEOJSON, encoding='utf-8') as f:
    gj = geojson.load(f)

with open(FILE_PATH_RESULTS, encoding='utf-8') as f:
    resultsjson = json.load(f)

def getWKR(wkr_name):
    results = [res for res in resultsjson]
    candidates = []

    for wkr in results:
        if(wkr['WKR_NAME'] == wkr_name):
            return wkr

        if distance(wkr['WKR_NAME'], wkr_name) <= 2:
            candidates.append(wkr)


    if len(candidates) != 0:
        variable=1
        if variable == '':
            variable = 1
        return candidates[int(variable)-1]
    else:
        r = {'WKR_NR': '', 'WKR_NAME':'', 'eligible_voters':'', 'union':'', 'spd':'', 'gruene':'', 'afd':'', 'linke':'', 'fdp':'', 'misc':''}
        return r

def getData(id):
    results = [res for res in resultsjson]
    for data in results:
        if data["WKR_NR"].replace(" ", "") == id:
            return data

def main():
    wkr_names = [i for i in gj['features']]
    #print(wkr_names)
    results = [res for res in resultsjson]

    with open(OUTPUT_PATH, "w") as f:
        new = {'features': []}
        i = 0
        for wkr in wkr_names:
            if YEAR in [2019, 2009, 2014]:
                new['type'] = gj['type']
                new['crs'] = gj['crs']
                new["parameters"] = {"election_type": MODE, "election_year": YEAR}
                id_ = wkr["properties"]["RS"].replace(" ", "")
                print(id_)
                r = getData(id_)
                if YEAR in [2009, 2014]:
                    if id_.startswith("0"):
                        r = getData(id_[1:])
                print(r)
                if r:
                    gj_feature = {}
                    gj_feature['type'] = wkr['type']
                    gj_feature['properties'] = wkr['properties']
                    gj_feature['geometry'] = wkr['geometry']

                    gj_feature['properties']['WKR_NAME'] = r['WKR_NAME']
                    gj_feature['properties']['LAND_NAME'] = land_dict[id_[0:2]]
                    gj_feature['properties']['eligible_voters'] = r['eligible_voters']
                    gj_feature['properties']['total_votes'] = r['total_votes']
                    gj_feature['properties']['union'] = r['union']
                    gj_feature['properties']['spd'] = r['spd']
                    gj_feature['properties']['gruene'] = r['gruene']
                    gj_feature['properties']['afd'] = r['afd']
                    gj_feature['properties']['linke'] = r['linke']
                    gj_feature['properties']['fdp'] = r['fdp']
                    gj_feature['properties']['misc'] = r['misc']
                    i += 1

                    new['features'].append(gj_feature)
            else:
                new["parameters"] = {"election_type": MODE, "election_year": YEAR}
                gj_name = wkr["properties"]["NAME_3"].replace(" Städte", ", Stadt")
                match = False
                save = None
                for res in resultsjson:
                    res_name = res["WKR_NAME"].split(",")[0]
                    if gj_name == res_name:
                        match = True
                        save = res
                if not match:
                    sim = 0
                    for res in resultsjson:
                        res_name = res["WKR_NAME"].split(",")[0]
                        if similar(gj_name, res_name) > sim:
                            sim = similar(gj_name, res_name)
                            save = res
                gj_feature = {}
                gj_feature['type'] = wkr['type']
                gj_feature['properties'] = wkr['properties']
                gj_feature['geometry'] = wkr['geometry']

                gj_feature['properties']['WKR_NAME'] = save['WKR_NAME']
                gj_feature['properties']['LAND_NAME'] = wkr["properties"]["NAME_1"]
                gj_feature['properties']['eligible_voters'] = save['eligible_voters']
                gj_feature['properties']['total_votes'] = save['total_votes']
                gj_feature['properties']['union'] = save['union']
                gj_feature['properties']['spd'] = save['spd']
                gj_feature['properties']['gruene'] = save['gruene']
                gj_feature['properties']['afd'] = save['afd']
                gj_feature['properties']['linke'] = save['linke']
                gj_feature['properties']['fdp'] = save['fdp']
                gj_feature['properties']['misc'] = save['misc']

                new['features'].append(gj_feature)

        f.write(json.dumps(new))


if __name__ == "__main__":
    main()
