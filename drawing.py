import pygame
import config

def draw_board(screen):
    screen.fill(config.desert)
    for x in range(config.grid_width):
        for y in range(config.grid_height):
            pygame.draw.rect(
                screen,
                config.black,
                (
                    config.board_left_x + x * config.tile_size,
                    config.board_top_y + y * config.tile_size,
                    config.tile_size,
                    config.tile_size,
                ),
                1,
            )
            if (x, y) in config.river_tiles:
                pygame.draw.rect(
                    screen,
                    config.river,
                    (
                        config.board_left_x + x * config.tile_size + 1,
                        config.board_top_y + y * config.tile_size + 1,
                        config.tile_size - 2,
                        config.tile_size - 2,
                    ),
                )

    pygame.draw.rect(
        screen,
        config.black,
        (
            config.board_left_x - 1,
            config.board_top_y,
            config.screen_width + 2,
            config.grid_height * config.tile_size,
        ),
        2,
    )

def draw_player_areas(screen):
    pygame.draw.rect(
        screen,
        config.black,
        (config.player_space_x1, config.window_height - config.player_space_height - 20, config.player_space_width, config.player_space_height),
        2,
    )
    pygame.draw.rect(
        screen,
        config.black,
        (config.player_space_x2, config.window_height - config.player_space_height - 20, config.player_space_width, config.player_space_height),
        2,
    )

    # Draw discard areas
    pygame.draw.rect(screen, config.dark_grey, config.player1_discard_area)
    discard_text1 = config.discard_font.render("P1 Discard", True, (255,255,255))
    screen.blit(discard_text1, (config.player1_discard_area.x + 10, config.player1_discard_area.y + 10))

    pygame.draw.rect(screen, config.dark_grey, config.player2_discard_area)
    discard_text2 = config.discard_font.render("P2 Discard", True, (255,255,255))
    screen.blit(discard_text2, (config.player2_discard_area.x + 10, config.player2_discard_area.y + 10))


def draw_pieces(screen, board_tiles, players, board_monuments, tiles_for_conflict=[]):
    for tile in board_tiles:
        screen.blit(tile.image, tile.rect)
    for monument in board_monuments:
        screen.blit(monument.image, monument.rect)

    for player in players:
        for leader in player.leaders.values():
            screen.blit(leader.image, leader.rect)
        for tile in player.hand:
            screen.blit(tile.image, tile.rect)
            if tile in tiles_for_conflict:
                pygame.draw.rect(screen, (255, 255, 0), tile.rect, 3) # Yellow border for selected tiles

def draw_monument_choices(screen, monuments):
    # Display monument choices in the center of the screen
    num_monuments = len(monuments)
    total_width = num_monuments * 150
    start_x = (config.window_width - total_width) // 2
    y = config.window_height // 2 - 70

    drawn_rects = []
    for i, monument in enumerate(monuments):
        # Create a temporary rect for display purposes, do not modify monument.rect
        temp_rect = monument.image.get_rect()
        temp_rect.topleft = (start_x + i * 150, y)
        screen.blit(monument.image, temp_rect)
        drawn_rects.append(temp_rect)
    return drawn_rects


def draw_scoreboard(screen, players, current_player_index):
    # Display current player's turn
    current_player_name = players[current_player_index].name
    turn_text = config.turn_font.render(f"{current_player_name}'s Turn", True, config.black)
    screen.blit(turn_text, (20, 20))

    score_y_pos = config.window_height - config.player_space_height - 20 + 10 + 70 + 10 + 70 + 10 # below hand
    for i, player in enumerate(players):
        text_color = config.red if i == current_player_index else config.black
        
        score_text = f"{player.name}'s Score: "
        text = config.score_font.render(score_text, True, text_color)
        
        # Center the whole score line
        score_line_width = text.get_width() + 4 * 70 # approx width of score items
        score_start_x = player.player_space_x + (config.player_space_width - score_line_width) // 2
        
        screen.blit(text, (score_start_x, score_y_pos))
        
        score_x = score_start_x + text.get_width()
        for color, score in player.score.items():
            pygame.draw.rect(screen, pygame.Color(color), (score_x, score_y_pos, 20, 20))
            score_val_text = config.score_font.render(f"{score}", True, text_color)
            screen.blit(score_val_text, (score_x + 25, score_y_pos))
            score_x += 70

def draw_warning_message(screen, message):
    text = config.warning_font.render(message, True, config.red)
    text_rect = text.get_rect(center=(config.window_width // 2, config.window_height // 2))
    screen.blit(text, text_rect)
