import pysvf
import sys

class ICFGTraversal:

    def __init__(self, pag):
        self.pag = pag
        self.icfg = pag.get_icfg()
        self.visited = set()
        self.path = []
        self.paths = set()
        self.callstack = []

    def identify_source(self):
        return [self.icfg.get_global_icfg_node()]

    def identify_sink(self):
        res = []
        cs = self.pag.get_call_sites()
        for c in cs:
            if c.get_called_function().get_name() == "sink":
                res.append(c)
            if c.get_called_function().get_name() == "svf_assert":
                res.append(c)
        return res
    
    def dfs(self, src: 'pysvf.ICFGEdge', dst: 'pysvf.ICFGNode'):
        # TODO: Implement your context-sensitive ICFG traversal here to traverse each program path (once for any loop) from src edge to dst node
        pass


    def print_path(self):
        # TODO: print each path once this method is called, and
        # add each path as a string into std::set<std::string> paths
        # Print the path in the format "START: 1->2->4->5->END", where -> indicate an ICFGEdge connects two ICFGNode IDs
        pass


    def get_paths(self):
        return self.paths

def test1():
    bc_file = "./python/Assignment-2/testcase/bc/test1.ll"
    pag = pysvf.get_pag(bc_file)
    traversal = ICFGTraversal(pag)
    sources = traversal.identify_source()
    sinks = traversal.identify_sink()
    for src in sources:
        for sink in sinks:
            for edge in src.get_out_edges():
                traversal.dfs(edge, sink)
    expected = {"START: 1->3->4->END"}
    assert expected == traversal.get_paths(), "test1 failed!"
    print("test1 passed!")
    pysvf.release_pag()

def test2():
    bc_file = "./python/Assignment-2/testcase/bc/test2.ll"
    pag = pysvf.get_pag(bc_file)
    traversal = ICFGTraversal(pag)
    sources = traversal.identify_source()
    sinks = traversal.identify_sink()
    for src in sources:
        for sink in sinks:
            for edge in src.get_out_edges():
                traversal.dfs(edge, sink)
    expected = {"START: 3->7->8->9->1->5->6->2->10->11->1->5->6->2->12->13->14->15->END"}
    assert expected == traversal.get_paths(), "test2 failed!"
    print("test2 passed!")
    pysvf.release_pag()

def test3():
    bc_file = "./python/Assignment-2/testcase/bc/test3.ll"
    pag = pysvf.get_pag(bc_file)
    traversal = ICFGTraversal(pag)
    sources = traversal.identify_source()
    sinks = traversal.identify_sink()
    for src in sources:
        for sink in sinks:
            for edge in src.get_out_edges():
                traversal.dfs(edge, sink)
    expected = {"START: 3->19->1->5->6->8->10->12->END", "START: 3->19->1->5->6->7->9->11->14->END"}
    assert expected == traversal.get_paths(), "test3 failed!"
    print("test3 passed!")
    pysvf.release_pag()

if __name__ == "__main__":
    test1()
    test2()
    test3()
