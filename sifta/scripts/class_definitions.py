import os
import sys
import hashlib
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET
from graphviz import Digraph

class ParentObject:
    def get_md5hash(self):
        md5 = hashlib.md5()
        md5.update(self.__str__())
        checksum = md5.hexdigest()
        return checksum

class IntentDefinition(ParentObject):
    def __init__(self, actions, categories, mimeTypes, data, componentType):
        assert(isinstance(actions, list))
        assert(isinstance(categories, list))
        assert(isinstance(mimeTypes, list))

        self.actions = actions
        self.categories = categories
        self.mimeTypes = mimeTypes
        self.data = data
        self.matchAll = False
        self.matchingClass = None
        self.componentType = componentType

    def __str__(self):
        #if len(self.actions) == 0:
        if self.matchingClass != None:
            return "Explicit Intent ({})".format(self.matchingClass)
        else:
            return "Actions: '{}'\nCategories: '{}' \nMime-types: '{}'\nData: '{}'\nComponent: '{}'".format(",".join([e for e in self.actions]), ",".join([e for e in self.categories]), ",".join([e for e in self.mimeTypes]), self.data, self.componentType)

    def get_intentdefinition_element(self, parent):
        intentDefinition = SubElement(parent, 'IntentDefinition',
                                      data = self.data,
                                      matchAll = str(self.matchAll),
                                      matchingClass = str(self.matchingClass),
                                      componentType = self.componentType,
                                      actions = ",".join(self.actions),
                                      categories = ",".join(self.categories),
                                      mimeTypes = ",".join(self.mimeTypes))

    @staticmethod
    def to_intentdefinition(definition_element):
        actions = definition_element.attrib["actions"].split(",") if len(definition_element.attrib["actions"]) else []
        categories = definition_element.attrib["categories"].split(",") if len(definition_element.attrib["categories"]) else []
        mimeTypes = definition_element.attrib["mimeTypes"].split(",") if len(definition_element.attrib["mimeTypes"]) else []
        data = definition_element.attrib["data"]
        matchAll = definition_element.attrib["matchAll"]
        matchingClass = definition_element.attrib["matchingClass"]
        componentType = definition_element.attrib["componentType"]

        intentdefiniton = IntentDefinition(actions, categories, mimeTypes, data, componentType)
        intentdefiniton.matchAll = matchAll == "True"
        intentdefiniton.matchingClass = None if matchingClass == "None" else matchingClass
        return intentdefiniton

class Intent(ParentObject):
    def __init__(self, intentDefinition, app):
        self.intentDefinition = intentDefinition
        self.app = app

    def __str__(self):
        return "Intent(\n{}\n)".format(self.intentDefinition)

    def to_xml(self):
        intent = Element('Intent', app = self.app)
        child = self.intentDefinition.get_intentdefinition_element(intent)
        return tostring(intent)

    @staticmethod
    def from_xml(xmlstring):
        root = ET.fromstring(xmlstring)
        app = root.attrib['app']
        definition = root.find("IntentDefinition")
        intentdefinition = IntentDefinition.to_intentdefinition(definition)

        intent = Intent(intentdefinition, app)

        return intent

class IntentResult(ParentObject):
    def __init__(self, intentDefinition, app):
        self.intentDefinition = intentDefinition
        self.app = app

    def __str__(self):
        return "IntentResult(\n{}\n)".format(self.intentDefinition)

    def to_xml(self):
        intent = Element('IntentResult', app = self.app)
        child = self.intentDefinition.get_intentdefinition_element(intent)
        return tostring(intent)

    @staticmethod
    def from_xml(xmlstring):
        root = ET.fromstring(xmlstring)
        app = root.attrib['app']
        definition = root.find("IntentDefinition")
        intentdefinition = IntentDefinition.to_intentdefinition(definition)

        intentResult = IntentResult(intentdefinition, app)

        return intentResult

class Flow(ParentObject):
    def __init__(self, source, sink, app):
        assert(not isinstance(source, Sink))
        assert(not isinstance(sink, Source))

        self.source = source
        self.sink = sink
        self.app = app
    def __str__(self):
        return "Flow(\n\tsource: {}\n\t sink: {}".format(self.source, self.sink)

