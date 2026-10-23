# Builds country-game.html from template.html and the data files next to it.
#   python3 assemble.py                 -> country-game.html (the page as published in Claude)
#   python3 standalone.py country-game.html index.html   -> a standalone website file
import json, os
here = os.path.dirname(os.path.abspath(__file__))
p = lambda name: os.path.join(here, name)
data = json.load(open(p('data.json'), encoding='utf-8'))
t = open(p('template.html'), encoding='utf-8').read()
out = (t.replace('__DATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
        .replace('__FLAGS__', open(p('flags.json'), encoding='utf-8').read())
        .replace('__LEARN__', open(p('learn.json'), encoding='utf-8').read()))
assert '</script' not in json.dumps(data), 'data must not contain a closing script tag'
open(p('country-game.html'), 'w', encoding='utf-8').write(out)
print('built country-game.html', len(out), 'bytes')
