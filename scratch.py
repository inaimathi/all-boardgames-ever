import xml.etree.ElementTree as ET
import re, os, json

def snapshot(fname):
    return ET.parse(fname).getroot().getchildren()

def allGamesIn(dirname):
    fs = os.listdir(dirname)
    for fname in fs:
        if fname.endswith("xml"):
            try:
                parsed = snapshot(os.path.join(dirname, fname))
                for game in parsed:
                    yield game
            except:
                print "FAILED", fname
                return

def bggToFb(key):
    keyTable = { "playingtime": "playing-time",
                 "minplayers": "minimum-players",
                 "maxplayers": "maximum-players",
                 "yearpublished": "year-published",
                 "usersrated": "users-rated",
                 "bayesaverage": "bayesian-average",
                 "stddev": "standard-deviation",
                 "numcomments": "num-comments",
                 "averageweight": "average-weight",
                 "suggested_playerage": "suggested-player-age",
                 "language_dependence": "language-dependence" }
    if keyTable.get(key):
        return keyTable[key]
    elif key.startswith("boardgame"):
        return key[9:]
    else:
        return key

def names(games, res={}):
    def inc(name):
        try:
            res[name]
            res[name] += 1
        except:
            res[name] = 1
    def tally(node):
        for c in node.getchildren():
            inc(c.tag)
            if c.getchildren():
                tally(c)
    for g in games:
        tally(g)
    return res

def ints():
    num = 0
    while True:
        yield num
        num += 1

def mInt(thing):
    try:
        return int(thing)
    except:
        None

def mFloat(thing):
    try:
        return float(thing)
    except:
        None

###### THIS IS UGLY, UGLY GARBAGE ####################
def pushVal(d, key, val):
    if d.get(key):
        d[key].append(val)
    else:
        d[key] = [val]

def gameToDict(game):
    res={ "polls": []}
    if game.tag == "game":
        res["bgg-id"] = mInt(game.attrib.get("gameid"))
    elif game.tag == "boardgame":
        res["bgg-id"] = mInt(game.attrib.get("objectid"))

    for node in game.getchildren():
        if node.tag in ["ranks", "boardgamepodcastepisode"]:
            None
        elif node.tag == "boardgameexpansion":
            if node.attrib.get("inbound"):
                pushVal(res, "expansion-of", node.text)
            else:
                pushVal(res, "expansion", node.text)            
        elif node.tag == "statistics":
            for c in node.getchildren()[0].getchildren():
                key = bggToFb(c.tag)
                val = c.text
                if not c.tag == "ranks":
                    if c.tag in ["minplayers", "maxplayers", "playingtime", "yearpublished", "age", "usersrated", "owned", "trading", "wanting", "wishing", "numcomments", "numweights"]:
                        res[key] = mInt(val)
                    else:
                        res[key] = mFloat(val)
        elif node.tag in ["minplayers", "maxplayers", "playingtime", "yearpublished", "age", "usersrated", "owned", "trading", "wanting", "wishing", "numcomments", "numweights"]:
            res[bggToFb(node.tag)] = mInt(node.text)
        elif node.tag in ["average", "bayesaverage", "stddev", "median", "averageweight"]:
            res[bggToFb(node.tag)] = mFloat(node.text)
        elif node.tag == "description":
            res[bggToFb(node.tag)] = node.text
        elif node.tag == "name" and node.attrib.get("primary"):
            res["primary-name"] = node.text
        elif node.tag == "publisher":
            pub = node.getchildren()[0].text
            pushVal(res, "publisher", pub)
        elif node.tag == "poll":
            total = mInt(node.attrib.get("totalvotes"))
            if total > 0:
                poll = { "total-votes": mInt(node.attrib.get("totalvotes")), "results": {}}
                if node.attrib.get("name") == "suggested_numplayers":
                    poll["name"] = "suggested-players"
                    for res_set in node.getchildren():
                        num = res_set.attrib.get("numplayers")
                        poll["results"][num] = {}
                        for r in res_set.getchildren():
                            poll["results"][num][r.attrib.get("value")] = mInt(r.attrib.get("numvotes"))
                else:
                    poll["name"] = bggToFb(node.attrib.get("name"))
                    for r in node.getchildren()[0].getchildren():
                        poll["results"][r.attrib.get("value")] = mInt(r.attrib.get("numvotes"))
                res["polls"].append(poll)
        else:
            pushVal(res, bggToFb(node.tag), node.text)
    if not res["polls"]:
        del res["polls"]
    return res
######################################################

def printNode(node, indent=""):
    for c in node.getchildren():
        cc = c.getchildren()
        print indent, c.tag, c.attrib, c.text
        if cc:
            printNode(c, indent + "   ")

def collate(dirname, fname):
    with open(fname, 'a') as db:
        ct = 0
        for g in allGamesIn(dirname):
            ct += 1
            try:
                obj = gameToDict(g)
                print obj.get("primary-name"), ct, "..."
                db.write(json.dumps(obj))
                db.write("\n")
                db.flush()
            except:
                print "FAILED on", g
                printNode(g, "   ")
                return