class InternalFlow(ParentObject):
    def __init__(self, source, sink, app):
        self.source = source
        self.sink = sink
        self.app = app

    def __str__(self):
        return "InternalFlow(\n\tSource:\n\t\t{}\n\tSink:\n\t\t{}".format(self.source, self.sink)

    def toFlow(self):
        source = self.source
        sink = self.sink

        if isinstance(self.source, str):
            source = Source(self.app, self.source)

        if isinstance(self.sink, str):
                sink = Sink(self.app, self.sink)

        return Flow(source, sink, self.app)

class IntentFilter(ParentObject):
    def __init__(self, intentDefinition, app, priority):
        self.intentDefinition = intentDefinition
        self.app = app
        self.priority = priority

    def __str__(self):
        return "IntentFilter(\n{}\n)".format(self.intentDefinition)

    def to_xml(self):
        intent = Element('IntentFilter', app = self.app, priority = str(self.priority))
        child = self.intentDefinition.get_intentdefinition_element(intent)
        return tostring(intent)

    @staticmethod
    def from_xml(xmlstring):
        root = ET.fromstring(xmlstring)
        app = root.attrib['app']
        priority = root.attrib['priority']
        definition = root.find("IntentDefinition")
        intentdefinition = IntentDefinition.to_intentdefinition(definition)

        intentFilter = IntentFilter(intentdefinition, app, int(priority))

        return intentFilter

class SourceSink(ParentObject):
    def __init__(self, app, method):
        self.app = app
        self.method = method

class Source(SourceSink):
    def __str__(self):
        a = self.method.split(": ")
        b = a[-1].split(" ")
        c = b[-1].split("(")[0]
        d = a[1].split(".")[-1]
        res = "{} \n{}.{}()".format(a[0],d, c)
        return res
        #return "{}".format(self.method)

    def to_xml(self):
        source = Element('Source', app = self.app, method = self.method)
        return tostring(source)

    @staticmethod
    def from_xml(xmlstring):
        root = ET.fromstring(xmlstring)
        app = root.attrib['app']
        method = root.attrib['method']
        return Source(app, method)

class Sink(SourceSink):
    def __str__(self):
        a = self.method.split(": ")
        b = a[-1].split(" ")
        c = b[-1].split("(")[0]
        d = a[0].split(".")[-1]
        res = "{} \n{}.{}()".format("Sink",d, c)
        return res

    def to_xml(self):
        source = Element('Sink', app = self.app, method = self.method)
        return tostring(source)

    @staticmethod
    def from_xml(xmlstring):
        root = ET.fromstring(xmlstring)
        app = root.attrib['app']
        method = root.attrib['method']
        return Sink(app, method)

class TypeDistribution:
    def __init__(self, src, snk, intent, intres, uncat):
        self.SourceCount = src
        self.SinkCount = snk
        self.IntentCount = intent
        self.IntentResultCount = intres
        self.UncategorizedVertexCount = uncat

