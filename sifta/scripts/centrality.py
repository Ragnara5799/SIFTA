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
from appGraph_definition import AppGraph

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

def computeAppsInFlows(allFlows, graph):
    appsToFlow = dict()
    allApps = set()
    for flow in allFlows:
        apps = set()
        for edge in flow.edges:
            if edge in graph.edges:
                for app in graph.edges[edge]:
                    apps.add(app)
                    allApps.add(app)
        newPair = {flow:apps}
        appsToFlow.update(newPair)
    return [appsToFlow,allApps]

def computeEdgesInFlows(allFlows, graph):
    appsToFlow = []
    for flow in allFlows:
        apps = []
        for edge in flow.edges:
            if edge in graph.edges:
                edgeSet = set()
                for app in graph.edges[edge]:
                    edgeSet.add(app)
                apps.append(edgeSet)
        appsToFlow.append(apps)
    return appsToFlow

def computeFirstSupportSet(appsToFlow, allApps):
    appSupport = dict()
    for app in allApps:
        supportCounter = 0
        for flow in appsToFlow:
            if app in appsToFlow[flow]:
                supportCounter += 1
        newPair = {app : supportCounter}
        appSupport.update(newPair)
    return appSupport

def computeSupportSetEdgeBased(edgeToFlow, appTupel):
    appSupport = dict()
    for app in appTupel:
        supportCounter = 0
        for edge in edgeToFlow:
            removedEdges = []
            if len(app) <= len(edge):
                if containsAppCombosInDifferentEdges(app, edge, 0, removedEdges) == 1:
                    supportCounter += 1
        newPair = {app: supportCounter}
        appSupport.update(newPair)
    return appSupport

def computeSupportSet(appsToFlow, appTupel):
    appSupport = dict()
    for app in appTupel:
        supportCounter = 0
        for flow in appsToFlow:
            isInFlow = 0
            for singleApp in app:
                if singleApp not in appsToFlow[flow]:
                    isInFlow += 1
            if isInFlow == 0:
                supportCounter += 1
        newPair = {app: supportCounter}
        appSupport.update(newPair)
    return appSupport

def computeNextAppSet(singleApps, previousSupportDict, removedAppCombos, supportMinimum, step):
    appsForNextStep = set()
    permutations = set()
    newAppSet = list()
    # compute candidates for next step
    for app in previousSupportDict:
        if previousSupportDict[app] > supportMinimum:
            appsForNextStep.add(app)
        else:
            removedAppCombos.append(app)
    for app in appsForNextStep:
        for singleApp in singleApps:
            if singleApp not in app:
                newTupel = ()
                if step == 2:
                    newTupel = newTupel + (app,)
                else:
                    newTupel = newTupel + app
                newTupel = newTupel + (singleApp,)
                if newTupel not in permutations:
                    if containsRemovedAppCombos(newTupel, removedAppCombos) == 0:
                        newPermutations = itertools.permutations(newTupel,step)
                        for per in newPermutations:
                            permutations.add(per)
                        newAppSet.append(newTupel)
    return (newAppSet,removedAppCombos)
                        
def containsAppCombosInDifferentEdges(appCombo, edgeSet, deep, removedEdges):
    if deep >= len(appCombo):
        return 1
    currentApp = appCombo[deep]
    for edge in edgeSet:
        if edge not in removedEdges:
            if currentApp in edge:
                removedEdges.append(edge)
                if containsAppCombosInDifferentEdges(appCombo, edgeSet, deep + 1, removedEdges) == 1:
                    removedEdges.remove(edge)
                    return 1
                else:
                    removedEdges.remove(edge)
    return 0

def containsRemovedAppCombos(newTupel, removedAppCombos):
    contains = 0
    for removedCombo in removedAppCombos:  
        contains = 1 
        for app in removedCombo:
            if app not in newTupel:
                contains = 0
        if contains == 1:
            return 1
    return 0

def setMining(singleApps, startSupportDict, appsToFlow ,removedAppCombos, supportMinimum, step):
    newAppSet = computeNextAppSet(singleApps, startSupportDict, removedAppCombos, supportMinimum, step)
    nextAppSet = newAppSet[0]
    newRemovedAppCombos = newAppSet[1]
    currentStep = step
    while len(nextAppSet) != 0:
        print("next AppSet size: " + str(len(nextAppSet)))
        print("start step " + str(currentStep) + " at " + str(time.localtime()))
        nextSupportDict = computeSupportSet(appsToFlow, nextAppSet)
        output = open("SupportSet" + str(currentStep) + ".pkl", 'w')
        pickle.dump(nextSupportDict, output)
        output.close()
        output2 = open("removedAppCombos" + str(currentStep) + ".pkl", 'w')
        pickle.dump(newRemovedAppCombos, output2)
        output2.close()
        print("step " + str(currentStep) + " finished at " + str(time.localtime()))
        currentStep += 1
        newAppSet = computeNextAppSet(singleApps, nextSupportDict, newRemovedAppCombos, supportMinimum, currentStep)
        nextAppSet = newAppSet[0]
        newRemovedAppCombos = newAppSet[1]

