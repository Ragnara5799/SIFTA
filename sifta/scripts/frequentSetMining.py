# -*- coding: ascii -*-
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
'''
Berechnet ein dictionary, welches einem Flow des Graphen einer Menge von Apps zuordnet
die in diesem Flow vorkommen.
Gleichzeitig wird auch ein set aller Apps berechnet und beides zurueckgegeben.
'''
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

'''
Berechnet eine Liste von Listen, die Sets enthalten.
Fuer jeden Flow wird ein Liste erstellt. Fuer jede Kante in dem Flow
wird ein Set alle Apps dieser Kante erstellt und der Liste des Flows hinzugefuegt.
Diese Listen werden dann als Liste zurueckgegeben.
'''
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

'''
Hier wird das erste SupportSet berechnet.
Dabei wird fuer jede App berechnet in wievielen flows sie vorkommt.
Diese daten werden in einem Dictionary gespeichert.
'''
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

'''
Hier wird das erste SupportSet fuer den Clustergraphen berechnet.
Dabei wird fuer jede App berechnet in wievielen Kanten sie vorkommt.
Diese Daten werden dann in einem Dictionary gespeichert.
'''
def computeFirstSupportSetSameEdge(appsToFlow, allApps, graph):
    appSupport = dict()
    for app in allApps:
        newPair = {app: 0}
        appSupport.update(newPair)
    for edge in graph.edges:
        for app in graph.edges[edge]:
            if app in appSupport:
                counter = appSupport[app] + 1
                newPair = {app : counter}
                appSupport.update(newPair)
    return appSupport

'''
Hier wird ein SupportSet fuer das setMining mit der Option "sameFlowDifferentEdges" berechnet.
Dabei wird fuer jede tupel von Apps in appTupel berechnet, in wievielen Flows sie gemeinsam vorkommen,
ohne dabei auf der selben Kante zu liegen
'''
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

'''
Hier wird ein SupportSet fuer den Clustergraphen berechnet.
Dabei wird fuer jede AppTupel auf einer Kante des Graphen vorkommt.
'''
def computeSupportSetSameEdge(appTupel, graph):
    appSupport = dict()
    advanceCounter = 0
    for app in appTupel:
        newPair = {app:0}
        appSupport.update(newPair)
    for edge in graph.edges:
        advanceCounter += 1
        if advanceCounter%100 == 0:
            print(advanceCounter)
        for app in graph.edges[edge]:
            for app2 in graph.edges[edge]:
                if app != app2:
                    if (app,app2) in appSupport:
                        counter = appSupport[(app,app2)] + 1
                        newPair = {(app,app2):counter}
                        appSupport.update(newPair)
    return appSupport

'''
Hier wird ein SupportSet fuer das setMining mit der Option "sameFlow" berechnet.
Dabei wird fuer jede tupel von Apps in appTupel berechnet, in wievielen Flows sie gemeinsam vorkommen.
'''
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

'''
Hier wird das naechste Set von AppTupel berechnet.
Dabei werden alle Kombinationen der einzelnen Apps mit den vorhandenen AppTupel berechnet, wobei
die Tupel die das supportMinimum (also die mindest Anzahl wie haeufig sie auf der selben Kante/Fluss
vorkommen muessen um im weiteren Verlauf des Algorithmus beachtet zu werden.) nicht erreichen herausgefiltert
werden.
'''
def computeNextAppSet(singleApps, previousSupportDict, removedAppCombos, supportMinimum, step):
    appsForNextStep = set()
    permutations = set()
    newAppSet = list()
    if step == 2:
        for firstApp in singleApps:
            for secondApp in singleApps:
                if firstApp != secondApp:
                    newSet = set()
                    newSet.add(firstApp)
                    newSet.add(secondApp)
                    newList = (firstApp, secondApp)
                    if newList not in permutations:
                        newAppSet.append(newList)
                        permutations.add((secondApp,firstApp))
        return (newAppSet,removedAppCombos)
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

