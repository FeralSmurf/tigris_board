import pygame
import sys
import copy
import random

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
window_width, window_height = screen.get_size()
pygame.display.set_caption("Tigris and Euphrates")

grid_width = 16
grid_height = 11
tile_size = 70

screen_width = grid_width * tile_size
screen_height = grid_height * tile_size + 150
pygame.display.set_caption("Tigris and Euphrates")

board_left_x = (window_width - screen_width) // 2
board_top_y = (window_height - screen_height) // 2 - 20

desert = (233, 200, 144)
black = (0, 0, 0)
river = (138, 202, 238)
red = (255, 0, 0)
undo_button_color = (200, 200, 200)
undo_button_hover_color = (180, 180, 180)

river_tiles = [
    (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (4, 2), (4, 1), (4, 0), (5, 0), (6, 0),
    (7, 0), (8, 0), (12, 0), (12, 1), (12, 2), (13, 2), (13, 3), (14, 3), (15, 3),
    (15, 4), (14, 4), (14, 5), (14, 6), (13, 6), (12, 6), (12, 7), (12, 8), (11, 8),
    (10, 8), (9, 8), (8, 8), (7, 8), (6, 8), (6, 7), (5, 7), (4, 7), (3, 7), (3, 6),
    (2, 6), (1, 6), (0, 6),
]

temple_with_treasure = pygame.image.load("temple_with_treasure.bmp")
temple_with_treasure = pygame.transform.scale(temple_with_treasure, (tile_size, tile_size))

temple_with_treasure_tiles = [
    (1, 1), (5, 2), (5, 9), (1, 7), (10, 0), (10, 10), (15, 1), (5, 2), (13, 4), (14, 8), (8, 6),
]

leader_tokens = {
    "black": pygame.image.load("black_leader_1.bmp"),
    "blue": pygame.image.load("blue_leader_1.bmp"),
    "red": pygame.image.load("red_leader_1.bmp"),
    "green": pygame.image.load("green_leader_1.bmp"),
}

for color in leader_tokens:
    leader_tokens[color] = pygame.transform.scale(leader_tokens[color], (70, 70))

other_tokens = {
    "market": pygame.image.load("market.bmp"),
    "city": pygame.image.load("city.bmp"),
    "farm": pygame.image.load("farm.bmp"),
    "temple": pygame.image.load("temple.bmp"),
}

for token in other_tokens:
    other_tokens[token] = pygame.transform.scale(other_tokens[token], (70, 70))

class Tile:
    def __init__(self, tile_type, image):
        self.tile_type = tile_type
        self.image = image
        self.rect = self.image.get_rect()

class Player:
    def __init__(self, name, player_space_x):
        self.name = name
        self.score = {"red": 0, "blue": 0, "green": 0, "black": 0}
        self.hand = []
        self.leaders = {
            "black": Tile("black_leader", leader_tokens["black"].copy()),
            "blue": Tile("blue_leader", leader_tokens["blue"].copy()),
            "red": Tile("red_leader", leader_tokens["red"].copy()),
            "green": Tile("green_leader", leader_tokens["green"].copy()),
        }

        if self.name == "Player 2":
            for leader in self.leaders.values():
                darken_surface = pygame.Surface(leader.image.get_size(), flags=pygame.SRCALPHA)
                darken_surface.fill((0, 0, 0, 50))  # Black with 50 alpha
                leader.image.blit(darken_surface, (0, 0))

        self.player_space_x = player_space_x
        self.place_leaders()

    def place_leaders(self):
        y_pos = window_height - player_space_height - 20 + 10 # top of player space + 10px padding
        x_start = self.player_space_x + (player_space_width - (4 * 70 + 3 * 10)) // 2 # Center the leaders block
        self.leaders["black"].rect.topleft = (x_start, y_pos)
        self.leaders["blue"].rect.topleft = (x_start + 80, y_pos)
        self.leaders["red"].rect.topleft = (x_start + 160, y_pos)
        self.leaders["green"].rect.topleft = (x_start + 240, y_pos)

    def draw_hand(self, tile_bag):
        for _ in range(6):
            if tile_bag:
                self.hand.append(tile_bag.pop())
        self.arrange_hand()

    def arrange_hand(self):
        y_pos = window_height - player_space_height - 20 + 10 + 70 + 10 # under leaders
        x_start = self.player_space_x + (player_space_width - (6 * 70 + 5 * 10)) // 2 # Center the hand block
        for i, tile in enumerate(self.hand):
            tile.rect.topleft = (x_start + i * 80, y_pos)

    def refill_hand(self, tile_bag):
        needed = 6 - len(self.hand)
        for _ in range(needed):
            if tile_bag:
                self.hand.append(tile_bag.pop())
        self.arrange_hand()


def create_tile_bag():
    bag = []
    # 30 Farm (blue), 15 Market (green), 6 Temple (red), 6 Settlement (black)
    for _ in range(30):
        bag.append(Tile("farm", other_tokens["farm"]))
    for _ in range(15):
        bag.append(Tile("market", other_tokens["market"]))
    for _ in range(6):
        bag.append(Tile("temple", other_tokens["temple"]))
    for _ in range(6):
        bag.append(Tile("city", other_tokens["city"]))
    random.shuffle(bag)
    return bag

tile_bag = create_tile_bag()

player_space_width = 500
player_space_height = 200
discard_area_width = 150
gap_between_player_areas = 50
gap_between_discard_and_player = 10

total_player_zone_width = (2 * player_space_width) + gap_between_player_areas + (2 * discard_area_width) + (2 * gap_between_discard_and_player)
overall_start_x = (window_width - total_player_zone_width) // 2

player_space_x1 = overall_start_x + discard_area_width + gap_between_discard_and_player
player_space_x2 = player_space_x1 + player_space_width + gap_between_player_areas

player1 = Player("Player 1", player_space_x1)
player2 = Player("Player 2", player_space_x2)
player1.draw_hand(tile_bag)
player2.draw_hand(tile_bag)

players = [player1, player2]
current_player_index = 0
actions_taken = 0
board_tiles = []
discard_pile = []
tiles_marked_for_discard = []

player1_discard_area = pygame.Rect(overall_start_x, window_height - player_space_height - 20, discard_area_width, player_space_height)
player2_discard_x_pos = player_space_x2 + player_space_width + gap_between_discard_and_player
player2_discard_area = pygame.Rect(player2_discard_x_pos, window_height - player_space_height - 20, discard_area_width, player_space_height)
dark_grey = (105, 105, 105)


for (x, y) in temple_with_treasure_tiles:
    temple_tile = Tile("temple", temple_with_treasure)
    temple_tile.rect.topleft = (
        board_left_x + x * tile_size,
        board_top_y + y * tile_size,
    )
    is_occupied = False
    for t in board_tiles:
        if t.rect.topleft == temple_tile.rect.topleft:
            is_occupied = True
            break
    if not is_occupied:
        board_tiles.append(temple_tile)

warning_message = ""
warning_message_timer = 0
warning_font = pygame.font.Font(None, 48)

# Undo button setup
undo_button_width = 100

undo_button_height = 50
undo_button_x = window_width - undo_button_width - 20
undo_button_y = 20

# End Turn button setup
end_turn_button_width = 120
end_turn_button_height = 50
end_turn_button_x = window_width - end_turn_button_width - 20
end_turn_button_y = 80
end_turn_button_color = (200, 200, 200)
end_turn_button_hover_color = (180, 180, 180)

# Replace Tiles button setup
replace_button_width = 160
replace_button_height = 50
replace_button_x = window_width - replace_button_width - 20
replace_button_y = 140
replace_button_color = (200, 200, 200)
replace_button_hover_color = (180, 180, 180)


# Track previous positions for undo functionality
previous_leader_positions = {}
previous_hand_positions = {}


dragging_tile = None
dragging_leader = None
original_drag_pos = None

def snap_to_grid(pos):
    x = (pos[0] - board_left_x) // tile_size
    y = (pos[1] - board_top_y) // tile_size
    if 0 <= x < grid_width and 0 <= y < grid_height:
        return (board_left_x + x * tile_size,
                board_top_y + y * tile_size)
    return pos


def save_previous_positions():
    global previous_leader_positions, previous_hand_positions
    previous_leader_positions = {p.name: {color: leader.rect.copy() for color, leader in p.leaders.items()} for p in players}
    previous_hand_positions = {p.name: [tile.rect.copy() for tile in p.hand] for p in players}


def undo_last_move():
    global players
    if previous_leader_positions and previous_hand_positions:
        for p in players:
            for color, rect in previous_leader_positions[p.name].items():
                p.leaders[color].rect = rect
            for i, rect in enumerate(previous_hand_positions[p.name]):
                p.hand[i].rect = rect


tile_color_map = {
    "farm": "blue",
    "market": "green",
    "temple": "red",
    "city": "black",
}

def update_score(placed_tile):
    tile_x = (placed_tile.rect.x - board_left_x) // tile_size
    tile_y = (placed_tile.rect.y - board_top_y) // tile_size
    
    placed_color = tile_color_map.get(placed_tile.tile_type)
    if not placed_color:
        return

    # Find the kingdom the tile is in.
    # We pass the placed_tile to ignore, because it's not yet part of board_tiles when this is called.
    # But its rect is at the new position. So get_kingdom needs to see the board state *before* this tile was placed
    # But wait, update_score is called *after* the tile is placed (rect is updated).
    # And get_kingdom will use get_tile_at, which will find the tile itself unless we ignore it.
    # The tile is part of the kingdom it creates/joins, so we should NOT ignore it.
    kingdom = get_kingdom(tile_x, tile_y, players)
    if not kingdom:
        return

    # Look for a leader of the same color in the kingdom.
    leader_found = False
    for kx, ky in kingdom:
        tile_in_kingdom = get_tile_at(kx, ky, players)
        if tile_in_kingdom and "leader" in tile_in_kingdom.tile_type:
            leader_color_in_kingdom = tile_in_kingdom.tile_type.split('_')[0]
            if leader_color_in_kingdom == placed_color:
                # Find which player owns this leader
                for p in players:
                    if tile_in_kingdom in p.leaders.values():
                        p.score[placed_color] += 1
                        print(f"DEBUG: Scored 1 {placed_color} point for {p.name} via {leader_color_in_kingdom} leader.")
                        leader_found = True
                        break # found player
                if leader_found:
                    break # found leader
    
    if leader_found:
        return

    # If no leader of the tile's color is found, look for the black leader (king).
    king_found = False
    for kx, ky in kingdom:
        tile_in_kingdom = get_tile_at(kx, ky, players)
        if tile_in_kingdom and tile_in_kingdom.tile_type == "black_leader":
            # Find which player owns the king
            for p in players:
                if tile_in_kingdom in p.leaders.values():
                    p.score[placed_color] += 1
                    print(f"DEBUG: Scored 1 {placed_color} point for {p.name} via black leader (king).")
                    king_found = True
                    break # found player
            if king_found:
                break # found king


def get_tile_at(grid_x, grid_y, players, ignore_piece=None):
    # Check board_tiles (for tiles from previous turns)
    for t in board_tiles:
        if t is ignore_piece:
            continue
        t_x = (t.rect.x - board_left_x) // tile_size
        t_y = (t.rect.y - board_top_y) // tile_size
        if t_x == grid_x and t_y == grid_y:
            return t

    for p in players:
        # Check leaders on the board
        for l in p.leaders.values():
            if l is ignore_piece:
                continue
            # Check if it's on the grid part of the screen
            if l.rect.left >= board_left_x and l.rect.top < board_top_y + grid_height * tile_size:
                l_x = (l.rect.x - board_left_x) // tile_size
                l_y = (l.rect.y - board_top_y) // tile_size
                if l_x == grid_x and l_y == grid_y:
                    return l

        # Check tiles in player hands that are on the board this turn
        for t in p.hand:
            if t is ignore_piece:
                continue
            # Check if it's on the grid part of the screen
            if t.rect.left < board_left_x + screen_width and \
               t.rect.top < board_top_y + grid_height * tile_size and \
               t.rect.left >= board_left_x and \
               t.rect.top >= board_top_y:
                t_x = (t.rect.x - board_left_x) // tile_size
                t_y = (t.rect.y - board_top_y) // tile_size
                if t_x == grid_x and t_y == grid_y:
                    return t

    return None


def get_kingdom(grid_x, grid_y, players, ignore_piece=None):
    if get_tile_at(grid_x, grid_y, players, ignore_piece) is None:
        return set()
    kingdom = set()
    visited = set()
    queue = [(grid_x, grid_y)]
    visited.add((grid_x, grid_y))

    while queue:
        x, y = queue.pop(0)
        kingdom.add((x, y))

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx < grid_width and 0 <= ny < grid_height and (nx, ny) not in visited:
                if get_tile_at(nx, ny, players, ignore_piece) is not None:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return kingdom


def is_valid_move(piece, pos, players):
    grid_x = (pos[0] - board_left_x) // tile_size
    grid_y = (pos[1] - board_top_y) // tile_size
    print(f"--- Checking valid move for {piece.tile_type} at ({grid_x}, {grid_y}) ---")

    if not (0 <= grid_x < grid_width and 0 <= grid_y < grid_height):
        print("DEBUG: Invalid - Off board")
        return False

    occupant = get_tile_at(grid_x, grid_y, players, ignore_piece=piece)
    if occupant is not None:
        print(f"DEBUG: Invalid - Space occupied by {occupant.tile_type}")
        return False
    
    print("DEBUG: Space is not occupied.")

    if piece.tile_type == "farm":
        print(f"DEBUG: Piece is a farm. Checking river tiles. Target is in river_tiles: {(grid_x, grid_y) in river_tiles}")
        if (grid_x, grid_y) not in river_tiles:
            print("DEBUG: Invalid - Farm not on a river tile.")
            return False
    elif (grid_x, grid_y) in river_tiles:
        print("DEBUG: Invalid - Non-farm tile on a river tile.")
        return False

    print("DEBUG: Tile placement rules passed.")

    if "leader" in piece.tile_type:
        print("DEBUG: Piece is a leader, checking leader rules...")
        leader_color = piece.tile_type.split('_')[0]

        is_adjacent_to_temple = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                adjacent_tile = get_tile_at(nx, ny, players, ignore_piece=piece)
                if adjacent_tile and adjacent_tile.tile_type == "temple":
                    print(f"DEBUG: Found adjacent temple at ({nx}, {ny})")
                    is_adjacent_to_temple = True
                    break
        if not is_adjacent_to_temple:
            print("DEBUG: Invalid - Leader not adjacent to a temple.")
            return False
        
        print("DEBUG: Leader is adjacent to a temple.")

        adjacent_kingdoms = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                if get_tile_at(nx, ny, players, ignore_piece=piece) is not None:
                    is_new_kingdom = True
                    for k in adjacent_kingdoms:
                        if (nx, ny) in k:
                            is_new_kingdom = False
                            break
                    if is_new_kingdom:
                        adjacent_kingdoms.append(get_kingdom(nx, ny, players, ignore_piece=piece))
        
        print(f"DEBUG: Found {len(adjacent_kingdoms)} adjacent kingdoms.")

        for kingdom in adjacent_kingdoms:
            for kx, ky in kingdom:
                tile_in_kingdom = get_tile_at(kx, ky, players, ignore_piece=piece)
                if tile_in_kingdom and "leader" in tile_in_kingdom.tile_type:
                    if tile_in_kingdom.tile_type.split('_')[0] == leader_color:
                        if tile_in_kingdom != piece:
                            print(f"DEBUG: Invalid - Found leader of same color in kingdom at ({kx}, {ky})")
                            return False
    
    print("--- Move is valid ---")
    return True

def end_turn():
    global current_player_index, actions_taken, board_tiles, tiles_marked_for_discard
    current_player = players[current_player_index]

    tiles_marked_for_discard.clear()
    
    # Identify placed tiles and remove them from hand
    placed_tiles = [
        tile for tile in current_player.hand 
        if tile.rect.left < board_left_x + screen_width and
           tile.rect.top < board_top_y + grid_height * tile_size and
           tile.rect.left >= board_left_x and
           tile.rect.top >= board_top_y
    ]
    board_tiles.extend(placed_tiles)
    current_player.hand = [tile for tile in current_player.hand if tile not in placed_tiles]
    
    current_player.refill_hand(tile_bag)
    current_player_index = (current_player_index + 1) % len(players)
    actions_taken = 0

def is_point_in_rect(point, rect):
    return rect.collidepoint(point)


def draw_scoreboard():
    global current_player_index
    font = pygame.font.Font(None, 28)
    
    # Display current player's turn
    turn_font = pygame.font.Font(None, 48)
    current_player_name = players[current_player_index].name
    turn_text = turn_font.render(f"{current_player_name}'s Turn", True, black)
    screen.blit(turn_text, (20, 20))

    score_y_pos = window_height - player_space_height - 20 + 10 + 70 + 10 + 70 + 10 # below hand
    for i, player in enumerate(players):
        text_color = red if i == current_player_index else black
        
        score_text = f"{player.name}'s Score: "
        text = font.render(score_text, True, text_color)
        
        # Center the whole score line
        score_line_width = text.get_width() + 4 * 70 # approx width of score items
        score_start_x = player.player_space_x + (player_space_width - score_line_width) // 2
        
        screen.blit(text, (score_start_x, score_y_pos))
        
        score_x = score_start_x + text.get_width()
        for color, score in player.score.items():
            pygame.draw.rect(screen, pygame.Color(color), (score_x, score_y_pos, 20, 20))
            score_val_text = font.render(f"{score}", True, text_color)
            screen.blit(score_val_text, (score_x + 25, score_y_pos))
            score_x += 70

while True:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                end_turn_button_rect = pygame.Rect(end_turn_button_x, end_turn_button_y, end_turn_button_width, end_turn_button_height)
                if is_point_in_rect(mouse_pos, end_turn_button_rect):
                    end_turn()
                    continue

                replace_button_rect = pygame.Rect(replace_button_x, replace_button_y, replace_button_width, replace_button_height)
                if is_point_in_rect(mouse_pos, replace_button_rect):
                    if actions_taken < 2 and 0 < len(tiles_marked_for_discard) <= 5:
                        actions_taken += 1
                        current_player = players[current_player_index]
                        for tile in tiles_marked_for_discard:
                            if tile in current_player.hand:
                                current_player.hand.remove(tile)
                                discard_pile.append(tile)
                        current_player.refill_hand(tile_bag)
                        tiles_marked_for_discard.clear()
                        if actions_taken >= 2:
                            end_turn()
                    elif actions_taken >= 2:
                        warning_message = "No more actions this turn!"
                        warning_message_timer = 120
                    elif len(tiles_marked_for_discard) == 0:
                        warning_message = "No tiles marked for discard."
                        warning_message_timer = 120
                    elif len(tiles_marked_for_discard) > 5:
                        warning_message = "Cannot discard more than 5 tiles."
                        warning_message_timer = 120
                    continue

                if actions_taken < 2:
                    if is_point_in_rect(mouse_pos, pygame.Rect(undo_button_x, undo_button_y, undo_button_width, undo_button_height)):
                        undo_last_move()
                        continue

                    current_player = players[current_player_index]
                    for color, leader in current_player.leaders.items():
                        if is_point_in_rect(mouse_pos, leader.rect):
                            save_previous_positions()
                            dragging_leader = leader
                            original_drag_pos = leader.rect.copy()
                            break
                    if not dragging_leader:
                        for tile in current_player.hand:
                            if is_point_in_rect(mouse_pos, tile.rect):
                                save_previous_positions()
                                dragging_tile = tile
                                original_drag_pos = tile.rect.copy()
                                break
                else:
                    warning_message = "No more actions this turn!"
                    warning_message_timer = 120

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if dragging_leader:
                    new_pos_tuple = snap_to_grid(dragging_leader.rect.center)
                    if is_valid_move(dragging_leader, new_pos_tuple, players):
                        dragging_leader.rect.topleft = new_pos_tuple
                        if dragging_leader.rect.topleft != original_drag_pos.topleft:
                            actions_taken += 1
                    else:
                        dragging_leader.rect.topleft = original_drag_pos.topleft
                        warning_message = "Invalid move!"
                        warning_message_timer = 120
                    dragging_leader = None
                    original_drag_pos = None
                    if actions_taken >= 2:
                        end_turn()
                
                elif dragging_tile:
                    current_player = players[current_player_index]
                    current_discard_area = player1_discard_area if current_player == player1 else player2_discard_area
                    if current_discard_area.collidepoint(dragging_tile.rect.center):
                        if dragging_tile not in tiles_marked_for_discard:
                            tiles_marked_for_discard.append(dragging_tile)
                    else:
                        if dragging_tile in tiles_marked_for_discard:
                            tiles_marked_for_discard.remove(dragging_tile)
                        
                        new_pos_tuple = snap_to_grid(dragging_tile.rect.center)
                        if is_valid_move(dragging_tile, new_pos_tuple, players):
                            dragging_tile.rect.topleft = new_pos_tuple
                            if dragging_tile.rect.topleft != original_drag_pos.topleft:
                                actions_taken += 1
                            update_score(dragging_tile)
                        else:
                            dragging_tile.rect.topleft = original_drag_pos.topleft
                            warning_message = "Invalid move!"
                            warning_message_timer = 120
                    dragging_tile = None
                    original_drag_pos = None
                    if actions_taken >= 2:
                        end_turn()

        elif event.type == pygame.MOUSEMOTION:
            if dragging_leader:
                dragging_leader.rect.center = mouse_pos
            if dragging_tile:
                dragging_tile.rect.center = mouse_pos


    screen.fill(desert)
    for x in range(grid_width):
        for y in range(grid_height):
            pygame.draw.rect(
                screen,
                black,
                (
                    board_left_x + x * tile_size,
                    board_top_y + y * tile_size,
                    tile_size,
                    tile_size,
                ),
                1,
            )
            if (x, y) in river_tiles:
                pygame.draw.rect(
                    screen,
                    river,
                    (
                        board_left_x + x * tile_size + 1,
                        board_top_y + y * tile_size + 1,
                        tile_size - 2,
                        tile_size - 2,
                    ),
                )

    pygame.draw.rect(
        screen,
        black,
        (
            board_left_x - 1,
            board_top_y,
            screen_width + 2,
            grid_height * tile_size,
        ),
        2,
    )

    pygame.draw.rect(
        screen,
        black,
        (player_space_x1, window_height - player_space_height - 20, player_space_width, player_space_height),
        2,
    )
    pygame.draw.rect(
        screen,
        black,
        (player_space_x2, window_height - player_space_height - 20, player_space_width, player_space_height),
        2,
    )

    # Draw discard areas
    pygame.draw.rect(screen, dark_grey, player1_discard_area)
    font = pygame.font.Font(None, 24)
    discard_text1 = font.render("P1 Discard", True, (255,255,255)) # white text
    screen.blit(discard_text1, (player1_discard_area.x + 10, player1_discard_area.y + 10))

    pygame.draw.rect(screen, dark_grey, player2_discard_area)
    discard_text2 = font.render("P2 Discard", True, (255,255,255))
    screen.blit(discard_text2, (player2_discard_area.x + 10, player2_discard_area.y + 10))

    # Draw undo button
    undo_button_rect = pygame.Rect(undo_button_x, undo_button_y, undo_button_width, undo_button_height)
    button_color = undo_button_hover_color if undo_button_rect.collidepoint(mouse_pos) else undo_button_color
    pygame.draw.rect(screen, button_color, undo_button_rect)

    font = pygame.font.Font(None, 36)
    undo_text = font.render("Undo", True, black)
    text_rect = undo_text.get_rect(center=undo_button_rect.center)
    screen.blit(undo_text, text_rect)

    # Draw end turn button
    end_turn_button_rect = pygame.Rect(end_turn_button_x, end_turn_button_y, end_turn_button_width, end_turn_button_height)
    end_turn_color = end_turn_button_hover_color if end_turn_button_rect.collidepoint(mouse_pos) else end_turn_button_color
    pygame.draw.rect(screen, end_turn_color, end_turn_button_rect)

    end_turn_text = font.render("End Turn", True, black)
    end_turn_text_rect = end_turn_text.get_rect(center=end_turn_button_rect.center)
    screen.blit(end_turn_text, end_turn_text_rect)

    # Draw Replace Tiles button
    replace_button_rect = pygame.Rect(replace_button_x, replace_button_y, replace_button_width, replace_button_height)
    replace_color = replace_button_hover_color if replace_button_rect.collidepoint(mouse_pos) else replace_button_color
    pygame.draw.rect(screen, replace_color, replace_button_rect)

    replace_text = font.render("Replace Tiles", True, black)
    replace_text_rect = replace_text.get_rect(center=replace_button_rect.center)
    screen.blit(replace_text, replace_text_rect)

    for tile in board_tiles:
        screen.blit(tile.image, tile.rect)

    for player in players:
        for leader in player.leaders.values():
            screen.blit(leader.image, leader.rect)
        for tile in player.hand:
            screen.blit(tile.image, tile.rect)

    draw_scoreboard()
    if warning_message_timer > 0:
        text = warning_font.render(warning_message, True, red)
        text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
        screen.blit(text, text_rect)
        warning_message_timer -= 1
    else:
        warning_message = ""
    
    pygame.display.flip()

