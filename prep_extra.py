# Builds flags.json (193 minified SVG flags) and learn.json (official name, subregion, capital, coordinates).
# Needs the same source repositories as build.py, plus lipis/flag-icons.
import json, os, re, unicodedata

ROOT = os.environ.get('SRC_ROOT', '/home/claude')   # folder holding the cloned data repositories
meta = {m['cca3']: m for m in json.load(open(f'{ROOT}/mledoze/countries/countries.json'))}
codes = json.load(open('data.json'))['countries'].keys()

# flags
flags = {}
for c in codes:
    svg = open(f"{ROOT}/lipis/flag-icons/flags/4x3/{meta[c]['cca2'].lower()}.svg").read()
    flags[c] = re.sub(r'>\s+<', '><', svg).strip()
json.dump(flags, open('flags.json', 'w'), separators=(',', ':'), ensure_ascii=False)

# capitals: match mledoze's capital name to a Natural Earth capital city of that country
def n(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
    return s.lower().replace('-', ' ').replace("'", '')
places = json.load(open(f'{ROOT}/nvkelso/natural-earth-vector/geojson/ne_10m_populated_places_simple.geojson'))
byc = {}
for f in places['features']:
    p = f['properties']
    if p['featurecla'] in ('Admin-0 capital', 'Admin-0 capital alt'):
        byc.setdefault(p['adm0_a3'], []).append(p)
caps = {}
for c in codes:
    name = (meta[c].get('capital') or [''])[0]
    cands = byc.get(c, [])
    hit = [x for x in cands if n(name) in (n(x['name']), n(x['nameascii'])) or n(name) in n(x['namealt'] or '')]
    pick = hit[0] if hit else max((x for x in cands if x['featurecla'] == 'Admin-0 capital'), key=lambda x: x['pop_max'], default=None)
    if pick:
        caps[c] = [name or pick['name'], round(pick['latitude'], 4), round(pick['longitude'], 4)]
# hand corrections
caps['BDI'] = ['Gitega', -3.4271, 29.9246]
caps['GNQ'] = ['Malabo', caps['GNQ'][1], caps['GNQ'][2]]
caps['PLW'] = ['Ngerulmud', 7.5006, 134.6242]
caps['NRU'] = ['Yaren', -0.5477, 166.9209]
caps['MNG'][0] = 'Ulaanbaatar'
caps['LKA'] = ['Sri Jayawardenepura Kotte', 6.9022, 79.9087]
assert len(caps) == 193, len(caps)
learn = {c: [meta[c]['name']['official'], meta[c].get('subregion') or meta[c]['region'], *caps[c]] for c in codes}
json.dump(learn, open('learn.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('flags', len(flags), 'learn', len(learn))
