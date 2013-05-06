#!/usr/bin/env python
import config
import reader
from ugraph import *
from graph_tool.all import *
import sys
from sets import Set

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
        g.output()

def vertices_deg_k(k,g,find_one=False, exact=False):
    result = []
    for v in g.vertices():
        if (not exact and v.out_degree() >= k) or (exact and v.out_degree() == k):
           if (v.is_valid()):
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
    print "\tThe spanning tree has {0} vertices and {1} edges and {2} leaves".format(g.num_vertices(), g.num_edges(),len(vertices_deg_k(1, g, exact=True)))
    return True

def construct_T_i(v,g):
    T_i = UGraph()

    v_prime = T_i.add_vertex( g.find_name(v) )
    for c in v.out_neighbours():
        c_prime = T_i.add_vertex( g.find_name(c) )
        T_i.add_edge(v_prime, c_prime)
    return T_i

def expandable_leaf_highest_priority(T_i, g):
    low_priority = None
    for v in T_i.vertices():
        r = g.find_vertex( T_i.find_name(v) ) #find corresponding vertex in g
        count = 0
        if r is not None and v.out_degree() == 1:
            if r.out_degree() >= 3:
                count = 0
                for c in r.all_neighbours():
                    if T_i.find_vertex( g.find_name(c) ) is None:
                        count+=1
                    if count >= 2:
                        return (r,2)
            if r.out_degree() == 2:
                for y in r.all_neighbours():
                    count = 0
                    for c in y.all_neighbours():
                        if T_i.find_vertex( g.find_name(c) ) is None:
                            count+=1
                        if count > 2:
                            return (r,1)
                        if count == 2:
                            low_priority = r
                if low_priority is not None:
                    return (low_priority,3)
                else: 
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
    u_T_i = T_i.find_vertex( g.find_name(u) )
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
        print "Our vertex of deg >= 3 is {0} = {1}".format(g.find_name(v), repr(v))
        T_i = construct_T_i(v, g)
        print "\tOur T_i is a graph with {0} vertices and {1} edges".format(T_i.num_vertices(), T_i.num_edges())
        expandable_leaf = expandable_leaf_highest_priority(T_i, g)
        while expandable_leaf is not None:
            print "\tOur expandable leaf is {0} with case {1}".format(g.find_name(expandable_leaf[0]), expandable_leaf[1])
            u = expandable_leaf[0]
            case = expandable_leaf[1]
            if (case == 2):
                T_i = expand_case_b(u, T_i, g)
            else:
                T_i = expand_case_a(u, T_i, g)
            print "\tOur expanded T_i is a graph with {0} vertices and {1} edges".format(T_i.num_vertices(), T_i.num_edges())
            expandable_leaf = expandable_leaf_highest_priority(T_i, g)
        f.union(T_i)
        print "\tOur f is a graph with {0} vertices and {1} edges".format(f.num_vertices(), f.num_edges())
        g.intersect(T_i)
        print "\tOur g is a graph with {0} vertices and {1} edges".format(g.num_vertices(), g.num_edges())
        #Remove from g all vertices in T_i and all edges incident to them
        v_deg_three = vertices_deg_k(3, g, True)
    #Connect the trees in F and all vertices not in F to form a spanning tree T
    for v in g.vertices():
        v_obj = f.add_vertex(g.find_name(v))
        print "\tAdding vertex {0}".format(v_obj)
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
    f_scc = make_scc(f)
    non_leaves = Set([f.find_name(v) for v in vertices_deg_k(2, f)])
    a = False
    b = False
    c = False
    while len(f_scc) > 1:
        non_leaves_in_first_scc = non_leaves.intersection(f_scc[0])
        non_leaves_not_in_first_scc = non_leaves.difference(f_scc[0])
        leaves_not_in_first_scc = Set([v for scc in f_scc for v in scc]).difference(non_leaves).difference(f_scc[0])
        foo = False
        if a == False:
            for v in non_leaves_in_first_scc:
                if foo == True:
                    break
                for e in g.find_vertex(v).all_edges():
                    dest = e.source() if g.find_name(e.source()) != v else e.target()
                    dest_name = g.find_name(dest)
                    if dest_name in non_leaves_not_in_first_scc:
                        f.add_edge(f.find_vertex(v), f.find_vertex(dest_name))
                        dest_cc = 0
                        for i in range(1, len(f_scc)):
                            if dest_name in f_scc[i]:
                                dest_cc = i 
                        f_scc[0] = f_scc[0].union(f_scc[dest_cc])
                    #    print "Adding edge ({0},{1}) between scc 0 and {2}".format(v, dest_name, dest_cc)
                        del f_scc[dest_cc]
                        foo = True
                        break
        a = True
     #   print "A is true"
        if b == False and len(f_scc) > 1:
            for v in f_scc[0].difference(non_leaves_in_first_scc):
                if foo == True:
                    break
                for e in g.find_vertex(v).all_edges():
                    dest = e.source() if g.find_name(e.source()) != v else e.target()
                    dest_name = g.find_name(dest)
                    if dest_name in non_leaves_not_in_first_scc:
                        f.add_edge(f.find_vertex(v), f.find_vertex(dest_name))
                        dest_cc = 0
                        for i in range(1, len(f_scc)):
                            if dest_name in f_scc[i]:
                                dest_cc = i 
                        f_scc[0] = f_scc[0].union(f_scc[dest_cc])
                        del f_scc[dest_cc]
                  #      print "Adding edge ({0},{1}) between scc 0 and {2}".format(v, dest_name, dest_cc)
                        foo = True
                        break
        b = True
     #   print "B is true"  
        if c == False and len(f_scc) > 1:
            for v in non_leaves_in_first_scc:
                if foo == True:
                    break
                for e in g.find_vertex(v).all_edges():
                    dest = e.source() if g.find_name(e.source()) != v else e.target()
                    dest_name = g.find_name(dest)
                #    print "Edge ({0},{1}) and dest {2} and v={3}".format(g.find_name(e.source()), g.find_name(e.target()), dest_name, v)
                #    print leaves_not_in_first_scc
                    if dest_name in leaves_not_in_first_scc:
                        f.add_edge(f.find_vertex(v), f.find_vertex(dest_name))
                        dest_cc = 0
                        for i in range(1, len(f_scc)):
                            if dest_name in f_scc[i]:
                                dest_cc = i 
                        f_scc[0] = f_scc[0].union(f_scc[dest_cc])
                 #       print "Adding edge ({0},{1}) between scc 0 and {2}".format(v, dest_name, dest_cc)
                        del f_scc[dest_cc]
                        foo = True
                        break
        c = True
      #  print "C is true"
        if len(f_scc) > 1:
            for v in f_scc[0].difference(non_leaves_in_first_scc):
                if foo == True:
                    break
                for e in g.find_vertex(v).all_edges():
                    dest = e.source() if g.find_name(e.source()) != v else e.target()
                    dest_name = g.find_name(dest)
                    if dest_name in leaves_not_in_first_scc:
                        f.add_edge(f.find_vertex(v), f.find_vertex(dest_name))
                        dest_cc = 0
                        for i in range(1, len(f_scc)):
                            if dest_name in f_scc[i]:
                                dest_cc = i 
                        f_scc[0] = f_scc[0].union(f_scc[dest_cc])
                        del f_scc[dest_cc]
                   #     print "Adding edge ({0},{1}) between scc 0 and {2}".format(v, dest_name, dest_cc)
                        foo = True
                        break
        break
     #   print "SCC length = {0}".format(len(f_scc))
    return f


def find_mlst(g):
    return make_spanning(make_leafy_forest(g.copy()), g)

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
            print "\tERROR: Graph {0} is not a spanning tree!".format(i)
    output_graphs(mlsts)
