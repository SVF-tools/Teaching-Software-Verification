from Utils import Node, Edge, Graph
class GraphTraversal:
    def __init__(self):
        self.visited = set()
        self.path = []
        self.paths = set()


    def print_path(self, path):
        # TODO: print each path once this method is called, and
        # add each path as a string into std::set<std::string> paths
        # Print the path in the format "START: 1->2->4->5->END", where -> indicate an edge connecting two node IDs
        pass

    def dfs(self, src_edge, dst):
        # TODO: Implement your depth first search here to traverse each program path (once for any loop) from src to dst
        pass

    def get_paths(self):
        return self.paths




if __name__ == "__main__":
    # Initialize nodes
    node0 = Node(0)
    node1 = Node(1)
    node2 = Node(2)
    node3 = Node(3)
    node4 = Node(4)
    node5 = Node(5)

    # Initialize edges
    edge0 = Edge(node0, node1)
    edge1 = Edge(node1, node2)
    edge2 = Edge(node1, node3)
    node1.add_out_edge(edge1)
    node1.add_out_edge(edge2)
    edge3 = Edge(node2, node4)
    edge4 = Edge(node3, node4)
    node2.add_out_edge(edge3)
    node3.add_out_edge(edge4)
    edge5 = Edge(node4, node5)
    node4.add_out_edge(edge5)

    # Initialize graph
    g = Graph()
    g.add_node(node1)
    g.add_node(node2)
    g.add_node(node3)
    g.add_node(node4)
    g.add_node(node5)

    # Expected answer
    expected_answer = {"START: 1->2->4->5->END", "START: 1->3->4->5->END"}

    # Test
    dfs = GraphTraversal()
    dfs.dfs(edge0, node5)
    assert dfs.get_paths() == expected_answer, "Test case failed!"
    print("Test case passed!")
