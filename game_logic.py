import random
from game_objects import Tile, Monument
from assets import other_tokens, monument_without_treasure
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


def get_tile_color(tile):
    if not tile:
        return None
    if isinstance(tile, Monument):
        return None
    if isinstance(tile, Tile):
        return config.tile_color_map.get(tile.tile_type)
    return None


def get_kingdom(grid_x, grid_y, players, board_tiles, board_monuments, ignore_piece=None):
    start_tile = get_tile_at(grid_x, grid_y, players, board_tiles, board_monuments, ignore_piece)
    if not start_tile:
        return set()
    
    # It doesn't matter the color of the tiles. Any group of contiguous tiles is a kingdom
    # kingdom_color = get_tile_color(start_tile)
    # if kingdom_color is None:
    #     return set()

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
                tile = get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece)
                if tile:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return kingdom

def is_valid_move(piece, pos, players, board_tiles, board_monuments):
    print(f"\n--- Inside is_valid_move for {piece.tile_type if hasattr(piece, 'tile_type') else 'Monument type'} at {pos} ---")

    grid_x = (pos[0] - config.board_left_x) // config.tile_size
    grid_y = (pos[1] - config.board_top_y) // config.tile_size

    if not (0 <= grid_x < config.grid_width and 0 <= grid_y < config.grid_height):
        print("  -> Invalid: Outside board boundaries.")
        return False

    occupant = get_tile_at(grid_x, grid_y, players, board_tiles, board_monuments, ignore_piece=piece)
    if occupant is not None:
        print(f"  -> Invalid: Space occupied by {occupant.tile_type if hasattr(occupant, 'tile_type') else 'Monument type'}.")
        return False

    if piece.tile_type == "farm":
        if (grid_x, grid_y) not in config.river_tiles:
            print("  -> Invalid: Farm not on river tile.")
            return False
    elif (grid_x, grid_y) in config.river_tiles:
        print("  -> Invalid: Non-farm piece on river tile.")
        return False

    if isinstance(piece, Tile) and "leader" in piece.tile_type:
        print("  -> Piece is a leader. Checking specific rules.")
        leader_color = piece.tile_type.split('_')[0]

        is_adjacent_to_monument = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
                adjacent_tile = get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=piece)
                if adjacent_tile:
                    print(f"    -> Neighbor at ({nx},{ny}) is: {adjacent_tile.tile_type if hasattr(adjacent_tile, 'tile_type') else 'Monument type'}")
                if (adjacent_tile and isinstance(adjacent_tile, Monument)) or \
                   (adjacent_tile and isinstance(adjacent_tile, Tile) and adjacent_tile.tile_type == "monument"):
                    is_adjacent_to_monument = True
                    print("    -> Valid: Adjacent to monument.")
                    break
        if not is_adjacent_to_monument:
            print("  -> Invalid: Not adjacent to any monument.")
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


    print("--- is_valid_move: Returning True ---")
    return True

def get_kingdom_leaders(kingdom, players, board_tiles, board_monuments, ignore_piece=None):
    leaders = []
    if not kingdom:
        return leaders
    
    for kx, ky in kingdom:
        piece = get_tile_at(kx, ky, players, board_tiles, board_monuments, ignore_piece=ignore_piece)
        if piece and isinstance(piece, Tile) and "leader" in piece.tile_type:
            leaders.append(piece)
    return leaders

