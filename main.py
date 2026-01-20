import pygame
import sys
from config import *
from assets import monument_with_treasure
from game_objects import Player, Tile, create_monuments
from game_logic import (
    create_tile_bag,
    snap_to_grid,
    save_previous_positions,
    undo_last_move,
    is_valid_move,
    update_score,
    end_turn,
    check_for_monument,
    remove_tile_at,
)
from drawing import (
    draw_board,
    draw_player_areas,
    draw_pieces,
    draw_scoreboard,
    draw_warning_message,
    draw_monument_choices,
)
from ui import (
    draw_undo_button,
    draw_end_turn_button,
    draw_replace_button,
    handle_monument_choice,
)

def calculate_winner(players):
    for player in players:
        player.treasures_as_wild = player.treasures
    
    for player in players:
        sorted_scores = sorted(player.score.values())
        player.final_score = sorted_scores[0] + player.treasures_as_wild

    winner = None
    max_score = -1

    for player in players:
        if player.final_score > max_score:
            max_score = player.final_score
            winner = player
        elif player.final_score == max_score:
            # Tie-breaking logic
            # Compare second-weakest, then third, etc.
            p1_scores = sorted(player.score.values())
            w_scores = sorted(winner.score.values())
            for i in range(1, 4):
                if p1_scores[i] > w_scores[i]:
                    winner = player
                    break
                elif p1_scores[i] < w_scores[i]:
                    break
    
    return winner

