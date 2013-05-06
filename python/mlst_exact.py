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
def sort_by_degree(V, degree):
    def sort(left, right):
        result = []
        while len(left) > 0 or len(right) > 0:
            if len(left) > 0 and len(right) > 0:
                if degree(left[0]) >= degree(right[0]):
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

def degree(v, g, V_IN, V_BN, V_LN, V_FL, V_Free):
    V_g = list(g.vertices())
    if (v in exclusive(V_g, union(V_IN, V_LN))):
        if (v in V_BN):
            return len(intersect(neighbors(v), union(V_Free, V_FL)))
        elif (v in V_Free):
            return len(intersect(neighbors(v), union(V_Free, union(V_FL, V_BN))))
        elif (v in V_FL):
            return len(intersect(neighbors(v), union(V_Free, V_BN)))

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

def find_mlst(g, V_g, V_Free, V_BN, V_IN, V_LN, V_FL):
    def degree(v):
        if (v in exclusive(V_g, union(V_IN, V_LN))):
            if (v in V_BN):
                return len(intersect(neighbors(v), union(V_Free, V_FL)))
            elif (v in V_Free):
                return len(intersect(neighbors(v), union(V_Free, union(V_FL, V_BN))))
            elif (v in V_FL):
                return len(intersect(neighbors(v), union(V_Free, V_BN)))
    def reduce_g():
        # reductions from definition 3
        # R1
        for (e in list(g.edges())):
            if ((e.source() in V_FL) and (e.target() in V_FL)) or ((e.source() in V_BN) and (e.target() in V_BN)):
                g.remove_edge(e)
        # R2
        for (v in V_BN):
            if degree(v) == 0:
                V_LN.append(v)
                V_BN.remove(v)
        # R3
        for (v in V_Free):
            if degree(v) == 1:
                V_FL.append(v)
                V_Free.remove(v)
        # R4
        for (v in V_Free):
            if len(intersect(neighbors(v), union(V_Free, V_FL))) == 0:
                V_FL.append(v)
                V_Free.remove(v)
        # R5?
        for (v in V_Free):
            if (degree(v) == 2):
                V_FL.append(v)
                V_Free.remove(v)
        # R6 - Cut Vertex
        # no rule yet
        # R7
        for (e in list(g.edges())):
            if (e.source() in V_LN and e.target() in exclusive(V_g, V_IN)):
                g.remove_edge(e)

    # base case
    if V_g == V_Free:
        V_Free = sort_by_degree(V_Free, degree)
        V_BN = V_Free[0]
        V_Free = V_Free[1:]
    else:
        V_Free = sort_by_degree(V_Free, degree) 

    reduce_g()
    if V_g == union(V_IN, V_LN):
        return len(V_LN)
    v = V_BN[0]
    V_BN = V_BN[1:]
    if (degree(v) >= 3 or (degree(v) == 2 and neighborsx(v, V_FL))):
        return # < v -> LN || v -> IN >
    elif degree(v) == 2:
        N_Free = neighborsx(v, V_Free)
        x_1 = N_Free[0]
        if (N_Free[i] <= x_1):
            x_2 = N_Free[i]
        else:
            x_2 = x_1
            x_1 = N_Free[i]
        if degree(x_1) == 2:
            z = exclusive(neighbors(x_1), [v])
            if z in V_Free:
                return # < v -> LN || v -> IN, x_1 -> IN || v -> IN, x_1 -> LN >
            elif z in V_FL:
                return # < v -> IN >
        elif exclusive(intersect(neighbors(x_1), neighbors(x_2)), V_FL) == [v] and all_v_d3(intersect(neighborsx(x_1, V_FL), neighborsx(x_2, V_FL))):
            return # < v -> LN || v -> IN, x_1 -> IN || v -> IN, x_1 -> LN, x_2 -> IN || v -> IN, x_1 -> LN, x_2 -> LN, N_Free(x_1, x_2) -> FL, N_BN(x_1, x_2) -> LN >
        elif exclusive(intersect(x_1, x_2), V_FL) != [v]:
            return # <v -> LN || v -> IN, x_1 -> IN || v -> IN, x_1 -> LN, x_2 -> IN >
    elif degree(v) == 1:
        # max path part... P = (v = v_0...)
        for z in exclusive(neighbors(v_k), P):
            if z in V_FL and degree(z) == 1:
                return # < v_0, ..., v_k -> IN, z -> LN >
            elif z in V_FL and degree(z) > 1:
                return # < v_0, ..., v_k-1 -> IN, v_k -> LN >
            elif z in V_BN:
                return # < v -> LN >
            elif z in V_Free:
                return # < v_0, ..., v_k -> IN, x -> IN, v -> LN >

    return g

# To run this program run: python mlst_exact.py file.in
if __name__ == '__main__':
    graphs = load_graphs();
    mlsts = []
    for i, g in enumerate(graphs):
        print "Processing graph {0} with {1} vertices and {2} edges".format(i, g.num_vertices(), g.num_edges())
        # inductive setup
        V_g = vertices(g)
        V_Free = V_g
        V_BN = [V_Free[0]]
        V_Free = V_Free[1:]
        V_IN = []
        V_LN = [] 
        V_FL = []
        mlst = find_mlst(g, V_g, V_Free, V_BN, V_IN, V_LN, V_FL)
        if (is_spanning_tree(mlst)):
            mlsts.append(mlst)
        else:
            print "ERROR: Graph {0} is not a spanning tree!".format(i)
            mlsts.append(mlst)
    output_graphs(mlsts)