def setMiningEdgeBased(singleApps, startSupportDict, edgesToFlow ,removedAppCombos, supportMinimum, step):
    newAppSet = computeNextAppSet(singleApps, startSupportDict, removedAppCombos, supportMinimum, step)
    nextAppSet = newAppSet[0]
    newRemovedAppCombos = newAppSet[1]
    currentStep = step
    while len(nextAppSet) != 0:
        print("next AppSet size: " + str(len(nextAppSet)))
        print("start step " + str(currentStep) + " at " + str(time.localtime()))
        nextSupportDict = computeSupportSetEdgeBased(edgesToFlow, nextAppSet)
        output = open("SupportSetEdgeBased" + str(supportMinimum) + "_" + str(currentStep) + ".pkl", 'w')
        pickle.dump(nextSupportDict, output)
        output.close()
        output2 = open("removedAppCombosEdgeBased" + str(supportMinimum) + "_" + str(currentStep) + ".pkl", 'w')
        pickle.dump(newRemovedAppCombos, output2)
        output2.close()
        print("step " + str(currentStep) + " finished at " + str(time.localtime()))
        currentStep += 1
        newAppSet = computeNextAppSet(singleApps, nextSupportDict, newRemovedAppCombos, supportMinimum, currentStep)
        nextAppSet = newAppSet[0]
        newRemovedAppCombos = newAppSet[1]    
  
def computeNumberOfFlowsForEachApp(allApps, allFlows, graph):
    appsToFlow = dict()
    counter = 0
    print("start algortihm")
    for app in allApps:
        if counter%100 == 0:
            print (counter)
        flowCount = 0
        for flow in allFlows:
            for edge in flow.edges:
                if edge in graph.edges:
                    if app in graph.edges[edge]:
                        flowCount +=1
                        break
        counter += 1
        newPair = {app:flowCount}
        appsToFlow.update(newPair)
    return appsToFlow

def computeNumberOfEdgesForEachApp(allApps, graph):
    appsToEdge = dict()
    counter = 0
    print("start algortihm")
    for app in allApps:
        if counter%100 == 0:
            print (counter)
        edgeCount = 0
        for edge in graph.edges:
            if app in graph.edges[edge]:
                edgeCount +=1
        counter += 1
        newPair = {app:edgeCount}
        appsToEdge.update(newPair)
    return appsToEdge
    
def computeNumberOfFlowsPerEdge(allFlows, edgeSet):
    edgeToFlows = dict()
    counter = 0
    print("start algortihm")
    for edge in edgeSet:
        if counter%100 == 0:
            print (counter)
        edgeCount = 0
        for flow in allFlows:
            if edge in flow.edges:
                edgeCount += 1
        counter += 1
        newPair = {edge:edgeCount}
        edgeToFlows.update(newPair)
    return edgeToFlows

def computeNumberOfFlowsPerIntent(allFlows, graph):
    intentsToFlows = dict()
    counter = 0
    for intent in graph.intents:
        if counter%100 == 0:
            print (counter)
        flowCount = 0
        for flow in allFlows:
            for edge in flow.edges:
                if intent in edge:
                    flowCount += 1
                    break
        counter += 1
        newPair = {intent:flowCount}
        intentsToFlows.update(newPair)
    return intentsToFlows
    
    
def computeNumberOfFlowsPerSource(allFlows, graph):
    sourceToFlows = dict()
    counter = 0
    for source in graph.sources:
        if counter%100 == 0:
            print (counter)
        flowCount = 0
        for flow in allFlows:
            for edge in flow.edges:
                if source in edge:
                    flowCount += 1
                    break
        counter += 1
        newPair = {source:flowCount}
        sourceToFlows.update(newPair)
    return sourceToFlows

def computeNumberOfFlowsPerSink(allFlows, graph):
    sinkToFlows = dict()
    counter = 0
    for sink in graph.sinks:
        if counter%100 == 0:
            print (counter)
        flowCount = 0
        for flow in allFlows:
            for edge in flow.edges:
                if sink in edge:
                    flowCount += 1
                    break
        counter += 1
        newPair = {sink:flowCount}
        sinkToFlows.update(newPair)
    return sinkToFlows

