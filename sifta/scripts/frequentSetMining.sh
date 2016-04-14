#!/bin/bash
# Outputpath ist der Ordner an dem die Ergebnisse gespeichert werden. Es ist auch der Ordner in dem die graph.xml und mappings.xml von Sifta liegen müssen.
OUTPUTPATH="/home/ragnara/Schreibtisch/AppAnalyse/Graph"
# Siftapath ist der Sifta-Ordner
SIFTAPATH="/home/ragnara/Schreibtisch/AppAnalyse/SIFTA_OLD"
FSUPPSETCOMPUTED="0"
if [ -f "$OUTPUTPATH/firstSupportSet.pkl" ];
then
    FSUPPSETCOMPUTED="1"
    echo "first Supportset already computed"
else
    FSUPPSETCOMPUTED="0"
    echo "compute first Supportset"
fi

# Das ist das Supportlimit für die Option "sameFlow" und ebenso das SupportLimit für das firstSupportSet der option "sameFlowDifferentEdges"
SUPPLIMIT="20000"
#Das ist das Supportlimit für die Option "sameFlowDifferentEdges". Für diese Option gibt es 2 SupportLimits, weil bei einem das SupportLimit entweder viel zu groß ist
# oder viel zu klein. Das kommt daher das das erste SupportSet für beide Optionen gleich ist, aber bei den weiteren Schritten die Supportsets für die Option "sameFlowDifferentEdges"
# viel kleinere Werte besitzen.
SUPPLIMITDIFEDGE="150"

time python $SIFTAPATH/sifta/scripts/frequentSetMining.py "sameFlowDifferentEdges" $OUTPUTPATH $SUPPLIMIT $FSUPPSETCOMPUTED $SUPPLIMITDIFEDGE
time python $SIFTAPATH/sifta/scripts/frequentSetMining.py "sameFlow" $OUTPUTPATH $SUPPLIMIT $FSUPPSETCOMPUTED


