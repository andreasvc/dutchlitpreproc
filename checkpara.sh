#!/bin/bash
export N=160

headtail () {
	head -c $N "$1"
	echo
	echo
	tail -c $N "$1"
	echo
	echo "--------------------"
	echo
}

pushd output/cleaned
for FNAME in *.txt
do
	headtail $FNAME
done
popd
