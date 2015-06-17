#       IntentDefinition(String[] actions, String[] category, String mimeType, String data, String packageName)
#
#		Intent(IntentDefinition intentDef, String component, String app)
#	    IntentFilter(IntentDefinition intentDef, String component, Int priority, String app)
#		IntentResult(Intent intent, String app) evt from and to?
#		Source(String app, String method)
#		Sink(String app, String method)
#
#		Flow(Object sender, Object reciever)
#

from collections import *
from collections import OrderedDict
from epicc_parser import parse_epicc
from class_definitions import *
import copy

script_path = os.path.dirname(os.path.realpath(__file__))
android_pfx = "{http://schemas.android.com/apk/res/android}"

INTENT = 0
INTENT_RESULT = 1

FlowdroidElement = namedtuple("FlowdroidElement", ["componentType", "component", "intentId", "type"])

''' The FlowSolver reads the data produced by flowdroid and epicc and prepares it for insertion in the graph. ''' 
class FlowSolver:
    def __init__(self, arguments):
        self.unsound = False
        self.internalflows = []
        self.flowMapping = dict()
        self.sources = set()
        self.intentResultIds = dict()
        self.errorcount = 0

        #Graph data structures
        self.graph = Graph()
        self.graph.load()
        epiccDataDict = dict()
        manifestDataDict = dict()
        flowdroidDataDict = dict()

        if not(sys.version_info[0] == 2 and sys.version_info[1] >= 7):
            self.die("Incompatible version of Python! This script needs Python 2.7.")

        if len(arguments[1:]) == 0:
            sys.stderr.write(
                ("Usage: %s [OPTIONS] [FILES]\n" % (sys.argv[0],)) +
                "Files: For each app, should include manifest, epicc, and flowdroid output.\n" +
                #"       To override package name, use 'pkg:filename' (UNTESTED).\n" +
                "Options: \n" +
                "  --unsound select the precision of the intent matching\n"
            )
            self.die("")

        fileNames = []
        args = iter(arguments[1:])

        # parse arguments to a list of file names, and set the parameters into fields
        for arg in args:
            try:
                if arg == "--unsound":
                    self.unsound = True
                else:
                    fileNames.append(arg)
            except StopIteration:
                self.die("Option '%s' expects an argument." % (arg,))
        fileCount = len(fileNames)
        currentCount = 0
        # Get the package name of all apps, and parse the file data into dictionaries
        for filename in fileNames:
            possible_package_name = filename.replace(".epicc", "")
            possible_package_name = possible_package_name.replace(".fd.xml", "")
            possible_package_name = possible_package_name.replace(".manifest.xml", "")
            if possible_package_name in self.graph.processedApps:
                continue
            currentCount += 1
            sys.stdout.write("\rLoading file " + str(currentCount) + " of " + str(fileCount))
            sys.stdout.flush()
            # if is epicc file
            try:
                if filename.endswith(".epicc"):
                    (pkg_name, epicc) = parse_epicc(filename, as_dict=True)
                    if pkg_name in self.graph.processedApps:
                        continue
                    epiccDataDict[pkg_name] = epicc
                #if is flowdroid file
                elif filename.endswith(".fd.xml"):
                    tree = ET.parse(filename)
                    root = tree.getroot()
                    pkg_name = root.attrib['package']
                    if pkg_name in self.graph.processedApps:
                        continue
                    flowdroidDataDict[pkg_name] = root
                #if is manifest file
                elif filename.endswith(".manifest.xml"):
                    xml = ET.parse(filename)
                    pkg_name = xml.find('.').attrib['package']
                    if pkg_name in self.graph.processedApps:
                        continue
                    manifestDataDict[pkg_name] = xml
                else:
                    self.die("wrong file format :-(")
            except:
                continue

        print("\n")

        keyCount = len(manifestDataDict.keys())
        currentKey = 0

        # combine the different data streams into a usable data structure
        for packageName in manifestDataDict.keys():

            currentKey += 1
            flowString = "\rCreating flows for " + str(currentKey) + " of " + str(keyCount) + " in package " + packageName
            sys.stdout.write(flowString + "(1/3)                                                                                 ") #hacks, so we know that we always overwrite the previous text
            sys.stdout.flush()

            try:
                flowDroidFlows = self.get_flows(flowdroidDataDict[packageName])
                epiccData = epiccDataDict[packageName]
                manifestData = manifestDataDict[packageName]
                self.graph.processedApps.add(packageName)
            except KeyError:
                #Error on parsing data in package
                print "\nError on parsing: " + packageName
                self.errorcount += 1
                manifestDataDict.pop(packageName, None)
                flowdroidDataDict.pop(packageName, None)
                epiccDataDict.pop(packageName, None)
                continue

            #lets get the intent filters for the app:
            intentFilters = self.read_intent_filters_from_manifest(manifestData, packageName)

            flowCount = len(flowDroidFlows)
            currentFlow = 0
            # match internal flows with intent info from Epicc
            for flow in flowDroidFlows[:]: #To Alex: the [:] syntax returns a copy of the list.

                currentFlow += 1

                sys.stdout.write(flowString + " (2/3) (Flow " + str(currentFlow) + " of " + str(flowCount) + ")")
                sys.stdout.flush()

                if isinstance(flow.source, FlowdroidElement) and flow.source.type == INTENT_RESULT and flow.source.intentId == None:
                    try:
                        epicc = epiccData[self.intentResultIds[flow.app]][0]
                    except Exception:
                        flowDroidFlows.remove(flow)
                        epicc = None

                    if not epicc:
                        continue
                    action = []
                    category = []
                    mimeTypes = []
                    data = ""
                    matchAll = False
                    matchingClass = None

                    #epicc is a dictionary that contains a key for each of the important properties. These entries in epicc is being converted to proper IntentDefinition objects.

                    if 'Action' in epicc:
                        actionString = epicc["Action"]
                        if actionString.startswith("["):
                            action = actionString[1:-1].split(",")
                        else:
                            action = [actionString]

                    if 'Type' in epicc:
                        typeString = epicc["Type"]
                        if typeString.startswith("["):
                            mimeTypes = typeString[1:-1].split(",")
                        else:
                            mimeTypes = [typeString]

                    if 'Categories' in epicc:
                        categoryString = epicc["Categories"]
                        #if categoryString.startswith("["):
                            #category = categoryString[1:-1].split(",")
                        #else:
                        category = categoryString
                    if 'Data' in epicc:
                        data = epicc["Data"]

                    if 'Top' in epicc and epicc["Top"]:
                        matchAll = True

                    if 'Class' in epicc:
                        matchingClass = epicc["Class"].replace("/", ".")

                    intentDefinition = IntentDefinition(action, category, mimeTypes, data, "Activity")


                    flow.source = IntentResult(intentDefinition=intentDefinition,app=flow.app)

                if isinstance(flow.sink, FlowdroidElement) and (flow.sink.intentId == None or flow.sink.intentId.startswith("newField_")):
                    epicc=None # reinitialize
                    if flow.sink.intentId == None:
                        #flow.sink = IntentResult(IntentDefinition([],[],[], "", ""), flow.app)
                        flowDroidFlows.remove(flow) # I have a case where epiccData is not None, flow.sink.intentID is None
                        continue
                    else:
                        try:
                            epicc = epiccData[flow.sink.intentId][0]
                        except Exception:
                            flowDroidFlows.remove(flow)
                            continue
                    if epicc==None: epicc=dict()
                    
                    action = []
                    category = []
                    mimeTypes = []
                    data = ""
                    matchAll = False
                    matchingClass = None

                    #epicc is a dictionary that contains a key for each of the important properties. These entries in epicc is being converted to proper IntentDefinition objects.
                    if 'Action' in epicc:
                        actionString = epicc["Action"]
                        if actionString.startswith("["):
                            action = actionString[1:-1].split(",")
                        else:
                            action = [actionString]

                    if 'Type' in epicc:
                        typeString = epicc["Type"]
                        if typeString.startswith("["):
                            mimeTypes = typeString[1:-1].split(",")
                        else:
                            mimeTypes = [typeString]

                    if 'Categories' in epicc:
                        categoryString = epicc["Categories"]
                        #if categoryString.startswith("["):
                            #category = categoryString[1:-1].split(",")
                        #else:
                        category = categoryString
                    if 'Data' in epicc:
                        data = epicc["Data"]

                    if 'Top' in epicc and epicc["Top"]:
                        matchAll = True

                    if 'Class' in epicc:
                        matchingClass = epicc["Class"].replace("/", ".")

                    intentDefinition = IntentDefinition(action, category, mimeTypes, data, flow.sink.componentType)
                    intentDefinition.matchAll = matchAll
                    intentDefinition.matchingClass = matchingClass

                    if flow.sink.type == INTENT:
                        flow.sink = Intent(intentDefinition, flow.app)
                    else:
                        flow.sink = IntentResult(intentDefinition, flow.app)


            #Match internal flows with intent filters from the manifest

            appflows = set()

            for flow in flowDroidFlows:
                _flow = flow.toFlow()
                if isinstance(_flow.source, FlowdroidElement) and _flow.source.intentId == None:
                    component = _flow.source.component
                    componentType = _flow.source.componentType

                    componentIntentFilters = intentFilters.get(component, [])

                    if(len(componentIntentFilters) == 0):
                        definition = IntentDefinition([], [], [], "", componentType)
                        definition.matchingClass = component
                        _flow.source = IntentFilter(definition, _flow.app, 0)
                        appflows.add(_flow)

                    for intentFilter in componentIntentFilters:
                        newFlow = copy.deepcopy(_flow)
                        newFlow.source = intentFilter

                        appflows.add(newFlow)
                else:
                    appflows.add(_flow)


            '''
            The following matches all flows within a single app to connect explicit intents together to single flows.
            We are not interested in explicit intents as these only happens within an app, but we are interested in linking
            together sources with implicit intents, which might happen across several internal components.
            TODO: Check for Intent Results
            '''
            stillWorking = True

            permutations = 0
            tracker = set()
            oldFlows = set()
            for e in appflows:
                str_e = str(e)
                if str_e not in tracker:
                    tracker.add(str_e)
                    oldFlows.add(e)

            seenbefore = set()
            while stillWorking:
                permutations += 1

                stillWorking = False
                newFlows = set()
                flowCount = 0
                for flow1 in oldFlows:
                    flowCount += 1
                    if flowCount % 100 == 0:
                        sys.stdout.write(flowString + "(3/3) (Matching internal intents, permutation: " + str(permutations) + ", Flows: " + str(flowCount) + ", seenBefore: " + str(len(seenbefore)) + ")")
                        sys.stdout.flush()

                    added = False
                    if (isinstance(flow1.sink, Intent) or isinstance(flow1.sink, IntentResult)) and flow1.sink.intentDefinition.matchingClass != None:
                        for flow2 in oldFlows:
                            if isinstance(flow2.source, IntentFilter):
                                if(flow1.sink.intentDefinition.matchingClass == flow2.source.intentDefinition.matchingClass):
                                    newFlow = Flow(flow1.source, flow2.sink, flow1.app)

                                    if str(newFlow) not in seenbefore:
                                        newFlows.add(newFlow)
                                        seenbefore.add(str(newFlow))
                                    stillWorking = True
                                    added = True

                    if not added:
                        newFlows.add(flow1)

                if stillWorking:
                    oldFlows = newFlows

            appflows = oldFlows

            '''
            This part of the algorithm runs through all flows and puts the data in several datastructures used to build the graph.
            All elements are converted to hash strings, and put in hashToObjectMapping, with the hash as a key and the object as a value.
            Intents are added to the intents dictionary, with the intent hash as the key and a set of app names as the result.
            IntentFilters are added to filterToSinkMapping with the filter hash as the key and a set of sinks as the value.
            IntentResults are added to the onResult, with the IntentResult hash as the key and a set of app names as the value.
            '''
            for flow in appflows:
                if "Explicit Intent (" in str(flow.source) or ("Explicit Intent (" in str(flow.sink) and not isinstance(flow.sink, IntentResult)):
                    continue
                if "FlowdroidElement" in str(flow.source) or "FlowdroidElement" in str(flow.sink):
                    continue
                sourceHash = flow.source.get_md5hash()
                sinkHash = flow.sink.get_md5hash()
                if sourceHash not in self.graph.hashToObjectMapping:
                    self.graph.hashToObjectMapping[sourceHash] = flow.source
                if sinkHash not in self.graph.hashToObjectMapping:
                    self.graph.hashToObjectMapping[sinkHash] = flow.sink
                if isinstance(flow.sink, IntentResult) and not isinstance(flow.source, IntentFilter):
                    intent = Intent(intentDefinition = flow.sink.intentDefinition, app = flow.sink.app)
                    intentHash = intent.get_md5hash()
                    if "android.intent.action.MAIN" not in flow.sink.intentDefinition.actions:
                        if intentHash not in self.graph.intents:
                            self.graph.intents[intentHash] = set()
                        self.graph.intents[intentHash].add(flow.source.app)
                        self.graph.hashToObjectMapping[intentHash] = intent
                        src = flow.source
                        internalflow = Flow(source = src, sink = intent, app=flow.app)
                        self.internalflows.append(internalflow)
                    continue

                if isinstance(flow.sink, Intent):
                    intentHash = flow.sink.get_md5hash()
                    if "android.intent.action.MAIN" not in flow.sink.intentDefinition.actions:
                        if intentHash not in self.graph.intents:
                            self.graph.intents[sinkHash] = set()
                        self.graph.intents[sinkHash].add(flow.source.app)
                        if not isinstance(flow.source, IntentFilter):
                            self.internalflows.append(flow)
                if isinstance(flow.source, IntentFilter):
                    if sourceHash not in self.graph.filterToSinkMapping:
                        self.graph.filterToSinkMapping[sourceHash] = set()
                    self.graph.filterToSinkMapping[sourceHash].add(sinkHash)
                elif isinstance(flow.source, IntentResult):
                    if sourceHash not in self.graph.onResult:
                        self.graph.onResult[sourceHash] = set()
                    self.graph.onResult[sourceHash].add(flow.source.app)
                    self.internalflows.append(flow)
                elif isinstance(flow.source, Source) and isinstance(flow.sink, Sink):
                    self.internalflows.append(flow)

        print("\n")

    def die(self, text):
        sys.stderr.write(text + "\n")
        sys.exit(1)

    '''
    Reads all the filters from an entire manifest file.
    Returns a dictionary with component names (package + component name) as the key and a list of filters as the value.
    '''
    def read_intent_filters_from_manifest(self, root, appName):
        ret = dict()
        # Intent filters can be used with Activities as well as Activity-aliases
        # Alias is used to have a different label for the same activity
        all_components = root.findall(".//activity") + root.findall(".//activity-alias") + root.findall(".//receiver") + root.findall(".//service")
        for component in all_components:
            componentType = component.tag
            if(componentType == "receiver"):
                componentType = "BroadcastReceiver"

            if(componentType == "activity-alias"):
                componentType = "Activity"

            filter_list = []
            # Component name for an Activity is stored as the "name" attribute
            if component.tag == "activity" or component.tag == "service" or component.tag == "receiver":
                if (android_pfx + "name") in component.attrib:
                    comp_name = component.attrib[android_pfx + "name"]
                else: continue # cannot use this activity/service/receiver
            # Component name for an Activity-alias is stored as the "targetActivity" attribute
            elif component.tag == "activity-alias":
                comp_name = component.attrib[android_pfx + "targetActivity"]

            if comp_name.startswith("."):
                comp_name = root.find('.').attrib['package'] + comp_name
            elif "." not in comp_name:
                 comp_name = root.find('.').attrib['package'] + "." + comp_name

            for intent_node in component.findall(".//intent-filter"):
                filter_list.append(self.read_intent_filter(intent_node, componentType, appName))
            ret.setdefault(comp_name, []);
            ret[comp_name] += filter_list
        return ret

    '''
    This methods reads an intent filter for a specific component in a specific app.
    Called by read_intent_filters_from_manifest.
    Returns an IntentFilter object as a result.
    '''
    def read_intent_filter(self, intent_node, component_type, appName):
        assert(isinstance(intent_node, ET.Element))
        assert(intent_node.tag == 'intent-filter')
        # instantiate an empty definition
        intentDefinition = IntentDefinition([], [], [], "", component_type.capitalize())
        # fill in parameters into our definition from the xml
        for sub in intent_node.findall("*"):
            filter_attr = OrderedDict()
            for (key, val) in sub.attrib.iteritems():
                # E.g., key might be "android:name" (for action and category) or
                # "android:scheme" (for data), but with "android:" expanded out to
                # android_pfx.
                key = key.replace(android_pfx,"")
                filter_attr[key] = val

            if sub.tag == 'action':
                intentDefinition.__dict__['actions'].append(filter_attr['name'])
            elif sub.tag == 'category':
                categoryItem = filter_attr['name']
                if categoryItem != "android.intent.category.DEFAULT":
                    intentDefinition.__dict__['categories'].append(categoryItem)
            elif sub.tag == 'data':
                mType = filter_attr.get('mimeType', None)
                if mType != None:
                    intentDefinition.mimeTypes.append(mType)
            else:
                #We do not handle intent filters inside intent filters.
                #We dont want to die when it happens.
                #self.die("Unexpected tag in intent-filter: '%s'!" % (sub.tag,))
                sys.stdout.write("Unexpected tag in intent-filter: '%s'!" % (sub.tag,))
        # instantiate an Intentfilter based on the intent definition
        intentFilter = IntentFilter(intentDefinition, appName, 0)
        return intentFilter

    '''
    This method parses the FlowDroid XML output into FlowDroidElements and finally into InternalFlow elements.
    '''
    def get_flows(self, root):
        pkg_name = root.attrib['package']
        ret = [] #result is a list of InternalFlow objects

        for flow in root.findall("flow"):
            sinkMethod = flow.find("sink").attrib['method']
            if flow.find("sink").attrib.get('is-intent') == "1":
                intent_id = flow.find("sink").attrib.get('intent-id')
                componentType = flow.find("sink").attrib.get('component-type').capitalize()

                if componentType == "":
                    componentType = "Activity"

                if (intent_id is None):
                    sys.stderr.write("Error: Intent in %s is missing intent-id!\n" % pkg_name)
                if("startActivityForResult" in flow.find("sink").attrib.get('method')):
                    sink = FlowdroidElement(component = None, componentType = "Activity", intentId = intent_id, type = INTENT_RESULT)
                    self.intentResultIds[pkg_name] = intent_id
                else:
                    sink = FlowdroidElement(component = None, componentType = componentType, intentId = intent_id, type = INTENT)
            elif flow.find("sink").attrib.get('is-intent-result') == "1":
                componentType = "Activity"
                sink = FlowdroidElement(component = None, componentType = componentType, intentId = None, type = INTENT_RESULT)
            else:
                sink = "Sink:" + sinkMethod

            for src_node in flow.findall("source"):
                sourceMethod = src_node.attrib['method']

                component = src_node.attrib['component']
                #is "android.content.Intent" correct, or do we get to many src included?
                if "@parameter2: android.content.Intent" in sourceMethod or "onActivityResult" in sourceMethod:
                    for child in src_node:
                        if child.tag == "in" and "onActivityResult" in child.text:
                            #onActivityResult
                            source = FlowdroidElement(component = component, componentType = "Activity", intentId = None, type = INTENT_RESULT)
                            break
                elif ("android.content.Intent" in sourceMethod) or ("getIntent" in sourceMethod):

                    source = FlowdroidElement(component = component, componentType = "", intentId = None, type = INTENT)

                else:
                    source = "Src: " + sourceMethod
                #FIXME: What if the the source and sinks are in different components?
                ret.append(InternalFlow(source, sink, pkg_name))

        return ret

    def match_any_string(self, x):
        return (x == '<any_string>') and not self.unsound

    '''
    This method implements the action, category, and data tests described in
    http://developer.android.com/guide/components/intents-filters.html#Resolution
    Epicc does not produce URI information, so we ignore the URI tests.
    '''
    def match_intent_attr(self, intent, intentFilter):

        assert(isinstance(intent, Intent) or isinstance(intent, IntentResult))
        assert(isinstance(intentFilter, IntentFilter))

        if intent.intentDefinition.matchAll:
            return (not self.unsound)

        if(intent.intentDefinition.componentType != intentFilter.intentDefinition.componentType):
            return False

        # Check if the intent is an explicit intent.
        if intent.intentDefinition.matchingClass != None:
            # Lots of false positives here for <any_string>.
            # TODO: Can explicit intents be explicitly designated using an
            # activity alias?  If so, we need to the use information in
            # glo.act_alias_to_targ.
            return ((intent.intentDefinition.matchingClass == intentFilter.intentDefinition.matchingClass) or self.match_any_string(intent.intentDefinition.matchingClass))

        # Action test
        act_ok = (
            (((intent.intentDefinition.actions is None) or self.match_any_string(intent.intentDefinition.actions)) and len(IntentFilter.intentDefinition.actions) > 0) or
            (set(intent.intentDefinition.actions) & set(intentFilter.intentDefinition.actions)))

        if(len(intent.intentDefinition.actions) == 0):
            # act_ok = True 
            # this is necessary for some test cases (e.g., ICC-Bench Implicit3) which use Intents without action labels.
            # setting act_ok to true is more precise in theory.
            # however, Intents without actions should not occur much in practice and bugs in epicc etc. generate Intents without actions.
            # so, we set act_ok to false usually:
            act_ok = False

        if not act_ok:
            return False


        ############################################################
        # For each category in intent, must be a match in filter.
        # Zero categories in intent, but many in filter: still can be received.
        cat_ok = (
            (not len(intent.intentDefinition.categories)) or any(self.match_any_string(x) for x in intent.intentDefinition.categories) or
            (not len([e for e in intent.intentDefinition.categories if e != "" and e not in intentFilter.intentDefinition.categories])))
        #(set(intent.intentDefinition.categories) & set(intentFilter.intentDefinition.categories)) == intent.intentDefinition.actions)
        if not cat_ok:
            return False
        # If glo.unsound, then False negatives returned if <any_string> is
        # intent category EPICC returns and the filter actually matches that
        # category EPICC doesn't process
        ############################################################
        # TODO: data MIME type
        # An intent filter can declare zero or more data elements. Rules:
        # 1. An intent that contains neither a URI nor a MIME type passes the test only if the filter does not specify any URIs or MIME types.
        # (Can't test for this): 2. An intent that contains a URI but no MIME type (neither explicit nor inferable from the URI) passes the test only if its URI matches per test
        # 3. An intent that contains a MIME type but not a URI passes the test only if the filter lists the same MIME type and does not specify a URI format.
        # 4. (Can't test for last rule, since depends on URI)

        # Mime Type test
        #If both the filter and the intent has no Mime Types then it is a match.
        if not len(intent.intentDefinition.mimeTypes):
            if not len(intentFilter.intentDefinition.mimeTypes):
                return True
        else: #Else the mime type of the intent must match one of the mime types in the filter.
            mtype = intent.intentDefinition.mimeTypes[0]
            if mtype in intentFilter.intentDefinition.mimeTypes:
                return True
            else:
                first = mtype.split('/')[0]
                for type in intentFilter.intentDefinition.mimeTypes:
                    t_split = type.split('/')
                    if len(t_split) > 1:
                        t_fst = t_split[0]
                        t_snd = t_split[1]
                        if t_snd == '*' and first == t_fst:
                            return True
        return False

