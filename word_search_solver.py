import time

# --- Simple Backtracking/DFS Solver ---
def solve_word_search_simple(grid, words):
    """
    Finds all words in the grid using a simple search algorithm.
    This is effectively a backtracking/DFS approach.
    """
    start_time = time.perf_counter()
    found_words = {}
    rows, cols = len(grid), len(grid[0])
    word_set = set(words)

    for word in word_set:
        if word in found_words:
            continue
        for r in range(rows):
            for c in range(cols):
                # Search in all 8 directions from (r, c)
                for dr, dc in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                    path = []
                    match = True
                    for i in range(len(word)):
                        nr, nc = r + i * dr, c + i * dc
                        if not (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == word[i]):
                            match = False
                            break
                        path.append((nr, nc))
                    
                    if match:
                        found_words[word] = path
                        break # Move to the next word
            if word in found_words:
                break # Move to the next word
    
    elapsed = time.perf_counter() - start_time
    return (found_words, f"{elapsed:.12f}")
# --- Advanced Trie-based Solver (Corrected) ---
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.word = None

def build_trie(words):
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.word = word
    return root

def solve_word_search_trie(grid, words):
    """
    Finds all words using a more efficient and corrected Trie-based search.
    """
    start_time = time.perf_counter()
    root = build_trie(words)
    found_words = {}
    rows, cols = len(grid), len(grid[0])
    word_set = set(words)

    def _search_in_direction(r, c, dr, dc, node, path):
        """Searches recursively in a single direction."""
        # Boundary check
        if not (0 <= r < rows and 0 <= c < cols):
            return

        char = grid[r][c]
        if char not in node.children:
            return

        # Move to the next node in the trie
        node = node.children[char]
        new_path = path + [(r, c)]

        if node.is_end_of_word:
            # Use setdefault to store the first path found for a word
            found_words.setdefault(node.word, new_path)

        # Continue searching in the same direction
        _search_in_direction(r + dr, c + dc, dr, dc, node, new_path)


    # Main loop to start the search from every cell
    for r in range(rows):
        # Early exit if all words are found
        if len(found_words) == len(word_set):
            break
        for c in range(cols):
            if len(found_words) == len(word_set):
                break
            # From each cell (r, c), start a new search in all 8 directions
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                _search_in_direction(r, c, dr, dc, root, [])

    elapsed = time.perf_counter() - start_time
    return (found_words, f"{elapsed:.12f}")