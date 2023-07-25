import os
import csv
import pandas as pd
import random
import pygame


def generate_game_maps(path, level, x, y):
    layer_names = ["Floor", "Collisions", "Interactions", "Monsters"]
    
    # Create a directory for the level if it doesn't exist
    level_path = os.path.join(path, f"floor_{level}")
    os.makedirs(level_path, exist_ok=True)
    
    # Create a blank "logs.txt" file (or erase its contents if it already exists)
    logs_path = os.path.join(level_path, "logs.txt")
    with open(logs_path, "w") as file:
        pass
    
    # For each layer, generate a CSV file
    for layer_name in layer_names:
        file_name = f"map_{level}_{layer_name}.csv"
        file_path = os.path.join(level_path, file_name)
        df = pd.DataFrame(-1, index=range(x), columns=range(y))
        df.to_csv(file_path, index=False)
        # Write the map data to a CSV file
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            # write x rows
            for _ in range(x):
                # each row is a list of y "-1" values
                writer.writerow(['-1'] * y)
    return logs_path

class Node:
    def __init__(self, data=None):
        self.data = data
        self.left = None
        self.right = None



def random_split(rect, DUNGEON_WIDTH = 400,DUNGEON_HEIGHT = 400,MIN_ROOM_SIZE = 20,MIN_ROOM_RATIO = 0.5,depth=800,):
    if depth == 0:
        return rect, rect

    if random.randint(0, 1) == 0:
        # Horizontal split
        r1 = rect.copy()
       
        r1.height = random.randrange(MIN_ROOM_SIZE, r1.height)
        r2 = rect.copy()
        r2.height -= r1.height
        r2.top += r1.height
        # Discard by ratio
        r1_h_ratio = r1.height / r1.width
        r2_h_ratio = r2.height / r2.width
        if r1_h_ratio < MIN_ROOM_RATIO or r2_h_ratio < MIN_ROOM_RATIO:
            return random_split(rect,DUNGEON_WIDTH,DUNGEON_HEIGHT,MIN_ROOM_SIZE,MIN_ROOM_RATIO, depth-1)
    else:
        # Vertical split
        r1 = rect.copy()
       
        r1.width = random.randrange(MIN_ROOM_SIZE, r1.width)
        r2 = rect.copy()
        r2.width -= r1.width
        r2.left += r1.width
        # Discard by ratio
        r1_w_ratio = r1.width / r1.height
        r2_w_ratio = r2.width / r2.height
        if r1_w_ratio < MIN_ROOM_RATIO or r2_w_ratio < MIN_ROOM_RATIO:
            return random_split(rect, DUNGEON_WIDTH,DUNGEON_HEIGHT,MIN_ROOM_SIZE,MIN_ROOM_RATIO,depth-1)
    
    return r1, r2


def split_container(rect, niter,DUNGEON_WIDTH = 400,DUNGEON_HEIGHT = 400,MIN_ROOM_SIZE = 30,MIN_ROOM_RATIO = 0.5):
    root = Node(data=rect)
    if niter != 0:
        left, right = random_split(rect,DUNGEON_WIDTH,DUNGEON_HEIGHT,MIN_ROOM_SIZE,MIN_ROOM_RATIO)
        root.left = split_container(left, niter - 1,DUNGEON_WIDTH,DUNGEON_HEIGHT,MIN_ROOM_SIZE,MIN_ROOM_RATIO)
        root.right = split_container(right, niter - 1,DUNGEON_WIDTH,DUNGEON_HEIGHT,MIN_ROOM_SIZE,MIN_ROOM_RATIO)
    return root


def generate_dungeon(DUNGEON_WIDTH = 400,DUNGEON_HEIGHT = 400,MIN_ROOM_SIZE = 30,MIN_ROOM_RATIO = 0.5):
    main_rect = pygame.Rect((0, 0), (DUNGEON_WIDTH, DUNGEON_HEIGHT))
    rect_tree = split_container(main_rect, 5,DUNGEON_WIDTH,DUNGEON_HEIGHT,MIN_ROOM_SIZE,MIN_ROOM_RATIO)

    return rect_tree


