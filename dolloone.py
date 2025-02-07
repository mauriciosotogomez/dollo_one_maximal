import networkx as nx
import matplotlib.pyplot as plt
import copy
import RedBlackGraph as rbg 
from argparse import ArgumentParser


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

########################

# Create a new instance of the BlackRedGraph
graph = rbg.RedBlackGraph()
data_file = 'data/example_01.txt'
verbose = args.v

# Get problem input matrix
if args.input_file is not None:
    data_file = args.input_file

graph.read_from_file(data_file)
if verbose:
    graph.plot_graph()

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
            print('CASE CONTAINED')
            next_characters = list(Cc)
            rb_graph.reduce(next_characters,verbose)
            reduction_extension = reduction_recursive(rb_graph)
            return next_characters+reduction_extension
        # Ci empty
        else :
            print('CASE UNIVERSAL')            
            minimal_species = rb_graph.get_minimal_size_black_species()
            print('Minimal size species:', minimal_species)
        
            for s0 in minimal_species :
                rb_graph_copy = copy.deepcopy(rb_graph)
                next_characters = list(Grb.neighbors(s0))
                print('Try:', s0, next_characters)
                rb_graph_copy.reduce(next_characters, verbose)
                reduction_extension = reduction_recursive(rb_graph_copy)
             
                if 'fail' not in reduction_extension :
                    return next_characters+reduction_extension
            
                print('FAIL WITH:', s0)
                print('=======')
            return ['fail']
        
    # Ci is not empty
    else : 
        print('CASE pi_U')
        next_characters = rb_graph.compute_pi_U()
        rb_graph.reduce(next_characters, verbose)
        reduction_extension = reduction_recursive(rb_graph)
        return next_characters+reduction_extension

reduction = reduction_recursive(graph)
is_correct = ('fail' not in reduction) 
print()
if is_correct :
    print("\033[1m\033[92m {}\033[00m" .format('SUCESS:')) # Green
    print(reduction)
else :
    print("\033[91m {}\033[00m" .format('FAIL')) # Red

# reduction =  ['C'+str(i) for i in [1,2,3,4,6,5]]
# graph.reduce(reduction)





