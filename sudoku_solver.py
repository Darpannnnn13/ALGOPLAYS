import time
import heapq

# --- Common Helper Functions ---
def is_valid(board, row, col, num):
    for x in range(9):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[i + start_row][j + start_col] == num:
                return False
    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

# --- DFS (Backtracking) Solver ---
def solve_sudoku_dfs(board):
    start_time = time.perf_counter()
    board_copy = [row[:] for row in board]
    solution_steps = []

    def solve():
        find = find_empty(board_copy)
        if not find:
            return True
        row, col = find

        for i in range(1, 10):
            if is_valid(board_copy, row, col, i):
                board_copy[row][col] = i
                solution_steps.append({"pos": (row, col), "val": i, "type": "place"})
                if solve():
                    return True
                board_copy[row][col] = 0
                solution_steps.append({"pos": (row, col), "val": 0, "type": "backtrack"})
        return False

    if solve():
        elapsed = time.perf_counter() - start_time
        return (board_copy, solution_steps, f"{elapsed:.12f}")
    else:
        elapsed = time.perf_counter() - start_time
        return (None, [], f"{elapsed:.12f}")

# --- A* Solver ---
def get_possible_values(board, row, col):
    if board[row][col] != 0:
        return []
    
    possible = []
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            possible.append(num)
    return possible

def find_empty_mrv(board):
    min_len = 10
    best_pos = None
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                possible = get_possible_values(board, r, c)
                if len(possible) < min_len:
                    min_len = len(possible)
                    best_pos = (r, c)
    return best_pos

def solve_sudoku_astar(board):
    start_time = time.perf_counter()
    
    start_board_tuple = tuple(map(tuple, board))
    g_score = 81 - sum(row.count(0) for row in board)
    h_score = 81 - g_score
    f_score = g_score + h_score
    
    open_list = [(f_score, g_score, start_board_tuple, [])]
    visited = {start_board_tuple}

    while open_list:
        _, g, current_board_tuple, steps = heapq.heappop(open_list)
        current_board = [list(row) for row in current_board_tuple]

        if g == 81:
            elapsed = time.perf_counter() - start_time
            return (current_board, steps, f"{elapsed:.12f}")

        pos = find_empty_mrv(current_board)
        if not pos:
            continue
        
        r, c = pos
        possible_values = get_possible_values(current_board, r, c)

        for val in possible_values:
            new_board = [row[:] for row in current_board]
            new_board[r][c] = val
            new_board_tuple = tuple(map(tuple, new_board))

            if new_board_tuple not in visited:
                new_g = g + 1
                new_h = 81 - new_g
                new_f = new_g + new_h
                
                new_steps = steps + [{"pos": (r, c), "val": val, "type": "place"}]
                heapq.heappush(open_list, (new_f, new_g, new_board_tuple, new_steps))
                visited.add(new_board_tuple)

    elapsed = time.perf_counter() - start_time
    return (None, [], f"{elapsed:.12f}")

# --- AC-3 (Constraint Propagation) + Backtracking Solver ---
def solve_sudoku_ac3(board):
    start_time = time.perf_counter()
    board_copy = [row[:] for row in board]
    solution_steps = []

    domains = {}
    for r in range(9):
        for c in range(9):
            if board_copy[r][c] == 0:
                domains[(r, c)] = list(range(1, 10))
            else:
                domains[(r, c)] = [board_copy[r][c]]

    def ac3():
        queue = []
        for r in range(9):
            for c in range(9):
                for c2 in range(9):
                    if c != c2: queue.append(((r, c), (r, c2)))
                for r2 in range(9):
                    if r != r2: queue.append(((r, c), (r2, c)))
                start_row, start_col = 3 * (r // 3), 3 * (c // 3)
                for i in range(3):
                    for j in range(3):
                        if (r, c) != (start_row + i, start_col + j):
                            queue.append(((r, c), (start_row + i, start_col + j)))
        
        while queue:
            (xi, xj) = queue.pop(0)
            if revise(xi, xj):
                if len(domains[xi]) == 0:
                    return False
                r, c = xi
                for c2 in range(9):
                    if c != c2: queue.append(((r, c2), xi))
                for r2 in range(9):
                    if r != r2: queue.append(((r2, c), xi))
                start_row, start_col = 3 * (r // 3), 3 * (c // 3)
                for i in range(3):
                    for j in range(3):
                        if (r, c) != (start_row + i, start_col + j):
                            queue.append(((start_row + i, start_col + j), xi))
        return True

    def revise(xi, xj):
        revised = False
        for x in domains[xi]:
            if len(domains[xj]) == 1 and x in domains[xj]:
                domains[xi].remove(x)
                revised = True
        return revised

    def solve_with_backtracking():
        find = find_empty(board_copy)
        if not find:
            return True
        row, col = find

        for value in domains[(row, col)]:
            if is_valid(board_copy, row, col, value):
                board_copy[row][col] = value
                solution_steps.append({"pos": (row, col), "val": value, "type": "place"})
                if solve_with_backtracking():
                    return True
                board_copy[row][col] = 0
                solution_steps.append({"pos": (row, col), "val": 0, "type": "backtrack"})
        return False

    if ac3() and solve_with_backtracking():
        elapsed = time.perf_counter() - start_time
        return (board_copy, solution_steps, f"{elapsed:.12f}")
    else:
        elapsed = time.perf_counter() - start_time
        return (None, [], f"{elapsed:.12f}")
