#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk"
    exit
fi
export outdir=$1
export apk_file=$2
export outdir=`readlink -m $outdir`

apk_base=`basename $apk_file`
apk_base=${apk_base%%.apk}
apk_xform=$outdir/$apk_base.apk

#ulimit -v $max_mem -t $max_time

export flowdroid="java $jvm_flags -Dfile.encoding=UTF-8 -cp $jar_path/soot-trunk.jar:$jar_path/soot-infoflow-new.jar:$jar_path/soot-infoflow-android-new.jar:$jar_path/axml-2.0.jar soot.jimple.infoflow.android.TestApps.Test"

echo Running FlowDroid on $apk_file
orig_wd=`pwd`
cd $jar_path

$flowdroid $apk_xform $sdk_platforms --nostatic --aplength 1 --aliasflowins --pathalgo "contextsensitive" --out $outdir/$apk_base.fd.xml &> $outdir/log/$apk_base.flowdroid.log

#$flowdroid $apk_xform $sdk_platforms --nostatic --aplength 1 --aliasflowins --filterunverifiableflows --pathalgo "contextsensitive" --out $outdir/$apk_base.fd.xml &> $outdir/log/$apk_base.flowdroid.log

#--nostatic --aplength 1 --aliasflowins --nocallbacks --layoutmode none
err=$?; if [ $err -ne 0 ]; then echo "Failure!"; exit $err; fi
cd $orig_wd
