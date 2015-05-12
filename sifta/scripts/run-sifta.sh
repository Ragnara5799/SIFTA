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


export jvm_flags="-Xmx600m"
export max_mem=2250000
export max_time=4200
export python=python2

#---------------------------------------------------------

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
        timeout 600s $script_path/run-transformer.sh $outdir $apk_file
    	if [ $? -ne 0 ]; then continue; fi
    	timeout 600s $script_path/run-epicc.sh $outdir $apk_file
    	timeout 600s $script_path/run-flowdroid.sh $outdir $apk_file
	
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
