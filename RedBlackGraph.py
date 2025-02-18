import networkx as nx
import matplotlib.pyplot as plt

class RedBlackGraph:
    def __init__(self, characters=None, species=None, edges=None):
        if characters is None:
            self.characters = {
                'intersection': set(),
                'universal': set(),
                'contained': set(),
                'active': set()  # New set for active characters
            }
        else:
            self.characters = characters

        if species is None:
            self.species = {
                'black': set(),
                'red': set()
            }
        else:
            self.species = species

        if edges is None:
            self.edges = {
                'black': [],
                'red': []
            }
        else:
            self.edges = edges

        # Initialize graph    
        self.graph = nx.Graph()

        # Initialize dictionaries for character node counters
        self.character_counters = {}
        for char in self.characters['intersection'] | self.characters['universal'] | self.characters['contained'] | self.characters['active']:
            self.character_counters[char] = [0, 0]  # [red_neighbors, black_neighbors]

        # Initialize dictionaries for species node counters
        self.species_counters = {}
        for sp in self.species['black'] | self.species['red']:
            self.species_counters[sp] = [0, 0]  # [active_neighbors, inactive_neighbors]        

    def add_character(self, character, subset):
        self.characters[subset].add(character)
        self.character_counters[character]=[0,0]
        self.graph.add_node(character, bipartite=0)

    def add_species(self, species, color):
        self.species[color].add(species)
        self.species_counters[species]=[0,0]
        self.graph.add_node(species, bipartite=1)

    def add_edge(self, character, species, color):
        if color not in ['black', 'red']:
            raise ValueError("Invalid edge color")
        if character not in self.characters['intersection'] | self.characters['universal'] | self.characters['contained'] | self.characters['active']:
            raise ValueError("Invalid character")
        if species not in self.species['black'] | self.species['red']:
            raise ValueError("Invalid species")
        
        # Update node counters
        if color == 'black':
            self.species_counters[species][1] += 1
            if species in self.species['red']: # self.species_counters[species][0] > 0 : # red species
                self.character_counters[character][0] += 1
            else:
                self.character_counters[character][1] += 1
        else: # red edge
            self.character_counters[character][0] += 1
            self.species_counters[species][0] += 1
            # If a new red species 
            if species in self.species['black']:
                # Update species color
                self.species['black'].remove(species)
                self.species['red'].add(species)
                # Update species neighbors counters
                for char_species in self.graph.neighbors(species):
                    self.character_counters[char_species][0] += 1
                    self.character_counters[char_species][1] += -1
            
        # Add edge to the set and to the graph
        self.edges[color].append((character, species))
        self.graph.add_edge(character, species, color=color)

    def remove_edge(self, character, species, color):
        if (character, species) not in self.edges[color]:
            raise ValueError("Invalid edge or color")

        # Remove edge to the set and to the graph
        self.edges[color].remove((character, species))
        self.graph.remove_edge(character, species)

        # Update node counters
        if color == 'black': # black edge
            self.species_counters[species][1] += -1
            if species in self.species['red']: # self.species_counters[species][0] > 0 : # red species
                self.character_counters[character][0] += -1
            else:
                self.character_counters[character][1] += -1
        else: # red edge
            self.character_counters[character][0] += -1
            self.species_counters[species][0] += -1
            # If the species becomes black (removed species becomes black)
            if self.species_counters[species][0] == 0 :
            # species_neighbors = set(self.graph.neighbors(species))
            # if all(character not in self.characters['active'] for character in species_neighbors):
                # Update species color
                self.species['red'].discard(species)
                self.species['black'].add(species)
                # Update species neighbors counters
                for char_species in self.graph.neighbors(species):
                    self.character_counters[char_species][0] += -1
                    self.character_counters[char_species][1] += 1

    def get_species(self):
        return self.species['red'] , self.species['black']

    def from_networkx_graph(self, nx_graph):
        """
        Initialize a RedBlackGraph object from a NetworkX graph object.
        Args:
            nx_graph (networkx.Graph): The NetworkX graph object.
        """
        # Iterate over nodes
        for node, data in nx_graph.nodes(data=True):
            if data.get('bipartite') == 0:  # Character node
                self.add_character(node, 'universal')
            else:  # Species node
                self.add_species(node, 'black')

        # Iterate over edges
        for character in self.characters:
            if data.get('bipartite') == 0:  # Character node
                self.add_character(node, 'universal')
            else:  # Species node
                self.add_species(node, 'black')

        for u, v, data in nx_graph.edges(data=True):
            color = data.get('color', 'black')
            if nx_graph.nodes[u]['bipartite'] == 0 : # u is character
                self.add_edge(u, v, color)
            else : # u is species
                self.add_edge(v, u, color)
            
        # Initialize the graph object
        self.graph = nx_graph

    def plot_graph(self):
        char_nodes = [n for n,v in self.graph.nodes(data=True) if v['bipartite'] == 0] 
        species_nodes = [n for n,v in self.graph.nodes(data=True) if v['bipartite'] == 1]
        
        pos = nx.bipartite_layout(self.graph, char_nodes, scale=3, align='horizontal')
        nx.draw_networkx_nodes(self.graph, pos, nodelist=char_nodes, node_color='b', node_size=1500,alpha=0.2)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=species_nodes, node_color='gray', node_size=1500,alpha=0.2)
        
        black_edges = [(u,v) for u,v,e in self.graph.edges(data=True) if e['color'] == 'black']
        red_edges =   [(u,v) for u,v,e in self.graph.edges(data=True) if e['color'] == 'red']
        nx.draw_networkx_edges(self.graph, pos, edgelist=black_edges, edge_color='k')
        nx.draw_networkx_edges(self.graph, pos, edgelist=red_edges, edge_color='r')
        
        char_labels = {node: node for node in char_nodes}
        species_labels = {node: node for node in species_nodes}
        labels = {**char_labels, **species_labels}
        
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=10, font_color='k')
        
        plt.axis('off')
        plt.show()

    def read_from_file(self, file_path):
        with open(file_path, 'r') as file:
            # Read the first line to get the number of species and characters
            num_species, num_characters = map(int, file.readline().split())

            # Skip the empty line
            file.readline()

            # Initialize the species and characters sets
            self.species = {'black': set(), 'red': set()}
            self.characters = {'intersection': set(), 'universal': set(), 'contained': set(), 'active': set()}

            # Read the binary matrix
            adjacency_matrix = []
            
            for _ in range(num_species):
                row = file.readline().strip().split()
                adjacency_matrix.append([int(val) for val in row])

            # Construct the graph from the adjacency matrix
            for j in range(num_characters):
                character_name = f'C{j + 1}'
                self.add_character(character_name, 'universal')  # Assume all characters are initially universal

            for i, row in enumerate(adjacency_matrix):
                species_name = f'S{i + 1}'
                self.add_species(species_name, 'black')  # Assume all species are initially black
                # Add edges
                for j, value in enumerate(row):
                    if value == 1:
                        character_name = f'C{j + 1}'
                        self.add_edge(character_name, species_name, 'black')

            # Initialize the graph object
            self.graph = nx.Graph()
            for character in self.characters['intersection'] | self.characters['universal'] | self.characters['contained'] | self.characters['active']:
                self.graph.add_node(character, bipartite=0)
            for species in self.species['black'] | self.species['red']:
                self.graph.add_node(species, bipartite=1)
            for color, edges in self.edges.items():
                for u, v in edges:
                    self.graph.add_edge(u, v, color=color)

    def realize(self, character_name):
        # print('======')
        # print(f'REALIZE character: {character_name}')

        if character_name not in self.characters['intersection'] | self.characters['universal'] | self.characters['contained']:
            raise ValueError(f"Invalid character name: {character_name}")

        # Find the connected component of the character
        species_in_component =  self.get_species_in_connected_component(character_name)
        # Get the neighbors of the character
        neighbors = set(self.graph.neighbors(character_name))

        # Create red edges to non-neighbors in the same connected component and remove black edges
        for species in species_in_component:
            if species not in neighbors:
                self.add_edge(character_name, species, 'red')
            else:
                self.remove_edge(character_name, species, 'black')

        # Move the character to the 'active' set
        for char_set in {'intersection','universal','contained'} :
            if character_name in self.characters[char_set]:
                self.characters[char_set].remove(character_name)
        self.characters['active'].add(character_name)
        
        # Remove universal red characters
        while True:
            universal_red_characters = []
            # Search an universal red character
            for char in self.characters['active']:
                char_neighbors = set(self.graph.neighbors(char))
                species_in_component =  self.get_species_in_connected_component(char)
                if (len(char_neighbors)>0) & (len(char_neighbors) == len(species_in_component)):
                    universal_red_characters.append(char)
            if universal_red_characters :
                char_to_remove = universal_red_characters.pop()
                neighbors = set(self.graph.neighbors(char_to_remove))
                # Remove red edges
                for species in neighbors:
                    self.remove_edge(char_to_remove, species, 'red')
            else :
                break
            
        #_,_,_,_ = self.update_partition()
        #self.print_status()
        

    def print_status(self):
        print(f'Species in black: {self.species["black"]}')
        print(f'Species in red : {self.species["red"]}')
        print('--')
        print(f'Characters in intersection: {self.characters["intersection"]}')
        print(f'Characters in universal: {self.characters["universal"]}')
        print(f'Characters in contained: {self.characters["contained"]}')
        print(f'Characters in active: {self.characters["active"]}')
        print('--')
        print(f'Species counters  : {self.species_counters}')
        print(f'Character counters: {self.character_counters}')
        print('--')
        
    def get_species_in_connected_component(self, character_name):
        component = nx.node_connected_component(self.graph, character_name)
        species_in_component = {node for node in component if self.graph.nodes[node]['bipartite'] == 1}
        return species_in_component

    def reduce(self, reduction, verbose=False):
        for character in reduction:
            self.realize(character)
            if verbose:
                self.plot_graph()

    def update_partition(self):
        temp_intersection = set()
        temp_universal = set()
        temp_contained = set()

        for character in  self.characters['intersection'] | self.characters['universal'] | self.characters['contained']:
            
            # Get the connected component and neighbors of the character
            species_in_component = self.get_species_in_connected_component(character)
            neighbors = set(self.graph.neighbors(character))
            
            # Check the rules for each set      
            has_red_species = any(species in self.species['red'] for species in neighbors)
            has_black_species = any(species in self.species['black'] for species in neighbors)
            has_non_neighbor_red_species = any(species in self.species['red'] and species not in neighbors for species in species_in_component)            
            has_red_species = self.character_counters[character][0] > 0
            has_black_species = self.character_counters[character][1] > 0
            has_non_neighbor_red_species = self.character_counters[character][0] < len(self.species['red'])
            # Compute partition
            if has_black_species and has_red_species and has_non_neighbor_red_species:
                temp_intersection.add(character)
            elif has_black_species and (not has_non_neighbor_red_species) :
                temp_universal.add(character)
            elif all(neighbor in self.species['red'] for neighbor in neighbors):
                temp_contained.add(character)
    
        # Update the sets
        self.characters['intersection'] = temp_intersection
        self.characters['universal'] = temp_universal
        self.characters['contained'] = temp_contained

        return  self.characters['intersection'], self.characters['universal'], self.characters['contained'], self.characters['active']

    def get_graph(self) :
        return self.graph

    def get_minimal_size_black_species(self) :
        # Compute degrees for the subset of species nodes
        #species_nodes = [n for n,v in self.graph.nodes(data=True) if v['bipartite'] == 1] 
        black_species_nodes = self.species['black']
        species_degrees = {node: self.graph.degree(node) for node in black_species_nodes}
        species_degrees = dict( (n,deg) for n,deg in species_degrees.items() if deg > 0 )
        # Find the minimum degree
        min_degree = min(species_degrees.values())
    
        # Return all nodes with the minimum degree
        return [node for node, degree in species_degrees.items() if degree == min_degree]

    def compute_pi_U (self) :
        '''
        This function computes order pi_U of characters in intersection and universal according to the neighborhood in S^m_B 
        '''    
        min_black_neighbors = self.species['black']
        minimal_intersection = ''
        
         # Compute the minimum character in  intersection
        for character in  self.characters['intersection'] :
            character_black_neighbors= set(self.graph.neighbors(character)) & self.species['black']
            if len(character_black_neighbors) < len(min_black_neighbors) :
                minimal_intersection = character
                min_black_neighbors = character_black_neighbors
        #print(f'Minimal intersection: {minimal_intersection}')

        species_out_of_minimal = []
        # Compute order pi_U
        if self.characters['intersection'] :
            species_out_of_minimal = [(minimal_intersection, 0)]
            for character in self.characters['intersection'] | self.characters['universal'] :
                s = set(self.graph.neighbors(character)).intersection(set(self.species['black'])) -  min_black_neighbors
                if len(s) > 0 : 
                    species_out_of_minimal.append( (character,len(s)) )
        # Return the maximal character in the order
        #print(species_out_of_minimal)
        return [s[0] for s in sorted(species_out_of_minimal, key=lambda x: x[1], reverse=True)]
