class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.out_edges = set()

    def get_node_id(self):
        return self.node_id

    def get_out_edges(self):
        return self.out_edges

    def add_out_edge(self, edge):
        self.out_edges.add(edge)


class Edge:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def get_src(self):
        return self.src

    def get_dst(self):
        return self.dst


class Graph:
    def __init__(self):
        self.nodes = set()

    def get_nodes(self):
        return self.nodes

    def add_node(self, node):
        self.nodes.add(node)
