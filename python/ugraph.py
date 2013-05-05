from graph_tool.all import *

class UGraph(Graph):
    def __init__(self):
        Graph.__init__(self, directed=False)
        self.names = self.new_vertex_property("int")
        self.vertex_properties["names"] = self.names
        self.inv_names = {}
    def add_vertex(self, name):
        v = super(UGraph, self).add_vertex()
        self.names[v] = name
        self.inv_names[name] = v
        return v
    def find_vertex(self, name):
        try:
            return self.inv_names[name]
        except:
            return None
    def find_name(self, v):
        try:
            return self.names[v]
        except:
            return None