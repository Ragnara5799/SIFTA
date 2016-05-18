import sys
import os
import random
import operator
from collections import *
from graphviz import Digraph
from class_definitions import *

from sets import Set #for filtering
from itertools import ifilter
from random import randint


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

def findPath(graph):
    visitedGraph = set()
    currentFlow = []

'''
Berechnet fuer alle Apps in cuttingApps, wie viele Flows sie trennen, wenn man sie entfernt.
'''
def computeFlowsCutByApps(cuttingApps, graph, allFlows):
    flowsCutByApps = dict()
    currentApp = set()
    appKeys = []
    appValues = []
    counter = 0
    for app in cuttingApps:
        counter += 1
        if(counter%100 == 0):
            print(str(counter))
        currentApp.clear()
        currentApp.add(app)
        appKeys.append(app)
        flowCutCounter = 0
        for flow in allFlows:
            minWeight = -1
            for edge in flow.edges:
                if edge in graph.edges:
                    if minWeight == -1:
                        minWeight = len(graph.edges[edge] - currentApp)
                    else:
                        newWeight = len(graph.edges[edge] - currentApp)
                        if newWeight < minWeight:
                            minWeight = newWeight
            if minWeight == 0:
                flowCutCounter += 1
        appValues.append(flowCutCounter)
    appZip = zip(appKeys,appValues)
    appToCutFlows = dict(appZip)
    return appToCutFlows

'''
Berechnet alle Apps, die mindestens einen Fluss trennen, wenn sie entfernt werden.
'''
def computeCuttingApps(graph, allFlows):
    cuttingApps = set()
    for flow in allFlows:
        minWeight = -1
        for edge in flow.edges:
            if edge in graph.edges:
                if len(graph.edges[edge]) == 1:
                    for app in graph.edges[edge]:
                        cuttingApps.add(app)
    return cuttingApps


'''
Berechnet einen partiellen min-cut des Graphen.
Mit partiellen mincut meinen wir, dass der Algorithmus solange Apps entfernt, bis genug Flows getrennt wurden
um das Ziel zu erreichen, mit der Einschraenkung das nur Apps entfernt werden, die mindestens einen Flow trennen wenn
nur die App alleine entfernt wird.
Das Ziel ist die mindest Anzahl der getrennten Flows in Prozent.
Der Algorithums stoppt entweder wenn das Ziel erreicht wurde, oder wenn keine App mehr die Einschraenkung
erfuellt.
'''
def computePartialMinCut(graph, allFlows, goal):
    allFlowsCopy = allFlows.copy()
    appsToRemove = set()
    while len(allFlowsCopy) != 0:
        cuttingApps = computeCuttingApps(graph, allFlowsCopy)
        if len(cuttingApps) == 0:
            break
        if float(len(allFlowsCopy)) / float(len(allFlows)) <= 1 - goal:
            break
        appToCutFlows = computeFlowsCutByApps(cuttingApps, graph, allFlowsCopy)
        sortedAppToCutFlows = sorted(appToCutFlows.items(), key=operator.itemgetter(1))
        appsToRemove.add(sortedAppToCutFlows[-1][0])
        allFlowsCopy = updateFlows(allFlowsCopy, appsToRemove)
    return [appsToRemove, allFlowsCopy]

'''
Aktualisiert alle Flows im Graphen, indem bereits entfernte Apps auch auf den Kanten entfernt werden
'''
def updateFlows(allFlows, removedApps):
    flowsToRemove = set()
    for flow in allFlows:
        minWeight = -1
        for edge in flow.edges:
            if edge in graph.edges:
                if minWeight == -1:
                    minWeight = len(graph.edges[edge] - removedApps)
                else:
                    newWeight = len(graph.edges[edge] - removedApps)
                    if newWeight < minWeight:
                        minWeight = newWeight
        if minWeight == 0:
            flowsToRemove.add(flow)
    for flow in flowsToRemove:
        allFlows.discard(flow)
    return allFlows


'''
Berechnet ein Set von Apps, die alle Flows im Graphen trennen, wenn man sie entfernt.
Aufgrund der Abhaengigkeiten zwischen den Kanten, kann nicht garantiert werden dass dieses Set minimal ist.
'''
def computeMinCut(graph, allFlows):
    removedEdges = set()
    removedApps = set()
    minWeightSum = 0
    numberOfMinWeight = 0
    flowCutCounter = 0
    for flow in allFlows:
        # ueberprueft ob im aktuellen flow eine Kante vorhanden ist,die bereits entfernt wurde
        if len(set(flow.edges).intersection(removedEdges)) == 0:
            minWeight = -1
            edgeToRemove = -1
            for edge in flow.edges:
                if edge in graph.edges:
                    if minWeight == -1:
                        minWeight = len(graph.edges[edge] - removedApps)
                        edgeToRemove = edge
                    else:
                        newWeight = len(graph.edges[edge] - removedApps)
                        if newWeight < minWeight:
                            minWeight = newWeight
                            edgeToRemove = edge
            if minWeight != -1:
                numberOfMinWeight += 1
                minWeightSum = minWeightSum + minWeight
                removedEdges.add(edgeToRemove)
                for app in graph.edges[edgeToRemove]:
                    removedApps.add(app)
        else:
            flowCutCounter = flowCutCounter + 1
    return removedApps
                
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
        
        
# ---------------------min cut part-------------------------
    ouputDirectory = args[2]  
    nodeCounter = 0
    print("beginn mincut algorithm")
    print("AllFlowsCount: " + str(len(allFlows)))
    removedApps = computeMinCut(graph,allFlows)
    print("removed Apps MinCut: " + str(len(removedApps)))
    allApps = set()
    for edge in graph.edges:
        for app in graph.edges[edge]:
            allApps.add(app)
    print("all apps: " + str(len(allApps)))   
    for edge in graph.edges:     
        print(graph.edges[edge])
        break
    cuttingApps = computeCuttingApps(graph, allFlows)
    flowsCutByApps = computeFlowsCutByApps(cuttingApps, graph, allFlows)
    sortedFlowsCutByApps = sorted(flowsCutByApps.items(), key=operator.itemgetter(1))
    file = open(str(ouputDirectory) + "flowsCutByApps.txt","w")
    for flow in sortedFlowsCutByApps:
        file.write(str(flow) + "\n")
    file.close()
    print("Cutting Apps Size: " + str(len(cuttingApps)))
    minimumCut = float(sys.argv[1]) #0.97
    appsToRemove = computePartialMinCut(graph, allFlows, minimumCut)
    file = open(str(ouputDirectory) + '/partialMinCut.txt', 'w')
    file.write("minimum Percent of Flows Cut: " + str(minimumCut) + "\n")
    file.write("removed partial apps: " + str(appsToRemove[0]) + "\n")
    file.write("flows that are left: " + str(len(appsToRemove[1])) + "\n")
    file.write("all Flows : " + str(len(allFlows)) + "\n")
    file.close()
    print("removed partial apps: " + str(appsToRemove[0]))
    print("flows that are left: " + str(len(appsToRemove[1])))
    print("all Flows : " + str(len(allFlows)))
    

main(sys.argv)