'''
Main class of the Graph
The graph object holds the datastructures necessary to completely represent the graph, but also
the datastructures necessary for inserting new flows, to properly fit the existing flows.
The class also support methods for saving its structure to an xml file (for persistence and portability)
as well as loading in an xml file.
'''
class Graph:
    intents = dict()
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

    def getTypeDistribution(self):
        src = 0
        snk = 0
        intent = 0
        intres = 0
        uncategorized = 0
        for v in self.nodes:
            if isinstance(self.hashToObjectMapping[v], Source):
                src+=1
            elif isinstance(self.hashToObjectMapping[v], Sink):
                snk+=1
            elif isinstance(self.hashToObjectMapping[v], Intent):
                intent+=1
            elif isinstance(self.hashToObjectMapping[v], IntentResult):
                intres+=1
            else:
                uncategorized+=1
        return TypeDistribution(src,snk,intent, intres, uncategorized)

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

    def getPresenceConditionHistogram(self):
        histogram = dict()
        for edge in self.edges:
            if len(self.edges[edge]) not in histogram:
                histogram[len(self.edges[edge])] = 0
            histogram[len(self.edges[edge])]+=1
        return histogram

    def printAllStatistics(self):
        sys.stdout.write("Gathering statistics")
        statisticFile = open("statistics.txt", 'w')

        statisticFile.write("Number of Nodes: {}".format(self.getNumberOfVertices()))
        statisticFile.write("\nNumber of Edges: {}".format(self.getNumberOfEdges()))
        statisticFile.write("\nMin Degree: {} \nMax Degree: {}".format(self.getMinDegree(), self.getMaxDegree()))
        statisticFile.write("\nMedian Degree: {}".format(self.getMedianDegree()))
        statisticFile.write("\nAverage Degree: {}".format(self.getAverageDegree()))
        statisticFile.write("\nNumber of Apps per Edge: {}".format(self.getPresenceConditionCount()))
        statisticFile.write("\nMin number of Apps per Edge: {}".format(self.getMinimumNumberOfPresenceConditions()))
        statisticFile.write("\nMax number of Apps per Edge: {}".format(self.getMaximumNumberOfPresenceConditions()))
        statisticFile.write("\nMedian number of Apps per Edge: {}".format(self.getPresenceConditionMedian()))
        statisticFile.write("\nAverage number of Apps per Edge: {}".format(self.getAverageNumberOfPresenceConditions()))
        distrib = self.getTypeDistribution()
        statisticFile.write("\nType Distribution")
        statisticFile.write("\n\tSources: {}".format(distrib.SourceCount))
        statisticFile.write("\n\tSinks: {}".format(distrib.SinkCount))
        statisticFile.write("\n\tIntents: {}".format(distrib.IntentCount))
        statisticFile.write("\n\tIntent Results: {}".format(distrib.IntentResultCount))

        histogram = self.getVertexDegreeHistogram()
        statisticFile.write("\nHistogram: (degree : frequency)")
        for h in sorted(list(histogram.keys())):
            statisticFile.write("\n\t{} : {}".format(h,histogram[h]))

        degreehistofile = open("degree_histogram.txt", 'w')
        degreehistofile.write("Degree\tFrequency\n")
        for v in sorted(list(histogram.keys())):
            degreehistofile.write(str(v))
            degreehistofile.write("\t")
            degreehistofile.write(str(histogram[v]))
            degreehistofile.write("\n")

        pc_histogram = self.getPresenceConditionHistogram()
        statisticFile.write("\nHistogram: (number of pc : frequency)")
        for h in sorted(list(pc_histogram.keys())):
            statisticFile.write("\n\t{} : {}".format(h,pc_histogram[h]))

        pc_histofile = open("presencecondition_histogram.txt", 'w')
        pc_histofile.write("Number of PCs\tFrequency\n")
        for v in sorted(list(pc_histogram.keys())):
            pc_histofile.write(str(v))
            pc_histofile.write("\t")
            pc_histofile.write(str(pc_histogram[v]))
            pc_histofile.write("\n")

        pc_histofile.close()
        degreehistofile.close()
        statisticFile.close()
        sys.stdout.write("Finished gathering statistics. Saved to file statistics.txt.")

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

    def save(self):
        sys.stderr.write("Saving Graph\n")
        seenBefore = set()
        graph = Element("Graph")
        processed_apps = SubElement(graph, "ProcessedApps")
        nodes = SubElement(graph, "Nodes")

        for appId in self.processedApps:
            app = SubElement(processed_apps, "App")
            app.text = appId

        for nodeHash, edges in self.nodes.iteritems():
            if nodeHash not in seenBefore:

                node = SubElement(nodes, "Node", hash=nodeHash)
                seenBefore.add(nodeHash)
            for edgeHash in edges:
                try:

                    edge = SubElement(node, "Edge", to = edgeHash)
                    edgeApps = SubElement(edge, "Apps")
                    for appId in self.edges[nodeHash,edgeHash]:
                        app = SubElement(edgeApps, "App")
                        app.text = appId
                except:
                    pass
        graphFile = open(self.graphFileName, "w+")
        graphFile.write(tostring(graph))
        graphFile.close()

        #hash to element
        topmapping = Element("Mappings")

        hashmappings = SubElement(topmapping, "HashToObjectList")
        for mappingKey in self.hashToObjectMapping:
            value = self.hashToObjectMapping[mappingKey]
            SubElement(hashmappings, "Mapping", hash = mappingKey, object = value.to_xml(), type= str(value.__class__))

        filtermappings = SubElement(topmapping, "FilterToSinks")
        for mappingKey in self.filterToSinkMapping:
            values = self.filterToSinkMapping[mappingKey]
            filter = SubElement(filtermappings, "Filter", hash=mappingKey)
            sinks = SubElement(filter, "Sinks")
            for e in values:
                sink = SubElement(sinks, "Sink")
                sink.text = e

        intentmappings = SubElement(topmapping, "IntentToAppMapping")

        for intentKey in self.intents:
            apps = self.intents[intentKey]
            intent = SubElement(intentmappings, "Intent", hash=intentKey)
            appsElement = SubElement(intent, "Apps")
            for appName in apps:
                app = SubElement(appsElement, "App")
                app.text = appName

        intentresultmappings = SubElement(topmapping, "IntentResultToAppMapping")

        for intentKey in self.onResult:
            apps = self.onResult[intentKey]
            intent = SubElement(intentresultmappings, "IntentResult", hash=intentKey)
            appsElement = SubElement(intent, "Apps")
            for appName in apps:
                app = SubElement(appsElement, "App")
                app.text = appName


        mappingsFile = open(self.mappingFileName, "w+")
        mappingsFile.write(tostring(topmapping))
        mappingsFile.close()
        sys.stderr.write("Finished saving graph to file\n")

    def load(self):
        sys.stderr.write("Loading graph\n")
        if not os.path.isfile(self.graphFileName) or not os.path.isfile(self.graphFileName):
            print "cant find files"
            return

        graphfile = open(self.graphFileName, "r")
        mappingfile = open(self.mappingFileName, "r")

        graphXML = ET.fromstring("".join(graphfile.readlines()))
        mappingXML = ET.fromstring("".join(mappingfile.readlines()))

        classpath = "class_definitions."

        mappings = mappingXML.find("HashToObjectList").findall("Mapping")
        for mapping in mappings:
            hash = mapping.attrib["hash"]
            xml = mapping.attrib["object"]
            if classpath+"Source" == mapping.attrib["type"]:
                obj = Source.from_xml(xml)
                self.sources.add(obj.get_md5hash())
            elif classpath+"Sink" == mapping.attrib["type"]:
                obj = Sink.from_xml(xml)
            elif classpath+"Intent" == mapping.attrib["type"]:
                obj = Intent.from_xml(xml)
            elif classpath+"IntentResult" == mapping.attrib["type"]:
                obj = IntentResult.from_xml(xml)
            elif classpath+"IntentFilter" == mapping.attrib["type"]:
                obj = IntentFilter.from_xml(xml)
            self.hashToObjectMapping[hash] = obj

        filtermappings = mappingXML.find("FilterToSinks").findall("Filter")
        for f in filtermappings:
            sinks = f.find("Sinks").findall("Sink")
            hash = f.attrib["hash"]
            self.filterToSinkMapping[hash] = set()
            for s in sinks:
                self.filterToSinkMapping[hash].add(s.text)

        apps = graphXML.find("ProcessedApps").findall("App")
        for app in apps:
            self.processedApps.add(app.text)

        nodes = graphXML.find("Nodes")

        for node in nodes.findall("Node"):
            hash = node.attrib["hash"]
            self.nodes[hash] = set()
            for edge in node.findall("Edge"):
                tohash = edge.attrib["to"]
                self.nodes[hash].add(tohash)
                self.edges[(hash, tohash)] = set()
                for app in edge.find("Apps").findall("App"):
                    self.edges[(hash, tohash)].add(app.text)


        intentmappings = mappingXML.find("IntentToAppMapping").findall("Intent")

        for intent in intentmappings:
            appSet = set()

            apps = intent.find("Apps").findall("App")
            for app in apps:
                appSet.add(app.text)

            self.intents[intent.attrib["hash"]] = appSet

        intentresultmappings = mappingXML.find("IntentResultToAppMapping").findall("IntentResult")

        for intentresult in intentresultmappings:
            appSet = set()

            apps = intentresult.find("Apps").findall("App")
            for app in apps:
                appSet.add(app.text)

            self.onResult[intentresult.attrib["hash"]] = appSet
