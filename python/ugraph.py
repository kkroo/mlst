from graph_tool.all import *
from reader import *

class GraphToolInFileReader(Reader):
    def read_input_file(self):
        nums = self.read_numbers('Cannot parse the number of input graphs.', 1)

        num_cases = nums[0]
        graphs = []
        for i in range(num_cases):
            self.case_num = i+1
            g = self.read_input_graph()
            graphs.append(g)

        self.case_num += 1
        self.readline()
        if len(self.line) > 0:
            raise self.exception_with_expected('Extra lines after Graph ' +
                    '#{0} (line 1 says the number of graphs is {0}).'.
                    format(num_cases), 'Expecting EOF.')

        return graphs
    def read_input_graph(self):
        nums = self.read_numbers('Cannot parse the number of edges.', 1)

        num_edges = nums[0]
        if num_edges > config.MAX_NUM_EDGES:
            raise self.exception('Number of edges cannot '+
                    'exceed {0}.'.format(config.MAX_NUM_EDGES))
        g = UGraph()
        v_added = {}
        for i in range(num_edges):
            nums = self.read_numbers('Cannot parse the next edge.', 2)
            v1 = int(nums[0]); v2 = int(nums[1]);
            v1_obj = g.find_vertex(v1)
            v2_obj = g.find_vertex(v2)
            if (v1_obj is None):
                v1_obj = g.add_vertex(v1)
            if (v2_obj is None):
               v2_obj = g.add_vertex(v2)
            g.add_edge(v1_obj, v2_obj)

        return g

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
                self.clear_vertex(v_obj)
                self.remove_vertex(v_obj)
                del self.inv_names[v_name]
                self.reindex_names()

    def output(self):
        ret = ""
        ret += (str(self.num_edges())) + "\n"
        for e in self.edges():
           ret += ("{0} {1}\n".format(self.find_name( e.source() ), self.find_name( e.target() ) ))
        return ret

    def copy(self):
        new_u = UGraph()
        for v in self.vertices():
            new_u.add_vertex(self.find_name(v))
        for e in self.edges():
            v1 = new_u.find_vertex(self.find_name(e.source()))
            v2 = new_u.find_vertex(self.find_name(e.target()))
            if (v1 is not None and v2 is not None and v1.is_valid() and v2.is_valid() ):
                new_u.add_edge(v1, v2)
        return new_u

class SCCVisitor(DFSVisitor):
    def __init__(self):
        self.vertices = []

    def discover_vertex(self, u):
        self.vertices.append(u)