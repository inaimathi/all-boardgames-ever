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
def gameToDict(game):
    res={ "polls": []}
    if game.tag == "game":
        res["bgg-id"] = mInt(game.attrib.get("gameid"))
    elif game.tag == "boardgame":
        res["bgg-id"] = mInt(game.attrib.get("objectid"))
    for node in game.getchildren():
        if node.tag in ["ranks", "boardgamepodcastepisode"]:
            None
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
            if res.get("publisher"):
                res["publisher"] = res["publisher"].append(pub)
            else:
                res["publisher"] = [pub]
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
            key = bggToFb(node.tag)
            val = node.text
            if res.get(key):
                res[key].append(val)
            else:
                res[key] = [val]
    if not res["polls"]:
        del res["polls"]
    return res
######################################################

class Base:
    def __init__(self, fname):
        self.__gen = ints()
        self.id = 0
        self.base = []
        self.fname = fname

    def write(self):
        with open(fname, 'a') as f:
            for fact in self.base:
                f.write(json.dumps(fact))

    def fresh_id(self):
        self.id = self.__gen.next()
        return self.id

    def addGame(self, node):
        entry_id = self.fresh_id()
        if node.tag == "game":
            self.base.append([entry_id, "bgg-id", mInt(node.attrib.get("gameid"))])
        elif node.tag == "boardgame":
            self.base.append([entry_id, "bgg-id", mInt(node.attrib.get("objectid"))])
        for c in node.getchildren():
            self.addFact(c, entry_id)

    def addFact(self, node, entry_id):
        if node.tag in ["ranks", "boardgamepodcastepisode"]:
            None
        elif node.tag in ["statistics", "ratings"]:
            for c in node.getchildren():
                self.addFact(c, entry_id)
        elif node.tag == "poll":
            self.addPoll(node, entry_id)
        elif node.tag == "name" and node.attrib.get("primary"):
            self.base.append([entry_id, "primary-name", node.text])
            self.base.append([entry_id, node.tag, node.text])
        elif node.tag in ["minplayers", "maxplayers", "playingtime", "yearpublished", "age", "usersrated", "owned", "trading", "wanting", "wishing", "numcomments", "numweights"]:
            self.base.append([entry_id, bggToFb(node.tag), mInt(node.text)])
        elif node.tag in ["average", "bayesaverage", "stddev", "median", "averageweight"]:
            self.base.append([entry_id, bggToFb(node.tag), mFloat(node.text)])
        elif node.tag == "publisher" and node.getchildren():
            self.base.append([entry_id, node.tag, node.getchildren()[0].text])
        else:
            self.base.append([entry_id, bggToFb(node.tag), node.text])

    def addPoll(self, node, entry_id):
        poll_id = self.fresh_id()
        self.base.append([poll_id, "poll", node.attrib.get("title")])
        self.base.append([poll_id, "relates-to", entry_id])
        self.base.append([poll_id, "total-votes", mInt(node.attrib.get("totalvotes"))])

        if node.attrib.get("name") == "suggested_numplayers":
            self.base.append([entry_id, "suggested-players", "Woo!"])
            for res_set in node.getchildren():
                for res in res_set.getchildren():
                    self.base.append([poll_id, (res.attrib.get("value"), res_set.attrib.get("numplayers")), mInt(res.attrib.get("numvotes"))])
        else:
            for res in node.getchildren()[0].getchildren():
                self.base.append([poll_id, res.attrib.get("value"), mInt(res.attrib.get("numvotes"))])

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
