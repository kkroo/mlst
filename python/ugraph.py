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
    def reindex_names(self):
        self.names = self.vertex_properties["names"]
        self.inv_names = {}     
        for v in self.vertices():
            self.inv_names[ self.find_name(v) ] = v
    def find_vertex(self, name):
        try:
            v = self.inv_names[name]
            if (not v.is_valid()):
                self.reindex_names()
                return self.find_vertex(name)
            return v
        except:
            return None
    def find_name(self, v):
        try:
            return self.names[v]
        except:
            return None
    def union(self, g):
        for e in g.edges():
            v1 = g.find_name( e.source() )
            v2 = g.find_name( e.target() )
            v1_obj = self.find_vertex(v1)
            v2_obj = self.find_vertex(v2)
            new_edge = False
            if (v1_obj is None):
                v1_obj = self.add_vertex(v1)
                new_edge = True
            if (v2_obj is None):
               v2_obj = self.add_vertex(v2)
               new_edge = True
            if (new_edge is True):
                self.add_edge(v1_obj, v2_obj)
    def difference(self, g):   
        for v in g.vertices():
            v_name = g.find_name(v)
            v_obj = self.find_vertex(v_name)
            if (v_obj is not None):
                self.remove_vertex(v_obj, fast=True)
                del self.inv_names[v_name]

    def output(self):
        print(str(self.num_edges()))
        for e in self.edges():
           print("{0} {1}".format(self.find_name( e.source() ), self.find_name( e.target() ) ))
    def copy(self):
        new_u = UGraph()
        for v in self.vertices():
            new_u.add_vertex(self.find_name(v))
        for e in self.edges():
            new_u.add_edge(e.source(), e.target())
        return new_u

class SCCVisitor(DFSVisitor):
    def __init__(self):
        self.vertices = []

    def discover_vertex(self, u):
        self.vertices.append(u)