def update_score(placed_tile, players, board_tiles, board_monuments):
    tile_x = (placed_tile.rect.x - config.board_left_x) // config.tile_size
    tile_y = (placed_tile.rect.y - config.board_top_y) // config.tile_size
    
    placed_color = config.tile_color_map.get(placed_tile.tile_type)
    if not placed_color:
        return

    kingdom = get_kingdom(tile_x, tile_y, players, board_tiles, board_monuments)
    if not kingdom:
        return

    kingdom_leaders = get_kingdom_leaders(kingdom, players, board_tiles, board_monuments)

    # Score for leader of same color
    leader_found = False
    for leader in kingdom_leaders:
        leader_color = leader.tile_type.split('_')[0]
        if leader_color == placed_color:
            for p in players:
                if leader in p.leaders.values():
                    p.score[placed_color] += 1
                    print(f"SCORE: {p.name} scores 1 point in {placed_color} via {leader.tile_type}. New score: {p.score[placed_color]}")
                    leader_found = True
                    break # score once per tile placement for this color
            if leader_found:
                break
    
    if leader_found:
        return

    # Score for king (black leader) if no other leader of the right color scored
    for leader in kingdom_leaders:
        if "black_leader" in leader.tile_type:
            for p in players:
                if leader in p.leaders.values():
                    p.score[placed_color] += 1
                    print(f"SCORE: {p.name} scores 1 point in {placed_color} via black leader. New score: {p.score[placed_color]}")
                    return # Score once per tile placement

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
        first_tile = get_tile_at(coords[0][0], coords[0][1], players, board_tiles, board_monuments)
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
        
        # Find all unique kingdoms adjacent to the monument
        adjacent_kingdoms = []
        for i in range(2):
            for j in range(2):
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = monument_x + i + dx, monument_y + j + dy
                    
                    # Ensure adjacent tile is on board and not part of the monument itself
                    on_board = 0 <= nx < config.grid_width and 0 <= ny < config.grid_height
                    part_of_monument = monument_x <= nx < monument_x + 2 and monument_y <= ny < monument_y + 2
                    if not (on_board and not part_of_monument):
                        continue

                    # If it's a tile, get its kingdom
                    if get_tile_at(nx, ny, players, board_tiles, board_monuments):
                        kingdom = get_kingdom(nx, ny, players, board_tiles, board_monuments)
                        if kingdom and kingdom not in adjacent_kingdoms:
                            adjacent_kingdoms.append(kingdom)

        # Now score for each color of the monument
        for color in monument.colors:
            for p in players:
                player_has_leader_for_color = False
                for kingdom in adjacent_kingdoms:
                    leaders = get_kingdom_leaders(kingdom, players, board_tiles, board_monuments)
                    for leader in leaders:
                        if leader in p.leaders.values() and leader.tile_type.split('_')[0] == color:
                            p.score[color] += 1
                            player_has_leader_for_color = True
                            break # Found leader for this player and color, break from leaders loop
                    if player_has_leader_for_color:
                        break # break from kingdoms loop

def claim_treasures(players, board_tiles, board_monuments):
    all_kingdoms = []
    visited_tiles = set()
    player_who_claimed = None
    treasures_claimed = 0

    for y in range(config.grid_height):
        for x in range(config.grid_width):
            if (x, y) not in visited_tiles:
                kingdom = get_kingdom(x, y, players, board_tiles, board_monuments)
                if kingdom:
                    all_kingdoms.append(kingdom)
                    visited_tiles.update(kingdom)

    for kingdom in all_kingdoms:
        treasures_in_kingdom = []
        for kx, ky in kingdom:
            tile = get_tile_at(kx, ky, players, board_tiles, board_monuments)
            if tile and isinstance(tile, Tile) and tile.has_treasure:
                treasures_in_kingdom.append(tile)

        if len(treasures_in_kingdom) > 1:
            trader_owner = None
            kingdom_leaders = get_kingdom_leaders(kingdom, players, board_tiles, board_monuments)
            for leader in kingdom_leaders:
                if leader.tile_type == "green_leader":
                    for p in players:
                        if leader in p.leaders.values():
                            trader_owner = p
                            break
                if trader_owner:
                    break
            
            if trader_owner:
                # For now, we will award all but one treasure. The rules about corner treasures are not implemented.
                num_treasures_to_award = len(treasures_in_kingdom) - 1
                trader_owner.treasures += num_treasures_to_award
                player_who_claimed = trader_owner.name
                treasures_claimed = num_treasures_to_award
                for i in range(num_treasures_to_award):
                    treasures_in_kingdom[i].has_treasure = False
                    treasures_in_kingdom[i].image = monument_without_treasure
    
    return player_who_claimed, treasures_claimed