'''
Diese Methode ueberprueft, ob eine AppCombo in einem Flow vorkommt mit der Einschraenkung
das alle Apps auf verschiedenen Kanten liegen.
Diese Methode ist rekursiv und etwas kompliziert.
edgeSet ist eine Liste von Kanten die jeweils ein Set enthaelt die die Apps auf dieser Kante enthalten.
Die Liste die diese Liste enhaelt wird in der Methode "computeEdgesInFlows" zuvor in der main-Methode 
berechnet "mainSameFlowDifferentEdges".
removedEdges speichert die Kanten auf denen bereits eine App liegt 
und somit fuer die anderen Apps Tabu ist. deep steht fuer die Tiefe der rekursion.
Zunaechst wird ueberprueft ob deep groesser als die Laenge der appCombination ist. Wenn das true ist,
bedeutet es das alle Apps der Combination auf verschiedenen Kanten untergebracht worden sind.
Somit dient diese Bedingung als Abbruchbedingung der Rekursion.
Dann wird fuer jede Kante, die noch nicht entfernt wurde ueberprueft ob die aktuelle betrachtete App
auf dieser Kante liegt. Wenn ja wird die Rekursion ausgefuehrt. Sollte keine Kante mehr gefunden werden,
die die App enthaelt wirdein false zurueckgegeben.
'''                        
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

'''
Ueberprueft ob das newTupel eine bereits aussortierte AppCombination
enthaelt. 
Beispiel: (A,B) wurde aussortiert. (B,C) nicht. Im Verlauf des Algorithmus
wird (A,B,C) erstellt. Da diese aber (A,B) enhaelt kann sie die supportMinimum nicht erfuellen
und kann sofort aussortiert werden.
'''
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

'''
Hier wird der Algorithmus fuer das Set-Mining ausgefuehrt.
Solange es noch AppCombinationen in nextAppSet gibt, wird fuer diese zuerst ein neues
SupportSet berechnet. Daraus wird dann dass naechste AppSet berechnet.
Anmerkung: Bei einem zu niedrigen SuppportMinimum werden viel zu wenige AppCombinationen aussortiert 
und die Groesse der nextAppSet explodiert, sowie die Laufzeit des Algorithmus wenn es nciht sogar zu einem
Abbruch wegen Speicherproblemen kommt.
Ausserdem werden in dieser Methode auch die SupportSets aller Schritte zwischengespeichert, sowohl in .pkl
um sie spaeter wieder einfach einlesen zu koennen, als auch in sortierter .txt Format um sich die Ergebnisse
ansehen zu koennen.
Auch die entfernten AppCombinationen werden gespeichert.
Dass wuerde ein weiterausfuehren des Algorithmus zu einem spaeteren Zeitpunkt erlauben.(Erfordert ein paar Anpassungen
in der entsprechenden main-Methode) 
'''
def setMining(singleApps, startSupportDict, appsToFlow ,removedAppCombos, supportMinimum, step, outputDirectory):
    newAppSet = computeNextAppSet(singleApps, startSupportDict, removedAppCombos, supportMinimum, step)
    nextAppSet = newAppSet[0]
    newRemovedAppCombos = newAppSet[1]
    currentStep = step
    while len(nextAppSet) != 0:
        print("next AppSet size: " + str(len(nextAppSet)))
        print("start step " + str(currentStep) + " at " + str(time.localtime()))
        nextSupportDict = computeSupportSet(appsToFlow, nextAppSet)
        output = open(str(outputDirectory) + "/SupportSet" + str(supportMinimum) + "_" + str(currentStep) + ".pkl", 'w')
        pickle.dump(nextSupportDict, output)
        output.close()
        
        sortedSupportSet = sorted(nextSupportDict.items(), key=operator.itemgetter(1))
        file = open(str(outputDirectory) + "/SupportSet" + str(supportMinimum) + "_" + str(currentStep) + ".txt", 'w')
        for suppSet in sortedSupportSet:
            file.write(str(suppSet) + "\n")
        file.close()
        
        output2 = open(str(outputDirectory) + "/removedAppCombos" + str(supportMinimum) + "_" + str(currentStep) + ".pkl", 'w')
        pickle.dump(newRemovedAppCombos, output2)
        output2.close()
        print("step " + str(currentStep) + " finished at " + str(time.localtime()))
        currentStep += 1
        newAppSet = computeNextAppSet(singleApps, nextSupportDict, newRemovedAppCombos, supportMinimum, currentStep)
        nextAppSet = newAppSet[0]
        newRemovedAppCombos = newAppSet[1]