'''
Graph builder class. It builds a Graph object and return it in the end.
Main responsibilities:
Match intents with intentfilters
Match intents with filters and intent results
Properly add nodes and their neighbours.
Properly add edges and the apps associated with those edges.
'''
class GraphBuilder:
    def __init__(self, flows, solver):
        self.flows = flows
        self.solver = solver
        self.graph = solver.graph

    def createGraph(self):
        sys.stdout.write("Building graph\n")

        '''
        The first part of the graph building match intents, filters and intent results with each other to properly build correlations between these nodes.
        '''
        for i in self.graph.intents:
             assasa = 0
             for f in self.graph.filterToSinkMapping.keys():
                 if self.solver.match_intent_attr(self.graph.hashToObjectMapping[i],self.graph.hashToObjectMapping[f]):
                     ''' i and f match '''
                     '''
                     Niklas: if no f matches i, nothing happens. This basically means we are not adding intents
                     with no receivers to the graph. However they are still saved, so if a filter in the future is
                     added that match the intent, then the intent is added to the graph and an edge to each
                     of the sinks of that filter from the intent is added as well.

                     This is to ensure that we save information about intents that MIGHT be interesting when analysing more apps,
                     but which is currently not interesting since there is no receivers of the intent.
                     '''
                     for e in self.graph.filterToSinkMapping[f]:
                         if isinstance(self.graph.hashToObjectMapping[e], IntentResult):
                             #continue
                             ''' sink e for current filter f is an IntentResult '''
                             for r in self.graph.onResult:
                                 apps = self.graph.intents[i].intersection(self.graph.onResult[r])
                                 '''
                                 Niklas:
                                 This part is a bit tricky and is one we have discussed quite extensively and which will also be adressed
                                 accordingly in the report. The issue is this (briefly summarized):

                                 We have a number of apps that send intent i.
                                 If intent i matches a filter, which has a sink of type IntentResult then the following flow is happening:
                                 source -> startActivityForResult() -> getIntent() -> setResult()

                                 Now the last missing piece is this:
                                 setResult -> onActivityResult() -> sink
                                 IntentResults that are sources of any specific flows are stored in the onResult dictionary.

                                 If an IntentResult is a source, that means we have the following flow:
                                 onActivityResult() -> sink

                                 So when we have:
                                 source -> startActivityForResult() -> getIntent() -> setResult()

                                 We are looking through onResult to find the missing piece.

                                 A match happens when the app that send the initial Intent, i, is also the app caught by the
                                 IntentResult, r. The way we do it is take the set of apps that send intent i, and intersect this
                                 with the apps that receives result r. The resulting set is all the apps they have in common.
                                 If they have apps in common then there is a link between the intent and the result, and we create an edge
                                 between them. So if the result is not caught by the app sending the intent, it is not the result we are looking for.

                                 The if len(apps) statement below is equal to saying:
                                 if (apps.notEmpty()) in other languages.
                                 Python interprets numbers greater than zero as true, no matter what value they have.
                                 So even if length is 367 or any other number it will still evaluate to true.
                                 '''
                                 if len(apps):
                                     if (i, r) not in self.graph.edges:
                                        self.graph.edges[(i, r)] = set()
                                     self.graph.edges[(i, r)] = self.graph.edges[(i,r)].union(apps)
                                     if i not in self.graph.nodes:
                                        self.graph.nodes[i] = set()
                                     self.graph.nodes[i].add(r)
                                     if r not in self.graph.nodes:
                                        self.graph.nodes[r] = set()
                         else:
                             '''
                             If an intent matches a filter that does not end in a IntentResult, it either ends in a sink, or another intent and we just connect them.
                             (no need to test this further)
                             '''
                             if (i, e) not in self.graph.edges:
                                 self.graph.edges[(i, e)] = set()
                             if i not in self.graph.nodes:
                                 self.graph.nodes[i] = set()
                             if e not in self.graph.nodes:
                                 self.graph.nodes[e] = set()
                             self.graph.nodes[i].add(e)
                             self.graph.edges[(i, e)].add(self.graph.hashToObjectMapping[f].app)
                             
        '''
        The current state is that the graph contains all inter-application flows. The missing parts are the intra-application flows, which
        is inserted below. Currently flows like:
        Flows like:
            Intent -> Sink
            Intent -> Intent
            Intent -> IntentResult
        are in the graph.
        
        Flows like:
            Source -> Intent
            Source -> Sink
            IntentResult -> sink
        are not present in the graph. They are added in the following code.
        '''

        '''
        This part of the algorithm runs through the internal flows from the FlowDroid analysis (modified by the EPICC output).
        This is fairly straight forward, where nodes are just inserted if they don't already exist.
        Some of the code below can easily be collapsed into fewer lines of code. The current structure made sense a couple
        of iterations ago where we did several different things depending on what type the node were.
        '''
        for flow in self.solver.internalflows:
            src = flow.source
            sink = flow.sink
            '''
            Niklas:
            flow.source can be of the following types:
            Source
            IntentResult
            IntentFilter

            flow.sink can be of the following types:
            Intent
            IntentResult
            Sink

            The str type is legacy from some of the first iterations of the code. When we reach this part of the algorithm, all str should
            have been replaced by an Object type instead. This is probably some legacy code that could be removed, but ill check up on it
            once I am cleaning up the code below anyway. If it is still a str it is because it managed to get by all the other checks we
            have throughout the code and got here. It might be some small corner cases that we haven't thought about.
            '''
            if "Explicit Intent (" in str(flow.source) or "Explicit Intent (" in str(flow.sink):
                continue
            if isinstance(flow.source, str) and isinstance(flow.sink, str):
                continue

            srcHash = src.get_md5hash()
            sinkHash = sink.get_md5hash()

            if isinstance(src, Source) and isinstance(sink, Sink):
                self.graph.sources.add(srcHash)
                self.graph.sinks.add(sinkHash)
                if (srcHash, sinkHash) not in self.graph.edges:
                    self.graph.edges[(srcHash, sinkHash)] = set()
                self.graph.edges[(srcHash, sinkHash)].add(flow.source.app)

            elif isinstance(src, Source):
                self.graph.sources.add(srcHash)
                if (srcHash, sinkHash) not in self.graph.edges:
                    self.graph.edges[(srcHash, sinkHash)] = set()
                self.graph.edges[(srcHash, sinkHash)].add(src.app)

            elif isinstance(sink, Sink):
                if (srcHash, sinkHash) not in self.graph.edges:
                    self.graph.edges[(srcHash, sinkHash)] = set()
                self.graph.edges[(srcHash, sinkHash)].add(sink.app)

            else: #src and sink are both intents
                if (srcHash, sinkHash) not in self.graph.edges:
                    self.graph.edges[(srcHash, sinkHash)] = set()
                self.graph.edges[(srcHash, sinkHash)].add(src.app)

            if srcHash not in self.graph.nodes and not isinstance(src, IntentFilter):
                self.graph.nodes[srcHash] = set()
            if sinkHash not in self.graph.nodes: # and isProperIntentOrString(src):
                self.graph.nodes[sinkHash] = set()

            if srcHash in self.graph.nodes and sinkHash in self.graph.nodes: # and isProperIntentOrString(src):
                self.graph.nodes[srcHash].add(sinkHash)
        return self.graph

inputFolder=sys.argv[1]
print "loading graph generation input files from folder " + str(inputFolder)

fileList=[]
'''
Files are loaded if files with the same prefix and endings
.epicc ,
.fd.xml , and
.manifest.xml
exist.
'''
for fileName in os.listdir(inputFolder):
    if fileName.endswith(".epicc"):
        basename=fileName[:-len(".epicc")]
        manifestFileName=basename+".manifest.xml"
        fdFileName=basename+".fd.xml"
        if (os.path.isfile(fdFileName) and os.path.isfile(manifestFileName)):
            fileList.append(fileName)
            fileList.append(manifestFileName)
            fileList.append(fdFileName)
            
#flowSolver = FlowSolver(sys.argv)
flowSolver = FlowSolver(fileList)
graphBuilder = GraphBuilder([], flowSolver)
graph = graphBuilder.createGraph()

print "Number of failed apps: " + str(flowSolver.errorcount)

'''
Niklas: all Sources are private and contain sensitive information in some way.
The taintpropagation will be done after "graph.save()". However we will probably
structure this a little differently with all the graph construction code in one file
and the taint analysis / graph querying in another. Since we are now persisting the
graph, it is possible to load only that (and not redo graph construction) to get the
tainted flows.
'''
graph.save()
