import random
from game_objects import Tile, Monument
from assets import other_tokens
import config

def create_tile_bag():
    bag = []
    # Red (Temples): 57 tiles
    for _ in range(57):
        bag.append(Tile("monument", other_tokens["monument"]))
    # Blue (Farms): 36 tiles
    for _ in range(36):
        bag.append(Tile("farm", other_tokens["farm"]))
    # Black (Settlements): 30 tiles
    for _ in range(30):
        bag.append(Tile("city", other_tokens["city"]))
    # Green (Markets): 30 tiles
    for _ in range(30):
        bag.append(Tile("market", other_tokens["market"]))
    random.shuffle(bag)
    return bag

def snap_to_grid(pos):
    x = (pos[0] - config.board_left_x) // config.tile_size
    y = (pos[1] - config.board_top_y) // config.tile_size
    if 0 <= x < config.grid_width and 0 <= y < config.grid_height:
        return (config.board_left_x + x * config.tile_size,
                config.board_top_y + y * config.tile_size)
    return pos

def save_previous_positions(players, previous_leader_positions, previous_hand_positions):
    previous_leader_positions.clear()
    previous_hand_positions.clear()
    for p in players:
        previous_leader_positions[p.name] = {color: leader.rect.copy() for color, leader in p.leaders.items()}
        previous_hand_positions[p.name] = [tile.rect.copy() for tile in p.hand]

def undo_last_move(players, previous_leader_positions, previous_hand_positions):
    if previous_leader_positions and previous_hand_positions:
        for p in players:
            if p.name in previous_leader_positions:
                for color, rect in previous_leader_positions[p.name].items():
                    p.leaders[color].rect = rect
            if p.name in previous_hand_positions:
                for i, rect in enumerate(previous_hand_positions[p.name]):
                    if i < len(p.hand):
                        p.hand[i].rect = rect

def get_tile_at(grid_x, grid_y, players, board_tiles, board_monuments, ignore_piece=None):
    # Check board_monuments
    for m in board_monuments:
        if m is ignore_piece:
            continue
        m_x = (m.rect.x - config.board_left_x) // config.tile_size
        m_y = (m.rect.y - config.board_top_y) // config.tile_size
        if m_x <= grid_x < m_x + 2 and m_y <= grid_y < m_y + 2:
            return m

    # Check board_tiles
    for t in board_tiles:
        if t is ignore_piece:
            continue
        t_x = (t.rect.x - config.board_left_x) // config.tile_size
        t_y = (t.rect.y - config.board_top_y) // config.tile_size
        if t_x == grid_x and t_y == grid_y:
            return t

    # Check leaders and hands of players
    for p in players:
        for l in p.leaders.values():
            if l is ignore_piece:
                continue
            if l.rect.left >= config.board_left_x and l.rect.top < config.board_top_y + config.grid_height * config.tile_size:
                l_x = (l.rect.x - config.board_left_x) // config.tile_size
                l_y = (l.rect.y - config.board_top_y) // config.tile_size
                if l_x == grid_x and l_y == grid_y:
                    return l
        for t in p.hand:
            if t is ignore_piece:
                continue
            if t.rect.left < config.board_left_x + config.screen_width and \
               t.rect.top < config.board_top_y + config.grid_height * config.tile_size and \
               t.rect.left >= config.board_left_x and \
               t.rect.top >= config.board_top_y:
                t_x = (t.rect.x - config.board_left_x) // config.tile_size
                t_y = (t.rect.y - config.board_top_y) // config.tile_size
                if t_x == grid_x and t_y == grid_y:
                    return t
    return None


def get_kingdom(grid_x, grid_y, players, board_tiles, board_monuments, ignore_piece=None):
    if get_tile_at(grid_x, grid_y, players, board_tiles, board_monuments, ignore_piece) is None:
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

            if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height and (nx, ny) not in visited:
                if get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece) is not None:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return kingdom

def is_valid_move(piece, pos, players, board_tiles, board_monuments):
    grid_x = (pos[0] - config.board_left_x) // config.tile_size
    grid_y = (pos[1] - config.board_top_y) // config.tile_size

    if not (0 <= grid_x < config.grid_width and 0 <= grid_y < config.grid_height):
        return False

    occupant = get_tile_at(grid_x, grid_y, players, board_tiles, board_monuments, ignore_piece=piece)
    if occupant is not None:
        return False

    if piece.tile_type == "farm":
        if (grid_x, grid_y) not in config.river_tiles:
            return False
    elif (grid_x, grid_y) in config.river_tiles:
        return False

    if "leader" in piece.tile_type:
        leader_color = piece.tile_type.split('_')[0]

        is_adjacent_to_monument = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
                adjacent_tile = get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=piece)
                if adjacent_tile and adjacent_tile.tile_type == "monument":
                    is_adjacent_to_monument = True
                    break
        if not is_adjacent_to_monument:
            return False

        adjacent_kingdoms = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
                if get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=piece) is not None:
                    is_new_kingdom = True
                    for k in adjacent_kingdoms:
                        if (nx, ny) in k:
                            is_new_kingdom = False
                            break
                    if is_new_kingdom:
                        adjacent_kingdoms.append(get_kingdom(nx, ny, players, board_tiles, board_monuments, ignore_piece=piece))

        for kingdom in adjacent_kingdoms:
            for kx, ky in kingdom:
                tile_in_kingdom = get_tile_at(kx, ky, players, board_tiles, board_monuments, ignore_piece=piece)
                if isinstance(tile_in_kingdom, Monument):
                    continue
                if tile_in_kingdom and "leader" in tile_in_kingdom.tile_type:
                    if tile_in_kingdom.tile_type.split('_')[0] == leader_color:
                        if tile_in_kingdom != piece:
                            return False
    return True

