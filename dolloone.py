import networkx as nx
import matplotlib.pyplot as plt
import copy
import RedBlackGraph as rbg 
from argparse import ArgumentParser
import itertools

#######################
# Read Input  #
#######################

parser = ArgumentParser()

parser.add_argument("-f", "--input_file",
                   dest="input_file", default=None,
                   help="use this .csv file as input")

parser.add_argument("-v",
                    action="store_true",
                    help="verbose")

args = parser.parse_args()
# Get problem input matrix

data_file = 'data/example_01.txt'
if args.input_file is not None:
    data_file = args.input_file

# verbose
verbose = args.v

########################

def all_permutations(rb_graph):
    graph=rb_graph.get_graph()
    characters= [node for node,data in graph.nodes(data=True) if data.get('bipartite') == 0]  
    for perm in itertools.permutations(characters) :
        rb_graph_copy = copy.deepcopy(rb_graph)
        rb_graph_copy.reduce(perm)
        Grb=rb_graph_copy.get_graph()
        # If no active characters
        if len(Grb.edges()) == 0 : # Sigma graph
            print(f'SUCESS: {perm} all permutations')
            return 
    print(f'NO DOLLO-1 all permutations')
    return

def reduction_recursive(rb_graph) :

    Ci,Cu,Cc,Ca = rb_graph.update_partition()
    Sr, Sb =rb_graph.get_species()
    Grb=rb_graph.get_graph()
    
    # If no active characters
    if len(Ci | Cu | Cc) == 0 : 
        if len(Grb.edges()) > 0 : # Sigma graph
            return ['fail']
        else :
            return list()
        
    if len(Ci) == 0 :
        if len(Cu) == 0 :
            #print('CASE CONTAINED')
            next_characters = list(Cc)
            rb_graph.reduce(next_characters,verbose)
            reduction_extension = reduction_recursive(rb_graph)
            return next_characters+reduction_extension
        # Ci empty
        else :
            #print('CASE UNIVERSAL')            
            minimal_species = rb_graph.get_minimal_size_black_species()
            #print('Minimal size species:', minimal_species)

            # Cycle on minimal species
            for s0 in minimal_species :
                rb_graph_copy = copy.deepcopy(rb_graph)
                next_characters = list(Grb.neighbors(s0))
                #print('Try:', s0, next_characters)
                rb_graph_copy.reduce(next_characters, verbose)
                reduction_extension = reduction_recursive(rb_graph_copy)
             
                if 'fail' not in reduction_extension :
                    return next_characters+reduction_extension
            
                #print('FAIL WITH:', s0)
                #print('=======')
            return ['fail']
        
    # Ci is not empty
    else : 
        #print('CASE pi_U')
        next_characters = rb_graph.compute_pi_U()
        rb_graph.reduce(next_characters, verbose)
        reduction_extension = reduction_recursive(rb_graph)
        return next_characters+reduction_extension

########
# MAIN #
########

# Create a new instance of the BlackRedGraph
graph = rbg.RedBlackGraph()
graph.read_from_file(data_file)
if verbose:
    graph.plot_graph()

# Connected components
G = graph.get_graph()
connected_components = [G.subgraph(c).copy() for c in nx.connected_components(G)]
print('---')
print(f'Numer of connected components: {len(connected_components)}')

for i, cc_graph in enumerate(connected_components) :
    print('---')
    rb_cc_graph = rbg.RedBlackGraph()
    rb_cc_graph.from_networkx_graph(cc_graph)
    
    n_red, n_black = rb_cc_graph.get_species() 
    n_species = len(n_red) + len(n_black)
    n_characters =  cc_graph.number_of_nodes()-n_species
    print(f' Connected component {i}\n Number of characters: {n_characters}\n Number of species: {n_species}\n Number of edges: {cc_graph.number_of_edges()}')
    #rb_cc_graph.print_status()
    print('---')

    reduction = reduction_recursive(rb_cc_graph)
    is_correct = ('fail' not in reduction)
    if is_correct :
        print(f'SUCESS: {reduction}')
    else :
        print(f'NO DOLLO-1')
#print()

all_permutations(graph)

