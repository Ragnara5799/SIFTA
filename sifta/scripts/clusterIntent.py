import sys
import os
import random
import operator
import pickle
import itertools
import time
from collections import *
from graphviz import Digraph
from class_definitions import *

from sets import Set #for filtering
from itertools import ifilter


class GraphFlow:
    def __init__(self, edges, pcs, mapping):
        self.edges = edges
        self.pcs = pcs
        self.mapping = mapping
 
    def __str__(self):
        nodeStr = ""
        appStr = ""
    
        for (index, (fromNode,toNode)) in enumerate(self.edges):
            nodeObject = self.mapping[toNode]

            if isinstance(nodeObject, Source):
                nodeStr += str(nodeObject).replace("\n", "").replace("Src ", "") + " --> "

            elif isinstance(nodeObject, Sink):
                nodeStr += str(nodeObject).replace("\n", "").replace("Sink ", "") + " "

            elif isinstance(nodeObject, Intent):
                #TODO add more properties
                type = "None"
                if len(nodeObject.intentDefinition.actions) > 0:
                    type = nodeObject.intentDefinition.actions[0]
                nodeStr += "Intent(" + type + ") --> "

            elif isinstance(nodeObject, IntentResult):
                #TODO add more properties
                nodeStr += "IntentResult --> "
        for pc in self.pcs:
            appStr += "|".join(pc) + ","

        return "Flow: " + nodeStr + "in apps (" + appStr[:-1] + ")"


graph = Graph()
graph.load()

#breakOffFlowCount= 1000000 # break after many flows found (probably too many then)
breakOffFlowCount= 3000000 # break after many flows found (probably too many then)

algorithm = "extended"
outputseverity = 0

pcapps = set()

edgeCount = dict()

for (hash, apps) in graph.edges.iteritems():
    for app in apps:
        if app not in edgeCount:
            edgeCount[app] = 0
        edgeCount[app] += 1


appsToIgnore = set()


for (app, count) in edgeCount.iteritems():
    if count > 1000000:
        appsToIgnore.add(app)

allFlows = set()
flowCount = 0

print "apps to ignore: %i" % len(appsToIgnore)

severityList = dict()
severityList["Sink:<android.util.Log: int e(java.lang.String,java.lang.String)>"] = 3
severityList["Sink:<android.util.Log: int v(java.lang.String,java.lang.String)>"] = 3
severityList["Sink:<android.os.Bundle: void putLongArray(java.lang.String,long[])>"] = 3
severityList["Sink:<android.telephony.SmsManager: void sendMultipartTextMessage(java.lang.String,java.lang.String,java.util.ArrayList,java.util.ArrayList,java.util.ArrayList)>"] = 3
severityList["Sink:<android.media.MediaRecorder: void setVideoSource(int)>"] = 3
severityList["Sink:<android.util.Log: int i(java.lang.String,java.lang.String)>"] = 3
severityList["Sink:<android.os.Handler: boolean sendMessage(android.os.Message)>"] = 3
severityList["Sink:<android.util.Log: int d(java.lang.String,java.lang.String)>"] = 3
severityList["Sink:<java.net.URL: void <init>(java.lang.String)>"] = 3
severityList["Sink:<org.apache.http.client.HttpClient: org.apache.http.HttpResponse execute(org.apache.http.client.methods.HttpUriRequest)>"] = 3
severityList["Sink:<android.content.ContentResolver: int update(android.net.Uri,android.content.ContentValues,java.lang.String,java.lang.String[])>"] = 3
severityList["Sink:<org.apache.http.message.BasicNameValuePair: void <init>(java.lang.String,java.lang.String)>"] = 3
severityList["Sink:<java.io.OutputStream: void write(byte[])>"] = 3
severityList["Sink:<android.content.ContentResolver: android.net.Uri insert(android.net.Uri,android.content.ContentValues)>"] = 3
severityList["Sink:<android.util.Log: int w(java.lang.String,java.lang.String)>"] = 3
severityList["Sink:<android.media.MediaRecorder: void setPreviewDisplay(android.view.Surface)>"] = 3
severityList["Sink:<org.apache.http.impl.client.AbstractHttpClient: org.apache.http.HttpResponse execute(org.apache.http.client.methods.HttpUriRequest)>"] = 3
severityList["Sink:<android.telephony.SmsManager: void sendTextMessage(java.lang.String,java.lang.String,java.lang.String,android.app.PendingIntent,android.app.PendingIntent)>"] = 3
severityList["Sink:<android.os.Bundle: void putParcelable(java.lang.String,android.os.Parcelable)>"] = 3
severityList["Sink:<android.content.ContentResolver: int delete(android.net.Uri,java.lang.String,java.lang.String[])>"] = 3
severityList["Sink:<java.io.FileOutputStream: void write(byte[])>"] = 3
severityList["Sink:<java.io.Writer: void write(java.lang.String)>"] = 3