def computeNumberOfIncomingEdgesPerIntent(graph):
    incomingEdgesPerIntent = dict()
    counter = 0
    for intent in graph.intents:
        if counter%100 == 0:
            print (counter)
        edgeCount = 0
        for edge in graph.edges:
            if edge[1] == intent:
                edgeCount = edgeCount + len(graph.edges[edge])
                break
        counter += 1
        newPair = {intent:edgeCount}
        incomingEdgesPerIntent.update(newPair)
    return incomingEdgesPerIntent

def computeNumberOfOutgoingEdgesPerIntent(graph):
    incomingEdgesPerIntent = dict()
    counter = 0
    for intent in graph.intents:
        if counter%100 == 0:
            print (counter)
        edgeCount = 0
        for edge in graph.edges:
            if edge[0] == intent:
                edgeCount = edgeCount + len(graph.edges[edge])
                break
        counter += 1
        newPair = {intent:edgeCount}
        incomingEdgesPerIntent.update(newPair)
    return incomingEdgesPerIntent   

def computeLengthOfFlows(graph, allFlows, minLength):
    flowCounter = 0     
    for flow in allFlows:
        if len(flow.edges) >= minLength:
            flowCounter += 1
    return flowCounter

def computeLengthOfFlowsDistribution(maxLength, graph, allFlows):
    counter = 1
    lengthToNumberOfFlows = dict()
    while counter < maxLength:
        flowCounter = computeLengthOfFlows(graph, allFlows, counter)
        newPair = {counter:flowCounter}
        lengthToNumberOfFlows.update(newPair)
        counter += 1
    return lengthToNumberOfFlows
        
def computeAppDegreeInAppGraph(appGraph):
    outgoingRet = dict()
    incomingRet = dict()
    for app in appGraph.apps:
        newOutPair = {app:0}
        newInPair = {app:0}
        outgoingRet.update(newOutPair)
        incomingRet.update(newInPair)
    for edge in appGraph.edges:
        incomingApp = edge[1]
        outgoingApp = edge[0]
        incomingDegree = incomingRet[incomingApp] + 1
        outgoingDegree = outgoingRet[outgoingApp] + 1
        newOutPair = {outgoingApp:outgoingDegree}
        newInPair = {incomingApp:incomingDegree}
        outgoingRet.update(newOutPair)
        incomingRet.update(newInPair)
    return (outgoingRet,incomingRet)
def computeAppDegreeInAppGraphLenOfEdges(appGraph):
    outgoingRet = dict()
    incomingRet = dict()
    for app in appGraph.apps:
        newOutPair = {app:0}
        newInPair = {app:0}
        outgoingRet.update(newOutPair)
        incomingRet.update(newInPair)
    for edge in appGraph.edges:
        incomingApp = edge[1]
        outgoingApp = edge[0]
        incomingDegree = incomingRet[incomingApp] + len(appGraph.edges[edge])
        outgoingDegree = outgoingRet[outgoingApp] + len(appGraph.edges[edge])
        newOutPair = {outgoingApp:outgoingDegree}
        newInPair = {incomingApp:incomingDegree}
        outgoingRet.update(newOutPair)
        incomingRet.update(newInPair)
    return (outgoingRet,incomingRet)
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
        
    if len(allFlows)==0:
        print("0 flows found!")
    else:
        if printSampleFlows:
            print("computing sample")
            sample = random.sample(Set(ifilter(lambda flow: len(flow.edges) > 2 , allFlows)), 10) # 100 flows with more than 2 nodes
            print("printing sample")
            printFlowDetails(sample)
        if printAllFlows:
            printFlowDetails(allFlows)
        maxLen=printFlowLengthsDetailsReturnMax(allFlows)
        printFirstFlowWithLen(allFlows, maxLen)
        if printAppStatistics:
            appStatistics(allFlows)
        if printStatistics:
            graph.printAllStatistics()
        #graph.drawGraph()
        #drawGraph()
#-------------------------------------------------------------------------------------------
#    counter = 0
#    flowSet = set()
#    for flow in allFlows:
#        if counter < 5:
#            for edge in flow.edges:
#                if edge[0] == "08e33a7af42aa81ba829c24b590559d9" and edge[1] == "daa47ff7f2f4c8c3de63fc83f8650c70":
#                    flowSet.add(flow)
#                    counter += 1
#    appSet = set()
#    for flow in flowSet:
#        file = open("/home/ragnara/Schreibtisch/AppAnalyse/Partitions/FlowsWithEdgeLog.txt", "a")
#        file.write("flow: " + str(flow) + "\n")
#        file.write("----------------------------------------\n")
#        file.close()
#        for edge in flow.edges:
#            if edge in graph.edges:
#                for app in graph.edges[edge]:
#                    appSet.add(app)
    
