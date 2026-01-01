import time
from collections import deque
import heapq

COORDS = {i: (i // 3, i % 3) for i in range(9)}

def get_neighbors(dot):
    r, c = COORDS[dot]
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                neighbor_dot = nr * 3 + nc
                neighbors.append(neighbor_dot)
    return neighbors

def manhattan_distance(dot1, dot2):
    r1, c1 = COORDS[dot1]
    r2, c2 = COORDS[dot2]
    return abs(r1 - r2) + abs(c1 - c2)

# --- AI Solvers ---

def solve_pattern_lock_bfs(target_pattern):
    start_time = time.perf_counter()
    start_node = [target_pattern[0]]
    queue = deque([start_node])
    visited = {tuple(start_node)}

    while queue:
        path = queue.popleft()

        if path == target_pattern:
            end_time = time.perf_counter()
            return path, (end_time - start_time)

        if len(path) >= len(target_pattern):
            continue

        last_dot = path[-1]
        for neighbor in get_neighbors(last_dot):
            if neighbor not in path:
                new_path = path + [neighbor]
                if tuple(new_path) not in visited and tuple(target_pattern)[:len(new_path)] == tuple(new_path):
                    visited.add(tuple(new_path))
                    queue.append(new_path)
    end_time = time.perf_counter()
    return [], (end_time - start_time)

def solve_pattern_lock_dfs(target_pattern):
    start_time = time.perf_counter()
    start_node = [target_pattern[0]]
    stack = [start_node]
    visited = {tuple(start_node)}

    while stack:
        path = stack.pop()

        if path == target_pattern:
            end_time = time.perf_counter()
            return path, (end_time - start_time)

        if len(path) >= len(target_pattern):
            continue

        last_dot = path[-1]
        for neighbor in reversed(get_neighbors(last_dot)):
            if neighbor not in path:
                new_path = path + [neighbor]
                if tuple(new_path) not in visited and tuple(target_pattern)[:len(new_path)] == tuple(new_path):
                    visited.add(tuple(new_path))
                    stack.append(new_path)
    end_time = time.perf_counter()
    return [], (end_time - start_time)

def solve_pattern_lock_astar(target_pattern):
    """Solves the pattern lock using A* Search."""
    start_time = time.perf_counter()
    start_node = [target_pattern[0]]
    
    def heuristic(path):
        return len(target_pattern) - len(path)

    open_list = [(heuristic(start_node), 0, start_node)]
    g_scores = {tuple(start_node): 0}

    while open_list:
        _, g_score, path = heapq.heappop(open_list)

        if path == target_pattern:
            end_time = time.perf_counter()
            return path, (end_time - start_time)

        last_dot = path[-1]
        for neighbor in get_neighbors(last_dot):
            if neighbor not in path:
                new_path = path + [neighbor]
                new_g_score = g_score + 1
                
                if tuple(target_pattern)[:len(new_path)] == tuple(new_path) and new_g_score < g_scores.get(tuple(new_path), float('inf')):
                    g_scores[tuple(new_path)] = new_g_score
                    f_score = new_g_score + heuristic(new_path)
                    heapq.heappush(open_list, (f_score, new_g_score, new_path))
                    
    end_time = time.perf_counter()
    return [], (end_time - start_time)

def solve_pattern_lock_greedy(target_pattern):
    """Solves the pattern lock using Greedy Best-First Search."""
    start_time = time.perf_counter()
    start_node = [target_pattern[0]]

    def heuristic(path):
        """Heuristic: Manhattan distance to the next correct dot in the sequence."""
        if len(path) >= len(target_pattern):
            return 0
        
        last_dot = path[-1]
        next_target_dot = target_pattern[len(path)]
        return manhattan_distance(last_dot, next_target_dot)

    open_list = [(heuristic(start_node), start_node)]
    visited = {tuple(start_node)}

    while open_list:
        _, path = heapq.heappop(open_list)

        if path == target_pattern:
            end_time = time.perf_counter()
            return path, (end_time - start_time)

        if len(path) >= len(target_pattern):
            continue

        last_dot = path[-1]
        for neighbor in get_neighbors(last_dot):
            if neighbor not in path:
                new_path = path + [neighbor]
                if tuple(new_path) not in visited and tuple(target_pattern)[:len(new_path)] == tuple(new_path):
                    visited.add(tuple(new_path))
                    h_score = heuristic(new_path)
                    heapq.heappush(open_list, (h_score, new_path))

    end_time = time.perf_counter()
    return [], (end_time - start_time)
