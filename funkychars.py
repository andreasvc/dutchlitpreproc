"""An overview of ALL non-ascii characters per file.

For example (single quotation marks required):
python3 funkychars.py '*/*.txt'
"""
import os
import sys
from glob import glob
import unicodedata
from collections import Counter


def main(path):
	"""Search through all files matching the `path` glob and print funky
	characters."""
	for fname in sorted(glob(path)):
		cnt = Counter()
		normallines = lines = 0
		with open(fname, encoding='utf8') as inp:
			for line in inp:
				cnt.update([a for a in line if not a.isascii()])
				normallines += unicodedata.is_normalized('NFC', line)
				lines += 1
		pct = round(100 * normallines / lines, 1)
		print(os.path.basename(fname))
		print(f'Unicode NFC lines: {normallines} / {lines} ({ pct } %)')
		foundany = False
		for weirdchar, count in cnt.most_common():
			foundany = True
			charname = unicodedata.name(weirdchar, '<<UNKNOWN>>')
			print('%10s %5d %s' % (repr(weirdchar), count, charname))
		if not foundany:
			print('<none!>')
		print()

if __name__ == '__main__':
	if len(sys.argv) == 2:
		main(sys.argv[1])
	else:
		print(__doc__)
