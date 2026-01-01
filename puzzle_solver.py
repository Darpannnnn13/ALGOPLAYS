import time
import heapq
from collections import deque
from math import sqrt

def get_neighbors(state):
    size = int(sqrt(len(state)))
    zero_index = state.index(0)
    x, y = zero_index % size, zero_index // size
    neighbors = []
    
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            new_state = list(state)
            new_index = ny * size + nx
            new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
            neighbors.append(tuple(new_state))
            
    return neighbors

def manhattan_distance(state):
    size = int(sqrt(len(state)))
    distance = 0
    for i, num in enumerate(state):
        if num != 0:
            goal_x, goal_y = (num - 1) % size, (num - 1) // size
            current_x, current_y = i % size, i // size
            distance += abs(goal_x - current_x) + abs(goal_y - current_y)
    return distance

def solve_puzzle_astar(initial_state):
    start_time = time.perf_counter()
    
    goal_state = tuple(list(range(1, len(initial_state))) + [0])
    
    open_list = [(manhattan_distance(initial_state), initial_state, [initial_state])]
    visited = {tuple(initial_state)}
    
    while open_list:
        _, current_state, path = heapq.heappop(open_list)
        
        if tuple(current_state) == goal_state:
            elapsed = time.perf_counter() - start_time
            return (path, f"{elapsed:.10f}")
            
        for neighbor in get_neighbors(current_state):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [list(neighbor)]
                priority = len(new_path) - 1 + manhattan_distance(neighbor)
                heapq.heappush(open_list, (priority, list(neighbor), new_path))
    elapsed = time.perf_counter() - start_time
    return (None, f"{elapsed:.10f}")

def solve_puzzle_bfs(initial_state):
    start_time = time.perf_counter()
    
    goal_state = tuple(list(range(1, len(initial_state))) + [0])
    
    queue = deque([(initial_state, [initial_state])])
    visited = {tuple(initial_state)}
    
    while queue:
        current_state_list, path = queue.popleft()
        
        if tuple(current_state_list) == goal_state:
            elapsed = time.perf_counter() - start_time
            return (path, f"{elapsed:.10f}")
            
        for neighbor in get_neighbors(current_state_list):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((list(neighbor), path + [list(neighbor)]))

    elapsed = time.perf_counter() - start_time
    return (None, f"{elapsed:.10f}")

def solve_puzzle_iddfs(initial_state):
    start_time = time.perf_counter()
    size = int(sqrt(len(initial_state)))
    goal_state = tuple(list(range(1, size*size)) + [0])
    
    def dls(path, depth_limit):
        current_state = tuple(path[-1])
        if current_state == goal_state:
            return path
        if len(path) > depth_limit:
            return None
        for neighbor in get_neighbors(list(current_state)):
            if tuple(neighbor) not in [tuple(p) for p in path]:
                new_path = path + [list(neighbor)]
                result = dls(new_path, depth_limit)
                if result is not None:
                    return result
        return None

    for depth in range(35):
        result_path = dls([initial_state], depth)
        if result_path:
            elapsed = time.perf_counter() - start_time
            return (result_path, f"{elapsed:.10f}")
            
    elapsed = time.perf_counter() - start_time
    return (None, f"{elapsed:.10f}")
