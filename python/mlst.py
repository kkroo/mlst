#!/usr/bin/env python
import config
import reader
from graph_tool.all import *
import sys

def load_graphs():
    infile = config.DEFAULT_INPUT_FILE if len(sys.argv) <= 1 else sys.argv[1]

    graphs = None
    try:
        f = open(infile)
        in_reader = reader.GraphToolInFileReader(f)
        graphs = in_reader.read_input_file()
        print("Loaded {0} graphs from file '{1}' sucessfully.\n".format(len(graphs), infile))

    except IOError as e:
        print("Error reading '{0}' ({1}).\n".format(infile, e))
    except reader.ReaderException as e:
        print("({0}) {1}\n".format(infile, e))

    return graphs

def output_graphs(graphs):
    print(len(graphs))
    for i, g in enumerate(graphs):
        print(str(g.num_edges()) + " " + str(is_spanning_tree(g)))
        v_names = g.vertex_properties["names"]
        for e in g.edges():
           print("{0} {1}".format(v_names[e.source()],v_names[e.target()]))

def vertices_deg_k(k,g,find_one=False):
    result = []
    for v in g.vertices():
        if v.out_degree() >= k:
            result.append(v)
            if find_one:
                break
    return result
    
def is_spanning_tree(g):
    num_vertices = g.num_vertices()
    num_edges = g.num_edges()
    if num_edges != num_vertices - 1:
        return False
    if len(vertices_deg_k(1, g)) != num_vertices:
        return False
    return True

def construct_T_i(v,g):
    T_i = Graph(directed=False)
    
    new_names = T_i.new_vertex_property("int")
    old_names = g.vertex_properties["names"]

    new_v = T_i.add_vertex()
    new_names[new_v] = old_names[v]
    for c in v.out_neighbours():
        c_prime = T_i.add_vertex()
        new_names[c_prime] = old_names[c]
        T_i.add_edge(new_v, c_prime)
    T_i.vertex_properties["names"] = new_names
    return T_i

def expandable_leaf_highest_priority(v, T_i, g):
    return None

def expand_case_a(u, T_i, g):
    return None

def expand_case_b(u, T_i, g):
    return None


def find_mlst(g):
    f = Graph(directed=False)
    v_deg_three = vertices_deg_k(3, g, True)
    while len(v_deg_three) != 0:
        v = v_deg_three[0]
        T_i = construct_T_i(v, g)
        print "Build T_i with root {0}, {1} vertices and {2} edges".format(v, T_i.num_vertices(), T_i.num_edges())
        expandable_leaf = (v, T_i, g)
        while expandable_leaf is not None:
            u = expandable_leaf[0]
            case = expandable_leaf[1]
            if (case == 2):
                expand_case_b(u, T_i, g)
            else:
                expand_case_a(u, T_i, g)
            expandable_leaf = (v, T_i, g)
            break
        break
        #Merge f and T_i
        #Remove from g all vertices in T_i and all edges incident to them
    #Connect the trees in F and all vertices not in F to form a spanning tree T
    return g

# To run this program run: python mlst.py file.in
if __name__ == '__main__':
    graphs = load_graphs();
    mlsts = []
    for i, g in enumerate(graphs):
        print "Processing graph {0} with {1} vertices and {2} edges".format(i, g.num_vertices(), g.num_edges())
        mlst = find_mlst(g)
        if (is_spanning_tree(mlst)):
            mlsts.append(mlst)
        else:
            print "ERROR: Graph {0} is not a spanning tree!".format(i)
    output_graphs(mlsts)
