
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import time
import re
import random
from flask_session import Session
from math import sqrt
from collections import Counter

# Solver Imports
from number_guessing_solver import solve_number_guessing
from maze_solver import dfs_solver, bfs_solver, astar_solver, greedy_solver
from puzzle_solver import solve_puzzle_astar, solve_puzzle_bfs, solve_puzzle_iddfs
from sudoku_solver import solve_sudoku_dfs, solve_sudoku_astar, solve_sudoku_ac3
from word_search_solver import solve_word_search_simple, solve_word_search_trie
from memory_solver import solve_memory_dfs, solve_memory_astar, solve_memory_greedy
from pattern_lock_solver import solve_pattern_lock_dfs, solve_pattern_lock_bfs, solve_pattern_lock_astar, solve_pattern_lock_greedy

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# NOTE: route for /ai_animation kept later in the file (avoid duplicates)
ADMIN_EMAIL = "admin@college.com"
ADMIN_PASSWORD = "admin123"

# --- FILE PATH CONSTANTS ---
PROGRESS_FILE = "user_progress.json"
USERS_FILE = "users.json"
EXPLANATIONS_FILE = "explanations.json"

CONFIG_FILE = "game_config.json"
GAME_LEVEL_FILES = {
    "maze": "data/maze_levels.json",
    "puzzle": "data/puzzle_levels.json",
    "sudoku": "data/sudoku_levels.json",
    "word_search": "data/word_search_levels.json",
    "number_guessing": "data/number_guessing_levels.json",
    "math_quiz": "data/math_quiz_levels.json",
    "memory": "data/memory_levels.json",
    "hangman": "data/hangman_levels.json",
    "pattern_lock": "data/pattern_lock_levels.json"
}

GAME_NAMES = {
    "maze": "Maze Solver", "puzzle": "Puzzle-8 Solver", "sudoku": "Sudoku",
    "word_search": "Word Search", "number_guessing": "Number Guessing",
    "memory": "Memory Flip", "math_quiz": "Math Quiz",
    "hangman": "Hangman", "pattern_lock": "Pattern Lock"
}