def end_turn(current_player_index, players, tile_bag, board_tiles, board_monuments):
    current_player = players[current_player_index]
    message = ""
    
    # Tile placement, scoring, and monument checks are now handled in main.py's event loop.
    
    score_monuments(players, board_tiles, board_monuments)
    player_who_claimed, treasures_claimed = claim_treasures(players, board_tiles, board_monuments)
    if player_who_claimed:
        message = f"{player_who_claimed} claimed {treasures_claimed} treasures!"

    if not current_player.refill_hand(tile_bag):
        # Handle case where player cannot draw tiles
        message = f"{current_player.name} cannot draw enough tiles from the bag!"
        return current_player_index, 0, board_tiles, None, None, True, message

    game_over = check_game_end(board_tiles)
    
    current_player_index = (current_player_index + 1) % len(players)
    actions_taken = 0
    
    print(f"\n--- End of Turn ---")
    print(f"TURN: It is now {players[current_player_index].name}'s turn.")

    return current_player_index, actions_taken, board_tiles, None, None, game_over, message

def check_game_end(board_tiles):
    treasures_on_board = 0
    for tile in board_tiles:
        if tile.has_treasure:
            treasures_on_board += 1
    if treasures_on_board <= 2:
        return True
    return False

def remove_tile_at(grid_x, grid_y, players, board_tiles):
    # Check board_tiles
    tile_to_remove = None
    for t in board_tiles:
        t_x = (t.rect.x - config.board_left_x) // config.tile_size
        t_y = (t.rect.y - config.board_top_y) // config.tile_size
        if t_x == grid_x and t_y == grid_y:
            tile_to_remove = t
            break
    if tile_to_remove:
        board_tiles.remove(tile_to_remove)
        return

    # Check hands of players
    for p in players:
        tile_to_remove = None
        for t in p.hand:
            if t.rect.left >= config.board_left_x and t.rect.top >= config.board_top_y:
                t_x = (t.rect.x - config.board_left_x) // config.tile_size
                t_y = (t.rect.y - config.board_top_y) // config.tile_size
                if t_x == grid_x and t_y == grid_y:
                    tile_to_remove = t
                    break
        if tile_to_remove:
            p.hand.remove(tile_to_remove)
            return
def check_for_conflict(piece, pos, players, board_tiles, board_monuments):
    print(f"\n--- Inside check_for_conflict for {piece.tile_type} at {pos} ---")
    grid_x = (pos[0] - config.board_left_x) // config.tile_size
    grid_y = (pos[1] - config.board_top_y) // config.tile_size

    adjacent_kingdoms = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = grid_x + dx, grid_y + dy
        if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
            if get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=piece) is not None:
                print(f"  -> Found neighbor at ({nx}, {ny})")
                is_new_kingdom = True
                for k in adjacent_kingdoms:
                    if (nx, ny) in k:
                        print(f"    -> Neighbor is part of an already found kingdom.")
                        is_new_kingdom = False
                        break
                if is_new_kingdom:
                    print(f"    -> Finding new kingdom starting from ({nx}, {ny})")
                    new_kingdom = get_kingdom(nx, ny, players, board_tiles, board_monuments, ignore_piece=piece)
                    adjacent_kingdoms.append(new_kingdom)
                    print(f"    -> Found kingdom with {len(new_kingdom)} pieces.")

    print(f"  -> Found {len(adjacent_kingdoms)} adjacent kingdoms.")

    # A revolt occurs when a leader is placed in a kingdom that already has a leader of the same color.
    if isinstance(piece, Tile) and "leader" in piece.tile_type:
        leader_color = piece.tile_type.split('_')[0]
        for kingdom in adjacent_kingdoms:
            found_leaders = get_kingdom_leaders(kingdom, players, board_tiles, board_monuments, ignore_piece=piece)
            for leader in found_leaders:
                if leader.tile_type.split('_')[0] == leader_color:
                    return 'REVOLT', [leader_color]
    
    # A war happens when two kingdoms are united through the placement of a tile
    elif isinstance(piece, Tile) and "leader" not in piece.tile_type:
        if len(adjacent_kingdoms) > 1:
            all_leaders = []
            for kingdom in adjacent_kingdoms:
                all_leaders.extend(get_kingdom_leaders(kingdom, players, board_tiles, board_monuments))
            
            leader_colors = [l.tile_type.split('_')[0] for l in all_leaders]
            
            conflict_colors = []
            for color in set(leader_colors):
                if leader_colors.count(color) > 1:
                    conflict_colors.append(color)

            if conflict_colors:
                return 'WAR', conflict_colors

    return None, None

