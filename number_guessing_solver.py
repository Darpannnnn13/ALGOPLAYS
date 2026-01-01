import time
def solve_number_guessing(target, low, high, algorithm):
    start_time = time.perf_counter()
    path = []  
    if algorithm == 'Greedy': 
        while low <= high:
            mid = (low + high) // 2
            path.append(mid)
            if mid == target:
                break
            elif mid < target:
                low = mid + 1
            else:
                high = mid - 1
    elif algorithm == 'DFS':
        for i in range((low + high) // 2, low - 1, -1):
            path.append(i)
            if i == target: break
        if target > (low + high) // 2:
             for i in range((low + high) // 2 + 1, high + 1):
                path.append(i)
                if i == target: break
    else: 
        for i in range(low, high + 1):
            path.append(i)
            if i == target:
                break
    elapsed = time.perf_counter() - start_time
    return (path, f"{elapsed:.12f}")