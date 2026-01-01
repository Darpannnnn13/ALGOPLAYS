cases = {
    'human_only': {'human_guesses': 3, 'human_time': '1.23'},
    'ai_greedy_only': {'greedy_guesses': 2, 'greedy_time': 0.000123456},
    'ai_dfs_only': {'dfs_guesses': 0, 'dfs_time': 0.0},
    'human_zero': {'human_guesses': 0, 'human_time': 0},
    'none': None,
}

for name, data in cases.items():
    isPlayed = bool(data) and (
        ('human_guesses' in data if data is not None else False) or
        ('greedy_guesses' in data if data is not None else False) or
        ('dfs_guesses' in data if data is not None else False)
    )

    stats = []
    if data:
        if 'human_guesses' in data:
            timeText = f" ({data['human_time']})" if data.get('human_time') is not None and data.get('human_time') != '' else ''
            stats.append(f"You: {data['human_guesses']} guesses{timeText}")
        if 'greedy_guesses' in data:
            timeText = f" ({float(data['greedy_time']):.7f}s)" if data.get('greedy_time') is not None and data.get('greedy_time') != '' else ''
            stats.append(f"Greedy: {data['greedy_guesses']} guesses{timeText}")
        if 'dfs_guesses' in data:
            timeText = f" ({float(data['dfs_time']):.7f}s)" if data.get('dfs_time') is not None and data.get('dfs_time') != '' else ''
            stats.append(f"DFS: {data['dfs_guesses']} guesses{timeText}")

    print('CASE:', name)
    print('  isPlayed =', isPlayed)
    print('  stats:', stats)
    print()