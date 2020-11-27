import os
import json
import geojson

from Levenshtein import distance

FILE_PATH_GEOJSON = 'wahlkreise.geojson'
FILE_PATH_RESULTS = "results.json"


with open(FILE_PATH_GEOJSON, encoding='utf-8') as f:
    gj = geojson.load(f)

with open(FILE_PATH_RESULTS, encoding='utf-8') as f:
    resultsjson = json.load(f)


def main():
    wkr_names = [i for i in gj['features']]
    results = [res for res in resultsjson]



    with open('wahlkreise_results_2018.geojson', "w") as f:
        new = {}
        new['type'] = gj['type']
        new['crs'] = gj['crs']
        new['features'] = []

        i=0
        for wkr in wkr_names:
            gj_feature = {}
            gj_feature['type'] = wkr['type']
            gj_feature['properties'] = wkr['properties']
            gj_feature['geometry'] = wkr['geometry']

            gj_feature['properties']['eligible_voters'] = results[i].get('eligible_voters')
            gj_feature['properties']['union'] = results[i].get('union')
            gj_feature['properties']['spd'] = results[i].get('spd')
            gj_feature['properties']['gruene'] = results[i].get('gruene')
            gj_feature['properties']['afd'] = results[i].get('afd')
            gj_feature['properties']['linke'] = results[i].get('linke')
            gj_feature['properties']['fdp'] = results[i].get('fdp')
            gj_feature['properties']['misc'] = results[i].get('misc')
            i+=1

            new['features'].append(gj_feature)

        f.write(json.dumps(new))
if __name__ == "__main__":
    main()