# --- UTILITY FUNCTIONS ---
def load_json(file_path):
    if not os.path.exists(file_path): return {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return {}

def save_json(data, file_path):
    with open(file_path, "w", encoding='utf-8') as f: json.dump(data, f, indent=2)

def get_user_details():
    users = load_json(USERS_FILE)
    return {user['email']: user for user in users} if isinstance(users, list) else {}

def update_user_level(email, level_key, **kwargs):
    progress = load_json(PROGRESS_FILE)
    user_data = progress.get(email, {})
    level_data = user_data.get(level_key, {})
    level_data.update(kwargs)
    user_data[level_key] = level_data
    progress[email] = user_data
    save_json(progress, PROGRESS_FILE)

@app.route("/admin/user/<email>")
def admin_user_details(email):
    user = session.get("user")
    if not user or user["email"] != ADMIN_EMAIL: return redirect(url_for("login"))

    all_users = load_json(USERS_FILE)
    target_user = next((u for u in all_users if u['email'] == email), None)
    if not target_user: return "User not found", 404

    progress = load_json(PROGRESS_FILE).get(email, {})    
    progress_details = []
    for level_key, data in progress.items():
        try:
            game, diff, level = re.match(r"([a-z_]+)_(\w+)-(\d+)", level_key).groups()
            progress_details.append({
                "game": GAME_NAMES.get(game, game.replace('_', ' ').title()),
                "level": f"{diff.title()} {level}", "data": data})
        except (AttributeError, IndexError, ValueError): continue

    return render_template("admin_user_details.html", target_user=target_user, progress_details=progress_details)

# --- ADMIN ROUTES ---
@app.route("/admin_dashboard")
def admin_dashboard():
    user = session.get("user")
    if not user or user["email"] != ADMIN_EMAIL: return redirect(url_for("login"))
    
    users, progress = load_json(USERS_FILE), load_json(PROGRESS_FILE)
    
    # Add games_played count to each user
    for u in users:
        user_progress = progress.get(u['email'], {})
        u['games_played'] = len(user_progress)
        u['progress_details'] = []
        for level_key, data in user_progress.items():
            try:
                game, diff, level = re.match(r"([a-z_]+)_(\w+)-(\d+)", level_key).groups()
                u['progress_details'].append({
                    "key": level_key, "game": GAME_NAMES.get(game, game.replace('_', ' ').title()),
                    "level": f"{diff.title()} {level}"})
            except (AttributeError, IndexError, ValueError): continue

    game_counts, total_plays = Counter(), 0
    for user_progress in progress.values():
        total_plays += len(user_progress)
        for level_key in user_progress:
            match = re.match(r"([a-z_]+)_(\w+)-(\d+)", level_key)
            if match: game_counts[match.groups()[0]] += 1


    most_played_key = game_counts.most_common(1)[0][0] if game_counts else "N/A"
    stats = {
        "total_users": len(users), "total_plays": total_plays,
        "most_played_game": GAME_NAMES.get(most_played_key, "N/A"),
        "game_popularity": {GAME_NAMES.get(k, k): v for k, v in game_counts.items()}
    }
    return render_template("admin.html", user=user, stats=stats, users=users)

@app.route("/admin/games")
def admin_games():
    if not session.get("user") or session["user"]["email"] != ADMIN_EMAIL: return redirect(url_for("login"))
    return render_template("admin_games.html", games=GAME_NAMES)

@app.route("/admin/delete_user/<email>")
def admin_delete_user(email):
    if not session.get("user") or session["user"]["email"] != ADMIN_EMAIL: return redirect(url_for("login"))
    save_json([u for u in load_json(USERS_FILE) if u['email'] != email], USERS_FILE)
    progress = load_json(PROGRESS_FILE)
    if email in progress:
        del progress[email]
        save_json(progress, PROGRESS_FILE)
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/delete_progress/<email>/<level_key>")
def admin_delete_progress(email, level_key):
    if not session.get("user") or session["user"]["email"] != ADMIN_EMAIL: return redirect(url_for("login"))
    progress = load_json(PROGRESS_FILE)
    if email in progress and level_key in progress[email]:
        del progress[email][level_key]
        if not progress[email]: del progress[email]
        save_json(progress, PROGRESS_FILE)
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/levels/<game_name>")
def admin_edit_level_list(game_name):
    if not session.get("user") or session["user"]["email"] != ADMIN_EMAIL: return redirect(url_for("login"))
    file_path = GAME_LEVEL_FILES.get(game_name)
    if not file_path: return "Game not found", 404
    return render_template("admin_level_selection.html", game_name=game_name, levels=load_json(file_path))

@app.route("/admin/edit_level/<game_name>/<difficulty>/<level>")
def admin_edit_level(game_name, difficulty, level):
    if not session.get("user") or session["user"]["email"] != ADMIN_EMAIL: return redirect(url_for("login"))
    file_path = GAME_LEVEL_FILES.get(game_name)
    if not file_path: return "Game not found", 404
    level_data = load_json(file_path).get(difficulty, {}).get(level)
    if level_data is None: return "Level not found", 404
    return render_template("admin_level_editor.html", game_name=game_name, difficulty=difficulty, level=level, level_data=level_data)

@app.route("/admin/save_level", methods=["POST"])
def admin_save_level():
    if not session.get("user") or session["user"]["email"] != ADMIN_EMAIL: return jsonify({"status": "error", "message": "Unauthorized"}), 403
    req = request.json
    file_path = GAME_LEVEL_FILES.get(req['game_name'])
    if not file_path: return jsonify({"status": "error", "message": "Game not found"}), 404
    levels = load_json(file_path)
    if req['difficulty'] in levels and req['level'] in levels[req['difficulty']]:
        levels[req['difficulty']][req['level']] = req['data']
        save_json(levels, file_path)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Level not found"}), 404

@app.route("/admin/explanations", methods=["GET", "POST"])
def admin_edit_explanations():
    if not session.get("user") or session["user"]["email"] != ADMIN_EMAIL: return redirect(url_for("login"))
    
    if request.method == "POST":
        form_data = request.form
        new_explanations = {}
        
        for key, value in form_data.items():
            if key.startswith('new_'): continue
            try:
                game, algo, field = key.split('_', 2)
                if game not in new_explanations: new_explanations[game] = {}
                if algo not in new_explanations[game]: new_explanations[game][algo] = {}
                if field in ["how_it_works", "advantages", "disadvantages"]:
                    new_explanations[game][algo][field] = [line.strip() for line in value.splitlines() if line.strip()]
                else:
                    new_explanations[game][algo][field] = value
            except ValueError:
                continue

        new_game = form_data.get("new_game_key", "").strip()
        new_algo = form_data.get("new_algo_key", "").strip()
        if new_game and new_algo:
            if new_game not in new_explanations: new_explanations[new_game] = {}
            new_explanations[new_game][new_algo] = {
                "name": form_data.get("new_name", ""),
                "description": form_data.get("new_description", ""),
                "analogy": form_data.get("new_analogy", ""),
                "how_it_works": [line.strip() for line in form_data.get("new_how_it_works", "").splitlines() if line.strip()],
                "advantages": [line.strip() for line in form_data.get("new_advantages", "").splitlines() if line.strip()],
                "disadvantages": [line.strip() for line in form_data.get("new_disadvantages", "").splitlines() if line.strip()]
            }
        
        save_json(new_explanations, EXPLANATIONS_FILE)
        return redirect(url_for('admin_games'))

    explanations = load_json(EXPLANATIONS_FILE)
    return render_template("admin_edit_ai.html", explanations=explanations, GAME_NAMES=GAME_NAMES)

@app.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    user = session.get("user")
    if not user or user["email"] != ADMIN_EMAIL: return redirect(url_for("login"))

    if request.method == "POST":
        config_data = {
            "announcement": request.form.get("announcement", ""),
            "levelsPerDifficulty": int(request.form.get("levelsPerDifficulty", 5)),
            "pointsForWin": int(request.form.get("pointsForWin", 100))
        }
        save_json(config_data, CONFIG_FILE)
        return redirect(url_for('admin_settings'))

    config_data = load_json(CONFIG_FILE)
    return render_template("admin_settings.html", config=config_data)

# --- GENERAL & AUTH ROUTES ---
@app.route("/")
def home():
    config = load_json(CONFIG_FILE)
    announcement = config.get("announcement", "")
    return render_template("home.html", active_page="home", announcement=announcement)
@app.route("/games")
def games(): return render_template("games.html", active_page="games")
@app.route("/about")
def about(): return render_template("about.html", active_page="about")
@app.route("/explanation")
def explanation_page(): return render_template("explanation.html")

@app.route("/leaderboard")
def leaderboard():
    progress_data, user_details = load_json(PROGRESS_FILE), get_user_details()
    data = []
    for email, p in progress_data.items():
        if not p: continue
        user_info = user_details.get(email, {})
        total_games_played = len(p)
        data.append({"name": user_info.get('name', 'Unknown'), "username": user_info.get('username', 'unknown'), "progress": p, "total_games_played": total_games_played})
    return render_template("leaderboard.html", data=data, active_page="leaderboard")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["user"] = {"name": "Admin", "email": ADMIN_EMAIL}
            return redirect(url_for("admin_dashboard"))
        users = load_json(USERS_FILE)
        user = next((u for u in users if u["email"].lower() == email.lower() and u["password"] == password), None)
        if user:
            session["user"] = user
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user" not in session: return redirect(url_for("login"))
    if request.method == "POST":
        users = load_json(USERS_FILE)
        for u in users:
            if u["email"] == session["user"]["email"]:
                u["name"] = request.form["name"]
                u["username"] = request.form["username"]
                u["gender"] = request.form["gender"]
                if request.form.get("password"): u["password"] = request.form["password"]
                session["user"] = u
                break
        save_json(users, USERS_FILE)
        return redirect(url_for("home"))
    return render_template("edit_profile.html")

# --- GENERIC GAME ROUTES ---
@app.route("/mark_game_played/<string:level_key>", methods=["POST"])
def mark_game_played(level_key):
    if not session.get("user"): return jsonify({"error": "Not logged in"}), 401
    update_user_level(session["user"]["email"], level_key, **request.json)
    return jsonify({"status": "saved"})

@app.route("/api/explanations")
def get_explanations():
    return jsonify(load_json(EXPLANATIONS_FILE))

@app.route("/ai_animation")
def ai_animation():
    # Get query params for preselecting game and algo
    game = request.args.get("game", "maze")
    algo = request.args.get("algo", "bfs")
    # Pass to template for JS to use
    return render_template("ai_animation.html", game=game, algo=algo)

# --- GAME-SPECIFIC ROUTES ---

# Maze
@app.route("/maze_solver")
def maze_solver(): return render_template("maze_solver.html", active_page="games")
@app.route("/maze_solver/levels")
def show_maze_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/maze/<string:difficulty>/<int:level>")
def play_maze_level(difficulty, level):
    maze = load_json(GAME_LEVEL_FILES['maze']).get(difficulty, {}).get(str(level))
    if not maze: return "Maze level not found!", 404
    return render_template("level_maze.html", maze=maze, difficulty=difficulty, level=level, rows=len(maze), cols=len(maze[0]))
@app.route("/solve_maze", methods=["POST"])
def solve_maze_route():
    data = request.json
    solvers = {"DFS": dfs_solver, "BFS": bfs_solver, "A*": astar_solver, "Greedy": greedy_solver}
    start = time.perf_counter()
    solution = solvers[data['algorithm']](data['maze'])
    ai_time = time.perf_counter() - start
    if session.get("user") and solution:
        update_user_level(session["user"]["email"], data['level_key'], **{f"{data['algorithm'].lower().replace('*', 'star')}_time": f"{ai_time:.12f}"})
    return jsonify({"solution": solution, "ai_time": f"{ai_time:.12f}"})

# Puzzle
@app.route('/puzzle')
def puzzle_page(): return render_template('puzzle_solver.html', active_page='games')
@app.route('/puzzle/levels')
def show_puzzle_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_puzzle_levels.html", levels=load_json(GAME_LEVEL_FILES['puzzle']), progress=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route('/level/puzzle/<string:difficulty>/<int:level>', methods=['GET', 'POST'])
def play_puzzle_level(difficulty, level):
    level_key, all_puzzles = f"puzzle_{difficulty}-{level}", load_json(GAME_LEVEL_FILES['puzzle'])
    initial_state = all_puzzles.get(difficulty, {}).get(str(level))
    if not initial_state: return "Puzzle level not found!", 404
    if request.method == 'POST':
        data = request.get_json()
        solvers = {'BFS': solve_puzzle_bfs, 'IDDFS': solve_puzzle_iddfs, 'A*': solve_puzzle_astar}
        solution, ai_time = solvers[data['algorithm']](data['initial_state'])
        if session.get("user") and solution:
            update_user_level(session["user"]["email"], level_key, **{f"{data['algorithm'].lower().replace('*','star')}_time": ai_time})
        return jsonify({'solution': solution, 'ai_time': ai_time})
    return render_template('level_puzzle.html', difficulty=difficulty, level=level, initial_state=initial_state, grid_size=int(sqrt(len(initial_state))), next_level=level + 1 if level < 5 else None)

# Sudoku
@app.route("/sudoku")
def sudoku_page(): return render_template("sudoku_solver.html", active_page="games")
@app.route("/sudoku/levels")
def show_sudoku_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_sudoku_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/sudoku/<string:difficulty>/<int:level>")
def play_sudoku_level(difficulty, level):
    board = load_json(GAME_LEVEL_FILES['sudoku']).get(difficulty, {}).get(str(level))
    if not board: return "Sudoku level not found!", 404
    return render_template("level_sudoku.html", difficulty=difficulty, level=level, board=board)
@app.route("/solve_sudoku", methods=["POST"])
def solve_sudoku_route():
    data = request.json
    solvers = {"DFS": solve_sudoku_dfs, "A*": solve_sudoku_astar, "AC-3": solve_sudoku_ac3}
    solution, steps, ai_time = solvers[data['algorithm']](data['board'])
    if session.get("user") and solution:
        update_user_level(session["user"]["email"], data['level_key'], **{f"{data['algorithm'].lower().replace('*', 'star').replace('-','')}_time": ai_time})
    return jsonify({"solution": solution, "steps": steps, "ai_time": ai_time})

# Word Search
@app.route("/word_search")
def word_search_page(): return render_template("word_search_solver.html", active_page="games")
@app.route("/word_search/levels")
def show_word_search_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_word_search_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/word_search/<string:difficulty>/<int:level>")
def play_word_search_level(difficulty, level):
    level_data = load_json(GAME_LEVEL_FILES['word_search']).get(difficulty, {}).get(str(level))
    if not level_data: return "Word Search level not found!", 404
    return render_template("level_word_search.html", difficulty=difficulty, level=level, level_data=level_data)
@app.route("/solve_word_search", methods=["POST"])
def solve_word_search_route():
    data = request.json
    solvers = {"Simple": solve_word_search_simple, "Trie": solve_word_search_trie}
    found, ai_time = solvers[data['algorithm']](data['grid'], data['words'])
    if session.get("user") and found:
        update_user_level(session["user"]["email"], data['level_key'], **{f"{data['algorithm'].lower()}_time": ai_time})
    return jsonify({"found_words": found, "ai_time": ai_time})

# Number Guessing
@app.route("/number_guessing")
def number_guessing_page(): return render_template("number_guessing_solver.html", active_page="games")
@app.route("/number_guessing/levels")
def show_number_guessing_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_number_guessing_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/number_guessing/<string:difficulty>/<int:level>")
def play_number_guessing_level(difficulty, level):
    level_data = load_json(GAME_LEVEL_FILES['number_guessing']).get(difficulty, {}).get(str(level))
    if not level_data: return "Number Guessing level not found!", 404
    return render_template("level_number_guessing.html", difficulty=difficulty, level=level, level_data=level_data)
@app.route("/solve_number_guessing", methods=["POST"])
def solve_number_guessing_route():
    data = request.json
    ld = data['level_data']
    path, ai_time = solve_number_guessing(ld['number'], ld['range'][0], ld['range'][1], data['algorithm'])
    if session.get("user"):
        update_user_level(session["user"]["email"], data['level_key'], **{f"{data['algorithm'].lower()}_guesses": len(path), f"{data['algorithm'].lower()}_time": ai_time})
    return jsonify({"path": path, "ai_time": ai_time})

# Memory
@app.route("/memory")
def memory_page(): return render_template("memory_solver.html", active_page="games")
@app.route("/memory/levels")
def show_memory_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_memory_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/memory/<string:difficulty>/<int:level>")
def play_memory_level(difficulty, level):
    level_data = load_json(GAME_LEVEL_FILES['memory']).get(difficulty, {}).get(str(level), [])
    random.shuffle(level_data)
    cols = 4 if len(level_data) <= 16 else 6
    return render_template("level_memory.html", difficulty=difficulty, level=level, board=level_data, cols=cols)
@app.route("/solve_memory", methods=["POST"])
def solve_memory_route():
    data = request.json
    solvers = {"DFS": solve_memory_dfs, "A*": solve_memory_astar, "Greedy": solve_memory_greedy}
    path, ai_time = solvers[data['algorithm']](data['board'])
    if session.get("user") and path:
        update_user_level(session["user"]["email"], data['level_key'], **{f"{data['algorithm'].lower().replace('*', 'star')}_time": ai_time, f"{data['algorithm'].lower().replace('*', 'star')}_moves": len(path) // 2})
    return jsonify({"path": path, "ai_time": ai_time, "moves": len(path) // 2})

# Math Quiz
@app.route("/math_quiz")
def math_quiz_page(): return render_template("math_quiz.html", active_page="games")
@app.route("/math_quiz/levels")
def show_math_quiz_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_math_quiz_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/math_quiz/<string:difficulty>/<int:level>")
def play_math_quiz_level(difficulty, level):
    level_data = load_json(GAME_LEVEL_FILES['math_quiz']).get(difficulty, {}).get(str(level))
    if not level_data: return "Math Quiz level not found!", 404
    next_level = level + 1 if level < 5 else None
    return render_template("level_math_quiz.html", difficulty=difficulty, level=level, level_data=level_data, next_level_data={'difficulty': difficulty, 'level': next_level} if next_level else None)

# Hangman
@app.route("/hangman")
def hangman_page(): return render_template("hangman.html", active_page="games")
@app.route("/hangman/levels")
def show_hangman_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_hangman_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/hangman/<string:difficulty>/<int:level>")
def play_hangman_level(difficulty, level):
    level_data = load_json(GAME_LEVEL_FILES['hangman']).get(difficulty, {}).get(str(level))
    if not level_data: return "Hangman level not found!", 404
    return render_template("level_hangman.html", difficulty=difficulty, level=level, level_data=level_data)

# Pattern Lock
@app.route("/pattern_lock")
def pattern_lock_page(): return render_template("pattern_lock.html", active_page="games")
@app.route("/pattern_lock/levels")
def show_pattern_lock_levels():
    if not session.get("user"): return redirect(url_for("login"))
    return render_template("show_pattern_lock_levels.html", played_levels=load_json(PROGRESS_FILE).get(session["user"]["email"], {}))
@app.route("/level/pattern_lock/<string:difficulty>/<int:level>")
def play_pattern_lock_level(difficulty, level):
    pattern = load_json(GAME_LEVEL_FILES['pattern_lock']).get(difficulty, {}).get(str(level))
    if not pattern: return "Pattern Lock level not found!", 404
    return render_template("level_pattern_lock.html", difficulty=difficulty, level=level, pattern=pattern)
@app.route("/solve_pattern_lock", methods=["POST"])
def solve_pattern_lock_route():
    data = request.json
    solvers = {"DFS": solve_pattern_lock_dfs, "BFS": solve_pattern_lock_bfs, "A*": solve_pattern_lock_astar, "Greedy": solve_pattern_lock_greedy}
    solution, ai_time = solvers[data['algorithm']](data['pattern'])
    if session.get("user") and solution:
        update_user_level(session["user"]["email"], data['level_key'], **{f"{data['algorithm'].lower().replace('*', 'star')}_time": ai_time})
    return jsonify({"solution": solution, "ai_time": f"{ai_time:.12f}"})

# --- CONTEXT PROCESSOR ---
@app.context_processor
def inject_user_and_history():
    user = session.get("user")
    history = []
    if user:
        user_progress = load_json(PROGRESS_FILE).get(user.get("email"), {})
        for key, data in user_progress.items():
            try:
                game, diff, level = re.match(r"([a-z_]+)_(\w+)-(\d+)", key).groups()
                history.append({
                    "game": GAME_NAMES.get(game, game.replace('_', ' ').title()),
                    "level": f"{diff.title()} {level}", "difficulty": diff,
                    "is_won": not ('status' in data and data['status'] != 'won')
                })
            except (AttributeError, IndexError, ValueError): continue
        history.sort(key=lambda item: item['game'])
    return dict(user=user, history=history)

if __name__ == "__main__":
    app.run(debug=True)
