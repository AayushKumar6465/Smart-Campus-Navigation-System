import math

def euclidean_distance(node1, node2, nodes):
    x1, y1 = nodes[node1]["x"], nodes[node1]["y"]
    x2, y2 = nodes[node2]["x"], nodes[node2]["y"]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def manhattan_distance(node1, node2, nodes):
    x1, y1 = nodes[node1]["x"], nodes[node1]["y"]
    x2, y2 = nodes[node2]["x"], nodes[node2]["y"]
    return abs(x1 - x2) + abs(y1 - y2)