def update_score(placed_tile, players, board_tiles, board_monuments):
    tile_x = (placed_tile.rect.x - config.board_left_x) // config.tile_size
    tile_y = (placed_tile.rect.y - config.board_top_y) // config.tile_size
    
    placed_color = config.tile_color_map.get(placed_tile.tile_type)
    if not placed_color:
        return

    kingdom = get_kingdom(tile_x, tile_y, players, board_tiles, board_monuments)
    if not kingdom:
        return

    leader_found = False
    for kx, ky in kingdom:
        tile_in_kingdom = get_tile_at(kx, ky, players, board_tiles, board_monuments)
        if isinstance(tile_in_kingdom, Monument):
            continue
        if tile_in_kingdom and "leader" in tile_in_kingdom.tile_type:
            leader_color_in_kingdom = tile_in_kingdom.tile_type.split('_')[0]
            if leader_color_in_kingdom == placed_color:
                for p in players:
                    if tile_in_kingdom in p.leaders.values():
                        p.score[placed_color] += 1
                        leader_found = True
                        break
                if leader_found:
                    break
    
    if leader_found:
        return

    king_found = False
    for kx, ky in kingdom:
        tile_in_kingdom = get_tile_at(kx, ky, players, board_tiles, board_monuments)
        if isinstance(tile_in_kingdom, Monument):
            continue
        if tile_in_kingdom and tile_in_kingdom.tile_type == "black_leader":
            for p in players:
                if tile_in_kingdom in p.leaders.values():
                    p.score[placed_color] += 1
                    king_found = True
                    break
            if king_found:
                break

def get_tile_color(tile):
    if not tile:
        return None
    if isinstance(tile, Monument):
        return None
    if isinstance(tile, Tile):
        return config.tile_color_map.get(tile.tile_type)
    return None

def check_for_monument(grid_x, grid_y, players, board_tiles, board_monuments):
    # Check the four 2x2 squares that include the new tile
    for dx, dy in [(-1, -1), (-1, 0), (0, -1), (0, 0)]:
        top_left_x, top_left_y = grid_x + dx, grid_y + dy
        
        # Coordinates of the four tiles in the 2x2 square
        coords = [
            (top_left_x, top_left_y), (top_left_x + 1, top_left_y),
            (top_left_x, top_left_y + 1), (top_left_x + 1, top_left_y + 1)
        ]
        
        # Check if all tiles are on the board and of the same color
        first_tile = get_tile_at(coords[0][0], coords[0][1], players, board_tiles, board_monuments) # Corrected: added players, board_tiles, board_monuments arguments
        if not first_tile:
            continue
            
        first_color = get_tile_color(first_tile)
        if not first_color:
            continue
            
        all_match = True
        for x, y in coords[1:]:
            tile = get_tile_at(x, y, players, board_tiles, board_monuments)
            if not tile or get_tile_color(tile) != first_color:
                all_match = False
                break
        
        if all_match:
            return (top_left_x, top_left_y), first_color
            
    return None, None

def score_monuments(players, board_tiles, board_monuments):
    for monument in board_monuments:
        monument_x = (monument.rect.x - config.board_left_x) // config.tile_size
        monument_y = (monument.rect.y - config.board_top_y) // config.tile_size
        
        kingdom = get_kingdom(monument_x, monument_y, players, board_tiles, board_monuments)
        
        for color in monument.colors:
            for player in players:
                leader_in_kingdom = False
                for kx, ky in kingdom:
                    piece = get_tile_at(kx, ky, players, board_tiles, board_monuments)
                    if isinstance(piece, Tile) and piece.tile_type == f"{color}_leader" and piece in player.leaders.values():
                        leader_in_kingdom = True
                        break
                if leader_in_kingdom:
                    player.score[color] += 1

def end_turn(current_player_index, players, tile_bag, board_tiles, board_monuments):
    current_player = players[current_player_index]
    
    placed_tiles = [
        tile for tile in current_player.hand 
        if tile.rect.left < config.board_left_x + config.screen_width and
           tile.rect.top < config.board_top_y + config.grid_height * config.tile_size and
           tile.rect.left >= config.board_left_x and
           tile.rect.top >= config.board_top_y
    ]

    for tile in placed_tiles:
        grid_x = (tile.rect.x - config.board_left_x) // config.tile_size
        grid_y = (tile.rect.y - config.board_top_y) // config.tile_size
        monument_pos, monument_color = check_for_monument(grid_x, grid_y, players, board_tiles, board_monuments)
        if monument_pos:
            board_tiles.extend(placed_tiles)
            return current_player_index, 0, board_tiles, monument_pos, monument_color

    board_tiles.extend(placed_tiles)
    score_monuments(players, board_tiles, board_monuments)

    current_player.hand = [tile for tile in current_player.hand if tile not in placed_tiles]
    
    current_player.refill_hand(tile_bag)
    current_player_index = (current_player_index + 1) % len(players)
    actions_taken = 0
    
    return current_player_index, actions_taken, board_tiles, None, None

def remove_tile_at(grid_x, grid_y, players, board_tiles):
    # Check board_tiles
    for t in board_tiles:
        t_x = (t.rect.x - config.board_left_x) // config.tile_size
        t_y = (t.rect.y - config.board_top_y) // config.tile_size
        if t_x == grid_x and t_y == grid_y:
            board_tiles.remove(t)
            return

    # Check hands of players
    for p in players:
        for t in p.hand:
            if t.rect.left >= config.board_left_x and t.rect.top >= config.board_top_y:
                t_x = (t.rect.x - config.board_left_x) // config.tile_size
                t_y = (t.rect.y - config.board_top_y) // config.tile_size
                if t_x == grid_x and t_y == grid_y:
                    p.hand.remove(t)
                    return