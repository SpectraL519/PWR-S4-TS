import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy



def random_intensity_matrix(v: int, max_intensity: int) -> np.array:
    M = np.random.rand(v, v)
    c = max_intensity // 2
    M = M * c + c
    np.fill_diagonal(M, 0)
    return M.astype(np.int32)


def get_combinations(A: list) -> np.array:
    return np.array(np.meshgrid(*A)).T.reshape(-1, len(A))


def capacity(edge_intensity: int, package_size: int, factor: int) -> int:
    return 1000 if not edge_intensity else factor * edge_intensity * package_size


def set_edge_intensities(graph: nx.Graph, intensity_matrix: np.array) -> nx.Graph:
    nx.set_edge_attributes(graph, 0, "a")
    combinations = get_combinations([graph.nodes, graph.nodes])
    for (start, end) in combinations:
        if start != end:
            path = nx.shortest_path(graph, start, end)
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                graph[u][v]['a'] += intensity_matrix[start][end]
    return graph


def set_edge_capacities(graph: nx.Graph, mean_package_size: int, factor: int = 3) -> nx.Graph:
    nx.set_edge_attributes(graph, 0, "c")
    for (u, v) in graph.edges:
        graph[u][v]['c'] = capacity(graph[u][v]['a'], mean_package_size, factor)
    return graph


def init_topology(intensity_file: str, mean_package_size: int) -> tuple[nx.Graph, np.array]:
    # Assign intensities
    intensity_matrix = np.loadtxt(intensity_file, delimiter=',').astype(np.int32)

    # Create graph topology
    V = intensity_matrix.shape[0]
    cycle_size = V // 2
    graph = nx.disjoint_union(nx.cycle_graph(cycle_size - 1), nx.cycle_graph(cycle_size + 1))
    connect_cycles = [(v, v + cycle_size) for v in range(cycle_size - 1)]
    graph.add_edges_from(connect_cycles)

    # Assign edge intensities and capacities
    graph = set_edge_intensities(graph, intensity_matrix)
    graph = set_edge_capacities(graph, mean_package_size)
    

    assert(np.all([]))

    return graph, intensity_matrix


def overview(graph: nx.Graph, show: bool = False) -> None:
    print(f"Topology overview\n \
    Number of nodes: {graph.number_of_nodes()}\n \
    Number of edges: {graph.number_of_edges()}\n \
    Is connected: {nx.is_connected(graph)}\n \
    Isolated nodes: {nx.number_of_isolates(graph)}\n \
    Capacity > intensity = {all([graph[u][v]['c'] > graph[u][v]['a'] for (u, v) in graph.edges if u != v])}")

    if show:
        plt.figure(figsize=(12, 9))
        pos = nx.spring_layout(graph)
        nx.draw_networkx(graph, pos=pos, with_labels=True)
        nx.draw_networkx_edge_labels(graph, pos=pos, font_color='red')
        plt.show();


def T(graph: nx.Graph, total_intensity: int, mean_package_size: int) -> float:
    a = np.array([graph[u][v]['a'] for (u, v) in graph.edges]) # edge intensities
    c = np.array([graph[u][v]['c'] for (u, v) in graph.edges]) # edge capacities

    if np.any(a >= c / mean_package_size):
        return None
    return np.sum(a / (c / mean_package_size - a)) / total_intensity


def reliability(
    graph: nx.Graph, 
    intensity_matrix: np.array, 
    T_max: float, 
    p: float, 
    mean_package_size: int, 
    trials: int = 1000, 
) -> dict:
    metrics = {
        'passed': 0,
        'incoherent': 0,
        'overload': 0,
        'delay': 0,
    }

    g = deepcopy(graph)
    set_edge_intensities(g, intensity_matrix)

    total_intensity = intensity_matrix.sum()
    t_baseline = T(g, total_intensity, mean_package_size)

    for _ in range(trials):
        trial_graph = deepcopy(g)
        damaged_edges = [e for e in trial_graph.edges if np.random.random() > p]

        if damaged_edges:
            trial_graph.remove_edges_from(damaged_edges)
            if not nx.is_connected(trial_graph):
                metrics['incoherent'] += 1
                continue

            set_edge_intensities(trial_graph, intensity_matrix)
            capacities = np.array([graph[u][v]['c'] for (u, v) in trial_graph.edges])
            intensities = np.array([trial_graph[u][v]['a'] for (u, v) in trial_graph.edges])

            if (np.any(intensities * mean_package_size > capacities)):
                metrics['overload'] += 1
                continue
        
            t = T(trial_graph, total_intensity, mean_package_size)
        else:
            t = t_baseline
        
        if not t or t > T_max:
            metrics['delay'] += 1
            continue

        metrics['passed'] += 1
    
    metrics = {key: value / trials for key, value in metrics.items()}
    return metrics

v_reliability = np.vectorize(reliability)


def plot_results(
    results: dict,
    figsize: tuple[int, int] = (12, 10),
    title: str = None,
    constants: str = None,
    x_label: str = None,
):
    plt.figure(figsize=figsize)

    r_df = pd.DataFrame.from_dict(results, orient='index')
    plt.stackplot(r_df.index, 
                  r_df.passed.values,
                  r_df.incoherent.values,
                  r_df.overload.values,
                  r_df.delay.values,
                  labels=['passed trials', 'incoherent', 'overload', 'delay'],
                  colors=['g', 'r', 'b', 'y'])
    
    plt.title(f"{title}\n{constants}")
    plt.legend(loc='lower right')
    plt.xlabel(x_label)
    plt.xticks(r_df.index)
    plt.show();