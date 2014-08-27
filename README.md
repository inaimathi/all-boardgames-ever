# ALL BOARDGAMES EVER
###### Seriously, you guys.

This is a corpus and some minor data massaging of the [BoardGameGeek](http://boardgamegeek.com/) database. It was collected mostly from the [BGG Wayback archive](https://web.archive.org/web/*/http://files.boardgamegeek.com/snapshot/*), some light scraping of [BGGs' full boardgame list](http://boardgamegeek.com/browse/boardgame), and extensive use of the [BGG XML API](http://boardgamegeek.com/xmlapi).

### Included data

- The `snapshots/` directory contains [all historic snapshot XML files available at the Wayback Machine](https://web.archive.org/web/*/http://files.boardgamegeek.com/snapshot/*) (as of this writing, BGGs own current snapshot link leads to a `404` page)
- The `tiny.json` file is a series of JSON objects each of which encodes the `rating`, `name`, `rank`, `voter-count`,`id` and `link` (the BGG page dedicated to that game) of a single game. It was collected by scraping the [full boardgame list](http://boardgamegeek.com/browse/boardgame)
- The `medium.json.tar.gz` file is a series of JSON objects reflecting most of the information provided from BGG's XML API `stats=1` option. It drops `ranks` and `boardgamepodcastepisode` elements, but everything else is present. `polls` are only present for games that have one or more responders. This corpus also omits what looked like an admin test game that was represented in the original database (there were issues decoding it with `xml.etree.ElementTree`). It's compressed because the raw file is something like 130 mb
- The `medium.base.tar.gz` file is the same corpus as `medium.json.tar.gz`, but encoded in [`fact-base`](https://github.com/Inaimathi/fact-base) format.
- `games.tar.gz` contains 3403 `.xml` files. It represents the raw XML output of BGGs' API requests.

### Included code

- `scrape.py` and `scratch.py` are the utilities used to scrape and re-format data. Please, PLEASE don't program like this in real life.
- `base-xaaqaeil` is a [cl-notebook](https://github.com/Inaimathi/cl-notebook#cl-notebook) file that contains a bunch of basic data selections I've been trying out

### Various Notes

- In `scratch.py`, you'll find a procedure called `collate` which was used to generate `medium.json` from the (decompressed) XML files found in `games.tar.gz`. If you want this data in a different format, looking at that may or may not be a good idea.
- Don't trust the corpus unconditionally. In particular, there are a lot more games released in year `0` than you'd think there would be. I hypothesize that `year-published: 0` actually means "We have no fucking clue when this was published".
- This repository was, obviously, generated using data sourced from [BoardGameGeek](http://boardgamegeek.com), and BoardGameGeek via [the Internet Archive](https://web.archive.org/). It is consequently released under [insert license here]
