W, H = map(int, input().split())
N = int(input())

photos = []
for _ in range(N):
    x1, y1, x2, y2 = map(int, input().split())
    photos.append((x1, y1, x2, y2))

current_positions = set()

def generate_cells(x1, y1, x2, y2):
    cells = set()
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            cells.add((x, y))
    return cells

for idx, (x1, y1, x2, y2) in enumerate(photos):
    new_cells = generate_cells(x1, y1, x2, y2)
    if idx == 0:
        current_positions = new_cells
    else:
        next_positions = set()
        for (x, y) in current_positions:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 1 <= nx <= W and 1 <= ny <= H and (nx, ny) in new_cells:
                    next_positions.add((nx, ny))
        if not next_positions:
            print("No")
            exit()
        current_positions = next_positions

print("Yes")
