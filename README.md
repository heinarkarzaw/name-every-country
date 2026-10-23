# Name Every Country

A geography game on a 3D globe: Free, Map, Flag and Learn modes for the 193 UN member states.
The finished game is one file, `index.html`. Open it in a browser, or upload it to any static host.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The finished game, ready to host (built from the files below) |
| `template.html` | All game code: HTML, CSS and JavaScript, with `__DATA__`, `__FLAGS__`, `__LEARN__` placeholders |
| `data.json` | Country borders, names, alias keys, regions, centre points, areas |
| `flags.json` | The 193 flags as SVG |
| `learn.json` | Official names, subregions, capitals and capital coordinates |
| `assemble.py` | Fills the placeholders and writes `country-game.html` |
| `standalone.py` | Wraps the page in a full HTML document, giving `index.html` |
| `build.py` | Rebuilds `data.json` from the original open data |
| `prep_extra.py` | Rebuilds `flags.json` and `learn.json` from the original open data |

## Change the game and rebuild

You only need Python 3.

```
python3 assemble.py
python3 standalone.py country-game.html index.html
```

Then upload the new `index.html` to your GitHub repository (Add file → Upload files). Vercel redeploys it.
Never edit `index.html` in GitHub's browser editor: the file is too big for it and gets saved empty.

## Rebuild the data from scratch (optional)

Clone these into one folder, then point `SRC_ROOT` at it:

```
git clone --depth 1 https://github.com/mledoze/countries mledoze/countries
git clone --depth 1 https://github.com/lipis/flag-icons lipis/flag-icons
# Natural Earth: only two files are needed from github.com/nvkelso/natural-earth-vector
#   geojson/ne_50m_admin_0_countries.geojson
#   geojson/ne_10m_populated_places_simple.geojson
#   saved as nvkelso/natural-earth-vector/geojson/<file>

SRC_ROOT=/path/to/that/folder python3 build.py
SRC_ROOT=/path/to/that/folder python3 prep_extra.py
python3 assemble.py
```

## Credits and licenses

- Country borders and capital coordinates: Natural Earth (public domain), naturalearthdata.com
- Country names, regions and capitals: mledoze/countries, Open Database License (ODbL) 1.0.
  `data.json` and `learn.json` are derived from it and are shared under the ODbL 1.0 as well.
  Changes: kept the 193 UN members, added name aliases, split the Americas into North and South America,
  and set some capitals by hand (Burundi: Gitega, Palau: Ngerulmud, Sri Lanka: Sri Jayawardenepura Kotte,
  Equatorial Guinea: Malabo, Nauru: Yaren, Ulaanbaatar spelling).
- Flags: flag-icons, © 2013 Panayiotis Lipiridis, MIT License
- 3D globe: globe.gl, © 2019 Vasco Asturiano, MIT License, built on three.js (MIT)
- Fonts: Bricolage Grotesque and JetBrains Mono, SIL Open Font License, via Google Fonts
