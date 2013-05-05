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

# create a list of vertices from a graph
def vertices(g):
    V = []
    n = g.vertices()
    for x in n:
        V.append(x)
    return V

# sort a list of vertices by edge degree descending
def sort_by_degree(V):
    def sort(left, right):
        result = []
        while len(left) > 0 or len(right) > 0:
            if len(left) > 0 and len(right) > 0:
                if left[0].out_degree() >= right[0].out_degree():
                    result.append(left[0])
                    left = left[1:]
                else:
                    result.append(right[0])
                    right = right[1:]
            elif len(left) > 0:
                result.append(left[0])
                left = left[1:]
            elif len(right) > 0:
                result.append(right[0])
                right = right[1:]
        return result

    if len(V) <= 1:
        return V
    left = []
    right = []
    middle = len(V) // 2
    for x in range(0, middle):
        left.append(V[x])
    for x in range(middle, len(V)):
        right.append(V[x])
    left = sort_by_degree(left)
    right = sort_by_degree(right)
    return sort(left, right)


# neighbors : N(v) = {u in V | {u, v} in E }
def neighbors(v):
    n = []
    g = v.all_neighbours()
    for x in g:
        n.append(x)
    return n

# closed neighbors : N[v] = {v} U N(v)
def neighborsc(v):
    n = neighbors(v)
    n.append(v)
    return n

def degree(v, V_IN, V_BN, V_LN, V_FL, V_Free):
    if (v in )

# exclusive neighbors : Nx(v) = N(v) intersected with X
def neighborsx(v, X):
    n = neighbors(v)
    return intersect(n, X)

# intersection
def intersect(X, Y):
    return [filter(lambda i: i in X, sublist) for sublist in Y]

def union(X, Y):
    return list(frozenset(X + Y))

# X \ Y
def exclusive(X, Y):
    X_c = list(X)
    Y_c = list(Y)
    while len(Y_c) != 0:
        i = Y_c.pop()
        X_c.remove(i)
    return X_c

def is_spanning_tree(g):
    num_vertices = g.num_vertices()
    num_edges = g.num_edges()
    if num_edges != num_vertices - 1:
        return False
    if len(vertices_deg_k(1, g)) != num_vertices:
        return False
    return True

def find_mlst(g):
    def reduce_g(g, V_IN, V_BN, V_LN, V_FL, V_Free):
        # reductions from definition 3
        for (e in list(g.edges())):
            if ((e.source() in V_FL) and (e.target() in V_FL)) or ((e.source() in V_BN) and (e.target() in V_BN)):
                g.remove_edge(e)
        # if d(v) >= 3 or (d(v) = 2 and N_FL(v) != 0) then
        if (v.out_degree() >= 3 or (v.out_degree() == 2 and len(neighborsx(v, V_FL)) != 0)):
            0 # < v -> LN || v -> IN >

    # inductive setup
    # BN = {r}, IN = LN = FL = 0
    V_Free = sort_by_degree(vertices(g))
    V_BN = [V_Free[0]]
    V_Free = V_Free[1:]
    reduce_g([],V_BN,[],[],V_Free)

    return g

# To run this program run: python mlst_exact.py file.in
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
            mlsts.append(mlst)
    output_graphs(mlsts)
