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

    kingdom_color = get_tile_color(start_tile)
    if kingdom_color is None:
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
                tile = get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece)
                if tile and get_tile_color(tile) == kingdom_color:
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

    if isinstance(piece, Tile) and "leader" in piece.tile_type:
        leader_color = piece.tile_type.split('_')[0]

        is_adjacent_to_monument = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
                adjacent_tile = get_tile_at(nx, ny, players, board_tiles, board_monuments, ignore_piece=piece)
                if (adjacent_tile and isinstance(adjacent_tile, Monument)) or \
                   (adjacent_tile and isinstance(adjacent_tile, Tile) and adjacent_tile.tile_type == "monument"):
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


    return True

def get_kingdom_leaders(kingdom, players, board_tiles, board_monuments, ignore_piece=None):
    leaders = []
    if not kingdom:
        return leaders
    adjacent_squares = set()
    for kx, ky in kingdom:
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ax, ay = kx + dx, ky + dy
            if (0 <= ax < config.grid_width and 0 <= ay < config.grid_height) and (ax, ay) not in kingdom:
                adjacent_squares.add((ax, ay))
    
    for ax, ay in adjacent_squares:
        adj_piece = get_tile_at(ax, ay, players, board_tiles, board_monuments, ignore_piece=ignore_piece)
        if adj_piece and isinstance(adj_piece, Tile) and "leader" in adj_piece.tile_type:
            leaders.append(adj_piece)
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
                    leader_found = True
                    break # score once per tile placement for this color
            if leader_found:
                break
    
    if leader_found:
        return

    # Score for king (black leader) if no other leader of the right color scored
    for leader in kingdom_leaders:
        if leader.tile_type == "black_leader":
            for p in players:
                if leader in p.leaders.values():
                    p.score[placed_color] += 1
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
    grid_x = (pos[0] - config.board_left_x) // config.tile_size
    grid_y = (pos[1] - config.board_top_y) // config.tile_size

    adjacent_kingdoms = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = grid_x + dx, grid_y + dy
        if 0 <= nx < config.grid_width and 0 <= ny < config.grid_height:
            if get_tile_at(nx, ny, players, board_tiles, board_monuments) is not None:
                is_new_kingdom = True
                for k in adjacent_kingdoms:
                    if (nx, ny) in k:
                        is_new_kingdom = False
                        break
                if is_new_kingdom:
                    adjacent_kingdoms.append(get_kingdom(nx, ny, players, board_tiles, board_monuments))

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
    kingdom = None

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
                kingdom = k
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

    # Count adjacent temple tiles
    attacker_temples = 0
    defender_temples = 0

    # Attacker's adjacent temples
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = grid_x + dx, grid_y + dy
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
    
    # Add committed tiles from hand (placeholder)
    attacker_temples += committed_tiles.get(attacker.name, 0)
    defender_temples += committed_tiles.get(defender.name, 0)
    
    # Determine winner
    if attacker_temples > defender_temples:
        winner = attacker
        loser = defender
        loser_leader = defender_leader
    else: # Defender wins ties
        winner = defender
        loser = attacker
        loser_leader = attacker_leader

    # Update score and remove loser's leader
    winner.score['red'] += 1
    loser.reset_leader(loser_leader.tile_type.split('_')[0])

def get_leader_adjacent_squares(kingdom):
    adjacent_squares = set()
    for kx, ky in kingdom:
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ax, ay = kx + dx, ky + dy
            if (0 <= ax < config.grid_width and 0 <= ay < config.grid_height) and (ax, ay) not in kingdom:
                adjacent_squares.add((ax, ay))
    return adjacent_squares

