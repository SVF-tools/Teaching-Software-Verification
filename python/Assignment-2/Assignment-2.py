import pysvf
import sys

class ICFGTraversal:

    def __init__(self, pag):
        self.pag = pag
        self.icfg = pag.getICFG()
        self.visited = set()
        self.path = []
        self.paths = set()
        self.callstack = []

    def identifySource(self):
        return [self.icfg.getGlobalICFGNode()]

    def identifySink(self):
        res = []
        cs = self.pag.getCallSites()
        for c in cs:
            if c.getCalledFunction().getName() == "sink":
                res.append(c)
            if c.getCalledFunction().getName() == "svf_assert":
                res.append(c)
        return res
    
    def dfs(self, src: 'pysvf.ICFGEdge', dst: 'pysvf.ICFGNode'):
        # TODO: Implement your context-sensitive ICFG traversal here to traverse each program path (once for any loop) from src edge to dst node
        pass


    def printPath(self):
        # TODO: print each path once this method is called, and
        # add each path as a string into std::set<std::string> paths
        # Print the path in the format "START: 1->2->4->5->END", where -> indicate an ICFGEdge connects two ICFGNode IDs
        pass


    def getPaths(self):
        return self.paths

def test1():
    bcFile = "./python/Assignment-2/testcase/bc/test1.ll"
    pysvf.buildSVFModule(bcFile)
    pag = pysvf.getPAG()
    traversal = ICFGTraversal(pag)
    sources = traversal.identifySource()
    sinks = traversal.identifySink()
    for src in sources:
        for sink in sinks:
            traversal.dfs(pysvf.IntraCFGEdge(None, src), sink)
    expected = {"START: 0->1->3->4->END"}
    assert expected == traversal.getPaths(), "test1 failed!"
    print("test1 passed!")
    pysvf.releasePAG()

def test2():
    bcFile = "./python/Assignment-2/testcase/bc/test2.ll"
    pysvf.buildSVFModule(bcFile)
    pag = pysvf.getPAG()
    traversal = ICFGTraversal(pag)
    sources = traversal.identifySource()
    sinks = traversal.identifySink()
    for src in sources:
        for sink in sinks:
            traversal.dfs(pysvf.IntraCFGEdge(None, src), sink)
    expected = {"START: 0->3->7->8->9->1->5->6->2->10->11->1->5->6->2->12->13->14->15->END"}
    assert expected == traversal.getPaths(), "test2 failed!"
    print("test2 passed!")
    pysvf.releasePAG()

def test3():
    bcFile = "./python/Assignment-2/testcase/bc/test3.ll"
    pysvf.buildSVFModule(bcFile)
    pag = pysvf.getPAG()
    traversal = ICFGTraversal(pag)
    sources = traversal.identifySource()
    sinks = traversal.identifySink()
    for src in sources:
        for sink in sinks:
            traversal.dfs(pysvf.IntraCFGEdge(None, src), sink)
    expected = {"START: 0->3->19->1->5->6->8->10->12->END", "START: 0->3->19->1->5->6->7->9->11->14->END"}
    assert expected == traversal.getPaths(), "test3 failed!"
    print("test3 passed!")
    pysvf.releasePAG()

if __name__ == "__main__":
    test1()
    test2()
    test3()
