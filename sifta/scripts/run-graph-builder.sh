#!/bin/bash

script_path="$1"
outdir="$2"
echo "-----"
echo $script_path
echo $outdir
echo "---"

cd $outdir
python -t $script_path/compute-graph.py $($script_path/find-processed-apps.sh $outdir)
