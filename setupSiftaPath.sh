#!/bin/bash


thispath=$(readlink -f $0)
thispath=$(dirname $thispath)

siftapath=${thispath}/sifta
darepath=${thispath}/../dare-1.1.0-linux

#change paths
sed -i -- "s:~/git/androidThesis/sifta:${siftapath}:g" ${siftapath}/scripts/run-sifta.sh
sed -i -- "s:/home/niklas/Downloads/dare-1.1.0-linux:${darepath}:g" ${siftapath}/scripts/run-sifta.sh

