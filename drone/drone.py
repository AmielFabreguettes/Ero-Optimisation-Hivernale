from matplotlib.collections import LineCollection
import osmnx as ox
import networkx as nx
import time
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from math import *

def get_nearest_odd(G, point, odd_nodes):
    distances = { point: 0 }
    prev = { point: None }
    visited = set()

    queue = [(0, point)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

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
            return current_node, current_distance, path
        for neighbor in G.neighbors(current_node):
            if neighbor not in visited:
                edge_weights = []
                for key, data in G[current_node][neighbor].items():
                    edge_weights.append(data['length'])
                if not edge_weights:
                    continue
                edge_weight = min(edge_weights)
                new_dist = current_distance + edge_weight

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
        
        remaining.remove(closest)
        matching.append((u, closest, path))
    
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

def creer_video_parcours(G, parcours, filename='parcours.mp4', fps=30, segments_per_frame=20):  
    print(f"Video creation for {len(parcours)} steps...")
    
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
    ax.set_title('Drone route - Montréal')
    
    total_frames = len(all_segments) // segments_per_frame + 1
    
    print(f"Configuration: {segments_per_frame} segments per frame")
    print(f"Total frames: {total_frames}")
    print(f"Estimated duration: {total_frames/fps:.1f} seconds")
    
    def animate(frame):
        end_idx = min((frame + 1) * segments_per_frame, len(all_segments))
        
        segments_to_show = all_segments[:end_idx]
        lc.set_segments(segments_to_show)
        ax.set_title(f'Drone route - {end_idx:,}/{len(all_segments):,} segments')
        return [lc]
    
    ani = animation.FuncAnimation(fig, animate, frames=total_frames, 
                                 interval=1000//fps, blit=True, repeat=False)
    
    try:
        ani.save(filename, writer='ffmpeg', fps=fps, dpi=100, extra_args=['-vcodec', 'libx264'])
        print(f"MP4 saved: {filename}")
    except Exception as e: #Afficher la vidéo si la sauvegarde échoue
        plt.show()
    
    plt.close()

def calculate_drone_costs(distance):
    daily_cost = 100
    cost_per_km = 0.01
    drone_speed_kmh = 60 #Arbitraire car non précisé dans le sujet
    
    distance_km = distance / 1000
    flight_cost = distance_km * cost_per_km
    flight_time_hours = distance_km / drone_speed_kmh
    nb_days = ceil(flight_time_hours/24)
    cost = daily_cost * nb_days
    total = cost + flight_cost

    return distance_km, cost, flight_cost, total, flight_time_hours

def main(video=False):
    print("====================================================")
    print("Loading Montréal graph...")

    G = ox.load_graphml("drone/montreal.graphml")
    print(f"Full graph: {len(G.nodes):,} nodes, {len(G.edges):,} edges")

    G = G.to_undirected()
    G = nx.MultiGraph(G)

    print(f"Full graph (undirected): {len(G.nodes):,} nodes, {len(G.edges):,} edges")

    total_length, solve_time = chinese_postman(G)
    dist, cost, distcost, total, hours = calculate_drone_costs(total_length)
    
    print("====================================================")
    print(" DISTANCE RESULTS AND DRONE COSTS")
    print(f" Total drone distance: {dist:.2f} km ")
    print(f" Estimated flight time: {hours:.2f} heures \n")
    print(f" Drone cost: {cost:.2f} €")
    print(f" Drone route cost: {distcost:.2f} €")
    print(f" TOTAL COST: {total:.2f} €")
    print(f" Resolution time: {solve_time:.2f} seconds")

    if video:
        circuit_eulérien = list(nx.eulerian_circuit(G))
        parcours = [edge[0] for edge in circuit_eulérien] + [circuit_eulérien[-1][1]]
        creer_video_parcours(G, parcours, segments_per_frame=100)

if __name__ == "__main__":
    result = main()