def resolve_revolt(attacker_leader, players, board_tiles, board_monuments, committed_tiles):
    # Find the kingdom and the defender
    grid_x = (attacker_leader.rect.x - config.board_left_x) // config.tile_size
    grid_y = (attacker_leader.rect.y - config.board_top_y) // config.tile_size
    leader_color = attacker_leader.tile_type.split('_')[0]
    
    defender_leader = None
    
    # Find kingdoms adjacent to the attacker leader
    adjacent_kingdoms = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = grid_x + dx, grid_y + dy
        if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
            # We ignore the attacker leader itself when finding kingdoms
            tile = get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=attacker_leader)
            if tile is not None:
                k = get_kingdom(nx, ny, players, board_tiles, board_monuments, ignore_piece=attacker_leader)
                if k and k not in adjacent_kingdoms:
                    adjacent_kingdoms.append(k)
    
    # Find a defender leader of the same color adjacent to one of these kingdoms
    for k in adjacent_kingdoms:
        # We need to check for leaders adjacent to this kingdom, but ignore the attacker we just placed
        for leader in get_kingdom_leaders(k, players, board_tiles, board_monuments, ignore_piece=attacker_leader):
            if leader.tile_type.split('_')[0] == leader_color:
                defender_leader = leader
                break
        if defender_leader:
            break
            
    if not defender_leader:
        return None, None # Should not happen if check_for_conflict is correct

    # Determine attacker and defender players
    attacker = None
    defender = None
    for player in players:
        if attacker_leader in player.leaders.values():
            attacker = player
        if defender_leader in player.leaders.values():
            defender = player

    if not attacker or not defender:
        return None, None # Should not happen

    # Count adjacent temple tiles (red monument tiles) for each leader
    attacker_temples = 0
    defender_temples = 0

    # Attacker's adjacent temples
    attacker_grid_x = (attacker_leader.rect.x - config.board_left_x) // config.tile_size
    attacker_grid_y = (attacker_leader.rect.y - config.board_top_y) // config.tile_size
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = attacker_grid_x + dx, attacker_grid_y + dy
        if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
            tile = get_tile_at(nx, ny, players, board_tiles, board_monuments)
            if tile and isinstance(tile, Tile) and tile.tile_type == 'monument':
                attacker_temples += 1

    # Defender's adjacent temples
    defender_grid_x = (defender_leader.rect.x - config.board_left_x) // config.tile_size
    defender_grid_y = (defender_leader.rect.y - config.board_top_y) // config.tile_size
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = defender_grid_x + dx, defender_grid_y + dy
        if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
            tile = get_tile_at(nx, ny, players, board_tiles, board_monuments)
            if tile and isinstance(tile, Tile) and tile.tile_type == 'monument':
                defender_temples += 1
    
    # Add committed tiles from hand
    attacker_temples += committed_tiles.get(attacker.name, 0)
    defender_temples += committed_tiles.get(defender.name, 0)
    
    # Determine winner (defender wins ties)
    if attacker_temples > defender_temples:
        winner = attacker
        loser = defender
        loser_leader = defender_leader
    else:
        winner = defender
        loser = attacker
        loser_leader = attacker_leader

    # Update score and remove loser's leader
    winner.score['red'] += 1
    loser.reset_leader(loser_leader.tile_type.split('_')[0])
    
    print(f"\n--- REVOLT RESOLVED ---")
    print(f"REVOLT: {winner.name} wins against {loser.name}.")
    print(f"      -> {loser.name}'s {loser_leader.tile_type} is removed.")
    print(f"      -> {winner.name} gains 1 red point.")
    
    return winner, loser

