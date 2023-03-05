.PHONY: clean example

clean:
	rm -rf output

example: original/18066-h.htm
	bash pipeline.sh original/18066-h.htm 10000

original/18066-h.htm:
	mkdir -p original
	(cd original; wget http://www.gutenberg.lib.md.us/1/8/0/6/18066/18066-h/18066-h.htm)

genpara:
	python3 genpara.py 'output/converted/*.txt' output/paratext-uncorrected.csv

checkpara:
	bash checkpara.sh > output/checkpara.txt

funkychars:
	python3 funkychars.py 'output/tokenized/*.tok' > output/funkychars.txt