def main():
    tile_bag = create_tile_bag()
    color_map = {"red": red, "blue": blue, "green": green, "black": black}
    available_monuments = create_monuments(color_map)

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
    board_monuments = []
    game_state = 'GAME'
    monument_data = None
    monument_choice_rects = []
    winner = None

    for (x, y) in monument_with_treasure_tiles:
        monument_tile = Tile("monument", monument_with_treasure, has_treasure=True)
        monument_tile.rect.topleft = (
            board_left_x + x * tile_size,
            board_top_y + y * tile_size,
        )
        is_occupied = False
        for t in board_tiles:
            if t.rect.topleft == monument_tile.rect.topleft:
                is_occupied = True
                break
        if not is_occupied:
            board_tiles.append(monument_tile)

    warning_message = ""
    warning_message_timer = 0

    previous_leader_positions = {}
    previous_hand_positions = {}

    dragging_tile = None
    dragging_leader = None
    original_drag_pos = None

    while True:
        mouse_pos = pygame.mouse.get_pos()

        if game_state == 'GAME_OVER':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            draw_board(screen)
            draw_player_areas(screen)
            draw_pieces(screen, board_tiles, players, board_monuments)
            draw_scoreboard(screen, players, current_player_index)

            if winner:
                winner_text = f"Winner: {winner.name}"
                winner_font = pygame.font.Font(None, 100)
                text_surface = winner_font.render(winner_text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(window_width // 2, window_height // 2))
                screen.blit(text_surface, text_rect)

            pygame.display.flip()
            continue
        
        if game_state == 'AWAITING_MONUMENT_CHOICE':
            monument_pos, monument_color = monument_data
            
            # Filter monuments
            possible_monuments = []
            if monument_color == 'black':
                # Special rule for black tiles
                for monument in available_monuments:
                    if monument_color in monument.colors and monument.colors[0] != 'black':
                        possible_monuments.append(monument)
            else:
                for monument in available_monuments:
                    if monument_color in monument.colors:
                        possible_monuments.append(monument)
            
            if not possible_monuments:
                warning_message = "No valid monuments available to place."
                warning_message_timer = 120
                game_state = 'GAME'
                monument_data = None
                continue
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    selected_monument_index = handle_monument_choice(mouse_pos, monument_choice_rects)
                    if selected_monument_index is not None:
                        selected_monument = possible_monuments[selected_monument_index]
                        # Place monument
                        monument_x, monument_y = monument_pos
                        
                        selected_monument.rect.topleft = (
                            board_left_x + monument_x * tile_size,
                            board_top_y + monument_y * tile_size
                        )
                        board_monuments.append(selected_monument)
                        if selected_monument in available_monuments:
                            available_monuments.remove(selected_monument)
                        
                        # Remove underlying tiles
                        for dx in range(2):
                            for dy in range(2):
                                remove_tile_at(monument_x + dx, monument_y + dy, players, board_tiles)
                        
                        game_state = 'GAME'
                        monument_data = None
            
            draw_board(screen)
            draw_player_areas(screen)
            draw_pieces(screen, board_tiles, players, board_monuments)
            monument_choice_rects = draw_monument_choices(screen, possible_monuments)
            pygame.display.flip()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    end_turn_button_rect = pygame.Rect(end_turn_button_x, end_turn_button_y, end_turn_button_width, end_turn_button_height)
                    if end_turn_button_rect.collidepoint(mouse_pos):
                        current_player_index, actions_taken, board_tiles, monument_pos, monument_color, game_over, message = end_turn(current_player_index, players, tile_bag, board_tiles, board_monuments)
                        if message:
                            warning_message = message
                            warning_message_timer = 120
                        if game_over:
                            winner = calculate_winner(players)
                            game_state = 'GAME_OVER'
                        elif monument_pos:
                            game_state = 'AWAITING_MONUMENT_CHOICE'
                            monument_data = (monument_pos, monument_color)
                        tiles_marked_for_discard.clear()
                        continue

                    replace_button_rect = pygame.Rect(replace_button_x, replace_button_y, replace_button_width, replace_button_height)
                    if replace_button_rect.collidepoint(mouse_pos):
                        if actions_taken < 2 and 0 < len(tiles_marked_for_discard) <= 5:
                            actions_taken += 1
                            current_player = players[current_player_index]
                            for tile in tiles_marked_for_discard:
                                if tile in current_player.hand:
                                    current_player.hand.remove(tile)
                                    discard_pile.append(tile)
                            if not current_player.refill_hand(tile_bag):
                                warning_message = f"{current_player.name} cannot draw enough tiles from the bag!"
                                warning_message_timer = 120
                                winner = calculate_winner(players)
                                game_state = 'GAME_OVER'
                            tiles_marked_for_discard.clear()
                            if actions_taken >= 2:
                                current_player_index, actions_taken, board_tiles, monument_pos, monument_color, game_over, message = end_turn(current_player_index, players, tile_bag, board_tiles, board_monuments)
                                if message:
                                    warning_message = message
                                    warning_message_timer = 120
                                if game_over:
                                    winner = calculate_winner(players)
                                    game_state = 'GAME_OVER'
                                elif monument_pos:
                                    game_state = 'AWAITING_MONUMENT_CHOICE'
                                    monument_data = (monument_pos, monument_color)
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
                        undo_button_rect = pygame.Rect(undo_button_x, undo_button_y, undo_button_width, undo_button_height)
                        if undo_button_rect.collidepoint(mouse_pos):
                            undo_last_move(players, previous_leader_positions, previous_hand_positions)
                            continue

                        current_player = players[current_player_index]
                        for color, leader in current_player.leaders.items():
                            if leader.rect.collidepoint(mouse_pos):
                                save_previous_positions(players, previous_leader_positions, previous_hand_positions)
                                dragging_leader = leader
                                original_drag_pos = leader.rect.copy()
                                break
                        if not dragging_leader:
                            for tile in current_player.hand:
                                if tile.rect.collidepoint(mouse_pos):
                                    save_previous_positions(players, previous_leader_positions, previous_hand_positions)
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
                        if is_valid_move(dragging_leader, new_pos_tuple, players, board_tiles, board_monuments):
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
                            current_player_index, actions_taken, board_tiles, monument_pos, monument_color, game_over, message = end_turn(current_player_index, players, tile_bag, board_tiles, board_monuments)
                            if message:
                                warning_message = message
                                warning_message_timer = 120
                            if game_over:
                                winner = calculate_winner(players)
                                game_state = 'GAME_OVER'
                            elif monument_pos:
                                game_state = 'AWAITING_MONUMENT_CHOICE'
                                monument_data = (monument_pos, monument_color)                    
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
                            if is_valid_move(dragging_tile, new_pos_tuple, players, board_tiles, board_monuments):
                                dragging_tile.rect.topleft = new_pos_tuple
                                if dragging_tile.rect.topleft != original_drag_pos.topleft:
                                    actions_taken += 1
                                
                                # Move tile from hand to board
                                current_player.hand.remove(dragging_tile)
                                board_tiles.append(dragging_tile)
                                
                                update_score(dragging_tile, players, board_tiles, board_monuments)

                                grid_x = (new_pos_tuple[0] - board_left_x) // tile_size
                                grid_y = (new_pos_tuple[1] - board_top_y) // tile_size
                                
                                monument_pos, monument_color = check_for_monument(grid_x, grid_y, players, board_tiles, board_monuments)
                                if monument_pos:
                                    game_state = 'AWAITING_MONUMENT_CHOICE'
                                    monument_data = (monument_pos, monument_color)
                            else:
                                dragging_tile.rect.topleft = original_drag_pos.topleft
                                warning_message = "Invalid move!"
                                warning_message_timer = 120
                        dragging_tile = None
                        original_drag_pos = None
                        if actions_taken >= 2:
                            current_player_index, actions_taken, board_tiles, monument_pos, monument_color, game_over, message = end_turn(current_player_index, players, tile_bag, board_tiles, board_monuments)
                            if message:
                                warning_message = message
                                warning_message_timer = 120
                            if game_over:
                                winner = calculate_winner(players)
                                game_state = 'GAME_OVER'
                            elif monument_pos:
                                game_state = 'AWAITING_MONUMENT_CHOICE'
                                monument_data = (monument_pos, monument_color)

            elif event.type == pygame.MOUSEMOTION:
                if dragging_leader:
                    dragging_leader.rect.center = mouse_pos
                if dragging_tile:
                    dragging_tile.rect.center = mouse_pos

        draw_board(screen)
        draw_player_areas(screen)
        
        draw_undo_button(screen, mouse_pos)
        draw_end_turn_button(screen, mouse_pos)
        draw_replace_button(screen, mouse_pos)
        
        draw_pieces(screen, board_tiles, players, board_monuments)
        draw_scoreboard(screen, players, current_player_index)

        if warning_message_timer > 0:
            draw_warning_message(screen, warning_message)
            warning_message_timer -= 1
        else:
            warning_message = ""
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