def rect_list_from_tree(root_node):
    rect_list = []
    if root_node:
        rect_list = rect_list_from_tree(root_node.left)
        rect_list.append(root_node)
        rect_list.extend(rect_list_from_tree(root_node.right))
    return rect_list


def leaf_nodes_from_tree(root_node):
    node_list = []
    if root_node.left and root_node.right:
        node_list.extend(leaf_nodes_from_tree(root_node.left))
        node_list.extend(leaf_nodes_from_tree(root_node.right))
    else:
        node_list = [root_node]
    return node_list


def draw_paths(tree, surface):
    if tree.left is None or tree.right is None:
        return

    p1 = (tree.left.data.centerx * 5, tree.left.data.centery * 5)
    p2 = (tree.right.data.centerx * 5, tree.right.data.centery * 5)

    pygame.draw.line(surface, (127, 127, 127), p1, p2, width=10)

    draw_paths(tree.left, surface)
    draw_paths(tree.right, surface)
    
def generate_paths(tree):
    paths = []
    if tree.left is not None and tree.right is not None:
        p1 = (tree.left.data.centerx, tree.left.data.centery)
        p2 = (tree.right.data.centerx, tree.right.data.centery)
        paths.append((p1, p2))

        paths.extend(generate_paths(tree.left))
        paths.extend(generate_paths(tree.right))
    return paths


