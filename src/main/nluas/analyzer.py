"""
.. A wrapper for the Analyzer. It runs it as an XML-RPC server to isolate from 
    lengthy grammar-building times.

.. moduleauthor:: Luca Gilardi <lucag@icsi.berkeley.edu>

"""

import sys
from utils import Struct, update, display  # @UnusedImport
from xmlrpclib import ServerProxy  # @UnresolvedImport
from SimpleXMLRPCServer import SimpleXMLRPCServer  # @UnresolvedImport
from utils import interpreter
from pprint import pprint
from xmlrpclib import Fault
import time
from threading import Thread


# Possibly change this for your system
dll = {'linux': '/jre/lib/amd64/server/libjvm.so', 
       'darwin': '/jre/lib/server/libjvm.dylib',
       'win32': '/jre/bin/server/jvm.dll'}

try:
    import jpype, os  # @UnresolvedImport
    jpype.startJVM(os.environ['JAVA_HOME'] + dll[sys.platform],
                   '-ea', '-Xmx5g', '-Djava.class.path=lib/compling.core.jar')
    compling = jpype.JPackage('compling')
    SlotChain = getattr(compling.grammar.unificationgrammar, 'UnificationGrammar$SlotChain')
    getParses = compling.gui.util.Utils.getParses
    ParserException = jpype.JException(compling.parser.ParserException)  # @UnusedVariable
    ECGAnalyzer = compling.parser.ecgparser.ECGAnalyzer
    getDfs = compling.grammar.unificationgrammar.FeatureStructureUtilities.getDfs  # @UnusedVariable
except ImportError:
    from compling.grammar.unificationgrammar.UnificationGrammar import SlotChain
    from compling.gui.util.Utils import getParses
    from compling.parser import ParserException  # @UnusedImport
    from compling.parser.ecgparser import ECGAnalyzer
    from compling.grammar.unificationgrammar.FeatureStructureUtilities import getDfs  # @UnusedImport
    from compling.gui import AnalyzerPrefs
    from compling.grammar.ecg.Prefs import Property
    from compling.gui.AnalyzerPrefs import AP




class Analyzer(object):
    def __init__(self, prefs):
        self.analyzer = ECGAnalyzer(prefs)
        self.grammar = self.analyzer.grammar
        self.server = None


    def get_mappings(self):
        mappings = self.analyzer.getMappings()
        m = dict()
        for entry in mappings.entrySet():
            m[entry.key] = entry.value
        return m

    def get_lexicon(self):
        lexes = self.analyzer.getLexicon()
        return list(lexes)

    def get_parses(self, sentence):
        try:
            return getParses(sentence, self.analyzer)
        except ParserException:
            raise Fault(-1, u'The sentence "%s" has no valid parses.' % sentence)

    def get_mapping(self):
        v = AP.valueOf("MAPPING_PATH")
        return self.analyzer.getPrefs().getSetting(v)

        
    def parse(self, sentence):
        def root(parse):
            return parse.analyses[0].featureStructure.mainRoot
        
        def as_sequence(parse):
            def desc(slot):
                return (slot_type(slot), slot_index(slot), slot_typesystem(slot), slot_value(slot))
            
            slots = dict()
            root_ = root(parse)
            seq = [(parent, role) + desc(slots[s_id]) for parent, role, s_id in dfs('<ROOT>', root_, None, slots) if parent != -1]
            return (-1, '<ROOT>') + desc(root_), seq
        
        return [as_sequence(p) for p in self.get_parses(sentence)]


    def getConstructionSize(self):
        return len(self.analyzer.getGrammar().getAllConstructions())

    def getSchemaSize(self):
        return len(self.analyzer.getGrammar().getAllSchemas())


    def reload(self, prefs):
        """ Reloads grammar according to prefs file. """
        self.analyzer = ECGAnalyzer(prefs)
        self.grammar = self.analyzer.grammar

    def issubtype(self, typesystem, child, parent):
        """Is <child> a child of <parent>?
        """
        _ts = dict(CONSTRUCTION=self.grammar.cxnTypeSystem,
                   SCHEMA=self.grammar.schemaTypeSystem,
                   ONTOLOGY=self.grammar.ontologyTypeSystem)
        ts = _ts[typesystem]
        return ts.subtype(ts.getInternedString(child), ts.getInternedString(parent))

    def close(self):
        self.server.shutdown()


