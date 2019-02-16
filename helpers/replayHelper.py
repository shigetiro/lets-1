import os

from common import generalUtils
from constants import exceptions, dataTypes
from helpers import binaryHelper
from objects import glob

def buildFullReplay(scoreID=None, scoreData=None, rawReplay=None, relax):
    if all(v is None for v in (scoreID, scoreData)) or all(v is not None for v in (scoreID, scoreData)):
        raise AttributeError("Either scoreID or scoreData must be provided, not neither or both")

    if relax is None:
        raise AttributeError("Not specified whether the replay is relax or regular. WILL NOT BUILD REPLAY!")

    if scoreData is None:
        scoreData = glob.db.fetch(
            "SELECT scores{relax}.*, users.username FROM scores LEFT JOIN users ON scores{relax}.userid = users.id WHERE scores{relax}.id = {scoreID}".format(scoreID=scoreID, relax="_relax" if relax == 1 else ""))
    else:
        scoreID = scoreData["id"]
    if scoreData is None or scoreID is None:
        raise exceptions.scoreNotFoundError()

    if rawReplay is None:
        # Make sure raw replay exists
        fileName = ".data/replays/replay_{}.osr".format(scoreID)
        if not os.path.isfile(fileName):
            raise FileNotFoundError()

        # Read raw replay
        with open(fileName, "rb") as f:
            rawReplay = f.read()

    # Calculate missing replay data
    rank = generalUtils.getRank(int(scoreData["play_mode"]), int(scoreData["mods"]), int(scoreData["accuracy"]),
                                int(scoreData["300_count"]), int(scoreData["100_count"]), int(scoreData["50_count"]),
                                int(scoreData["misses_count"]))
    magicHash = generalUtils.stringMd5(
        "{}p{}o{}o{}t{}a{}r{}e{}y{}o{}u{}{}{}".format(int(scoreData["100_count"]) + int(scoreData["300_count"]),
                                                      scoreData["50_count"], scoreData["gekis_count"],
                                                      scoreData["katus_count"], scoreData["misses_count"],
                                                      scoreData["beatmap_md5"], scoreData["max_combo"],
                                                      "True" if int(scoreData["full_combo"]) == 1 else "False",
                                                      scoreData["username"], scoreData["score"], rank,
                                                      scoreData["mods"], "True"))
    # Add headers (convert to full replay)
    fullReplay = binaryHelper.binaryWrite([
        [scoreData["play_mode"], dataTypes.byte],
        [20150414, dataTypes.uInt32],
        [scoreData["beatmap_md5"], dataTypes.string],
        [scoreData["username"], dataTypes.string],
        [magicHash, dataTypes.string],
        [scoreData["300_count"], dataTypes.uInt16],
        [scoreData["100_count"], dataTypes.uInt16],
        [scoreData["50_count"], dataTypes.uInt16],
        [scoreData["gekis_count"], dataTypes.uInt16],
        [scoreData["katus_count"], dataTypes.uInt16],
        [scoreData["misses_count"], dataTypes.uInt16],
        [scoreData["score"], dataTypes.uInt32],
        [scoreData["max_combo"], dataTypes.uInt16],
        [scoreData["full_combo"], dataTypes.byte],
        [scoreData["mods"], dataTypes.uInt32],
        [0, dataTypes.byte],
        [0, dataTypes.uInt64],
        [rawReplay, dataTypes.rawReplay],
        [0, dataTypes.uInt32],
        [0, dataTypes.uInt32],
    ])

    # Return full replay
    return fullReplay