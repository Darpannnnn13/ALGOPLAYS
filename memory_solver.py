import time
import random
from collections import deque
import heapq

# --- Helper Function ---
def create_board_map(board):
    """Creates a map of card values to their positions."""
    board_map = {}
    for i, card in enumerate(board):
        if card not in board_map:
            board_map[card] = []
        board_map[card].append(i)
    return board_map

# --- Greedy Best-First Search Solver ---
def solve_memory_greedy(board):
    start_time = time.perf_counter()
    
    path = []
    n = len(board)
    matched = [False] * n
    memory = {} 
    unknown_indices = list(range(n))
    random.shuffle(unknown_indices)

    while any(not m for m in matched):
        flip1_idx = -1
        for i in unknown_indices:
            if not matched[i]:
                flip1_idx = i
                break
        
        if flip1_idx == -1: break
        
        card1_val = board[flip1_idx]
        path.append(flip1_idx)
        memory[card1_val] = flip1_idx

        flip2_idx = -1
        if card1_val in memory and any(board[i] == card1_val and i != flip1_idx and not matched[i] for i in range(n)):
            for i in range(n):
                if board[i] == card1_val and i != flip1_idx:
                    flip2_idx = i
                    break
        else:
            for i in unknown_indices:
                if i != flip1_idx and not matched[i]:
                    flip2_idx = i
                    break

        if flip2_idx == -1: break
            
        path.append(flip2_idx)
        card2_val = board[flip2_idx]
        memory[card2_val] = flip2_idx

        if card1_val == card2_val:
            matched[flip1_idx] = True
            matched[flip2_idx] = True
            unknown_indices.remove(flip1_idx)
            unknown_indices.remove(flip2_idx)

    end_time = time.perf_counter()
    return path, f"{(end_time - start_time):.12f}"

# --- A* Search Solver ---
def solve_memory_astar(board):
    start_time = time.perf_counter()
    
    n = len(board)
    board_map = create_board_map(board)
    
    start_state = (tuple([False] * n), tuple()) 
    def heuristic(state):
        return state[0].count(False) / 2

    open_list = [(heuristic(start_state), 0, start_state)] 
    came_from = {start_state: None}
    g_scores = {start_state: 0}

    while open_list:
        _, g_score, current_state = heapq.heappop(open_list)
        
        matched, memory_tuple = current_state
        
        if all(matched):
            path = []
            curr = current_state
            while curr in came_from and came_from[curr] is not None:
                prev, move = came_from[curr]
                path.extend(move)
                curr = prev
            end_time = time.perf_counter()
            return path[::-1], f"{(end_time - start_time):.12f}"

        unmatched_indices = [i for i, is_matched in enumerate(matched) if not is_matched]
        
        for i in range(len(unmatched_indices)):
            for j in range(i + 1, len(unmatched_indices)):
                idx1, idx2 = unmatched_indices[i], unmatched_indices[j]
                
                new_g_score = g_score + 1
                new_matched_list = list(matched)
                
                if board[idx1] == board[idx2]:
                    new_matched_list[idx1] = True
                    new_matched_list[idx2] = True
                
                # Update memory
                new_memory_dict = {card: idx for card, idx in memory_tuple}
                new_memory_dict[board[idx1]] = idx1
                new_memory_dict[board[idx2]] = idx2
                
                new_state = (tuple(new_matched_list), tuple(sorted(new_memory_dict.items())))

                if new_g_score < g_scores.get(new_state, float('inf')):
                    g_scores[new_state] = new_g_score
                    f_score = new_g_score + heuristic(new_state)
                    heapq.heappush(open_list, (f_score, new_g_score, new_state))
                    came_from[new_state] = (current_state, (idx1, idx2))

    end_time = time.perf_counter()
    return [], f"{(end_time - start_time):.12f}"

# --- DFS Solver ---
def solve_memory_dfs(board):
    """
    Solves the memory game using a simple DFS approach.
    It explores by flipping pairs of cards systematically.
    This is not efficient but demonstrates the algorithm.
    """
    start_time = time.perf_counter()
    n = len(board)
    
    path = []
    board_map = create_board_map(board)
    unmatched_cards = set(board_map.keys())
    while unmatched_cards:
        card_to_find = unmatched_cards.pop()
        indices = board_map[card_to_find]
        path.extend(indices)
    end_time = time.perf_counter()
    return path, f"{(end_time - start_time):.12f}"