def draw_dungeon_as_image(dungeon_tree, surface):
    surface.fill((0, 0, 0))
    # for node in rect_list_from_tree(dungeon_tree):
    #     r = node.data.copy()
    #     r.x *= 5
    #     r.y *= 5
    #     r.w *= 5
    #     r.h *= 5
    #     pygame.draw.rect(surface, (127, 127, 0), r, 1)

    rooms = []
    for node in leaf_nodes_from_tree(dungeon_tree):
        container_rect = node.data

        room_rect = container_rect.copy()
        room_rect.left = room_rect.left + random.randrange(0, room_rect.width // 2)
        room_rect.top = room_rect.top + random.randrange(0, room_rect.height // 2)
        room_rect.width = container_rect.width - (room_rect.left - container_rect.left)
        room_rect.height = container_rect.height - (room_rect.top - container_rect.top)
        room_rect.width -= random.randrange(0, room_rect.width // 2)
        room_rect.height -= random.randrange(0, room_rect.height // 2)
        rooms.append(room_rect)

        # Paint
        display_rect = room_rect.copy()
        display_rect.x *= 5
        display_rect.y *= 5
        display_rect.w *= 5
        display_rect.h *= 5
        pygame.draw.rect(surface, (127, 127, 127), display_rect)

    draw_paths(dungeon_tree, surface)
    pygame.display.flip()
    


def draw_dungeon(dungeon_tree, file_path, path_width,DUNGEON_WIDTH = 400,DUNGEON_HEIGHT = 400,MIN_ROOM_SIZE = 30,MIN_ROOM_RATIO = 0.5):
    # Create a 2D array representing the dungeon
    dungeon_map = [[1 for _ in range(DUNGEON_HEIGHT)] for _ in range(DUNGEON_WIDTH)]

    # Generate rooms and paths
    rooms = []
    for node in leaf_nodes_from_tree(dungeon_tree):
        container_rect = node.data

        room_rect = container_rect.copy()
        room_rect.left = room_rect.left + random.randrange(0, room_rect.width // 2)
        room_rect.top = room_rect.top + random.randrange(0, room_rect.height // 2)
        room_rect.width = container_rect.width - (room_rect.left - container_rect.left)
        room_rect.height = container_rect.height - (room_rect.top - container_rect.top)
        room_rect.width -= random.randrange(0, room_rect.width // 2)
        room_rect.height -= random.randrange(0, room_rect.height // 2)
        rooms.append(room_rect)

        # Fill the room with 0s in the dungeon_map
        for x in range(room_rect.left, room_rect.left + room_rect.width):
            for y in range(room_rect.top, room_rect.top + room_rect.height):
                dungeon_map[x][y] = 0

    # Generate paths
    paths = generate_paths(dungeon_tree)

    # Fill the paths with 0s in the dungeon_map
    for path in paths:
        if path[0][0] == path[1][0]:  # vertical path
            for x in range(path[0][0] - path_width // 2, path[0][0] + path_width // 2 + 1):
                for y in range(min(path[0][1], path[1][1]), max(path[0][1], path[1][1]) + 1):
                    if 0 <= x < DUNGEON_WIDTH and 0 <= y < DUNGEON_HEIGHT:
                        dungeon_map[x][y] = 0
        else:  # horizontal path
            for y in range(path[0][1] - path_width // 2, path[0][1] + path_width // 2 + 1):
                for x in range(min(path[0][0], path[1][0]), max(path[0][0], path[1][0]) + 1):
                    if 0 <= x < DUNGEON_WIDTH and 0 <= y < DUNGEON_HEIGHT:
                        dungeon_map[x][y] = 0

    # Rest of the draw_dungeon function...

  

    # Mark wall types in the dungeon_map
    for x in range(DUNGEON_WIDTH):
        for y in range(DUNGEON_HEIGHT):
            if dungeon_map[x][y] == 1:  # It's a wall
                dungeon_map[x][y] = determine_wall_type(dungeon_map, x, y)
 
     # Now that all the rooms and paths are generated, run the corner detection
    dungeon_map = corner_detection(dungeon_map)
    # Check if directory exists, if not, create it
       # Mark wall types in the dungeon_map
    # Mark wall types in the dungeon_map
    for x in range(DUNGEON_WIDTH):
        for y in range(DUNGEON_HEIGHT):
            if x==0 or y==0 or x==DUNGEON_WIDTH-1 or y==DUNGEON_HEIGHT-1:
                dungeon_map[x][y]= 1 # It's a wall
                dungeon_map[x][y] = determine_wall_type(dungeon_map, x, y)
        directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(dungeon_map)
    return rooms


def determine_wall_type(dungeon_map, x, y):
    # This is a very simple example and probably won't cover all cases.
    # You should expand this to handle corners and different wall types.
    width, height = len(dungeon_map), len(dungeon_map[0])
    if x > 0 and dungeon_map[x - 1][y] == 0:
        return 2  # right wall
    elif x < width - 1 and dungeon_map[x + 1][y] == 0:
        return 3  # left wall
    elif y > 0 and dungeon_map[x][y - 1] == 0:
        return 4  # bottom wall
    elif y < height - 1 and dungeon_map[x][y + 1] == 0:
        return 5  # top wall
    else:
     return 1  # return wall if none of the above conditions are met

def corner_detection(dungeon_map):
    width, height = len(dungeon_map), len(dungeon_map[0])

    # Iterate through each cell in the dungeon_map
    for x in range(1, width-1):
        for y in range(1, height-1):
            if x < width - 1 and y < height - 1 and dungeon_map[x][y+1] == 2 and dungeon_map[x+1][y] == 4 :
            
                dungeon_map[x][y] = 6 #top left corner
            elif x > 0 and y < height - 1 and dungeon_map[x][y-1] == 2 and dungeon_map[x+1][y] == 5 :
                
                dungeon_map[x][y] = 7 #top right corner
            elif  x < width - 1 and y > 0 and dungeon_map[x][y+1] == 3 and dungeon_map[x-1][y] == 4 :
                
                dungeon_map[x][y] = 8 #bottom left corner
            elif x > 0 and y > 0  and dungeon_map[x-1][y] == 5 and dungeon_map[x][y-1] == 3 :
               
                dungeon_map[x][y] = 9 #bottom right corner
           
    return dungeon_map




