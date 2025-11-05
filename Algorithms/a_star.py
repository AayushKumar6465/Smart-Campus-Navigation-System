import heapq
from Algorithms.heuristics import euclidean_distance, manhattan_distance


def find_neighbors(current_node, edges_list):
    neighbors = []
    for edge in edges_list:
        if edge['from'] == current_node:
            neighbors.append({'node': edge['to'], 'cost': edge['distance']})
        elif edge['to'] == current_node:
            neighbors.append({'node': edge['from'], 'cost': edge['distance']})
    return neighbors


def build_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]  


def a_star_search(graph_data, start_node, goal_node, heuristic = euclidean_distance):
    node_position = graph_data['nodes']
    edge_list = graph_data['edges']

    visit_order = 0
    priority_queue = [(0, visit_order, start_node)]
    visit_order += 1

    came_from = {}

    g_score = {start_node: 0}

    f_score = {start_node: heuristic(start_node, goal_node, node_position)}

    explored_nodes = []
    visited = set()

    while priority_queue:
        _, _, current_node = heapq.heappop(priority_queue)

        if current_node not in visited:
            explored_nodes.append(current_node)
            visited.add(current_node)

        if current_node == goal_node:
            path = build_path(came_from, current_node)
            return {
                'path': path,
                'cost': g_score[current_node],
                'nodes_explored': len(explored_nodes),
                'all_explored': explored_nodes,
                'success': True
            }
        
        for neighbor_info in find_neighbors(current_node, edge_list):
            neighbor_node = neighbor_info['node']
            edge_cost = neighbor_info['cost']

            new_cost = g_score[current_node] + edge_cost

            if neighbor_node not in g_score or new_cost < g_score[neighbor_node]:
                came_from[neighbor_node] = current_node
                g_score[neighbor_node] = new_cost

                f = new_cost + heuristic(neighbor_node, goal_node, node_position)
                f_score[neighbor_node] = f

                heapq.heappush(priority_queue, (f, visit_order, neighbor_node))
                visit_order += 1

    return {
        'path': [],
        'cost': float('inf'),
        'nodes_explored': len(explored_nodes),
        'all_explored': explored_nodes,
        'success': False
    }