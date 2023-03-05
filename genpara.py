"""Create initial file with line numbers of paratext
(for manual correction).

Usage: genpara.py 'converted/*.txt' paratext-uncorrected.csv
(quotes are important)
"""
import os
import sys
from glob import glob
import pandas as pd

def main():
	try:
		_, globpattern, outfname = sys.argv
	except ValueError:
		print(__doc__)
		return
	result = []
	for fname in sorted(glob(sys.argv[1])):
		with open(fname, encoding='utf8') as inp:
			lines = inp.readlines()
		name = os.path.splitext(os.path.basename(fname))[0]
		result.append((name, 1, len(lines)))

	df = pd.DataFrame(
			result,
			columns=['Label', 'start', 'end']).set_index('Label')
	df.to_csv(outfname)

if __name__ == '__main__':
	main()
