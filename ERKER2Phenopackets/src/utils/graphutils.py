from typing import Dict, List, Union

import networkx as nx
import pygraphviz as pgv
from matplotlib import pyplot as plt

from ERKER2Phenopackets.src.decorators import deprecated
from ERKER2Phenopackets.src.utils.polars_utils import imageplot


def linear_layout(G: nx.Graph) -> Dict:
    """Creates a linear layout for a graph.

    Layout is created by assigning each node a position on the x-axis in the order of
    ascending node index.

    :param G: a networkx graph
    :type G: nx.Graph
    :return: a dictionary with node positions (pos[node] = (x, y))
    :rtype: Dict
    """
    nodes_list = list(G.nodes())
    pos = {node: (index, 0) for index, node in enumerate(nodes_list)}
    return pos


def create_graph(vertex_labels, edge_labels, adjacency_list, directed=False) -> (
        nx.Graph):
    """Creates a networkx graph from vertex labels, edge labels and an adjacency list.

    vertex_labels is a list of strings
    edge_labels is a list of lists of strings where the edge between vertex i and
    vertex j is edge_labels[i][j]
    adjacency_list is a list of lists of integers where the adjacency list of vertex
    i is adjacency_list[i] and contains the indices of the adjacent vertices

    :param vertex_labels: a list of strings
    :type vertex_labels: List[str]
    :param edge_labels: a list of lists of strings
    :type edge_labels: List[List[str]]
    :param adjacency_list: a list of lists of integers
    :type adjacency_list: List[List[int]]
    :return: a new networkx graph
    :rtype: nx.Graph
    """
    G = nx.Graph()
    if directed:
        G = nx.DiGraph()

    for i, vl in enumerate(vertex_labels):
        G.add_node(i, label=vl)

    for i, al in enumerate(adjacency_list):
        for k, j in enumerate(al):
            G.add_edge(i, j, label=edge_labels[i][k])

    return G


@deprecated("Use pygraphviz plot instead")
def nx_graphplot(vertex_labels, edge_labels, adjacency_list):
    G = create_graph(vertex_labels, edge_labels, adjacency_list)

    pos = nx.planar_layout(G)

    # Create a mapping for node labels without numbers
    node_labels = {node: label['label'] for node, label in G.nodes(data=True)}

    # Draw the graph without node labels
    nx.draw(G, pos, with_labels=False, node_color='skyblue', node_size=800,
            font_weight='bold', font_size=12)

    # Draw node labels without numbers
    nx.draw_networkx_labels(G, pos, labels=node_labels)

    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title('Graph Visualization with Labels (No Node Numbers)')
    plt.show()
    return G


def graphplot(
        G: nx.Graph,
        file_path: str,
        return_pgv_graph: bool=False,
        layout_prog: str="dot",
        orientation: str="TB",
        file_format: str="png",
        figsize=None
) -> Union[None, pgv.AGraph]:
    """Plots a networkx graph with pygraphviz.

    :param G: The networkx graph to plot.
    :type G: nx.Graph
    :param file_path: The path to save the graph to.
    :type file_path: str
    :param return_pgv_graph: Whether to return the pygraphviz graph object.
    :type return_pgv_graph: bool
    :param layout_prog: The layout program to use, defaults to "dot".
    :type layout_prog: str
    :param orientation: The orientation of the graph, options: "TB" or "LR", defaults to
    "TD".
    :param file_format: The file format to save the graph to, defaults to "png".
    :type file_format: str
    :param figsize: The size of the figure, defaults to None.
    :type figsize: Union[None, Tuple[int, int]]
    :return: The pygraphviz graph object if return_pgv_graph is True.
    :rtype: Union[None, pygraphviz.AGraph]
    """
    G_pg = pgv.AGraph(strict=False, directed=True)

    for node, attr in G.nodes(data=True):
        G_pg.add_node(node, label=attr.get("label", str(node)))

    for edge in G.edges(data=True):
        src, dest, attr = edge
        G_pg.add_edge(src, dest, label=attr.get("label", ""))

    G_pg.graph_attr["rankdir"] = orientation

    G_pg.layout(prog=layout_prog)

    if file_path is not None:
        G_pg.draw(file_path, format=file_format)
    else:
        raise AttributeError("file_path must not be None")

    imageplot(file_path, figsize=figsize)

    if return_pgv_graph:
        return G_pg