'''
Macht das selbe wie die obere Methode nur mit entsprechenden Methoden
fuer die SupportSet Berechnung fuer die Option "sameFlowDifferentEdges"
'''
def setMiningEdgeBased(singleApps, startSupportDict, edgesToFlow ,removedAppCombos, supportMinimum, step, outputDirectory):
    newAppSet = computeNextAppSet(singleApps, startSupportDict, removedAppCombos, supportMinimum, step)
    nextAppSet = newAppSet[0]
    newRemovedAppCombos = newAppSet[1]
    currentStep = step
    while len(nextAppSet) != 0:
        print("next AppSet size: " + str(len(nextAppSet)))
        print("start step " + str(currentStep) + " at " + str(time.localtime()))
        nextSupportDict = computeSupportSetEdgeBased(edgesToFlow, nextAppSet)
        output = open(str(outputDirectory) + "/SupportSetEdgeBased" + str(supportMinimum) + "_" + str(currentStep) + ".pkl", 'w')
        pickle.dump(nextSupportDict, output)
        output.close() 
        sortedSupportSet = sorted(nextSupportDict.items(), key=operator.itemgetter(1))
        file = open(str(outputDirectory) + "/SupportSetEdgeBased" + str(supportMinimum) + "_" + str(currentStep) + ".txt", 'w')
        for suppSet in sortedSupportSet:
            file.write(str(suppSet) + "\n")
        file.close()
        output2 = open(str(outputDirectory) + "/removedAppCombosEdgeBased" + str(supportMinimum) + "_" + str(currentStep) + ".pkl", 'w')
        pickle.dump(newRemovedAppCombos, output2)
        output2.close()
        print("step " + str(currentStep) + " finished at " + str(time.localtime()))
        currentStep += 1
        newAppSet = computeNextAppSet(singleApps, nextSupportDict, newRemovedAppCombos, supportMinimum, currentStep)
        nextAppSet = newAppSet[0]
        newRemovedAppCombos = newAppSet[1]  

'''
Die main-Methode fuer die Option "sameFlowDifferentEdges".
Hier werden der Reihe nach die Vorbereitungen fuer den Set-Mining Algorithmus mit der Option
"sameFlowDifferentEdges" ausgefuehrt.
Dabei werden zum einen einige Listen und Set berechnet die fuer den Algorithmus noetig sind.
Ausserdem wird ueberprueft ob das erste SupportSet bereits berechnet wurde.
Das wird gemacht um Zeit zu sparen, da das erste SupportSet immer gleich bleibt, egal
welches Supportminimum gewaehlt wird und die Berechnung dieses Sets einigermassen aufwendig ist.
Ausserdem werden noch ein paar Informationen auf der Konsole ausgegeben.
Wichtig hierbei sind vorallem "intresting App" die die Anzahl der Apps angibt die das Supportminimum 
des ersten SupportSets erfuellen angeben. Ebenso wichtig ist "appSet", die die Groesse des ersten AppSet
angibt. Die beiden Groessen sind direkt voneinander abhaengig und wenn sie zu Gross sind, ist es sehr wahrscheinlich
das der Algorithmus nach ein paar Schritten stecken bleibt.(Aufgrund der explodierenden Groesse von AppSet)
'''
def mainSameFlowDifferentEdges(args,graph,allFlows):
    outputDirectory = args[2]
    supportLimit = int(args[3])
    supportLimitDifEdge = int (args[5])
    appsInFlows = computeAppsInFlows(allFlows, graph)
    appsOfFlows = appsInFlows[0]
    allApps = appsInFlows[1]
    fSSetAlreadyComputed = int(args[4])
    if fSSetAlreadyComputed == 0:
        firstSupportSet = computeFirstSupportSet(appsOfFlows, allApps)
        output = open(str(outputDirectory) + '/firstSupportSet.pkl','w')
        pickle.dump(firstSupportSet, output)
        output.close()
    input = open(str(outputDirectory) + '/firstSupportSet.pkl')
    firstSupportSet = pickle.load(input)
    input.close()
    edgesOfFlows = computeEdgesInFlows(allFlows, graph)
    print("appsOfFlows: " + str(len(appsOfFlows)))
    print("allApps: " + str(len(allApps)))
    interestingApps = set()
    for app in firstSupportSet:
        if firstSupportSet[app] > supportLimit: # supportLimit 140
            interestingApps.add(app)
    print("instresting Apps: " + str(len(interestingApps)))
    print("start Algorithm")
    removedAppCombos = list()
    setMiningEdgeBased(interestingApps, firstSupportSet, edgesOfFlows ,removedAppCombos, supportLimitDifEdge, 2,outputDirectory)