def resolve_war(placing_player, placed_tile, players, board_tiles, board_monuments, committed_tiles):
    grid_x = (placed_tile.rect.x - config.board_left_x) // config.tile_size
    grid_y = (placed_tile.rect.y - config.board_top_y) // config.tile_size

    # 1. Find adjacent kingdoms
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
        return None, None

    # 2. Find all leaders in the involved kingdoms
    all_leaders = []
    for kingdom in adjacent_kingdoms:
        all_leaders.extend(get_kingdom_leaders(kingdom, players, board_tiles, board_monuments))

    # 3. Group leaders by color
    leaders_by_color = {}
    for leader in all_leaders:
        color = leader.tile_type.split('_')[0]
        if color not in leaders_by_color:
            leaders_by_color[color] = []
        leaders_by_color[color].append(leader)

    # 4. Resolve conflicts for each color
    for color, leaders in leaders_by_color.items():
        if len(leaders) > 1:
            # There is a conflict for this color
            
            # Find the players involved in this conflict
            player1 = None
            player2 = None
            for p in players:
                if leaders[0] in p.leaders.values():
                    player1 = p
                if leaders[1] in p.leaders.values():
                    player2 = p
            
            if not player1 or not player2 or player1 == player2:
                continue

            # Determine attacker and defender
            if player1 == placing_player:
                attacker = player1
                defender = player2
                attacker_leader = leaders[0] if leaders[0] in player1.leaders.values() else leaders[1]
                defender_leader = leaders[0] if leaders[0] in player2.leaders.values() else leaders[1]
            else:
                attacker = player2
                defender = player1
                attacker_leader = leaders[0] if leaders[0] in player2.leaders.values() else leaders[1]
                defender_leader = leaders[0] if leaders[0] in player1.leaders.values() else leaders[1]

            # 5. Count tiles
            attacker_tiles = 0
            defender_tiles = 0

            # Find the kingdoms of the attacker and defender
            attacker_kingdom = None
            defender_kingdom = None
            for k in adjacent_kingdoms:
                leader_grid_x = (attacker_leader.rect.x - config.board_left_x) // config.tile_size
                leader_grid_y = (attacker_leader.rect.y - config.board_top_y) // config.tile_size
                if (leader_grid_x, leader_grid_y) in get_leader_adjacent_squares(k):
                    attacker_kingdom = k
                
                leader_grid_x = (defender_leader.rect.x - config.board_left_x) // config.tile_size
                leader_grid_y = (defender_leader.rect.y - config.board_top_y) // config.tile_size
                if (leader_grid_x, leader_grid_y) in get_leader_adjacent_squares(k):
                    defender_kingdom = k

            if attacker_kingdom:
                for kx, ky in attacker_kingdom:
                    tile = get_tile_at(kx, ky, players, board_tiles, board_monuments)
                    if tile and get_tile_color(tile) == color:
                        attacker_tiles += 1
            
            if defender_kingdom:
                for kx, ky in defender_kingdom:
                    tile = get_tile_at(kx, ky, players, board_tiles, board_monuments)
                    if tile and get_tile_color(tile) == color:
                        defender_tiles += 1
            
            # 6. Add committed tiles
            attacker_tiles += committed_tiles.get(attacker.name, 0)
            defender_tiles += committed_tiles.get(defender.name, 0)

            # 7. Determine winner and resolve
            if attacker_tiles > defender_tiles:
                winner = attacker
                loser = defender
                loser_leader = defender_leader
                loser_kingdom = defender_kingdom
            else: # Defender wins ties
                winner = defender
                loser = attacker
                loser_leader = attacker_leader
                loser_kingdom = attacker_kingdom

            # Winner gets points, loser's leader and tiles of that color are removed
            points = 0
            if loser_kingdom:
                # Create a copy of the kingdom to avoid issues with removing tiles while iterating
                loser_kingdom_copy = list(loser_kingdom)
                for kx, ky in loser_kingdom_copy:
                    tile = get_tile_at(kx, ky, players, board_tiles, board_monuments)
                    if tile and get_tile_color(tile) == color:
                        points += 1
                        remove_tile_at(kx, ky, players, board_tiles)
            
            winner.score[color] += points
            loser.reset_leader(loser_leader.tile_type.split('_')[0])

    return None, None




