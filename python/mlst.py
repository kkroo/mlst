#!/usr/bin/env python
import config
import reader

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
        print(g.num_edges())
        v_names = g.vertex_properties["names"]
        for e in g.edges():
           print("{0} {1}".format(v_names[e.source()],v_names[e.target()]))

def vertices_deg_k(k,G):
    result = []
    for v in G.vertices():
        if v.out_degree() >= k:
            result.append(v)
    return result

def vertex_deg_k(k,g):
    for v in g.vertices():
        if v.out_degree() >= k:
            return v
    return None
    
def is_spanning_tree(G):
    num_vertices = G.num_vertices()
    num_edges = g.num_edges()
    if num_edges != num_vertices - 1:
        return False
    if len(vertices_deg_k(1, G)) != num_vertices:
        return False
    return True

def tree(G):
    return None

# To run this program run: python mlst.py file.in
if __name__ == '__main__':
    graphs = load_graphs();
    output_graphs(graphs)