severityList["Src: <android.net.wifi.WifiInfo: java.lang.String getSSID()>"] = 3
severityList["Src: <org.apache.http.HttpResponse: org.apache.http.HttpEntity getEntity()>"] = 3
severityList["Src: <android.location.LocationManager: android.location.Location getLastKnownLocation(java.lang.String)>"] = 3
severityList["Src: <java.util.Calendar: java.util.TimeZone getTimeZone()>"] = 3
severityList["Src: <android.location.Location: double getLatitude()>"] = 3
severityList["Src: <android.bluetooth.BluetoothAdapter: java.lang.String getAddress()>"] = 3
severityList["Src: <android.database.Cursor: java.lang.String getString(int)>"] = 3
severityList["Src: <java.net.URLConnection: java.io.InputStream getInputStream()>"] = 3
severityList["Src: <android.accounts.AccountManager: android.accounts.Account[] getAccounts()>"] = 3
severityList["Src: <android.location.Location: double getLongitude()>"] = 3
severityList["Src: <android.content.ContentResolver: android.database.Cursor query(android.net.Uri,java.lang.String[],java.lang.String,java.lang.String[],java.lang.String)>"] = 3
severityList["Src: <android.content.pm.PackageManager: java.util.List getInstalledApplications(int)>"] = 3
severityList["Src: <android.telephony.TelephonyManager: java.lang.String getSimSerialNumber()>"] = 3
severityList["Src: <android.telephony.TelephonyManager: java.lang.String getDeviceId()>"] = 3
severityList["Src: <android.media.AudioRecord: int read(short[],int,int)>"] = 3
severityList["Src: <android.content.pm.PackageManager: java.util.List queryContentProviders(java.lang.String,int,int)>"] = 3
severityList["Src: <android.telephony.gsm.GsmCellLocation: int getCid()>"] = 3
severityList["Src: <android.telephony.TelephonyManager: java.lang.String getSubscriberId()>"] = 3
severityList["Src: <android.content.pm.PackageManager: java.util.List getInstalledPackages(int)>"] = 3
severityList["Src: <android.os.Handler: android.os.Message obtainMessage(int,java.lang.Object)>"] = 3
severityList["Src: <android.telephony.TelephonyManager: java.lang.String getLine1Number()>"] = 3
severityList["Src: <java.util.Locale: java.lang.String getCountry()>"] = 3
severityList["Src: <android.telephony.gsm.GsmCellLocation: int getLac()>"] = 3


sinks = set()
visitedEdges = set()

def traverse(nodeHash, flow):
    global flowCount
    children = graph.nodes[nodeHash]

   # if len(children) > 50:
   #     print len(children)
   #     children = set(list(children)[0:50])


    for child in children:
        # We have problems with IntentResults, so lets ignore them
        if isinstance(graph.hashToObjectMapping[child], IntentResult):
            continue

        #We want to ignore flows, where an app have more than a 100 flows (we have the list of apps in appsToIgnore)
        appsOnEdge = graph.edges[nodeHash,child]

        pcTRUE = False

        # Presence condition
        if len(pcapps) != 0:
            for app in appsOnEdge:
                if app in pcapps:
                    pcTRUE = True
                    break
        else:
            pcTRUE = True

        if algorithm == "extended":
            if (nodeHash,child) in flow.edges or not pcTRUE:
                continue

        else:
            if (nodeHash,child) in visitedEdges or not pcTRUE:
                continue
            visitedEdges.add((nodeHash,child))

        newFlow = GraphFlow(flow.edges[:], flow.pcs[:], graph.hashToObjectMapping)
        newFlow.edges.append((nodeHash, child))
        newFlow.pcs.append(appsOnEdge)

        datObject = graph.hashToObjectMapping[child]
        if isinstance(datObject, Sink):# or (graph.hashToObjectMapping[newFlow.edges[0][1]].method in severityList and isinstance(graph.hashToObjectMapping[newFlow.edges[1][1]], Intent)):

            # We dont want to look at Src --> Snk flows
          #  if len(newFlow.edges) == 2 and isinstance(graph.hashToObjectMapping[newFlow.edges[1][1]], Sink):
          #      continue


