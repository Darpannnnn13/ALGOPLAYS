from collections import deque
import heapq
import time

def dfs_solver(maze):
    rows, cols = len(maze), len(maze[0])
    visited = set()
    path = []
    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols) or maze[r][c] == 1 or (r, c) in visited:
            return False
        visited.add((r, c))
        path.append([r, c])
        if r == rows - 1 and c == cols - 1:
            return True
        if dfs(r + 1, c) or dfs(r, c + 1) or dfs(r - 1, c) or dfs(r, c - 1):
            return True
        path.pop()
        return False
    dfs(0, 0)
    return path

def bfs_solver(maze):
    rows, cols = len(maze), len(maze[0])
    queue = deque([(0, 0, [[0, 0]])])
    visited = set([(0, 0)])
    while queue:
        r, c, path = queue.popleft()
        if r == rows - 1 and c == cols - 1:
            return path
        for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited and maze[nr][nc] == 0:
                visited.add((nr, nc))
                queue.append((nr, nc, path + [[nr, nc]]))
    return []

def astar_solver(maze):
    rows, cols = len(maze), len(maze[0])
    start_node, end_node = (0, 0), (rows - 1, cols - 1)
    def heuristic(node):
        return abs(node[0] - end_node[0]) + abs(node[1] - end_node[1])
    open_list = [(heuristic(start_node), start_node)]
    came_from, g_score = {}, {start_node: 0}
    while open_list:
        _, current = heapq.heappop(open_list)
        if current == end_node:
            path = []
            while current in came_from:
                path.append(list(current))
                current = came_from[current]
            path.append(list(start_node))
            return path[::-1]
        for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            neighbor = (current[0] + dr, current[1] + dc)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and maze[neighbor[0]][neighbor[1]] == 0:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor], g_score[neighbor] = current, tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor)
                    heapq.heappush(open_list, (f_score, neighbor))
    return []

def greedy_solver(maze):
    rows, cols = len(maze), len(maze[0])
    start_node, end_node = (0, 0), (rows - 1, cols - 1)
    
    def heuristic(node):
        return abs(node[0] - end_node[0]) + abs(node[1] - end_node[1])

    open_list = [(heuristic(start_node), start_node)]
    came_from = {start_node: None}
    visited = {start_node}

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == end_node:
            path = []
            while current is not None:
                path.append(list(current))
                current = came_from[current]
            return path[::-1]

        for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            neighbor = (current[0] + dr, current[1] + dc)

            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and maze[neighbor[0]][neighbor[1]] == 0 and neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                heapq.heappush(open_list, (heuristic(neighbor), neighbor))
    
    return []