def get_leader_adjacent_squares(kingdom):
    adjacent_squares = set()
    for kx, ky in kingdom:
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ax, ay = kx + dx, ky + dy
            if (0 <= ax < config.grid_width and 0 <= ay < config.grid_height) and (ax, ay) not in kingdom:
                adjacent_squares.add((ax, ay))
    return adjacent_squares

def resolve_war(placing_player, placed_tile, players, board_tiles, board_monuments, committed_tiles):
    # This function is complex and has multiple potential conflicts (one for each color).
    # We will return the first winner/loser pair we find for the UI message.
    first_result = None

    # 1. Find adjacent kingdoms before the merge
    grid_x = (placed_tile.rect.x - config.board_left_x) // config.tile_size
    grid_y = (placed_tile.rect.y - config.board_top_y) // config.tile_size
    adjacent_kingdoms = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = grid_x + dx, grid_y + dy
        if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
            # Use ignore_piece to get kingdoms *before* the merge
            if get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=placed_tile) is not None:
                is_new_kingdom = True
                for k in adjacent_kingdoms:
                    if (nx, ny) in k:
                        is_new_kingdom = False
                        break
                if is_new_kingdom:
                    adjacent_kingdoms.append(get_kingdom(nx, ny, players, board_tiles, board_monuments, ignore_piece=placed_tile))
    
    if len(adjacent_kingdoms) < 2:
        return None, None

    # 2. Find all leaders and group by color
    all_leaders = []
    for kingdom in adjacent_kingdoms:
        all_leaders.extend(get_kingdom_leaders(kingdom, players, board_tiles, board_monuments))

    leaders_by_color = {}
    for leader in all_leaders:
        color = leader.tile_type.split('_')[0]
        if color not in leaders_by_color:
            leaders_by_color[color] = []
        leaders_by_color[color].append(leader)
    
    # 3. Resolve conflicts for each color
    for color, leaders in leaders_by_color.items():
        if len(leaders) < 2:
            continue # No conflict for this color

        # We assume a 2-player game, so a conflict of a color involves exactly two leaders.
        leader_A, leader_B = leaders[0], leaders[1]

        # Find owners of the leaders
        player_A, player_B = None, None
        for p in players:
            if leader_A in p.leaders.values():
                player_A = p
            if leader_B in p.leaders.values():
                player_B = p
        
        if not player_A or not player_B or player_A == player_B:
            continue # Should not happen in a 2-player game with proper setup

        # Find which pre-merge kingdom each leader belonged to
        kingdom_A, kingdom_B = None, None
        for k in adjacent_kingdoms:
            # A leader is adjacent to a kingdom if its position is in the set of squares adjacent to the kingdom
            leader_A_pos = ((leader_A.rect.x - config.board_left_x) // config.tile_size, (leader_A.rect.y - config.board_top_y) // config.tile_size)
            if leader_A_pos in get_leader_adjacent_squares(k):
                kingdom_A = k
            
            leader_B_pos = ((leader_B.rect.x - config.board_left_x) // config.tile_size, (leader_B.rect.y - config.board_top_y) // config.tile_size)
            if leader_B_pos in get_leader_adjacent_squares(k):
                kingdom_B = k

        # 5. Count tiles of the conflict color in each kingdom
        strength_A = 0
        if kingdom_A:
            for kx, ky in kingdom_A:
                tile = get_tile_at(kx, ky, players, board_tiles, board_monuments)
                if tile and get_tile_color(tile) == color:
                    strength_A += 1

        strength_B = 0
        if kingdom_B:
            for kx, ky in kingdom_B:
                tile = get_tile_at(kx, ky, players, board_tiles, board_monuments)
                if tile and get_tile_color(tile) == color:
                    strength_B += 1
        
        # 6. Add committed tiles from hand
        strength_A += committed_tiles.get(player_A.name, 0)
        strength_B += committed_tiles.get(player_B.name, 0)

        # 7. Determine attacker/defender and winner
        if placing_player == player_A:
            attacker, defender = player_A, player_B
            attacker_strength, defender_strength = strength_A, strength_B
        else: # placing_player must be player_B
            attacker, defender = player_B, player_A
            attacker_strength, defender_strength = strength_B, strength_A

        if attacker_strength > defender_strength:
            winner, loser = attacker, defender
            loser_leader = leader_B if placing_player == player_A else leader_A
            loser_kingdom = kingdom_B if placing_player == player_A else kingdom_A
        else: # Defender wins ties
            winner, loser = defender, attacker
            loser_leader = leader_A if placing_player == player_A else leader_B
            loser_kingdom = kingdom_A if placing_player == player_A else kingdom_B
        
        if first_result is None:
            first_result = (winner, loser)

        # 8. Resolve: remove loser's leader and tiles, grant points
        loser.reset_leader(loser_leader.tile_type.split('_')[0])
        
        points = 0
        if loser_kingdom:
            # Important: iterate over a copy as we are removing items
            for kx, ky in list(loser_kingdom):
                tile = get_tile_at(kx, ky, players, board_tiles, board_monuments)
                if tile and get_tile_color(tile) == color:
                    points += 1
                    remove_tile_at(kx, ky, players, board_tiles)
        winner.score[color] += points

        print(f"\n--- WAR: {color} CONFLICT RESOLVED ---")
        print(f"WAR: {winner.name} wins against {loser.name}.")
        print(f"   -> {loser.name}'s {loser_leader.tile_type} is removed.")
        print(f"   -> {winner.name} gains {points} {color} points.")

    return first_result if first_result else (None, None)


def get_players_in_conflict(conflict_type, conflict_protagonists, players, board_tiles, board_monuments):
    if conflict_type == 'REVOLT':
        attacker_leader = conflict_protagonists['attacker']
        grid_x = (attacker_leader.rect.x - config.board_left_x) // config.tile_size
        grid_y = (attacker_leader.rect.y - config.board_top_y) // config.tile_size
        leader_color = attacker_leader.tile_type.split('_')[0]
        
        defender_leader = None
        
        adjacent_kingdoms = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
                tile = get_tile_at(nx, ny, players, board_tiles, board_monuments)
                if tile is not None:
                    k = get_kingdom(nx, ny, players, board_tiles, board_monuments)
                    if k and k not in adjacent_kingdoms:
                        adjacent_kingdoms.append(k)
        
        for k in adjacent_kingdoms:
            for leader in get_kingdom_leaders(k, players, board_tiles, board_monuments):
                if leader.tile_type.split('_')[0] == leader_color:
                    defender_leader = leader
                    break
            if defender_leader:
                break
        
        attacker = None
        defender = None
        for player in players:
            if attacker_leader in player.leaders.values():
                attacker = player
            if defender_leader and defender_leader in player.leaders.values():
                defender = player
        
        return [p for p in [attacker, defender] if p is not None]

    elif conflict_type == 'WAR':
        placed_tile = conflict_protagonists['tile']
        grid_x = (placed_tile.rect.x - config.board_left_x) // config.tile_size
        grid_y = (placed_tile.rect.y - config.board_top_y) // config.tile_size

        adjacent_kingdoms = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
                tile = get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=placed_tile)
                if tile:
                    kingdom = get_kingdom(nx, ny, players, board_tiles, board_monuments, ignore_piece=placed_tile)
                    if kingdom and kingdom not in adjacent_kingdoms:
                        adjacent_kingdoms.append(kingdom)

        if len(adjacent_kingdoms) < 2:
            return []

        all_leaders = []
        for kingdom in adjacent_kingdoms:
            all_leaders.extend(get_kingdom_leaders(kingdom, players, board_tiles, board_monuments))
        
        players_in_conflict = set()
        for leader in all_leaders:
            for player in players:
                if leader in player.leaders.values():
                    players_in_conflict.add(player)
        
        return list(players_in_conflict)

    return []





