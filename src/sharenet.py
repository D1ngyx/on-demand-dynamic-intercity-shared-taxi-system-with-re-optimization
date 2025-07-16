import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
import pickle

CIRCLE_RADIUS = 1

class ShareNetwork:
    def __init__(self, total_node_numbers:int) -> None:
        self.share_network = [[] for _ in range(total_node_numbers)]
    
    def build_net(self, orders_list_, ):
        pass
    
    def calc_sg_degree(self, cur_orders_idx_, ):
        pass
    
    def save_graph(self, filename):
        # with open("share_network/" + filename, "wb") as f:
        with open(filename, "wb") as f:
            pickle.dump(self.share_network, f)

    def get_edge_nums(self):
        edge_num = 0
        for row in self.share_network:
            edge_num += len(row)
        return edge_num
    
    def visualize(self, filename):
        edge_num = 0
        adj_list = []
        for row in self.share_network:
            adj_list.append([tup[0] for tup in row])
            edge_num += len(row)

        """Distribute nodes evenly within a circle's area."""
        num_nodes = len(adj_list)
        positions = {}
        for i in range(num_nodes):
            r = np.sqrt(i / num_nodes) * CIRCLE_RADIUS  # Radius for this node (sqrt ensures even distribution in area)
            theta = np.pi * (3 - np.sqrt(5)) * i  # Golden angle in radians for even distribution
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            positions[i] = (x, y)

        """Create a network graph with a given number of nodes and adjacency list."""
        G = nx.Graph()
        for node, pos in positions.items():
            G.add_node(node, pos=pos)
        for idx, edges in enumerate(adj_list):
            for edge in edges:
                G.add_edge(idx, edge)

        """Draw"""
        pos = nx.get_node_attributes(G, 'pos')
        nx.draw(G, pos=pos, node_size=1, node_color='black', edge_color='red', with_labels=False, width=0.1)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.savefig(filename, dpi=300)
        plt.show()


""" Unit Test """
# total_node_numbers = 100
# share_network = ShareNetwork(total_node_numbers)
# # Generate random edges with weights
# for _ in range(200):  # You can adjust the number of edges as needed
#     u = random.randint(0, total_node_numbers - 1)
#     v = random.randint(0, total_node_numbers - 1)
#     w = random.randint(1, 50)  # Adjust the range of weights as needed
#     share_network.add_edge_from_u_to_v_with_weight(u, v, w)
# share_network.visualize()

# def even_circle_area_distribution(num_nodes, circle_radius=1):
#     """
#     Distribute nodes evenly within a circle's area.
#     """
#     positions = {}
#     for i in range(num_nodes):
#         r = np.sqrt(i / num_nodes) * CIRCLE_RADIUS  # Radius for this node (sqrt ensures even distribution in area)
#         theta = np.pi * (3 - np.sqrt(5)) * i  # Golden angle in radians for even distribution
#         x = r * np.cos(theta)
#         y = r * np.sin(theta)
#         positions[i] = (x, y)
#     return positions
#
# def create_network_graph(num_nodes, adj_list):
#     """
#     Create a network graph with a given number of nodes and adjacency list.
#     """
#     positions = even_circle_area_distribution(num_nodes)
#     G = nx.Graph()
#     for node, pos in positions.items():
#         G.add_node(node, pos=pos)
#     for idx, edges in enumerate(adj_list):
#         for edge in edges:
#             G.add_edge(idx, edge)
#     return G
#
# # Example usage
# num_nodes = 100  # Can be changed to 500, 1000, etc.
# adj_list=[[], [32, 35, 40, 46], [8, 88], [], [], [14], [], [], [2], [13], [], [], [], [9], [5], [16, 69], [15, 69], [], [38], [], [], [], [23], [22], [], [26], [25], [], [], [56], [], [51], [1, 35, 46, 85], [], [49], [1, 32, 46, 85], [], [], [18], [], [1], [], [64], [44], [43], [], [1, 32, 35, 85], [48], [47], [34], [], [31], [], [], [], [], [29], [65], [], [], [], [], [], [], [42], [57], [], [], [], [15, 16], [72, 73], [77], [70, 73], [70, 72], [75], [74], [78], [71], [76], [], [], [], [], [], [], [32, 35, 46], [88], [92], [2, 86], [91], [], [89], [87], [], [], [], [], [], [], []]
# # Create the graph
# G = create_network_graph(num_nodes, adj_list)
#
# # Draw the graph
# pos = nx.get_node_attributes(G, 'pos')
# nx.draw(G, pos=pos, node_size=10, node_color='black', edge_color='red', with_labels=False, width=0.2)
# plt.gca().set_aspect('equal', adjustable='box')
# plt.show()