'''
Die main-Methode fuer die Option "sameFlow".
Hier werden der Reihe nach die Vorbereitungen fuer den Set-Mining Algorithmus mit der Option
"sameFlow" ausgefuehrt.
Dabei werden zum einen einige Listen und Set berechnet die fuer den Algorithmus noetig sind.
Ausserdem wird ueberprueft ob das erste SupportSet bereits berechnet wurde.
Das wird gemacht um Zeit zu sparen, da das erste SupportSet immer gleich bleibt, egal
welches Supportminimum gewaehlt wird und die Berechnung dieses Sets einigermassen aufwendig ist.
Ausserdem werden noch ein paar Informationen auf der Konsole ausgegeben.
Wichtig hierbei sind vorallem "intresting App" die die Anzahl der Apps angibt die das Supportminimum 
des ersten SupportSets erfuellen angeben. Ebenso wichtig ist "appSet", die die Groesse des ersten AppSet
angibt. Die beiden Groessen sind direkt voneinander abhaengig und wenn sie zu Gross sind, ist es sehr wahrscheinlich
das der Algorithmus nach ein paar Schritten stecken bleibt.(Aufgrund der explodierenden Groesse von AppSet)
'''
def mainSameFlow(args,graph,allFlows):
    outputDirectory = args[2]
    supportLimit = int(args[3])
    appsInFlows = computeAppsInFlows(allFlows, graph)
    appsOfFlows = appsInFlows[0]
    allApps = appsInFlows[1]
    fSSetAlreadyComputed = int(args[4])
    if fSSetAlreadyComputed == 0:
        firstSupportSet = computeFirstSupportSet(appsOfFlows, allApps)
        output = open(str(outPutDirectory) + '/firstSupportSet.pkl','w')
        pickle.dump(firstSupportSet, output)
        output.close()
    input = open(str(outputDirectory) + '/firstSupportSet.pkl')
    firstSupportSet = pickle.load(input)
    input.close()
    print("appsOfFlows: " + str(len(appsOfFlows)))
    print("allApps: " + str(len(allApps)))
    interestingApps = set()
    for app in firstSupportSet:
        if firstSupportSet[app] > supportLimit:
            interestingApps.add(app)
    print("instresting Apps: " + str(len(interestingApps)))
    print("start Algorithm")
    removedAppCombos = list()
    setMining(interestingApps, firstSupportSet, appsOfFlows ,removedAppCombos, supportLimit, 2,outputDirectory)

'''
Die main-Methode fuer die Option "transformSetMiningIntoGraph".
Hier werden der Reihe nach die Vorbereitungen fuer den Set-Mining Algorithmus mit der Option
"transformSetMiningIntoGraph" ausgefuehrt.
Dabei werden zum einen einige Listen und Set berechnet die fuer den Algorithmus noetig sind.
Ausserdem wird ueberprueft ob das erste SupportSet bereits berechnet wurde.
Das wird gemacht um Zeit zu sparen, da das erste SupportSet immer gleich bleibt, egal
welches Supportminimum gewaehlt wird und die Berechnung dieses Sets einigermassen aufwendig ist.
Hier stoppt der Algorithmus bereits nach dem 2. Schritt. Es werden also nutr AppPaare untersucht, da wir 
nur diese Informationen fuer den Graphen brauchen der spaeter mit Clusterverfahren untersucht wird.
Im Anschluss an die SupportSet Berechnung werden diese Informationen dann zu einem Graphen umgewandelt.
Dabei bedeutet ein AppPaar das zwischen diesen beiden Apps eine Kante besteht. Der Wert aus dem SupportSet 
fuer dieses AppPaar gibt dann das Gewicht der Kante an.
'''
def mainTransformSetMiningGraph(args,graph, allFLows):
    outputDirectory = args[2]
    supportLimit = int(args[3])
    appsInFlows = computeAppsInFlows(allFlows, graph)
    appsOfFlows = appsInFlows[0]
    allApps = appsInFlows[1]
    fSSetAlreadyComputed = int(args[4])
    if fSSetAlreadyComputed == 0:
        firstSupportSet = computeFirstSupportSetSameEdge(appsOfFlows, allApps, graph)
        output = open(str(outPutDirectory) + '/firstSupportSetSameEdge.pkl','w')
        pickle.dump(firstSupportSet, output)
        output.close()
    input = open(str(outputDirectory) + '/firstSupportSetSameEdge.pkl')
    firstSupportSet = pickle.load(input)
    input.close()
    print("appsOfFlows: " + str(len(appsOfFlows)))
    print("allApps: " + str(len(allApps)))
    interestingApps = set()
    for app in firstSupportSet:
        if firstSupportSet[app] > supportLimit: # supportLimit 140
            interestingApps.add(app)
    print("instresting Apps: " + str(len(interestingApps)))
    appPairs = set()
    redundantAppPairs = set()
    for firstApp in interestingApps:
        for secondApp in interestingApps:
            if firstApp != secondApp:
                newSet = set()
                newSet.add(firstApp)
                newSet.add(secondApp)
                newList = (firstApp, secondApp)
                if newList not in redundantAppPairs:
                    appPairs.add(newList)
                redundantAppPairs.add((secondApp,firstApp))
    supportSet = computeSupportSetSameEdge(appPairs, graph)
    tranformSetMiningIntoGraph(supportSet, outputDirectory, args[5])

