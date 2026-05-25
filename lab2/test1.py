import numpy as np
import matplotlib.pyplot as plt
from collections import deque

def box_blur(arr: np.ndarray, r: int) -> np.ndarray:
    if r <= 0:
        return arr.astype(np.float32, copy=False)
    a = arr.astype(np.float32, copy=False)
    pad = r
    p = np.pad(a, ((pad, pad), (pad, pad)), mode="edge")
    s = p.cumsum(axis=0).cumsum(axis=1)
    k = 2 * r + 1
    total = s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k]
    return total / (k * k)

def add_hills(field: np.ndarray, rng: np.random.Generator, count: int) -> np.ndarray:
    h, w = field.shape
    yy, xx = np.mgrid[0:h, 0:w]
    out = field.astype(np.float32, copy=True)
    for _ in range(count):
        cy = int(rng.integers(0, h))
        cx = int(rng.integers(0, w))
        radius = int(rng.integers(max(8, min(h, w)//70), max(25, min(h, w)//18)))
        amp = float(rng.uniform(0.4, 1.2))
        dy = yy - cy
        dx = xx - cx
        d2 = dx*dx + dy*dy
        sigma2 = (radius * radius) / 2.5
        out += amp * np.exp(-d2 / (2.0 * sigma2))
    return out

def normalize_to_0_9(field: np.ndarray) -> np.ndarray:
    f = field.astype(np.float32, copy=False)
    mn = float(f.min())
    mx = float(f.max())
    if mx - mn < 1e-9:
        return np.zeros_like(f, dtype=np.uint8)
    f = (f - mn) / (mx - mn)
    return (f * 9.0 + 1e-6).astype(np.uint8)

def generate_map(n: int, student_seed: int) -> np.ndarray:
    rng = np.random.default_rng(student_seed * 10000 + n)
    noise = rng.random((n, n), dtype=np.float32)
    r1 = max(2, n // 90)
    r2 = max(7, n // 35)
    r3 = max(15, n // 20)
    a1 = box_blur(noise, r1)
    a2 = box_blur(noise, r2)
    a3 = box_blur(noise, r3)
    field = 0.55 * a1 + 0.30 * a2 + 0.15 * a3
    
    hill_count_dict = {100: 25, 500: 90, 1000: 160}
    hill_count = hill_count_dict.get(n, max(30, n // 6))
    field = add_hills(field, rng, hill_count)
    
    basin = box_blur(rng.random((n, n), dtype=np.float32), max(10, n // 18))
    field = field - 0.35 * basin
    return normalize_to_0_9(field)

class IslandAnalyzer:
    def __init__(self, grid_map):
        self.grid = grid_map
        self.h, self.w = grid_map.shape
        self.directions_4 = [(-1,0), (1,0), (0,-1), (0,1)]
        self.directions_8 = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

    def get_binary_map(self, sea_level):
        return (self.grid > sea_level).astype(int)

    def analyze_islands(self, sea_level):
        binary_map = self.get_binary_map(sea_level)
        visited = np.zeros_like(binary_map, dtype=bool)
        islands = []
        
        for r in range(self.h):
            for c in range(self.w):
                if binary_map[r, c] == 1 and not visited[r, c]:
                    queue = deque([(r, c)])
                    visited[r, c] = True
                    cells = []
                    coast_cells = []
                    perimeter = 0
                    
                    min_x, max_x = c, c
                    min_y, max_y = r, r

                    while queue:
                        curr_r, curr_c = queue.popleft()
                        cells.append((curr_r, curr_c))
                        
                        min_x = min(min_x, curr_c); max_x = max(max_x, curr_c)
                        min_y = min(min_y, curr_r); max_y = max(max_y, curr_r)
                        
                        is_coast = False
                        for dr, dc in self.directions_4:
                            nr, nc = curr_r + dr, curr_c + dc
                            if 0 <= nr < self.h and 0 <= nc < self.w:
                                if binary_map[nr, nc] == 0:
                                    is_coast = True
                                    perimeter += 1
                            else:
                                perimeter += 1 
                        
                        if is_coast:
                            coast_cells.append((curr_r, curr_c))
                            
                        for dr, dc in self.directions_8:
                            nr, nc = curr_r + dr, curr_c + dc
                            if 0 <= nr < self.h and 0 <= nc < self.w:
                                if binary_map[nr, nc] == 1 and not visited[nr, nc]:
                                    visited[nr, nc] = True
                                    queue.append((nr, nc))
                    
                    if cells:
                        islands.append({
                            'id': len(islands) + 1,
                            'area': len(cells),
                            'bbox': (min_x, min_y, max_x, max_y),
                            'width': max_x - min_x + 1,
                            'length': max_y - min_y + 1,
                            'perimeter': perimeter,
                            'coast_cells': coast_cells
                        })
        return islands

    def calculate_distances(self, islands, base_r, base_c, sea_level):
        binary_map = self.get_binary_map(sea_level)
        distances = {isl['id']: float('inf') for isl in islands}
        
        if not islands or binary_map[base_r, base_c] == 1:
            return distances

        queue = deque([(base_r, base_c, 0)])
        visited = np.zeros_like(binary_map, dtype=bool)
        visited[base_r, base_c] = True
        
        coast_map = {}
        for isl in islands:
            for r, c in isl['coast_cells']:
                coast_map[(r, c)] = isl['id']
                
        islands_found = 0
        total_islands = len(islands)
        
        while queue and islands_found < total_islands:
            r, c, dist = queue.popleft()
            if (r, c) in coast_map:
                isl_id = coast_map[(r, c)]
                if distances[isl_id] == float('inf'):
                    distances[isl_id] = dist
                    islands_found += 1
                    
            for dr, dc in self.directions_4:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.h and 0 <= nc < self.w:
                    if not visited[nr, nc] and binary_map[nr, nc] == 0:
                        visited[nr, nc] = True
                        queue.append((nr, nc, dist + 1))
        return distances

    def rank_islands(self, islands, distances):
        for isl in islands:
            dist = distances.get(isl['id'], float('inf'))
            isl['distance'] = dist
            isl['score'] = isl['area'] / (dist + 1) if dist != float('inf') else 0.0
                
        top_score = sorted(islands, key=lambda x: x['score'], reverse=True)[:5]
        top_closest = sorted([i for i in islands if i['distance'] != float('inf')], key=lambda x: x['distance'])[:5]
        return top_score, top_closest

    def find_shortest_bridge(self, islands, sea_level):
        if len(islands) < 2: return None
        sorted_by_area = sorted(islands, key=lambda x: x['area'], reverse=True)
        isl1, isl2 = sorted_by_area[0], sorted_by_area[1]
        
        binary_map = self.get_binary_map(sea_level)
        queue = deque()
        visited = np.zeros_like(binary_map, dtype=bool)
        
        for r, c in isl1['coast_cells']:
            queue.append((r, c, 0))
            visited[r, c] = True
            
        target_cells = set(isl2['coast_cells'])
        
        while queue:
            r, c, dist = queue.popleft()
                
            for dr, dc in self.directions_4:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.h and 0 <= nc < self.w:
                    
                    if (nr, nc) in target_cells:
                        return dist 
                        
                    if not visited[nr, nc] and binary_map[nr, nc] == 0:
                        visited[nr, nc] = True
                        queue.append((nr, nc, dist + 1))
        return float('inf')

    def find_optimal_base(self, islands, sea_level):
        if not islands: return None, float('inf')
        
        binary_map = self.get_binary_map(sea_level)
        total_distances = np.zeros((self.h, self.w), dtype=np.float32)
        
        for isl in islands:
            queue = deque()
            visited = np.zeros_like(binary_map, dtype=bool)
            island_dist = np.full((self.h, self.w), float('inf'))
            
            for r, c in isl['coast_cells']:
                queue.append((r, c, 0))
                visited[r, c] = True
                island_dist[r, c] = 0
                
            while queue:
                r, c, dist = queue.popleft()
                for dr, dc in self.directions_4:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.h and 0 <= nc < self.w:
                        if not visited[nr, nc] and binary_map[nr, nc] == 0:
                            visited[nr, nc] = True
                            queue.append((nr, nc, dist + 1))
                            island_dist[nr, nc] = dist + 1
            
            island_dist[island_dist == float('inf')] = 99999
            total_distances += island_dist
            
        water_mask = (binary_map == 0)
        if not np.any(water_mask): return None, float('inf')
        
        water_distances = np.where(water_mask, total_distances, float('inf'))
        min_idx = np.unravel_index(np.argmin(water_distances), water_distances.shape)
        min_dist = water_distances[min_idx]
        
        # Ось тут перетворюємо ці дивні типи у звичайні int
        return (int(min_idx[0]), int(min_idx[1])), min_dist

if __name__ == "__main__":
    STUDENT_SEED = 4  
    base_x, base_y = 0, 0 
    
    for n in (100, 500, 1000):
        print(f"\n{'='*50}")
        print(f"ГЕНЕРАЦІЯ ТА АНАЛІЗ МАПИ РОЗМІРОМ {n}x{n}")
        print(f"{'='*50}")
        
        grid = generate_map(n, STUDENT_SEED)
        analyzer = IslandAnalyzer(grid)
        
        sea_levels_to_test = [2, 4, 6, 8]
        best_sea_level = -1
        max_islands = -1
        
        print("Частина 5: Аналіз рівнів моря")
        for sl in sea_levels_to_test:
            islands = analyzer.analyze_islands(sl)
            distances = analyzer.calculate_distances(islands, base_y, base_x, sl)
            valid_dist = [d for d in distances.values() if d != float('inf')]
            avg_dist = sum(valid_dist) / len(valid_dist) if valid_dist else 0
            
            print(f"SL={sl} | Островів: {len(islands)} | Середня відстань: {avg_dist:.2f}")
            if len(islands) > max_islands:
                max_islands = len(islands)
                best_sea_level = sl
                
        print(f"\n=> Оптимальний рівень моря (найбільше островів): {best_sea_level}")
        
        islands = analyzer.analyze_islands(best_sea_level)
        distances = analyzer.calculate_distances(islands, base_y, base_x, best_sea_level)
        top_score, top_closest = analyzer.rank_islands(islands, distances)
        
        print(f"\n Частина 4: ТОП-5 Островів (SL={best_sea_level}) ---")
        for isl in top_score:
            print(f"ID:{isl['id']} | Площа:{isl['area']} | Відстань:{isl['distance']} | Score:{isl['score']:.2f}")
            
        print("\n ТОП-5 Найближчих островів")
        for isl in top_closest:
            print(f"ID:{isl['id']} | Відстань:{isl['distance']} | Площа:{isl['area']}")
            
        bridge_len = analyzer.find_shortest_bridge(islands, best_sea_level)
        print(f"\n Частина 6: Найкоротший міст")
        print(f"Мінімальна кількість водних клітин для з'єднання 2 найбільших островів: {bridge_len}")
        
        print(f"\n Частина 7: Плаваюча база")
        best_base, min_total_dist = analyzer.find_optimal_base(islands, best_sea_level)
        if best_base:
            avg_base_dist = min_total_dist / len(islands)
            print(f"Оптимальна база (y, x): {best_base}")
            print(f"Середня відстань до всіх островів: {avg_base_dist:.2f}")
            
        plt.figure(figsize=(6, 6))
        plt.imshow(grid, cmap="terrain")
        plt.colorbar(label="height")
        plt.title(f"Height map {n}x{n}")
        plt.plot(base_x, base_y, 'ro', markersize=8, label="Fixed Base")
        plt.legend()
        plt.show()