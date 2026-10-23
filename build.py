import json, unicodedata, re, sys

import os
ROOT = os.environ.get('SRC_ROOT', '/home/claude')   # folder holding the cloned data repositories
geo = json.load(open(f'{ROOT}/nvkelso/natural-earth-vector/geojson/ne_50m_admin_0_countries.geojson'))
meta = json.load(open(f'{ROOT}/mledoze/countries/countries.json'))

def norm(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = s.replace('&', 'and').replace('saint ', 'st ').replace('st. ', 'st ')
    s = re.sub(r'^the ', '', s)
    return re.sub(r'[^a-z]', '', s)

EXTRA = {
    'MMR': ['Burma'], 'USA': ['USA', 'America', 'United States of America', 'The States'],
    'GBR': ['UK', 'Britain', 'Great Britain', 'England', 'United Kingdom of Great Britain and Northern Ireland'],
    'CIV': ["Cote d'Ivoire"], 'CZE': ['Czech Republic'], 'SWZ': ['Swaziland'], 'MKD': ['Macedonia'],
    'TUR': ['Turkey'], 'TLS': ['East Timor'], 'CPV': ['Cabo Verde'], 'COD': ['Democratic Republic of the Congo', 'DRC', 'Congo Kinshasa', 'Zaire'],
    'COG': ['Republic of the Congo', 'Congo Brazzaville'], 'PRK': ['DPRK', 'Korea North'], 'KOR': ['Korea', 'Korea South', 'ROK'],
    'LAO': ['Lao'], 'VNM': ['Viet Nam'], 'RUS': ['Russian Federation'], 'SYR': ['Syrian Arab Republic'],
    'ARE': ['UAE', 'Emirates'], 'BIH': ['Bosnia', 'Bosnia Herzegovina'], 'KNA': ['St Kitts', 'Saint Kitts', 'St Kitts and Nevis'],
    'VCT': ['St Vincent', 'Saint Vincent'], 'LCA': ['St Lucia'], 'STP': ['Sao Tome'], 'FSM': ['Federated States of Micronesia'],
    'NLD': ['Holland'], 'GNB': ['Guinea Bissau'], 'TTO': ['Trinidad', 'Trinidad Tobago'], 'ATG': ['Antigua'],
    'PNG': ['Papua'], 'CAF': ['CAR'], 'DOM': ['DR', 'Dominican Rep'], 'BRN': ['Brunei Darussalam'], 'IRN': ['Persia'],
    'LKA': ['Ceylon'], 'KHM': ['Kampuchea'], 'BOL': ['Bolivia'], 'TZA': ['Tanzania'], 'MDA': ['Moldova'], 'VEN': ['Venezuela'],
    'GMB': ['The Gambia'], 'BHS': ['The Bahamas'], 'PHL': ['Phillipines', 'Philipines'], 'KGZ': ['Kirgizstan', 'Kyrgyz Republic'],
    'NZL': ['NZ', 'Aotearoa'], 'SAU': ['KSA'], 'CHE': ['Swiss Confederation'], 'IRL': ['Eire'],
}
# NE feature code -> quiz country code (pieces drawn as part of a country)
FEATURE_ALIAS = {'SDS': 'SSD', 'SOL': 'SOM', 'CYN': 'CYP', 'KAS': 'IND'}

countries = {}
for m in meta:
    if not m.get('unMember') or m['cca3'] == 'VAT':
        continue
    names = {m['name']['common'], m['name']['official'], *m.get('altSpellings', []), *EXTRA.get(m['cca3'], [])}
    keys = sorted({norm(n) for n in names if len(norm(n)) >= 2})
    region = m['region']
    if region == 'Americas':   # split into North America (incl. Central America, Caribbean) and South America
        region = 'South America' if m.get('subregion') == 'South America' else 'North America'
    countries[m['cca3']] = dict(n=m['name']['common'], k=keys, r=region, ll=m['latlng'], a=m['area'])
assert len(countries) == 193, len(countries)

# guard against alias collisions
seen = {}
for code, c in countries.items():
    for k in c['k']:
        if k in seen and seen[k] != code:
            print('collision', k, seen[k], code, file=sys.stderr)
        seen[k] = code
# drop ambiguous short keys
for code, c in countries.items():
    c['k'] = [k for k in c['k'] if not (len(k) <= 2 and code not in ('GBR', 'NZL', 'DOM'))]

# ---- learn-mode facts: official name, subregion, languages, currency, capital with real coordinates
places = json.load(open(f'{ROOT}/nvkelso/natural-earth-vector/geojson/ne_10m_populated_places_simple.geojson'))['features']
caps_by = {}
for f in places:
    p = f['properties']
    caps_by.setdefault(p['adm0_a3'], []).append(p)
    if p['sov_a3'] != p['adm0_a3']:
        caps_by.setdefault(p['sov_a3'], []).append(p)
ALIAS_A3 = {'SSD': ['SDS'], 'PSE': ['PSX']}
def fold(s): return norm(s or '')
missing_caps = []
for m in meta:
    code = m['cca3']
    if code not in countries:
        continue
    c = countries[code]
    c['o'] = m['name']['official']
    c['s'] = m.get('subregion', '')
    c['lang'] = list(m.get('languages', {}).values())[:4]
    c['cur'] = [v['name'] for v in m.get('currencies', {}).values()][:2]
    cap_names = m.get('capital', [])
    pool = caps_by.get(code, []) + sum((caps_by.get(a, []) for a in ALIAS_A3.get(code, [])), [])
    pick = None
    for cn in cap_names:  # prefer the place whose name matches the listed capital
        cands = [p for p in pool if fold(cn) in (fold(p['name']), fold(p['nameascii']), fold(p['namealt']))]
        if cands:
            pick = max(cands, key=lambda p: (p['adm0cap'], p['pop_max'] or 0)); break
    if not pick:
        cands = [p for p in pool if p['adm0cap'] == 1 and p['adm0_a3'] in [code] + ALIAS_A3.get(code, [])]
        if cands: pick = max(cands, key=lambda p: p['pop_max'] or 0)
    if pick:
        c['cap'] = {'n': cap_names[0] if cap_names else pick['name'], 'll': [round(pick['latitude'], 3), round(pick['longitude'], 3)]}
    else:
        missing_caps.append((code, cap_names))
print('capitals missing:', missing_caps, file=sys.stderr)

def rnd(coords, depth):
    if depth == 0:
        return [round(coords[0], 3), round(coords[1], 3)]
    out = [rnd(c, depth - 1) for c in coords]
    if depth == 1:  # ring: drop consecutive duplicates
        ded = [out[0]]
        for p in out[1:]:
            if p != ded[-1]:
                ded.append(p)
        out = ded if len(ded) >= 4 else out
    return out

feats = []
for f in geo['features']:
    p = f['properties']
    code = FEATURE_ALIAS.get(p['ADM0_A3'], p['ADM0_A3'])
    g = f['geometry']
    depth = 2 if g['type'] == 'Polygon' else 3
    feats.append({'type': 'Feature', 'properties': {'c': code if code in countries else None, 'n': p['NAME']},
                  'geometry': {'type': g['type'], 'coordinates': rnd(g['coordinates'], depth)}})

have = {f['properties']['c'] for f in feats}
missing = [c for c in countries if c not in have]
print('missing polygons:', missing, file=sys.stderr)

data = {'countries': countries, 'geo': {'type': 'FeatureCollection', 'features': feats}}
s = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'w').write(s)
print('bytes', len(s), file=sys.stderr)