#            sinks.add(datObject.method)

            #if datObject.method not in importantSinks :
            #    continue

            allFlows.add(newFlow)
            flowCount = flowCount + 1

            if flowCount % 10000 == 0:
                sys.stderr.write("\rFlow count: %i" % flowCount)
                sys.stderr.flush()
        else:
            if (flowCount > breakOffFlowCount):
                print ("more than %i flows. breaking off!" % breakOffFlowCount)
                return
            #print "down the rabithole we go! (flowlength: " + str(len(newFlow)) + ")"
            if (child in graph.nodes): #child has other children
                traverse(child, newFlow)


sys.stderr.write("Finding flows\n")
nodeCount = len(graph.sources)

def getColor(datString):
    if datString.startswith("Sink"):
        return "red"

    if datString.startswith("Src"):
        return "green"

    return ""

def drawGraph():
    seenBefore = set()
    seenEdges  = set()
    dot = Digraph(comment="Graph")
    print "FLOWS FOUND: " + str(len(allFlows))
    
    largestPCsize=0
    edgeWithlargestPCsize=None

    for flow in allFlows:
        edges = flow.edges

        for (fromHash, toHash) in edges:
            simp = str(graph.hashToObjectMapping[toHash])
            if simp not in seenBefore:
                color = getColor(simp)
                dot.node(simp, simp, color = color)
                seenBefore.add(simp)

            if fromHash == None:
                continue

            esimp = str(graph.hashToObjectMapping[fromHash])
            if esimp not in seenBefore:
                color = getColor(esimp)
                dot.node(esimp,esimp, color = color, constraint= False)
                seenBefore.add(esimp)
            try:
                if (fromHash, toHash) not in seenEdges:
                    numApps = len(graph.edges[fromHash,toHash])
                    if (numApps > largestPCsize):
                        largestPCsize=numApps
                        edgeWithlargestPCsize=(graph.hashToObjectMapping[fromHash],graph.hashToObjectMapping[toHash])
                    dot.edge(esimp,simp, label= "apps: " + str(numApps)) #+ ",\n".join([e.split(".")[-1] for e in list(graph.edges[fromHash,toHash])]))#
                    seenEdges.add((fromHash, toHash))
            except:
                pass
            before = hash
    print "Nodes in flows: %i" % len(seenBefore)
    print "Edges in flows: %i" % len(edges)
    if (largestPCsize>0):
        print "Largest PC Size: %i" % largestPCsize
        print "on Edge: " + str(edgeWithlargestPCsize[0]) + str(edgeWithlargestPCsize[1])
    dot.render("sifta-graph.gv", view=False)
    print "ALL DONE"


def printFlowDetails(flows):
    flowlengths = dict()

    #Dangerous
    print "High severity flows:"
    for flow in flows:
        (fromEdge, toEdge) = flow.edges[0]
        source = graph.hashToObjectMapping[toEdge]

        severity = severityList.get(source.method, -1)

        if severity == 3:
            print flow

    if outputseverity != 2:
        #Medium
        print "Medium severity flows:"
        for flow in flows:
            (fromEdge, toEdge) = flow.edges[0]
            source = graph.hashToObjectMapping[toEdge]

            severity = severityList.get(source.method, -1)

            if severity == 2:
                print flow

    if outputseverity == 0:
        #Low
        print "Low severity flows:"
        for flow in flows:
            (fromEdge, toEdge) = flow.edges[0]
            source = graph.hashToObjectMapping[toEdge]

            severity = severityList.get(source.method, -1)

            if severity == 1:
                print flow

    #Unknown
    print "Unknown severity flows:"
    for flow in flows:
        (fromEdge, toEdge) = flow.edges[0]
        source = graph.hashToObjectMapping[toEdge]

        severity = severityList.get(source.method, -1)

        if severity < 1:
            print flow


    for flow in flows:
        datLength = len(flow.edges)
        if datLength not in flowlengths:
            flowlengths[datLength] = 0
        flowlengths[datLength] += 1


    for (key, value) in flowlengths.iteritems():
        print "flows of length %i exists %i times" % (key, value)

    flowLengths = [len(i.edges) for i in flows]
    flowcountlength = len(flowLengths)

    totallength = float(sum(flowLengths))

    if flowcountlength != 0:
        print "Average flow length: %f" % (float(totallength / flowcountlength))
    else:
        print "Average flow length: NONE"