#    for app in appSet:
#        file = open("/home/ragnara/Schreibtisch/AppAnalyse/Partitions/AppsInFlowsWithEdgeLog.txt", "a")
#        file.write("app: " + str(app) + "\n")
#        file.write("----------------------------------------\n")
#        file.close()
    appsInFlows = computeAppsInFlows(allFlows, graph)
    appsOfFlows = appsInFlows[0]
    allApps = appsInFlows[1]
    appToInvestigate = "com.rekonsult.MTFashionAlert"
    edgeSet = set()
    for edge in graph.edges:
        if appToInvestigate in graph.edges[edge]:
            edgeSet.add(edge)
    
    count = 0
    for intent in graph.edges:
        if count < 10:
            print(intent)
            #print(graph.edges[intent])
            count += 1
    
    appGraph = AppGraph()
    appGraph.convertGraphIntoAppGraph(graph)
    print("lenght of Apps: " + str(len(appGraph.apps)))
    print("lenght of Edges: " + str(len(appGraph.edges)))
    counter = 0
    for edge in appGraph.edges:
        if counter < 10:
            print(edge)
            print(appGraph.edges[edge])
            counter += 1
    print "#######"
    appsOfEdge = set()
    for edge in graph.edges:
        if edge[1] == "daa47ff7f2f4c8c3de63fc83f8650c70":
            for app in graph.edges[edge]:
                appsOfEdge.add(app)
                
    '''                
    degreeDictionarys = computeAppDegreeInAppGraph(appGraph)
    output = open('degreeOfAppGraphNumberOfEdges.pkl', 'w')
    pickle.dump(degreeDictionarys, output)
    output.close()
    degDict = computeAppDegreeInAppGraphLenOfEdges(appGraph)
    output = open('degreeOfAppGraphLengthOfEdges.pkl', 'w')
    pickle.dump(degDict, output)
    output.close()
    '''   

    input = open('degreeOfAppGraphLengthOfEdges.pkl')
    data = pickle.load(input)
    input.close()
    dataOutgoing = data[0]
    dataIncoming = data[1]
    dataCombined = dict()
    for app in appGraph.apps:
        combinedDegree = dataOutgoing[app] + dataIncoming[app]
        newPair = {app:combinedDegree}
        dataCombined.update(newPair)
    '''    
    dataSorted = sorted(dataCombined.items(), key=operator.itemgetter(1))
    file = open("/home/ragnara/Schreibtisch/AppAnalyse/Graph/AppDegree.txt", "a")
    file.write("Degree,Count \n")
    for d in dataSorted:
        file.write(str(d) + "\n")
    file.close()
    '''
    
    degree = 0
    dataDegreeCount = dict()
    while degree < 8675:
        newPair = {degree:0}
        dataDegreeCount.update(newPair)
        degree += 1
    for data in dataCombined:
        dataCount = dataCombined[data]
        degreeCount = dataDegreeCount[dataCount] + 1
        newPair = {dataCount:degreeCount}
        dataDegreeCount.update(newPair)
    file = open("/home/ragnara/Schreibtisch/AppAnalyse/Graph/DegreeCount.csv", "a")
    file.write("Degree,Count \n")
    for d in dataDegreeCount:
        file.write(str(d) + "," + str(dataDegreeCount[d]) + "\n")
    file.close()
    


    #for app in appsOfEdge:
    #    print app

    #for edge in graph.edges:
    #    for app in graph.edges[edge]:
    #        if app == "com.redovals.divyaratna":
              #  print edge
    
    #for edge in graph.edges:
        #if edge[0] == "08e33a7af42aa81ba829c24b590559d9" and edge[1] == "8e21facef8ca2ef165c99074d1a60adb":
           # print graph.edges[edge]
    
            
    #numberOfEdgesPerApp = computeLengthOfFlowsDistribution(20, graph, allFlows)
    #output = open('lengthOfFlowDistribution.pkl', 'w')
    #pickle.dump(numberOfEdgesPerApp, output)
    #output.close()
    
    #print(numberOfEdgesPerApp)
    #input = open('OutgoingEdgesPerIntent.pkl')
    #data = pickle.load(input)
    #input.close()
    #dataSorted = sorted(data.items(), key=operator.itemgetter(1))
    #for d in dataSorted:
    #    print(str(d))

    #print("edgeSet: " + str(len(edgeSet)))
    #print("edges; " + str(len(graph.edges)))
    #print("intents; " + str(len(graph.intents)))
    #count = 0
    #for sink in graph.sinks:
    #    print(sink)
    #for edge in edgeSet:
    #    print(str(edge) + " : " + str(len(graph.edges[edge])) )
    #print("------------------------------------")
    #for edge in edgeSet:
    #    print(str(edge) + " : " + str(graph.edges[edge]))
    
main(sys.argv)
