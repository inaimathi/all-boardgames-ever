# ALL BOARDGAMES EVER
###### Seriously, you guys.

This is a corpus and some minor data massaging of the [BoardGameGeek](http://boardgamegeek.com/) database. It was collected mostly from the [BGG Wayback archive](https://web.archive.org/web/*/http://files.boardgamegeek.com/snapshot/*), some light scraping of [BGGs' full boardgame list](http://boardgamegeek.com/browse/boardgame), and extensive use of the [BGG XML API](http://boardgamegeek.com/xmlapi).

### Included data

- The `snapshots/` directory contains [all historic snapshot XML files available at the Wayback Machine](https://web.archive.org/web/*/http://files.boardgamegeek.com/snapshot/*) (as of this writing, BGGs own current snapshot leads to a `404` page)
- The `tiny.json` file is a series of JSON objects each of which encodes the `rating`, `name`, `rank`, `voter-count`,`id` and `link` (the BGG page dedicated to that game) of a single game. It was collected by scraping the [full boardgame list](http://boardgamegeek.com/browse/boardgame)
- The `medium.json` file is a series of JSON objects reflecting most of the information provided from BGG's XML API `stats=1` option. It drops `ranks` and `boardgamepodcastepisode` elements, but everything else is present. `polls` are only present for games that have one or more responders. This corpus also omits what looked like an admin test game that was represented in the original database (there were issues decoding it with `xml.etree.ElementTree`).

### Included code

- `scrape.py` and `scratch.py` are the utilities used to scrape and re-format data. Please, PLEASE don't program like this in real life.
- `base-xaaqaeil` is a [cl-notebook](https://github.com/Inaimathi/cl-notebook#cl-notebook) base that contains a bunch of basic data munging I've been trying out
