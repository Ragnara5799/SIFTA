#!/bin/bash

script_name="$0"
script_name=`readlink -m "$script_name"`
export script_path=`dirname $script_name`
paths_local="$script_path/paths.local.sh"


#----------- change these parameters: -------------------
export sifta=~/git/androidThesis/sifta
export epicc_dir=$sifta/epicc
export dare_dir=/home/niklas/Downloads/dare-1.1.0-linux
export dare=$dare_dir/dare
export jar_path=$sifta/jars

export sdk_platforms=$sifta/platforms
export android_jar=$sdk_platforms/android-16/android.jar
export rt_jar=/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/rt.jar


export jvm_flags="-Xmx6000m"
#export jvm_flags="-Xmx60g"
#export jvm_flags="-Xmx4000m"
#export max_mem=2250000
#export max_time=2000
#these exports are unused
export max_mem=0
export max_time=0

export timeout_sec=1200 # 20 minutes
#export timeout_sec=86400 # 24 hours

export python=python2

#---------------------------------------------------------
java -version

if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk_1 ... apk_n"
    echo "No spaces are allowed in outdir or apk filenames."
    exit
fi
export outdir=$1
shift
export outdir=`readlink -m "$outdir"`
if [ -f "$outdir" ]; then
    if [ ! -d "$outdir" ]; then
	echo "Not a directory: $outdir"
	exit 1
    fi
fi

if [ ! -d "$outdir" ]; then mkdir "$outdir"; fi
if [ ! -d "$outdir/log" ]; then mkdir "$outdir/log"; fi

#ulimit -v $max_mem
comment=''
thishavefailed="false"
for apk_file in $@
do
	apk_base=`basename $apk_file`
	apk_base=${apk_base%%.apk}
    echo Processing $apk_base
    if [ -f "$outdir/$apk_base.apk" ]; 
    then
	echo $apk_file Exists;
    else
        /usr/bin/time -f TransformerTime:SystemTime:%S,UserTime:%U,Memory:%M,Real:%E /usr/bin/timeout -k 20s ${timeout_sec}s $script_path/run-transformer.sh $outdir $apk_file
    	if [ $? -ne 0 ]; then continue; fi
    	/usr/bin/time -f EpiccTime:SystemTime:%S,UserTime:%U,Memory:%M,Real:%E /usr/bin/timeout -k 20s ${timeout_sec}s $script_path/run-epicc.sh $outdir $apk_file
    	if [ $? -eq 124 ]; then echo "EPICC timeout"; fi
    	$script_path/run-flowdroid.sh $outdir $apk_file
    	
	
	thishavefailed="false"

	#assert that fd and epicc file exists!
	if [ ! -f "$outdir/$apk_base.fd.xml" ]; then
		echo FlowDroid failed;
		thishavefailed="true";
    	fi

	if [ ! -f "$outdir/$apk_base.epicc" ]; then
		echo Epicc failed;
		thishavefailed="true";
    	fi
	
	if [ $thishavefailed = "true" ]; then
	    echo "something went wrong for" $apk_base.apk;
	    rm "$outdir/$apk_base.fd.xml";
	    rm "$outdir/$apk_base.epicc";
	    rm "$outdir/$apk_base.manifest.xml"; 
	fi
    fi
done

echo $outdir
orig_wd=`pwd`
cd $outdir
$script_path/run-graph-builder.sh $script_path $outdir
cd $orig_wd
