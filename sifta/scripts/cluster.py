#!/usr/bin/env python
import community
import networkx as nx
import math
import csv
import random as rand
import sys
import matplotlib.pyplot as plt
import pickle

'''
Hier wird der Graph aus der Datei gelesen und gebaut.
'''
def buildG(G, file_, delimiter_, minimumWeight):
    #construct the weighted version of the contact graph from cgraph.dat file
    #reader = csv.reader(open("/home/kazem/Data/UCI/karate.txt"), delimiter=" ")
    file = open(file_)
    reader = csv.reader(file, delimiter=delimiter_)
    for line in reader:
        if len(line) > 2:
            if float(line[2]) > minimumWeight:
                #line format: u,v,w
                G.add_edge(int(line[0]),int(line[1]),weight=float(line[2]))
        else:
            #line format: u,v
            G.add_edge(int(line[0]),int(line[1]),weight=1.0)
    file.close()


'''
Loescht alle Kanten, deren Gewicht kleiner als weight ist.
'''
def deleteEdgesWithWeightSmallerThanX(G,weight):
    for edge in G.edges():
        if G[edge[0]][edge[1]]['weight'] <= weight:
            G.remove_edge(edge[0],edge[1])

'''
Berechnet alle Teilgraphen von G. 
'''
def computeIndependentSubgraphs(G):
    notVisitedNodes = set()
    nodesToCompute = set()
    subGraphs = list()
    for node in G.nodes():
        notVisitedNodes.add(node)
        nodesToCompute.add(node)
    for cNode in nodesToCompute:
        newGraphNodes = set()
        if cNode in notVisitedNodes:
            newGraphNodes.add(cNode)
            notVisitedNodes.remove(cNode)
            computedNodes = set()
            neighbors = G.neighbors(cNode)
            while len(neighbors) != 0:
                newNeighbors = set()
                for node in neighbors:
                    if node in notVisitedNodes:
                        notVisitedNodes.remove(node)
                        for n in G.neighbors(node):
                            newNeighbors.add(n)
                        newGraphNodes.add(node)
                neighbors = newNeighbors
            newG = nx.Graph(G.subgraph(newGraphNodes))
            subGraphs = subGraphs + [newG]
    return subGraphs  
    
'''
Speichert die Cluster, die groesser als 1 sind in Dateien.
Auserdem wird auf Cluster mit Groese 50 oder mehr ein weiterer Clusteralgorithmus ausgefuehrt.
Er funktoniert in diesem Fall(bei edgeLimit 28), aber kann Fehler auswerfen wenn an versucht
den Algorithmus auf mehrere Subgraphen auszufuehren, keine Ahnung wo der Fehler liegt.
'''
def saveCluster(outPutDirectory, subGraphs, idToApps, edgeLimit, outputName ):
    counter = 0
    
    for graph in subGraphs:
        if graph.number_of_nodes() > 1:
            output = open(str(outPutDirectory) + "/subGraphNodesFiltered_" + outputName + "_" + str(int(edgeLimit)) + "_" + str(counter) + ".txt", 'w')
            for node in graph.nodes():
                output.write(str(idToApps[node]) + "\n")
            output.close()
            counter += 1
        if graph.number_of_nodes() > 50:
            partition = community.best_partition(graph)
            counter2 = 0
            processing = 1
            while(processing == 1):
                processing = 0
                for p in partition:
                    if partition[p] == counter2:
                        processing = 1
                if processing == 1:
                    output2 = open(str(outPutDirectory) + "/subGraphNodesFilteredBigCluster_"+ outputName + "_" + str(int(edgeLimit)) + "_" + str(counter2) + ".txt", 'w')
                    for p in partition:
                        if partition[p] == counter2:
                            output2.write(str(idToApps[p]) + "\n")
                    output2.close()
                counter2 += 1
    
def main(argv):
    outputDirectory = argv[2]
    graph_fn = argv[1] + ".txt"
    edgeLimit = float(argv[3])
    outputName = argv[4]
    G = nx.Graph()
    buildG(G, graph_fn, ',', 0.0)    
    deleteEdgesWithWeightSmallerThanX(G,edgeLimit)
    subGraphs = computeIndependentSubgraphs(G)
    input = open(str(outputDirectory) + "/idToApps_" + str(outputName) + ".pkl")
    idToApps = pickle.load(input)
    input.close()
    saveCluster(outputDirectory, subGraphs, idToApps, edgeLimit, outputName )
    
    print G.number_of_nodes()
    print G.number_of_edges()
if __name__ == "__main__":
    sys.exit(main(sys.argv))
