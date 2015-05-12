Android Thesis files
=============
This is the repository containing the code for Sifta.
Sifta is based on DidFail

#Install
To install please read the setup guide in the sifta folder

#Related repositories
As part of our thesis we have also created the following other repositories:

1. IACBench - our test suite can be found at: https://github.com/Dyrborg/IACBench
2. FlowDroid - We have modified flowdroid, the modified version can be found in the following two repositories: 
https://github.com/mikaelHardo/soot-infoflow-android https://github.com/mikaelHardo/soot-infoflow

#How to run
In this example we will use the toy apps provided by didfail as an example (they are included in this repository).
In this example the repository is cloned in a folder called git for a user called "user"

1. run sifta with the following command:
/home/user/git/androidThesis/sifta/scripts/run-sifta.sh /home/user/git/androidThesis/sifta/toyapps/out /home/user/git/androidThesis/sifta/toyapps/*.apk
The first parameter is the "out" folder that will hold the output, the second paramter is the list of apps to analyse.
This will result in a mappings.xml and graph.xml file to be queried
2. Query your created graph, to do this you need to cd to the "out" folder and then run the "graph-querier" python file found in the scripts folder.