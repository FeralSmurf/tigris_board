import pygame
import sys
import copy

pygame.init()

grid_width = 16
grid_height = 11
tile_size = 70

screen_width = grid_width * tile_size 
screen_height = grid_height * tile_size + 150
window_width = screen_width + 700
window_height = screen_height + 140

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Tigris and Euphrates")

desert = (233, 200, 144)
black = (0, 0, 0)
river = (138, 202, 238)
undo_button_color = (200, 200, 200)
undo_button_hover_color = (180, 180, 180)

river_tiles = [
    (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (4, 2), (4, 1), (4, 0), (5, 0), (6, 0),
    (7, 0), (8, 0), (12, 0), (12, 1), (12, 2), (13, 2), (13, 3), (14, 3), (15, 3),
    (15, 4), (14, 4), (14, 5), (14, 6), (13, 6), (12, 6), (12, 7), (12, 8), (11, 8),
    (10, 8), (9, 8), (8, 8), (7, 8), (6, 8), (6, 7), (5, 7), (4, 7), (3, 7), (3, 6),
    (2, 6), (1, 6), (0, 6),
]

temple_with_treasure = pygame.image.load("temple_with_treasure.png")
temple_with_treasure = pygame.transform.scale(temple_with_treasure, (tile_size, tile_size))

temple_with_treasure_tiles = [
    (1, 1), (5, 2), (5, 9), (1, 7), (10, 0), (10, 10), (15, 1), (5, 2), (13, 4), (14, 8), (8, 6),
]

leader_tokens = {
    "black": pygame.image.load("black_leader_1.png"),
    "blue": pygame.image.load("blue_leader_1.png"),
    "red": pygame.image.load("red_leader_1.png"),
    "green": pygame.image.load("green_leader_1.png"),

    "black_2": pygame.image.load("black_leader_2.png"),
    "blue_2": pygame.image.load("blue_leader_2.png"),
    "red_2": pygame.image.load("red_leader_2.png"),
    "green_2": pygame.image.load("green_leader_2.png"),
}

for color in leader_tokens:
    leader_tokens[color] = pygame.transform.scale(leader_tokens[color], (70, 70))

other_tokens = {
    "market": pygame.image.load("market.png"),
    "city": pygame.image.load("city.png"),
    "farm": pygame.image.load("farm.png"),
    "temple": pygame.image.load("temple.png"),
    "market_2": pygame.image.load("market.png"),
    "city_2": pygame.image.load("city.png"),
    "farm_2": pygame.image.load("farm.png"),
    "temple_2": pygame.image.load("temple.png"),
}

for token in other_tokens:
    other_tokens[token] = pygame.transform.scale(other_tokens[token], (70, 70))

player_space_width = 850
player_space_height = 160
player_space_x1 = (window_width - player_space_width * 2 - 50) // 2
player_space_x2 = player_space_x1 + player_space_width + 50
player_space_y = window_height - player_space_height - 20

leader_positions = {
    "black": [player_space_x1 + 10, player_space_y + 10],
    "blue": [player_space_x1 + 90, player_space_y + 10],
    "red": [player_space_x1 + 170, player_space_y + 10],
    "green": [player_space_x1 + 250, player_space_y + 10],

    "black_2": [player_space_x2 + 10, player_space_y + 10],
    "blue_2": [player_space_x2 + 90, player_space_y + 10],
    "red_2": [player_space_x2 + 170, player_space_y + 10],
    "green_2": [player_space_x2 + 250, player_space_y + 10],
}

token_positions = {
    # For player 1
    "market": [player_space_x1 + 330, player_space_y + 10],
    "city": [player_space_x1 + 410, player_space_y + 10],
    "farm": [player_space_x1 + 490, player_space_y + 10],
    "temple": [player_space_x1 + 570, player_space_y + 10],
    # For player 2
    "market_2": [player_space_x2 + 330, player_space_y + 10],
    "city_2": [player_space_x2 + 410, player_space_y + 10],
    "farm_2": [player_space_x2 + 490, player_space_y + 10],
    "temple_2": [player_space_x2 + 570, player_space_y + 10],
}

# Undo button setup
undo_button_width = 100
undo_button_height = 50
undo_button_x = window_width - undo_button_width - 20
undo_button_y = 20

# Track previous positions for undo functionality
previous_leader_positions = {}
previous_token_positions = {}

leader_dragging = {color: False for color in leader_tokens}
token_dragging = {token: False for token in other_tokens}

def snap_to_grid(pos):
    x = (pos[0] - (window_width - screen_width) // 2) // tile_size
    y = (pos[1] - (window_height - screen_height) // 2) // tile_size
    if 0 <= x < grid_width and 0 <= y < grid_height:
        return ((window_width - screen_width) // 2 + x * tile_size, 
                (window_height - screen_height) // 2 + y * tile_size)
    return pos

def save_previous_positions():
    global previous_leader_positions, previous_token_positions
    previous_leader_positions = copy.deepcopy(leader_positions)
    previous_token_positions = copy.deepcopy(token_positions)

def undo_last_move():
    global leader_positions, token_positions
    if previous_leader_positions and previous_token_positions:
        leader_positions = copy.deepcopy(previous_leader_positions)
        token_positions = copy.deepcopy(previous_token_positions)

def is_point_in_rect(point, rect):
    return (rect[0] <= point[0] <= rect[0] + rect[2] and
            rect[1] <= point[1] <= rect[1] + rect[3])

while True:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if undo button is clicked
                if is_point_in_rect(event.pos, (undo_button_x, undo_button_y, undo_button_width, undo_button_height)):
                    undo_last_move()
                
                for color, pos in leader_positions.items():
                    if (
                        pos[0] <= event.pos[0] <= pos[0] + leader_tokens[color].get_width()
                        and pos[1] <= event.pos[1] <= pos[1] + leader_tokens[color].get_height()
                    ):
                        save_previous_positions()
                        leader_dragging[color] = True
                        mouse_x, mouse_y = event.pos
                
                for token, pos in token_positions.items():
                    if (
                        pos[0] <= event.pos[0] <= pos[0] + other_tokens[token].get_width()
                        and pos[1] <= event.pos[1] <= pos[1] + other_tokens[token].get_height()
                    ):
                        save_previous_positions()
                        token_dragging[token] = True
                        mouse_x, mouse_y = event.pos
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for color in leader_dragging:
                    if leader_dragging[color]:
                        leader_positions[color] = snap_to_grid(leader_positions[color])
                    leader_dragging[color] = False
                
                for token in token_dragging:
                    if token_dragging[token]:
                        token_positions[token] = snap_to_grid(token_positions[token])
                    token_dragging[token] = False
        
        elif event.type == pygame.MOUSEMOTION:
            for color, dragging in leader_dragging.items():
                if dragging:
                    mouse_x, mouse_y = event.pos
                    leader_positions[color] = [
                        mouse_x - leader_tokens[color].get_width() // 2,
                        mouse_y - leader_tokens[color].get_height() // 2,
                    ]
            
            for token, dragging in token_dragging.items():
                if dragging:
                    mouse_x, mouse_y = event.pos
                    token_positions[token] = [
                        mouse_x - other_tokens[token].get_width() // 2,
                        mouse_y - other_tokens[token].get_height() // 2,
                    ]

    screen.fill(desert)
    for x in range(grid_width):
        for y in range(grid_height):
            pygame.draw.rect(
                screen,
                black,
                (
                    (window_width - screen_width) // 2 + x * tile_size,
                    (window_height - screen_height) // 2 + y * tile_size,
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
                        (window_width - screen_width) // 2 + x * tile_size + 1,
                        (window_height - screen_height) // 2 + y * tile_size + 1,
                        tile_size - 2,
                        tile_size - 2,
                    ),
                )
            elif (x, y) in temple_with_treasure_tiles:
                screen.blit(
                    temple_with_treasure,
                    (
                        (window_width - screen_width) // 2 + x * tile_size,
                        (window_height - screen_height) // 2 + y * tile_size,
                    ),
                )

    pygame.draw.rect(
        screen,
        black,
        (
            (window_width - screen_width) // 2 - 1,
            (window_height - screen_height) // 2,
            screen_width + 2,
            grid_height * tile_size,
        ),
        2,
    )

    pygame.draw.rect(
        screen,
        black,
        (player_space_x1, player_space_y, player_space_width, player_space_height),
        2,
    )
    pygame.draw.rect(
        screen,
        black,
        (player_space_x2, player_space_y, player_space_width, player_space_height),
        2,
    )

    # Draw undo button
    undo_button_rect = pygame.Rect(undo_button_x, undo_button_y, undo_button_width, undo_button_height)
    button_color = undo_button_hover_color if undo_button_rect.collidepoint(mouse_pos) else undo_button_color
    pygame.draw.rect(screen, button_color, undo_button_rect)
    
    font = pygame.font.Font(None, 36)
    undo_text = font.render("Undo", True, black)
    text_rect = undo_text.get_rect(center=undo_button_rect.center)
    screen.blit(undo_text, text_rect)

    for color, pos in leader_positions.items():
        screen.blit(leader_tokens[color], pos)

    for token, pos in token_positions.items():
        screen.blit(other_tokens[token], pos)

    pygame.display.flip()
