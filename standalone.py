# Wraps the built page in its own document skeleton so it runs as a standalone website (index.html).
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
s = s.replace('<title>Name Every Country</title>', head + '<title>Name Every Country</title>', 1)
s = s.replace('<div id="globe"', '</head>\n<body>\n<div id="globe"', 1)
open(dst, 'w').write(s.rstrip() + '\n</body>\n</html>\n')
print('wrote', dst, len(s))
