import os
import json
import geojson

from Levenshtein import distance

FILE_PATH_GEOJSON = '1998GeometrieWahlkreise14DBT0.geojson'
FILE_PATH_RESULTS = "btw98_results.json"

OUTPUT_PATH = "F:/Repository/wcmpraktikum/Datasets/Combined/btw_98.geojson"

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
            r = getWKR(wkr['properties']['WKR_NAME'])
            mapping[wkr['properties']['WKR_NAME']] = getWKR(wkr['properties']['WKR_NAME'])['WKR_NAME']

            gj_feature = {}
            gj_feature['type'] = wkr['type']
            gj_feature['properties'] = wkr['properties']
            gj_feature['geometry'] = wkr['geometry']

            gj_feature['properties']['eligible_voters'] = r['eligible_voters']
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
