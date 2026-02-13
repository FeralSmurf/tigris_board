import pygame

pygame.init()

# Screen and window settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
window_width, window_height = screen.get_size()
pygame.display.set_caption("Tigris and Euphrates")

# Grid and tile settings
grid_width = 16
grid_height = 11
tile_size = 70

# Calculated screen dimensions
screen_width = grid_width * tile_size
screen_height = grid_height * tile_size + 150

# Board position
board_left_x = (window_width - screen_width) // 2
board_top_y = (window_height - screen_height) // 2 - 20

# Colors
desert = (244, 218, 185)
black = (0, 0, 0)
river = (138, 202, 238)
red = (255, 0, 0)
yellow = (255, 255, 0)

dark_grey = (105, 105, 105)
blue = (0, 0, 255)
green = (0, 255, 0)


# Game board layout
river_tiles = [
    (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (4, 2), (4, 1), (4, 0), (5, 0), (6, 0),
    (7, 0), (8, 0), (12, 0), (12, 1), (12, 2), (13, 2), (13, 3), (14, 3), (15, 3),
    (15, 4), (14, 4), (14, 5), (14, 6), (13, 6), (12, 6), (12, 7), (12, 8), (11, 8),
    (10, 8), (9, 8), (8, 8), (7, 8), (6, 8), (6, 7), (5, 7), (4, 7), (3, 7), (3, 6),
    (2, 6), (1, 6), (0, 6),
]

monument_with_treasure_tiles = [
    (1, 1), (5, 2), (5, 9), (1, 7), (10, 0), (10, 10), (15, 1), (5, 2), (13, 4), (14, 8), (8, 6),
]

# Player area settings
player_space_width = 500
player_space_height = 200
discard_area_width = 150
gap_between_player_areas = 50
gap_between_discard_and_player = 10

total_player_zone_width = (2 * player_space_width) + gap_between_player_areas + (2 * discard_area_width) + (2 * gap_between_discard_and_player)
overall_start_x = (window_width - total_player_zone_width) // 2

player_space_x1 = overall_start_x + discard_area_width + gap_between_discard_and_player
player_space_x2 = player_space_x1 + player_space_width + gap_between_player_areas

player1_discard_area = pygame.Rect(overall_start_x, window_height - player_space_height - 20, discard_area_width, player_space_height)
player2_discard_x_pos = player_space_x2 + player_space_width + gap_between_discard_and_player
player2_discard_area = pygame.Rect(player2_discard_x_pos, window_height - player_space_height - 20, discard_area_width, player_space_height)

# UI Button settings


end_turn_button_width = 120
end_turn_button_height = 50
end_turn_button_x = window_width - end_turn_button_width - 20
end_turn_button_y = 80
end_turn_button_color = (200, 200, 200)
end_turn_button_hover_color = (180, 180, 180)

replace_button_width = 160
replace_button_height = 50
replace_button_x = window_width - replace_button_width - 20
replace_button_y = 140
replace_button_color = (200, 200, 200)
replace_button_hover_color = (180, 180, 180)

commit_button_width = 120
commit_button_height = 50
player1_commit_button_x = 20
player2_commit_button_x = window_width - commit_button_width - 20
commit_button_y = 200
commit_button_color = (200, 200, 200)
commit_button_hover_color = (180, 180, 180)

# Tile color mapping for scoring
tile_color_map = {
    "farm": "blue",
    "market": "green",
    "monument": "red",
    "city": "black",
}

# Fonts
warning_font = pygame.font.Font(None, 48)
score_font = pygame.font.Font(None, 28)
turn_font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 36)
discard_font = pygame.font.Font(None, 24)
