from matplotlib.collections import LineCollection
import osmnx as ox
import networkx as nx
import time
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from snow_plows.opti import optimization
from math import *


def get_nearest_odd(G, point, odd_nodes):
    distances = { point: 0 }
    prev = { point: None }
    visited = set()

    queue = [(0, point)]

    while queue:
        current_dist, current_node = heapq.heappop(queue)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node in odd_nodes and current_node != point:
            path = []
            node = current_node
            while node is not None:
                path.append(node)
                node = prev[node]
            path.reverse()
            return current_node, current_dist, path
        for neighbor in G.neighbors(current_node):
            if neighbor not in visited:
                edge_weights = []
                for key, data in G[current_node][neighbor].items():
                    edge_weights.append(data['length'])
                if not edge_weights:
                    continue
                edge_weight = min(edge_weights)
                new_dist = current_dist + edge_weight

                if neighbor not in distances or new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        prev[neighbor] = current_node
                        heapq.heappush(queue, (new_dist, neighbor))

    return None, float('inf'), []



def fast_matching(G, odd_vertices):
    matching = []
    remaining = set(odd_vertices)
    
    while len(remaining) >= 2:
        u = remaining.pop()
        
        closest, dist, path = get_nearest_odd(G, u, remaining)
        #print(f"Sommet {u} le plus proche: {closest} à une distance de {dist:.2f} m")
        
        if closest is not None:
            remaining.remove(closest)
            matching.append((u, closest, path))
        else:
            raise ValueError("No odd vertex found to pair.")
    
    print(f"Pairing complete: {len(matching)} pairs")
    return matching

def chinese_postman(G):
    start_time = time.time()

    odd_vertices = [n for n in G.nodes() if G.degree(n) % 2 == 1]
    print(f"Number of odd-degree vertices: {len(odd_vertices):,}")
    matching = fast_matching(G, odd_vertices)

    edges_added = 0
    for u, v, path in matching:
        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]
            if G.has_edge(a, b):
                edge_data = G.get_edge_data(a, b)
                first_edge = next(iter(edge_data.values()))
                G.add_edge(a, b, **first_edge.copy())
                edges_added += 1
    
    print(f"Edges added: {edges_added}")
    
    odd_vertices_final = [n for n in G.nodes() if G.degree(n) % 2 == 1]
    print(f"Odd summits remaining: {len(odd_vertices_final)}")

    original_length = sum(data.get('length', 0) for _, _, data in G.edges(data=True))
    execution_time = time.time() - start_time
    
    return original_length, execution_time

def create_circuit(G, G_modifie):
    new_path = []
    path = list(nx.eulerian_path(G_modifie))
    visited_arcs =  set()
    for src, dest in path:
        if (G.has_edge(src, dest)):
            new_path.append((src,dest))
            visited_arcs.add((src,dest))
        else:
            subpath = nx.shortest_path(G, src, dest)
            tuples = [(subpath[i], subpath[i+1]) for i in range(len(subpath)-1)]
            new_path.extend(tuples)
            visited_arcs.update(tuples)
            if (dest, src) not in visited_arcs:
                visited_arcs.add((dest,src))
                new_path.append((dest,src))
                new_path.extend(tuples)
    return new_path

def creer_video_parcours(G, parcours, filename='parcours.mp4', fps=30, segments_per_frame=20):  
    print(f"Video creation for {len(parcours)} étapes...")
    
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    
    fig, ax = plt.subplots(figsize=(15, 12))
    
    node_x = [pos[node][0] for node in G.nodes() if node in pos]
    node_y = [pos[node][1] for node in G.nodes() if node in pos]
    ax.scatter(node_x, node_y, s=0.1, c='lightblue', alpha=0.3)
    
    all_segments = []
    for i in range(len(parcours) - 1):
        if parcours[i] in pos and parcours[i+1] in pos:
            segment = [(pos[parcours[i]][0], pos[parcours[i]][1]),
                      (pos[parcours[i+1]][0], pos[parcours[i+1]][1])]
            all_segments.append(segment)
    
    print(f"Calculated segments: {len(all_segments)}")
    
    lc = LineCollection([], colors='red', linewidths=1.5, alpha=0.8)
    ax.add_collection(lc)
    
    if node_x and node_y:
        ax.set_xlim(min(node_x), max(node_x))
        ax.set_ylim(min(node_y), max(node_y))
    ax.set_aspect('equal')
    ax.set_title('Snowplows routes - Montréal')
    
    
    total_frames = len(all_segments) // segments_per_frame + 1
    
    print(f"Configuration: {segments_per_frame} segments per frame")
    print(f"Total frames: {total_frames}")
    print(f"Estimated duration: {total_frames/fps:.1f} seconds")
    
    def animate(frame):
        end_idx = min((frame + 1) * segments_per_frame, len(all_segments))
        
        segments_to_show = all_segments[:end_idx]
        lc.set_segments(segments_to_show)
        ax.set_title(f'Snowplows routes - {end_idx:,}/{len(all_segments):,} segments')
        return [lc]
    
    ani = animation.FuncAnimation(fig, animate, frames=total_frames, 
                                 interval=1000//fps, blit=True, repeat=False)
    
    try:
        ani.save(filename, writer='ffmpeg', fps=fps, dpi=100, 
                 extra_args=['-vcodec', 'libx264'])
        print(f"MP4 saved: {filename}")
    except Exception as e:
        plt.show()
    
    plt.close()

def graph_cleaning(G):
    if G.number_of_nodes() == 0:
        return G.copy()
    
    G_modified = G.copy()
    
    isolated_nodes = list(nx.isolates(G_modified))
    if isolated_nodes:
        G_modified.remove_nodes_from(isolated_nodes)
    
    scc_components = list(nx.strongly_connected_components(G_modified))
    
    if len(scc_components) == 1:
        return G_modified
    
    largest_scc = max(scc_components, key=len)
    nodes_to_remove = []
    for component in scc_components:
        if component != largest_scc:
            nodes_to_remove.extend(list(component))
    
    G_modified.remove_nodes_from(nodes_to_remove)
    
    return G_modified

def main(sector, video=False, time_limit=2.0):
    print("====================================================")
    print(f"Loading {sector} graph...")

    G =ox.graph_from_place(f"{sector}, Montreal, Quebec, Canada", network_type='drive')
    G = graph_cleaning(G)
    print(f"Full graph: {len(G.nodes):,} nodes, {len(G.edges):,} edges")

    original = G.copy()

    if G.is_directed():
        G = G.to_undirected()
    
    if isinstance(G, nx.Graph):
        G = nx.MultiGraph(G)

    print(f"Full graph (undirected): {len(G.nodes):,} nodes, {len(G.edges):,} edges")

    total_length, solve_time = chinese_postman(G)

    parcours = create_circuit(original, G)
    parcours2 = [edge[0] for edge in parcours] + [parcours[-1][1]]

    if total_length is None:
        print("C PAS NORMAL CE TRUC, OSKOUR?")
        return
    
    opti_res = optimization(parcours, sector, time_limit, total_length)

    if video:
        creer_video_parcours(G, parcours2, segments_per_frame=1)

if __name__ == "__main__":
    result = main()