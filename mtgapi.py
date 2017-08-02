from flask import Flask, jsonify
import urllib
import shutil
import zipfile
import os
import json
import hashlib

mtgJsonUrl = 'https://mtgjson.com/json/AllSets-x.json.zip'
dataDir = './data/'
dataFile = 'AllSets-x.json'

application = Flask(__name__)

multiverseIdDict = dict()


@application.route("/update-data", methods=['POST'])
def updatedata(datafolder=dataDir):
    mtgjsonzip = datafolder + 'mtgson.zip'
    if not os.path.exists(datafolder):
        os.makedirs(datafolder)
    with urllib.request.urlopen(mtgJsonUrl) as response, open(mtgjsonzip, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(mtgjsonzip, 'r') as zip_ref:
        zip_ref.extractall(datafolder)
    os.remove(mtgjsonzip)
    return "done"


def load_data_in_cache(datafolder=dataDir, datafile=dataFile):
    mtgjson = datafolder + datafile
    if not os.path.exists(mtgjson):
        updatedata(datafolder)
    with open(mtgjson, encoding="utf-8") as data_file:
        allcards = json.load(data_file)
    for set in allcards:
        for card in allcards[set]['cards']:
            if 'multiverseid' in card.keys():
                multiverseIdDict[hashlib.md5(card['name'].encode('utf-8')).hexdigest()] = card['multiverseid']


@application.route("/")
@application.route("/<card_name>")
def getcardimageurl(card_name="Black Lotus"):
    if not multiverseIdDict:
        load_data_in_cache()
    return jsonify(multiverseIdDict[hashlib.md5(card_name.encode('utf-8')).hexdigest()])


if __name__ == "__main__":
    application.run(host='0.0.0.0', port='6666')
