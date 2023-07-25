import csv
import heapq
import random
from collections import deque
import math
# Define the point data structure
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)
    
    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)
    
class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def center(self):
        return Point(self.x + self.w / 2, self.y + self.h / 2)

def dijkstra_distance(start, end, file_path):
    # Define the grid
    grid = []

    # Read the grid data from the CSV file
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            grid.append([])
            for j, val in enumerate(row):
                grid[i].append(int(val))

    # Define the cost map
    costs = {Point(i, j): float('inf') for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == 0}
    costs[start] = 0  

    # Define the priority queue
    queue = [(0, start)]

    # Define the directions
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    # Run Dijkstra's algorithm
    while queue:
        current_cost, current_point = heapq.heappop(queue)
        if current_point == end:
            return current_cost
        for dx, dy in directions:
            new_point = Point(current_point.x + dx, current_point.y + dy)
            if new_point in costs:
                new_cost = current_cost + 1
                if new_cost < costs[new_point]:
                    costs[new_point] = new_cost
                    heapq.heappush(queue, (new_cost, new_point))

    return float('inf')  # Return infinity if there is no path

def mark_positions(player_position, boss_position, file_path):
    # Read the grid data from the CSV file
    with open(file_path, 'r') as file:
        grid = list(csv.reader(file))

    # Mark the player's and boss's positions
    grid[player_position.y][player_position.x] = 88
    grid[boss_position.y][boss_position.x] = 666

    # Write the modified grid back to the CSV file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(grid)

def place_characters(file_path, min_distance):
    # Read the grid data from the CSV file
    with open(file_path, 'r') as file:
        grid = list(csv.reader(file))
        
    walkable_positions = [(i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if int(cell) == 0]
    
    while True:
        # Randomly choose a walkable position for the player
        player_position = Point(*random.choice(walkable_positions))
        
        # Randomly choose a walkable position for the boss
        boss_position = Point(*random.choice(walkable_positions))
        
        # Check the distance between the player and the boss
        distance = dijkstra_distance(player_position, boss_position, file_path)
        
        if distance >= min_distance:
            return player_position, boss_position



def find_closest_walkable(start, file_path):
    # Read the grid data from the CSV file
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        grid = [list(map(int, row)) for row in reader]

    # Define the directions
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    # Initialize the BFS queue
    queue = deque([start])

    # Track the visited points
    visited = {start}

    while queue:
        current_point = queue.popleft()
        if grid[current_point.y][current_point.x] == 0:
            return current_point
        for dx, dy in directions:
            new_point = Point(current_point.x + dx, current_point.y + dy)
            if (0 <= new_point.x < len(grid[0]) and 
                0 <= new_point.y < len(grid) and
                new_point not in visited):
                queue.append(new_point)
                visited.add(new_point)

    # If there are no walkable cells, return None
    return None


import random



def find_closest_room_center(pos, rooms):
    def distance(p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    closest_center = None
    closest_distance = float('inf')
    closest_room = None

    for room in rooms:
        center_x = room.x + room.w / 2 + random.randint(-5, 5)
        center_y = room.y + room.h / 2 + random.randint(-5, 5)
        center = Point(center_x, center_y)
        d = distance(pos, center)
        if d < closest_distance:
            closest_distance = d
            closest_center = center
            closest_room = room

    closest_center = Point(int(closest_center.x ), int(closest_center.y))
    return closest_center



def find_biggest_room_center(pos, rooms):
    def area(room):
        return room.w * room.h

    biggest_room = None
    biggest_area = 0

    for room in rooms:
        a = area(room)
        if a > biggest_area:
            biggest_area = a
            biggest_room = room

    if biggest_room is None:
        return None

    center_x = biggest_room.x + biggest_room.w / 2 
    center_y = biggest_room.y + biggest_room.h / 2 
    center = Point(center_x, center_y)

    center = Point(int(center.x), int(center.y))
    return center




