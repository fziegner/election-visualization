import os
import json
import geojson

from Levenshtein import distance

FILE_PATH_GEOJSON = 'test2.geojson'
FILE_PATH_RESULTS = "ew04_results.json"

OUTPUT_PATH = "ew_2004.geojson"

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
        if(data["WKR_NR"] == id):
            return data

def main():
    wkr_names = [i for i in gj['features']]
    results = [res for res in resultsjson]

    with open(OUTPUT_PATH, "w") as f:
        new = {}
        new['type'] = gj['type']
        new['crs'] = gj['crs']
        new['features'] = []
        mapping = {}
        i=0
        for wkr in wkr_names:
            id = wkr["properties"]["RS"]
            r = getData(id)
            if r:
                gj_feature = {}
                gj_feature['type'] = wkr['type']
                gj_feature['properties'] = wkr['properties']
                gj_feature['geometry'] = wkr['geometry']

                gj_feature['properties']['WKR_NAME'] = r['WKR_NAME']
                gj_feature['properties']['LAND_NAME'] = land_dict[id[0:2]]
                gj_feature['properties']['eligible_voters'] = r['total_votes'] # !!! I changed eligible_voters to total_votes in the parser of the EW files !!!
                gj_feature['properties']['union'] = r['union']
                gj_feature['properties']['spd'] = r['spd']
                gj_feature['properties']['gruene'] = r['gruene']
                gj_feature['properties']['afd'] = r['afd']
                gj_feature['properties']['linke'] = r['linke']
                gj_feature['properties']['fdp'] = r['fdp']
                gj_feature['properties']['misc'] = r['misc']
                i+=1

                new['features'].append(gj_feature)

        f.write(json.dumps(new))
if __name__ == "__main__":
    main()
