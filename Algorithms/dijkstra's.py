import heapq
from Algorithms.a_star import find_neighbors, build_path


def dijkstra(graph, start, goal):
    node_position = graph['nodes']
    edges_list = graph['edges']
    
    visit_order = 0
    priority_queue = [(0, visit_order, start)]
    visit_order += 1
    
    came_from = {}
    
    g_score = {start: 0}
    
    explored_nodes = []
    visited = set()
    
    while priority_queue:
        _, _, current = heapq.heappop(priority_queue)
        
        if current not in visited:
            explored_nodes.append(current)
            visited.add(current)
        
        if current == goal:
            path = build_path(came_from, current)
            return {
                'path': path,
                'cost': g_score[current],
                'nodes_explored': len(explored_nodes),
                'all_explored': explored_nodes,
                'success': True
            }
        
        neighbors = find_neighbors(current, edges_list)
        
        for neighbor_info in neighbors:
            neighbor = neighbor_info['node']
            edge_cost = neighbor_info['cost']
            
            new_cost = g_score[current] + edge_cost
            
            if neighbor not in g_score or new_cost < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = new_cost
                
                heapq.heappush(priority_queue, (new_cost, visit_order, neighbor))
                visit_order += 1
    
    return {
        'path': [],
        'cost': float('inf'),
        'nodes_explored': len(explored_nodes),
        'all_explored': explored_nodes,
        'success': False
    }