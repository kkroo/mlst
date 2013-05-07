#!/usr/bin/env python
import config
import reader
from ugraph import *
from graph_tool.all import *
import sys
from sets import Set

"""
This algorithm is based loosely off of the approximation described in the paper paper by Solis-Oba:
    http://pdf.aminer.org/000/186/511/approximation_algorithm_for_finding_a_spanning_tree_with_maximum_number.pdf
"""

def vertices_deg_k(k,g,find_one=False, exact=False):
    result = []
    for v in g.vertices():
        if (not exact and v.out_degree() >= k) or (exact and v.out_degree() == k):
           if (v.is_valid()):
                result.append(v)
                if find_one:
                    break
    return result

def construct_T_i(v,g):
    T_i = UGraph()
    v_prime = T_i.add_vertex( g.find_name(v) )
    for c in v.out_neighbours():
        c_prime = T_i.add_vertex( g.find_name(c) )
        T_i.add_edge(v_prime, c_prime)
    return T_i

def expandable_leaf_highest_priority(T_i, g):
    low_priority = None
    MAX = 50 #the higher this number the more exhaustive the search
    MIN = 3 #dont make this smaller than 3
    for i in range(MAX, MIN - 1, -1):
        for v in T_i.vertices():
            r = g.find_vertex( T_i.find_name(v) ) #find corresponding vertex in g
            count = 0
            if r is not None and v.out_degree() == 1:
                if r.out_degree() >= i:
                    count = 0
                    for c in r.all_neighbours():
                        if T_i.find_vertex( g.find_name(c) ) is None:
                            count+=1
                        if count >= i - 1:
                            return (r,2)
                if r.out_degree() == 2:
                    for y in r.all_neighbours():
                        if T_i.find_vertex(g.find_name(y)) is not None:
                            continue
                        count = 0
                        for c in y.all_neighbours():
                            if T_i.find_vertex( g.find_name(c) ) is None:
                                count+=1
                            if count >= i - 1:
                                return (r,1)
                            if count == 2 and i == MIN:
                                low_priority = r
                        if low_priority is not None:
                            return (low_priority,3)
    return None

    
def expand_case_a(u, T_i, g):
    u_T_i = T_i.find_vertex( g.find_name(u) )
    for c in u.all_neighbours():
        if T_i.find_vertex( g.find_name(c) ) is None:
            child = T_i.add_vertex( g.find_name(c) )
            T_i.add_edge(u_T_i, child)
            for d in c.all_neighbours():
                grand_child_name = g.find_name(d)
                if T_i.find_vertex( grand_child_name ) is None:
                    grand_child = T_i.add_vertex( grand_child_name )
                    T_i.add_edge(child, grand_child)
    return T_i

def expand_case_b(u, T_i, g):
    u_T_i  = T_i.find_vertex( g.find_name(u) )
    for c in u.all_neighbours():
        if T_i.find_vertex( g.find_name(c) ) is None:
            child = T_i.add_vertex( g.find_name(c) )
            T_i.add_edge(u_T_i, child)
    return T_i


def make_leafy_forest(g):
    f = UGraph()
    v_deg_three = vertices_deg_k(3, g, True)
    while len(v_deg_three) != 0:
        v = v_deg_three[0]
        T_i = construct_T_i(v, g)
        expandable_leaf = expandable_leaf_highest_priority(T_i, g)
        while expandable_leaf is not None:            
            u = expandable_leaf[0]
            case = expandable_leaf[1]
            if (case == 2):
                T_i = expand_case_b(u, T_i, g)
            else:
                T_i = expand_case_a(u, T_i, g)            
            expandable_leaf = expandable_leaf_highest_priority(T_i, g)
        f.union(T_i)
        g.difference(T_i)
        v_deg_three = vertices_deg_k(3, g, True)
    for v in g.vertices():
        v_obj = f.add_vertex(g.find_name(v))
    return f

def make_scc(f):
    visited = []
    scc = []
    scc_count = -1
    for v in f.vertices():
        if v in visited:
            continue
        visitor = SCCVisitor()
        dfs_search(f, v, visitor)
        scc_count+=1
        visited+=visitor.vertices
        scc.append(Set([f.find_name(v) for v in visitor.vertices]))
    return scc