def printFirstFlowWithLen(flows, length):
    for flow in allFlows:
        datLength = len(flow.edges)
        if (datLength == length):
            print "first flow with length %i :\n" % length
            print flow
            break

def appStatistics(flows):
    print "App Stats:"
    occurrencesPerApp=dict()
    intermediaryApps=set() # apps that receive and intent and send an intent (can be used for info forwarding)
    for flow in allFlows:
        #get intermediary
        if (len(flow.pcs) > 2):
            for pc in flow.pcs[1:-1]: # all pcs but the first and last one
                for appId in pc:
                    intermediaryApps.add(appId)
        #get occurrances
        appsInPath=set()
        for pc in flow.pcs:
            for appId in pc:
                appsInPath.add(appId)
        for app in appsInPath:
            if app not in occurrencesPerApp:
                occurrencesPerApp[app] = 0
            occurrencesPerApp[app] += 1
    sortedOccurrences=sorted(occurrencesPerApp, key=occurrencesPerApp.get, reverse=True)
    
    print "Rank\t App ID\t Occurrences in Flows"
    for x in range(0,10):
        print x, "\t", sortedOccurrences[x], "\t", occurrencesPerApp[sortedOccurrences[x]]
    print "Total number of apps in pcs: ", len(occurrencesPerApp)
    appStatsFile = open("appOccurrences.csv", "w+")
    appStatsFile.write("AppID\tOccurrencesInFlows\n")
    for app in sortedOccurrences:
        appStatsFile.write(app + "\t" + str(occurrencesPerApp[app]) + "\n")
    appStatsFile.close()
    
    print "Total number intermediary apps: ", len(intermediaryApps)
    intermAppStatsFile = open("intermediaryApps.csv", "w+")
    intermAppStatsFile.write("AppID\n")
    for app in intermediaryApps:
        intermAppStatsFile.write(app + "\n")
    intermAppStatsFile.close()
    

def printFlowLengthsDetailsReturnMax(flows):
    flowlengths = dict()
    maxLen = 0
    for flow in allFlows:
        datLength = len(flow.edges)
        if datLength not in flowlengths:
            flowlengths[datLength] = 0
        flowlengths[datLength] += 1
        if datLength > maxLen:
            maxLen=datLength

    for (key, value) in flowlengths.iteritems():
        print "flows of length %i exists %i times" % (key, value)

    return maxLen

def printFlows(flows):
    print "-------- INTERNAL FLOWS ---------"
    for flow in allFlows:
        if len(flow) != 2:
            continue
        print "------------------------------"
        for hash in flow:
            realObject = graph.hashToObjectMapping[hash]

            if isinstance(realObject, Sink):
                print "" + str(realObject).replace(" \n", ": ")
            else:
                print "" + str(realObject).replace(" \n", ": ") + "\n--> (" + ",".join(graph.edges[(hash, flow[1])]) + ")"

    print "-----------------------------------"

    print "------------ INTER APP FLOWS -------------"

    for flow in allFlows:
        if len(flow) == 2:
            continue
        print "------------------------------"
        i = 0
        for hash in flow:
            realObject = graph.hashToObjectMapping[hash]

            if isinstance(realObject, Sink):
                print str(realObject)
            else:
                print str(realObject) + "\n--> (" + ",".join(graph.edges[(hash, flow[i + 1])]) + ")"
            i += 1

    
