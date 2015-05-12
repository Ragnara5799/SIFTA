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
apk_norm=`readlink -m $apk_file`

#ulimit -v $max_mem -t $max_time

export script_path=`dirname $0`

sootOutApk="$outdir/sootOutput/`basename $apk_norm`"
if [ -f "$sootOutApk" ]; then
    rm $sootOutApk
fi

export CLASSPATH=$jar_path/app-transformer.jar:$jar_path/soot-trunk.jar:$android_jar:$rt_jar
orig_wd=`pwd`
cd $outdir
echo Transforming $apk_file
echo -android-jars $sdk_platforms -process-dir $apk_norm 
java $jvm_flags -cp $CLASSPATH apptransformer.TransformAPKs_IntentSinks -android-jars $sdk_platforms -process-dir $apk_norm -cp $CLASSPATH &> $outdir/log/$apk_base.xform.log
err=$?; if [ $err -ne 0 ]; then echo "Failure!"; exit $err; fi
cd $orig_wd
mv $sootOutApk $outdir/$apk_base.apk
$script_path/extract-manifest.sh $apk_file > $outdir/$apk_base.manifest.xml