def make_spanning(f, g):

    def try_union (sources, dests):
        for v in sources:
            for e in g.find_vertex(v).all_edges():
                dest = e.source() if g.find_name(e.source()) != v else e.target()
                dest_name = g.find_name(dest)
                if (dest_name in f_scc[largest_scc]):
                    continue
                if dest_name in dests:
                    f.add_edge(f.find_vertex(v), f.find_vertex(dest_name))
                    dest_cc = None
                    for i in range(len(f_scc)):
                        if dest_name in f_scc[i] and i != largest_scc:
                            dest_cc = i
                    f_scc[largest_scc] = f_scc[largest_scc].union(f_scc[dest_cc])
                    del f_scc[dest_cc]
                    return True
        return False

    f_scc = make_scc(f)
    while len(f_scc) > 1:
        scc_sizes = [ len(scc) for scc in f_scc ]
        largest_scc = scc_sizes.index(max(scc_sizes))
        
        non_leaves = Set([f.find_name(v) for v in vertices_deg_k(2, f)])
        non_leaves_in_largest_scc = non_leaves.intersection(f_scc[largest_scc])
        non_leaves_not_in_largest_scc = non_leaves.difference(f_scc[largest_scc])

        leaves_in_largest_scc = f_scc[largest_scc].difference(non_leaves_in_largest_scc)
        leaves_not_in_largest_scc = Set([v for scc in f_scc for v in scc]).difference(non_leaves_not_in_largest_scc)

        if try_union(non_leaves_in_largest_scc, non_leaves_not_in_largest_scc):
            continue
        elif try_union(non_leaves_in_largest_scc, leaves_not_in_largest_scc):
            continue
        elif try_union(leaves_in_largest_scc, non_leaves_not_in_largest_scc):
            continue
        else:
            try_union(leaves_in_largest_scc, leaves_not_in_largest_scc)
    return f


def find_mlst(g):
    f = make_leafy_forest(g.copy())
    return make_spanning(f, g)


def load_graphs():
    infile = config.DEFAULT_INPUT_FILE if len(sys.argv) <= 1 else sys.argv[1]

    graphs = None
    try:
        f = open(infile)
        in_reader = GraphToolInFileReader(f)
        graphs = in_reader.read_input_file()
        print("Loaded {0} graphs from file '{1}' sucessfully.\n".format(len(graphs), infile))

    except IOError as e:
        print("Error reading '{0}' ({1}).\n".format(infile, e))
    except reader.ReaderException as e:
        print("({0}) {1}\n".format(infile, e))

    return graphs

def output_graphs(graphs):
    outfile = config.DEFAULT_OUTPUT_FILE if len(sys.argv) <= 1 else sys.argv[2]
    f = open(outfile, 'w')
    f.write(str(len(graphs)) + "\n")
    for i, g in enumerate(graphs):
        f.write(g.output())

def is_spanning_tree(g):
    num_vertices = g.num_vertices()
    num_edges = g.num_edges()
    if num_edges != num_vertices - 1:
        return False
    if len(vertices_deg_k(1, g)) != num_vertices:
        return False
    print("\tThe spanning tree has {0} vertices and {1} edges and {2} leaves\n".format(g.num_vertices(), g.num_edges(),len(vertices_deg_k(1, g, exact=True))))
    return True


# To run this program run: python mlst.py file.in file.out
if __name__ == '__main__':
    graphs = load_graphs();
    mlsts = []
    for i, g in enumerate(graphs):
        print("Processing graph {0} with {1} vertices and {2} edges".format(i, g.num_vertices(), g.num_edges()))
        mlst = find_mlst(g)
        if (is_spanning_tree(mlst)):
            mlsts.append(mlst)
            """ DRAWING AND VISULIZATION -- CREATE DIRECTORY NAMED draw IN EXECUTING DIRECTORY
            text = graphs[i].new_vertex_property("string")
            size = graphs[i].new_vertex_property("int")
            for v in graphs[i].vertices():
                text[v] = str(graphs[i].find_name(v))
                size[v] = 8
            graph_draw(graphs[i], nodesfirst=True, vertex_size=1, vertex_text=text, vertex_font_size=size, output="draw2/{0}.pdf".format(i))

            text = mlsts[i].new_vertex_property("string")
            size = mlsts[i].new_vertex_property("int")
            for v in mlsts[i].vertices():
                text[v] = str(mlsts[i].find_name(v))
                size[v] = 8
            graph_draw(mlsts[i],  nodesfirst=True, vertex_size=1, vertex_text=text, vertex_font_size=size, output="draw2/{0}_t.pdf".format(i))
            """
        else:
            print("\tERROR: Graph {0} is not a spanning tree!".format(i))
            exit()
    output_graphs(mlsts)
