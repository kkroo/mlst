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

def expandable_leaf_highest_priority(T_i, g):
    t_names_map = T_i.vertex_properties["names"].a
    t_names = {}
    for i in range(len(t_names_map)):
        v = T_i.vertex(i)
        t_names[t_names_map[v]] = v

    g_names_map = g.vertex_properties["names"].a
    g_names = {}
    for i in range(len(g_names_map)):
        v = g.vertex(i)
        g_names[g_names_map[v]] = v

    low_priority = None
    for v in T_i.vertices():
        r = g_names[t_names_map[v]] #find corresponding vertex in g
        count = 0
        if v.out_degree() == 1:
            if r.out_degree() >= 3:
                count = 0
                for c in r.all_neighbours():
                    if g_names_map[c] not in t_names:
                        count+=1
                    if count >= 2:
                        return (r,2)
            if r.out_degree() == 2:
                for y in r.all_neighbours():
                    count = 0
                    for c in y.all_neighbours():
                        if g_names_map[c] not in t_names:
                            count+=1
                        if count > 2:
                            return (r,1)
                        if count == 2:
                            low_priority = r
                if low_priority is not None:
                    return (low_priority,3)
                else: 
                    return None



def find_vertex_by_name(v,g):
    names = g.vertex_properties["names"].a
    for i in range(len(names)):
        if names[i] == v:
            return g.vertex(i)
    return None
        
def count_neighbours_notin(r,T_i):

    count = 0
    for c in r.all_neighbours():
        if g_names_map[c] not in t_names:
            count+=1
    return count
            


    
def expand_case_a(u, T_i, g):
    t_names = T_i.vertex_properties["names"].a
    g_names = g.vertex_properties["names"]
    v_obj = find_name_in_T(t_names, u)
    for c in u.all_neighbours():
        child = g_names[c]
        if not check_stupid_c_array(t_names, child):
            nvert = T_i.add_vertex()
            t_names[nvert] = child
            T_i.add_edge(v_obj, nvert)
            for e in c.all_neighbours():
                grandchild = g_names[e]
                if not check_stupid_c_array(t_names, grandchild):
                    gverty = T_i.add_vertex()
                    t_names[gverty] = grandchild
                    T_i.add_edge(nvert, qverty)
    return T_i

def expand_case_b(u, T_i, g):
    t_names = T_i.vertex_properties["names"].a
    g_names = g.vertex_properties["names"]
    v_obj = find_name_in_T(t_names, u)
    for i in range(len(t_names)):
        if t_names[i] == v:
            v_obj = T_i.vertex(i)
            break
    for c in u.all_neighbours():
        name = g_names[c]
        if not check_stupid_c_array(t_names, name):
            nvert = T_i.add_vertex()
            t_names[n_vert] = name
            T_i.add_edge(v_obj, nvert)
    return T_i

def find_name_in_T(prop, inp):
    for i in range(len(prop)):
        if prop[i] == inp:
            return T_i.vertex(i)
            
def check_stupid_c_array(stupid, inp):
    for i in range(len(stupid)):
        if stupid[i] == inp:
            return True


def find_mlst(g):
    g_names_map = g.vertex_properties["names"]
    f = Graph(directed=False)
    v_deg_three = vertices_deg_k(3, g, True)
    while len(v_deg_three) != 0:
        v = v_deg_three[0]
        T_i = construct_T_i(v, g)

        expandable_leaf = expandable_leaf_highest_priority(T_i, g)
        print expandable_leaf
        print "Our expandable leaf is {0} with case {1}".format(g_names_map[expandable_leaf[0]], expandable_leaf[1])
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