def slot_index(slot):
    return slot.slotIndex        

def slot_type(slot):
    # if not slot.typeConstraint: print '##', slot
    return slot.typeConstraint.type if slot and slot.typeConstraint else None

def slot_typesystem(slot):
    return slot.typeConstraint.typeSystem.name if slot and slot.typeConstraint else None

def slot_value(slot):
    return slot.atom[1:-1] if slot.atom else None

def slot(semspec, path, relative=None):
    """Returns the slot at the end of <path>, a slot 
    chain (a dot-separated list of role names)."""
    if relative:
        return semspec.getSlot(relative, SlotChain(path))
    else:
        return semspec.getSlot(SlotChain(path))

def test(args):
    """Just test the analyzer.
    """
    prefs, sent = args

    display('Creating analyzer with grammar %s ... ', prefs, term=' ')
    analyzer = Analyzer(prefs)
    display('done.')

    for p in analyzer.parse(sent):
        pprint(p)
        
def atom(slot):
    "Does slot contain an atomic type?"
    return slot.atom[1:-1] if slot.atom else ''

def dfs(name, slot, parent, seen):
    slotIndex = slot.slotIndex 
    seen[slotIndex] = slot
    if slot.features:
        for e in slot.features.entrySet():
            # <name, slot> pairs
            n, s = unicode(e.key).replace('-', '_'), e.value
            if s.slotIndex not in seen:
                for x in dfs(n, s, slot, seen):
                    yield x 
            else:
                yield slotIndex, n, s.slotIndex
    yield parent.slotIndex if parent else -1, name, slot.slotIndex
   
def server(obj, host='localhost', port=8090):
    server = SimpleXMLRPCServer((host, port), allow_none=True, encoding='utf-8')
    server.register_instance(obj)
    display('server ready (listening to http://%s:%d/).', host, port)
    server.serve_forever()
    return server  # Added

def usage_time(start, end, analyzer):
    print("Inversion time:")
    print(end - start)
    print("Num constructions: ")
    print(analyzer.getConstructionSize())
    print("Num schemas: ")
    print(analyzer.getSchemaSize())
    print("Total: ")
    print(analyzer.getConstructionSize() + analyzer.getSchemaSize())

def main(args):
    display(interpreter())
    display('Starting up Analyzer ... ', term='')
    start = time.time()
    analyzer = Analyzer(args[1])
    end = time.time()
    #usage_time(start, end, analyzer)
    try:
<<<<<<< HEAD
        #server_thread = Thread(target=server, kwargs={'obj': analyzer, 'host': host, 'port': port})
        #serve = server_thread.start()
        serve = server(analyzer, host, port)
        analyzer.server = serve
=======
        server_thread = Thread(target=server, kwargs={'obj': analyzer})
        #serve = server_thread.start()
        server_thread.run()
        #serve = server(analyzer)
        #analyzer.server = serve
>>>>>>> a0b9784902f8697dcb7af34b4899eb3c3fe9e42f
    except Exception, e:
        print(e)
        print "Address " + host + ":" + str(port) + " is already in use. Using Analyzer on existing server. Kill that process to restart with a new Analyzer." 

def test_remote(sentence ='Robot1, move to location 1 2!'):
    from feature import as_featurestruct
    a = ServerProxy('http://localhost:8090')
    d = a.parse(sentence)
    s = as_featurestruct(d[0])
    return s
    
# TODO: update this
def test_local(sentence='Robot1, move to location 1 2!'):
    from feature import as_featurestruct
    display('Starting up Analyzer ... ', term='')
    a = Analyzer('grammar/robots.prefs')
    display('done.\n', 'analyzing', sentence)
    d = a.parse(sentence)
    pprint(d)
#     s = as_featurestruct(d[0])
#     return s
    return d
    
def usage():
    display('Usage: analyzer.py <preference file>')
    sys.exit(-1)
    


if __name__ == '__main__':
    if '-t' in sys.argv:
        test(sys.argv[2:])
    elif '-l' in sys.argv:
        test_local(*sys.argv[2:3])
    else:
        if len(sys.argv) != 2:
            usage()
        main(sys.argv)
