#!/bin/bash
OUTPUTPATH="/home/ragnara/Schreibtisch/AppAnalyse/Graph/MinCut"
SIFTAPATH="/home/ragnara/Schreibtisch/AppAnalyse/SIFTA_OLD"
PARTIALMINCUTLIMIT="0.6"

 time python $SIFTAPATH/sifta/scripts/min-cut.py $PARTIALMINCUTLIMIT $OUTPUTPATH


