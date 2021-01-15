import os
import json
import geojson

from Levenshtein import distance

FILE_PATH_GEOJSON = 'F:/Repository/wcmpraktikum/Datasets/Wahlkreise_geojson/2017GeometrieWahlkreise19DBT5.geojson'
FILE_PATH_RESULTS = "F:/Repository/wcmpraktikum/Datasets/Wahlergebnisse/btw17_results.json"

OUTPUT_PATH = "F:/Repository/wcmpraktikum/Datasets/Combined/btw_2017.geojson"

# Mode: btw, ew
MODE = "btw"


with open(FILE_PATH_GEOJSON, encoding='utf-8') as f:
    gjson = geojson.load(f)

with open(FILE_PATH_RESULTS, encoding='utf-8') as f:
    resultsjson = json.load(f)

# Input geojson feature object
# with geometry, type
# and properties: LAND_NAME, LAND_NR, WKR_NAME, WKR_NR
def getWKR(wkr):
    results = [res for res in resultsjson]
    candidates = []

    wkr_nr = wkr['properties']['WKR_NR']
    wkr_name = wkr['properties']['WKR_NAME']

    # First try to match geojson feature wkr to wkr in resultsjson per WKR_ID
    for res in resultsjson:
        if res['WKR_NR'] == wkr_nr:
            #print("match")
            #print(wkr_name)
            #print(res['WKR_NAME'])
            return res

    #If not found, try to match over WKR_NAME
    for res in resultsjson:
        wkr_name = wkr_name.upper()
        wkr_name = wkr_name.replace('-', ' ')
        wkr_name = wkr_name.replace('Ä', 'AE')
        wkr_name = wkr_name.replace('Ö', 'OE')
        wkr_name = wkr_name.replace('Ü', 'UE')
        wkr_name = wkr_name.replace('ß', ' ')
        wkr_name = wkr_name.replace('AE', ' ')
        wkr_name = wkr_name.replace('UE', ' ')
        wkr_name = wkr_name.replace('OE', ' ')

        res_name = res['WKR_NAME']
        res_name = res_name.upper()
        res_name = res_name.replace('-', ' ')
        res_name = res_name.replace('Ä', 'AE')
        res_name = res_name.replace('Ö', 'OE')
        res_name = res_name.replace('Ü', 'UE')
        res_name = res_name.replace('ß', ' ')
        res_name = res_name.replace('AE', ' ')
        res_name = res_name.replace('UE', ' ')
        res_name = res_name.replace('OE', ' ')

        # if distance of WKR_NAME and option is 0, return this resultsjson wkr
        if distance(wkr_name, res_name) == 0:
            #print("match")
            #print(wkr_name)
            #print(res_name)
            return res
        # if not found, take next option with distance under 2 -> Umlaute are replaced with whitespace so distance between potential ü and _ is 2
        elif distance(wkr_name, res_name) <= 2:
            #print("match")
            #print("Candidate: " + res_name)
            return res

    # if no match is found return None
    #print("\nNo match found for: " + str(wkr_name) + "\n")
    return None


def main():
    print("Number of gejson-features " + str(len(gjson['features'])))
    print("Number of result objects " + str(len(resultsjson)))
    errors = []
    i = 0

    with open(OUTPUT_PATH, "w") as out:
        new = {}
        new['type'] = gjson['type']
        new['crs'] = gjson['crs']
        new['features'] = []

        for f in gjson['features']:
            if getWKR(f):
                i+=1
                wkr = getWKR(f)
                #print(f)
                #print(wkr)

                feature = {}
                feature['type'] = f['type']
                feature['properties'] = f['properties']
                feature['geometry'] = f['geometry']

                feature['properties']['eligible_voters'] = wkr['eligible_voters']
                feature['properties']['union'] = wkr['union']
                feature['properties']['spd'] = wkr['spd']
                feature['properties']['grune'] = wkr['gruene']
                feature['properties']['afd'] = wkr['afd']
                feature['properties']['linke'] = wkr['linke']
                feature['properties']['fdp'] = wkr['fdp']
                feature['properties']['misc'] = wkr['misc']

                new['features'].append(feature)

            else:
                errors.append(f['properties']['WKR_NAME'])


        out.write(json.dumps(new))

    print("Matches found: " + str(i))
    print("No matches found for: " + str(errors))

if __name__ == "__main__":
    main()
