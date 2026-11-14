import heapq, math
import numpy as np

_N8 = [(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,math.sqrt(2)),(-1,1,math.sqrt(2)),(1,-1,math.sqrt(2)),(1,1,math.sqrt(2))]

def astar(cost, start, goal):
    """8-connected A* over a cost multiplier grid. Returns (path, total_cost) or (None, inf).
    Step cost = geometric length * mean multiplier of the two cells. Heuristic is admissible
    because every multiplier is >= 1."""
    h, w = cost.shape
    if not np.isfinite(cost[start]) or not np.isfinite(cost[goal]):
        return None, math.inf
    g = {start: 0.0}; prev = {}; pq = [(0.0, start)]; closed = set()
    while pq:
        _, cur = heapq.heappop(pq)
        if cur in closed: continue
        if cur == goal:
            path = [cur]
            while cur in prev: cur = prev[cur]; path.append(cur)
            return path[::-1], g[goal]
        closed.add(cur)
        r, c = cur
        for dr, dc, d in _N8:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and np.isfinite(cost[nr, nc]):
                if dr and dc and not (np.isfinite(cost[r, nc]) and np.isfinite(cost[nr, c])):
                    continue   # no diagonal corner-cutting between blocked cells
                ng = g[cur] + d * 0.5 * (cost[r, c] + cost[nr, nc])
                if ng < g.get((nr, nc), math.inf):
                    g[(nr, nc)] = ng; prev[(nr, nc)] = cur
                    heapq.heappush(pq, (ng + math.hypot(goal[0]-nr, goal[1]-nc), (nr, nc)))
    return None, math.inf

def route_through(cost, waypoints):
    """Chain A* legs through waypoints. Returns (full_path, per_leg_costs) or (None, None)."""
    full, legs = [], []
    for a, b in zip(waypoints[:-1], waypoints[1:]):
        p, c = astar(cost, a, b)
        if p is None: return None, None
        full += p if not full else p[1:]; legs.append(c)
    return full, legs

def path_stats(path, slope, cell_m, walk_speed):
    pts = np.array(path)
    length = float(np.sum(np.hypot(*np.diff(pts, axis=0).T))) * cell_m
    return {"length_m": round(length, 1),
            "max_slope_deg": round(float(slope[tuple(pts.T)].max()), 1),
            "time_min": round(length / walk_speed / 60, 1)}
