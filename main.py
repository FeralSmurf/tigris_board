import pygame
import sys
from config import *
from assets import temple_with_treasure
from game_objects import Player, Tile
from game_logic import (
    create_tile_bag,
    snap_to_grid,
    save_previous_positions,
    undo_last_move,
    is_valid_move,
    update_score,
    end_turn,
)
from drawing import (
    draw_board,
    draw_player_areas,
    draw_pieces,
    draw_scoreboard,
    draw_warning_message,
)
from ui import (
    draw_undo_button,
    draw_end_turn_button,
    draw_replace_button,
)

def main():
    tile_bag = create_tile_bag()

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

    previous_leader_positions = {}
    previous_hand_positions = {}

    dragging_tile = None
    dragging_leader = None
    original_drag_pos = None

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    end_turn_button_rect = pygame.Rect(end_turn_button_x, end_turn_button_y, end_turn_button_width, end_turn_button_height)
                    if end_turn_button_rect.collidepoint(mouse_pos):
                        current_player_index, actions_taken, board_tiles = end_turn(current_player_index, players, tile_bag, board_tiles)
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
                            current_player.refill_hand(tile_bag)
                            tiles_marked_for_discard.clear()
                            if actions_taken >= 2:
                                current_player_index, actions_taken, board_tiles = end_turn(current_player_index, players, tile_bag, board_tiles)
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
                        if is_valid_move(dragging_leader, new_pos_tuple, players, board_tiles):
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
                            current_player_index, actions_taken, board_tiles = end_turn(current_player_index, players, tile_bag, board_tiles)
                    
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
                            if is_valid_move(dragging_tile, new_pos_tuple, players, board_tiles):
                                dragging_tile.rect.topleft = new_pos_tuple
                                if dragging_tile.rect.topleft != original_drag_pos.topleft:
                                    actions_taken += 1
                                update_score(dragging_tile, players, board_tiles)
                            else:
                                dragging_tile.rect.topleft = original_drag_pos.topleft
                                warning_message = "Invalid move!"
                                warning_message_timer = 120
                        dragging_tile = None
                        original_drag_pos = None
                        if actions_taken >= 2:
                            current_player_index, actions_taken, board_tiles = end_turn(current_player_index, players, tile_bag, board_tiles)

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
        
        draw_pieces(screen, board_tiles, players)
        draw_scoreboard(screen, players, current_player_index)

        if warning_message_timer > 0:
            draw_warning_message(screen, warning_message)
            warning_message_timer -= 1
        else:
            warning_message = ""
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