'''
Die Methode wandelt die Informationen aus dem SupportSet fuer AppPaare
in einen Graphen um und speichert diesen in einem einfachen Textformat.
Bsp: A,B,20 bedeutet das eine Kante zwischen A und B besteht mit dem Kantengewicht 20.
'''    
def tranformSetMiningIntoGraph(data, outputDirectory, outputName):
    allApps = set()
    for appTupel in data:
        allApps.add(appTupel[0])
        allApps.add(appTupel[1])
    print("apps: " + str(len(allApps)))
    appsToId = dict()
    idToApps = dict()
    id = 0
    for app in allApps:
        appsToIdPair = {app : id}
        idToAppsPair = {id : app}
        appsToId.update(appsToIdPair)
        idToApps.update(idToAppsPair)
        id += 1
    outputFile = open(str(outputDirectory) + "/" + str(outputName) + ".txt", 'w')
    for appTupel in data:
        outputFile.write(str(appsToId[appTupel[0]]) + "," + str(appsToId[appTupel[1]]) + "," + str(data[appTupel]) + "\n")
    outputFile.close()
    appsToIdOutput = open(str(outputDirectory) + "/appsToId_" + str(outputName) + ".pkl",'w')
    idToAppsOutput = open(str(outputDirectory) + "/idToApps_" + str(outputName) + ".pkl",'w')
    pickle.dump(appsToId,appsToIdOutput)
    pickle.dump(idToApps,idToAppsOutput)
    appsToIdOutput.close()
    idToAppsOutput.close()

'''
Diese Methode sortiert ein SupportSet und schreibt es in eine .txt-Datei
'''
def sortSupportSet(input, output):
    inputFile = open(input)
    data = pickle.load(inputFile)
    dataSorted = sorted(data.items(), key=operator.itemgetter(1))
    file = open(output, "a")
    for d in dataSorted:
        file.write(str(d) + "\n")
    file.close()
        
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
    '''
    Hier werden verschiedene Typen von frequentSetMining berechnet.
    Bei der Option 'sameFlow' wird der Zaehler fuer eine Gruppe von Apps dann    
    erhoeht, wenn sich alle Apps der Gruppe im selben flow des Graphen befinden.
    
    Bei der Option 'sameFlowDifferentEdges' gilt zusaetzlich die Einschraenkung, dass
    sich alle Apps auf verschiedenen Kanten innerhalb des flows befinden.
    
    Bei der Option transformSetMiningIntoGraph gilt die Einschraenkung das sich alle Apps
    der Gruppe auf der selben Kante befinden muessen. Diese Berechnng wird spaeter fuer Clustering
    gebraucht, bei der wir versuchen Gruppen von Apps zu finden die aehnlich verhalten bzw. kommunizieren.
    Ebenso wird in dieser Option ein Graph berechnet und in einer Datei gespeichert, der fuer das Clustering
    Programm verwendet wird
    '''
    
        
    if args[1] == 'sameFlowDifferentEdges':
        mainSameFlowDifferentEdges(args,graph,allFlows)
    elif args[1] == 'sameFlow':
        mainSameFlow(args,graph,allFlows)
    elif args[1] == 'transformSetMiningIntoGraph':
        mainTransformSetMiningGraph(args,graph,allFlows)


    
main(sys.argv)
