from subprocess import call
import sys, os, re, requests, cssselect, lxml.html, json

def group_by(seq, by=1):
    res = []
    for elem in seq:
        res.append(elem)
        if len(res) == by:
            yield res
            res = []
    if res:
        yield res

def __str(node):
    return node.text_content().strip()

def __bggPage(relative):
    return lxml.html.fromstring(requests.get("http://boardgamegeek.com/" + relative).content)

def __rankPage(ct):
    return __bggPage("browse/boardgame/page/" + str(ct))

def extractGames(page, f):
    rows = page.cssselect("#collectionitems > tr")
    res = []
    for r in rows[1:]:
        tds = r.cssselect("td")
        name = __str(tds[2].cssselect("a")[0])
        print "    ", name
        entry = json.dumps({"rank": __str(tds[0]), 
                            "name": name, 
                            "id": tds[2].cssselect("a")[0].attrib["href"].split("/")[2],
                            "link": tds[2].cssselect("a")[0].attrib["href"],
                            "rating": __str(tds[3]), 
                            "voter-count": __str(tds[5])})
        f.write(entry)
        f.write("\n")
    f.flush()

def allIds(fname):
    with open(fname, 'r') as db:
        return [json.loads(line)["id"] for line in db]

def minimalInfo(fname, start, end):
    with open(fname, "a") as db:
        for i in xrange(start, end+1):
            print "Getting page", i
            pg = __rankPage(i)
            extractGames(pg, db)

def inDepthInfo(all_ids, by=20):
    for r in group_by(all_ids, by):
        ids = ",".join((str(i) for i in r))
        call(["wget", "http://boardgamegeek.com/xmlapi/boardgame/" + ids + "?stats=1","-O", str(r[0])+"-to-"+str(r[-1])+".xml"])