def computeJointIntents(listOfApps,graph,fileName):
    output = open(fileName, 'w')
    for edge in graph.edges:
        isShare = 0
        for app in listOfApps:
            for app2 in listOfApps:
                if app != app2:
                    if app in graph.edges[edge] and app2 in graph.edges[edge]:
                        isShare = 1
        if isShare == 1:
            output.write(str(edge) + "\n")
            output.write(str(graph.hashToObjectMapping[edge[0]]) + "\n")
            output.write(str(graph.hashToObjectMapping[edge[1]]) + "\n")
            #print(edge)
            #print(graph.hashToObjectMapping[edge[0]])
            #print(graph.hashToObjectMapping[edge[1]])
            output.write("-------------------\n")
    output.close()
    
def readClusterFile(file):
    f = open(file,'r')
    appList = set()
    for line in f:
        appList.add(line.rstrip())
    lines = [line.rstrip('\n') for line in f]
    f.close()
    for line in lines:
        print line
    return appList

def isAppOnEdgeWithIntent(graph, app, intentHash):
    for edge in graph.edges:
        if edge[0] == intentHash or edge[1] == intentHash:
            if app in graph.edges[edge]:
                return 1
    return 0
        
def main(args):
    global pcapps
    global outputseverity
    global algorithm

    prevarg = ""
    for arg in args:

        if prevarg == "-top":
            cap = int(arg)
            pcapps = list(graph.processedApps)[0:cap]
        if prevarg == "-applist":
            pcapps = set(arg.split(","))

        if prevarg == "-severity":
            outputseverity = int(arg)

        if prevarg == "-pathalgorithm":
            algorithm = arg
        prevarg = arg

    printAllFlows=False
    printStatistics=False
    printSampleFlows=False
    printAppStatistics=False
    arguments=sys.argv
    if (len(arguments[1:]) > 0):
        if "-printAllFlows" in arguments:
            print("Printing all flows.")
            printAllFlows=True
        if "-printSampleFlows" in arguments:
            print("Printing a sample of the flows (100 flows with length > 2).")
            printSampleFlows=True
        if "-printStatistics" in arguments:
            print("Printing statistics.")
            printStatistics=True
        if "-printAppStats" in arguments:
            print("Printing app statistics.")
            printAppStatistics=True
    if not printAllFlows:
        print("Printing only one flow of max. found length. Use -printAllFlows to print all.")
    if not printStatistics:
        print("Omitting graph statistics. Use -printStatistics to print them.")
        
    print "Running querier with algorithm: %s" % algorithm

    for node in graph.sources:
        global visitedEdges
        visitedEdges = set()
        if (not node in graph.nodes): #source has children
            print ("source is not key in graph.nodes list?!: " + node)
        else:
            traverse(node, GraphFlow([(None,node)], [], graph.hashToObjectMapping))
        if (flowCount > breakOffFlowCount):
            print ("more than %i flows. breaking off!" % breakOffFlowCount)
            break

#-------------------------------------------------------------------------------------------
    
    #listOfApps = set()
    counter = 0
    output = open("ClusterFiles/ScaleGestureDetectorResult.txt", 'w')
    #imageCapture
    #intentHashList = {'611ac312025310de6bd3cdd893163fe9', '1992e4ed013c3784994649e475134052'}
    #ScaleGestureDetector
    intentHashList = {'cc5d9a75787506a0b1dbc8c26e3035d3'}
    listOfApps = readClusterFile("/home/ragnara/Schreibtisch/AppAnalyse/communityDetection/community-master/ClusterFiles/subGraphNodesFiltered_28_21.txt")
    for app in listOfApps:
        isTrue = 0
        for intentHash in intentHashList:
            if isAppOnEdgeWithIntent(graph, app, intentHash) == 1:
                isTrue = 1
                output.write(str(app) + " is on edge with " + str(intentHash) + "\n")
            else:
                output.write(str(app) + " is not on edge with " + str(intentHash) + "\n")
        if isTrue == 1:
            print(str(app) + " is ok")
        else:
            print(str(app) + " is not ok")
    output.close()
    '''
    while counter <= 2: 
        listOfApps = readClusterFile("/home/ragnara/Schreibtisch/AppAnalyse/communityDetection/community-master/ClusterFiles/subGraphNodesFilteredBigCluster_28_"+ str(counter) +".txt")
        computeJointIntents(listOfApps,graph,"ClusterFiles/OutputBigCluster_28_" + str(counter) + ".txt")
        counter += 1
    '''
    
    
main(sys.argv)
