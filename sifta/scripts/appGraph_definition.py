import os
import sys
import hashlib
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET
from graphviz import Digraph
from class_definitions import *

class ParentObject:
    def get_md5hash(self):
        md5 = hashlib.md5()
        md5.update(self.__str__())
        checksum = md5.hexdigest()
        return checksum


'''
Main class of the Graph
The graph object holds the datastructures necessary to completely represent the graph, but also
the datastructures necessary for inserting new flows, to properly fit the existing flows.
The class also support methods for saving its structure to an xml file (for persistence and portability)
as well as loading in an xml file.
'''
class AppGraph:
    intents = dict()
    apps = set()
    filterToSinkMapping = dict()
    onResult = dict()
    hashToObjectMapping = dict()
    processedApps = set()
    nodes = dict()
    sources = set()
    sinks = set()
    edges = dict()
    graphFileName = "graph.xml"
    mappingFileName = "mappings.xml"

    def __init__(self):
        pass
    
    def convertGraphIntoAppGraph(self, graph):
        allApps =set()
        for edge in graph.edges:
            for app in graph.edges[edge]:
                allApps.add(app)
        self.apps = allApps
        self.intents = graph.intents
        for edge in graph.edges:
            appsInEdge = graph.edges[edge]
            for edge2 in graph.edges:
                if edge != edge2:
                    if edge[1] == edge2[0]:
                        appsInEdge2 = graph.edges[edge2]
                        for app in appsInEdge:
                            for app2 in appsInEdge2:
                                newEdge = (app,app2)
                                if newEdge in self.edges:
                                    intents = self.edges[newEdge]
                                    intents.add(edge[1])
                                    updatedPair = {newEdge:intents}
                                    self.edges.update(updatedPair)
                                else:
                                    intents = set()
                                    intents.add(edge[1])
                                    newPair = {newEdge:intents}
                                    self.edges.update(newPair)
                                    
    

    def getNumberOfVertices(self):
        return len(self.nodes.keys())

    def getNumberOfEdges(self):
        return len(self.edges.keys())

    def getVertexDegrees(self):
        degrees = {n:len(self.nodes[n]) for n in self.nodes} #degree of outgoing edges
        for node in self.nodes: #degree of incomming edges
            for n in self.nodes[node]:
                degrees[n]+=1
        return degrees

    def getMaxDegree(self):
        degrees = self.getVertexDegrees()
        return max([degrees[v] for v in degrees])

    def getMinDegree(self):
        degrees = self.getVertexDegrees()
        return min([degrees[v] for v in degrees])

    def getMedianDegree(self):
        degrees = self.getVertexDegrees()
        if len(degrees.keys()) == 0:
            return 0
        values = sorted([degrees[v] for v in degrees])
        length = len(degrees.keys())
        if length%2 != 0:
            return values[length/2]
        else:
            fst = values[length/2]
            snd = values[length/2-1]
            med = (float(fst)+float(snd))/float(2)
            return med

    def getAverageDegree(self):
        degrees = self.getVertexDegrees()
        if len(degrees.keys()) == 0:
            return 0
        return float(sum([degrees[v] for v in degrees]))/float(len(degrees.keys()))

    def getVertexDegreeHistogram(self):
        degrees = self.getVertexDegrees()
        histogram = dict()
        for vertex in degrees:
            if degrees[vertex] not in histogram:
                histogram[degrees[vertex]] = 0
            histogram[degrees[vertex]]+=1
        return histogram

    def getPresenceConditionCount(self):
        count = set()
        for e in self.edges:
            count = count.union(self.edges[e])
        return len(count)

    def getAverageNumberOfPresenceConditions(self):
        if len(self.edges.keys()) == 0:
            return 0
        sum = 0
        for e in self.edges:
            sum+=len(self.edges[e])
        return float(sum)/float(len(self.edges.keys()))

    def getPresenceConditionMedian(self):
        count = [len(self.edges[e]) for e in self.edges]
        if len(count) == 0:
            return 0
        s_count = sorted(count)
        length = len(s_count)
        if length % 2 != 0:
            return s_count[length/2]
        else:
            fst = count[length/2]
            snd = count[length/2-1]
            med = (float(fst)+float(snd))/float(2)
            return med

    def getMaximumNumberOfPresenceConditions(self):
        return max([len(self.edges[e]) for e in self.edges])

    def getMinimumNumberOfPresenceConditions(self):
        return min([len(self.edges[e]) for e in self.edges])
 
    def drawGraph(self):
        sys.stderr.write("Drawing graph\n")
        seenBefore = set()
        dot = Digraph(comment="Graph")
        for key,edges in self.nodes.iteritems():
            simp = str(self.hashToObjectMapping[key])
            if simp not in seenBefore:
                dot.node(simp, simp)
                seenBefore.add(simp)
            for e in edges:
                esimp = str(self.hashToObjectMapping[e])
                if esimp not in seenBefore:
                    dot.node(esimp,esimp)
                    seenBefore.add(esimp)
                try:
                    #dot.edge(simp,esimp, label= ",".join(self.edges[key,e]))
                    dot.edge(simp,esimp, label= "Apps: {}".format(len(self.edges[key,e])))
                except:
                    pass
        dot.render("graph-test.gv", view=True)

  