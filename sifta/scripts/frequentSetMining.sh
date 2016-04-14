#!/bin/bash
OUTPUTPATH="/home/ragnara/Schreibtisch/AppAnalyse/Graph"
SIFTAPATH="/home/ragnara/Schreibtisch/AppAnalyse/SIFTA_OLD"
FSUPPSETCOMPUTED="1"
if [ -f "$OUTPUTPATH/firstSupportSet.pkl" ];
then
    FSUPPSETCOMPUTED="1"
    echo "first Supportset already computed"
else
    FSUPPSETCOMPUTED="0"
    echo "compute first Supportset"
fi

SUPPLIMIT="20000"
SUPPLIMITDIFEDGE="150"

time python $SIFTAPATH/sifta/scripts/frequentSetMining.py "sameFlowDifferentEdges" $OUTPUTPATH $SUPPLIMIT $FSUPPSETCOMPUTED $SUPPLIMITDIFEDGE
time python $SIFTAPATH/sifta/scripts/frequentSetMining.py "sameFlow" $OUTPUTPATH $SUPPLIMIT $FSUPPSETCOMPUTED

