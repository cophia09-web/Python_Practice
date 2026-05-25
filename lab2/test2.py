import numpy as np
import time
from collections import deque

# Примітка: Додано базові функції генерації, щоб код був робочим "з коробки"
def generate_islands(n=100, seed=1, island_count=7):
    np.random.seed(seed)
    grid = np.zeros((n, n))
    for _ in range(island_count):
        y, x = np.random.randint(0, n, 2)
        radius = np.random.randint(n//10, n//4)
        for i in range(max(0, y-radius), min(n, y+radius)):
            for j in range(max(0, x-radius), min(n, x+radius)):
                dist = np.sqrt((i-y)**2 + (j-x)**2)
                if dist < radius:
                    grid[i, j] += (radius - dist)
    return grid

def height_to_binary(grid, sea_level):
    return (grid > sea_level).astype(int)

def find_islands(binary_map):
    h, w = binary_map.shape
    visited = np.zeros_like(binary_map, dtype=bool)
    islands = []

    for y in range(h):
        for x in range(w):
            if binary_map[y, x] == 1 and not visited[y, x]:
                # BFS для пошуку окремого острова
                cells = []
                queue = deque([(y, x)])
                visited[y, x] = True
                
                min_x, min_y = x, y
                max_x, max_y = x, y
                
                while queue:
                    cy, cx = queue.popleft()
                    cells.append((cy, cx))
                    min_x, max_x = min(min_x, cx), max(max_x, cx)
                    min_y, max_y = min(min_y, cy), max(max_y, cy)
                    
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if binary_map[ny, nx] == 1 and not visited[ny, nx]:
                                visited[ny, nx] = True
                                queue.append((ny, nx))
                
                # Розрахунок характеристик острова
                area = len(cells)
                width = max_x - min_x + 1
                height = max_y - min_y + 1
                perimeter = 0
                border_cells = []
                
                for cy, cx in cells:
                    is_border = False
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = cy + dy, cx + dx
                        if ny < 0 or ny >= h or nx < 0 or nx >= w or binary_map[ny, nx] == 0:
                            perimeter += 1
                            is_border = True
                    if is_border:
                        border_cells.append((cy, cx))

                islands.append({
                    "area": area,
                    "bbox": (min_x, min_y, max_x, max_y),
                    "width": width,
                    "height": height,
                    "perimeter": perimeter,
                    "border_cells": border_cells
                })
    return islands

def distance_to_islands(binary_map, base, islands):
    h, w = binary_map.shape
    visited = np.zeros_like(binary_map, dtype=bool)
    # Початкова точка - база на воді
    queue = deque([(base[0], base[1], 0)])
    visited[base[0], base[1]] = True

    directions4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    distances = {i: float("inf") for i in range(len(islands))}
    border_sets = [set(isl["border_cells"]) for isl in islands]

    while queue:
        y, x, d = queue.popleft()

        # Перевірка сусідніх клітинок на належність до островів
        for dy, dx in directions4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                for i, bset in enumerate(border_sets):
                    if (ny, nx) in bset:
                        # Якщо ми знайшли шлях коротший за існуючий
                        if d < distances[i]:
                            distances[i] = d

        # Рух по черзі BFS (тільки по воді)
        for dy, dx in directions4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                if binary_map[ny, nx] == 0 and not visited[ny, nx]:
                    visited[ny, nx] = True
                    queue.append((ny, nx, d + 1))
    return distances

def island_scores(islands, distances):
    result = []
    for i, isl in enumerate(islands):
        # Рейтинг: площа ділиться на (відстань + 1), щоб уникнути ділення на 0
        score = isl["area"] / (distances[i] + 1)
        result.append((i, score, distances[i]))
    
    # Сортування за спаданням рейтингу
    result.sort(key=lambda x: x[1], reverse=True)
    return result

# --- ОСНОВНИЙ БЛОК ВИКОНАННЯ ---
if __name__ == "__main__":
    params = ((100, 7), (500, 20), (1000, 35))
    sea_level = 3
    seed = 1   

    for n, island_count in params:
        print("\n" + "="*50)
        print(f"РОЗМІР КАРТИ: {n}x{n}")
        print("="*50)

        start = time.time()
        grid = generate_islands(n=n, seed=seed, island_count=island_count)
        print("Час генерації:", round(time.time() - start, 2), "сек")

        binary = height_to_binary(grid, sea_level)
        islands = find_islands(binary)

        print("Кількість островів:", len(islands))

        # Вибір випадкової точки води для бази
        water_y, water_x = np.where(binary == 0)
        if len(water_y) > 0:
            idx = np.random.randint(len(water_y))
            base = (water_y[idx], water_x[idx])
            
            distances = distance_to_islands(binary, base, islands)
            scores = island_scores(islands, distances)

            print("\nTOP-5 за рейтингом (Площа/Відстань):")
            for i, score, dist in scores[:5]:
                print(f"Острів {i}: score={round(score, 2)}, dist={dist}")
        else:
            print("На карті немає води для розміщення бази!")

            #плаваючу базу рахуємо тільки для 100x100 (щоб не було дуже довго)

        if n==100:

            best_pos,best_avg=best_base(binary,islands)

            print("Оптимальна база:",best_pos)

            print("Середня відстань:",round(best_avg,2))



            plt.figure(figsize=(6,6))

            plt.imshow(binary,cmap="terrain")

            plt.scatter(base[1],base[0],c="red",label="Base")

            plt.scatter(best_pos[1],best_pos[0],c="blue",label="Best Base")

            plt.legend()

            plt.title("Binary Map 100x100")

            plt.show()