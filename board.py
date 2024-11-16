import pygame
import sys

black_leader_x = 0
black_leader_y = 0
dragging = False
offset_x = 0
offset_y = 0

# Initialize pygame
pygame.init()

# Set the dimensions of the grid
grid_width = 16
grid_height = 11

# Set the size of each tile
tile_size = 70

# Calculate the size of the window
screen_width = grid_width * tile_size
screen_height = grid_height * tile_size + 150  # Leave some space for the pieces
window_width = screen_width + 100  # Extra space
window_height = screen_height + 100  # Extra space

# Create a window with the correct size
screen = pygame.display.set_mode((window_width, window_height))

# Set the title of the window
pygame.display.set_caption("Tigris and Euphrates")

# Define some colors
desert = (233, 200, 144)
black = (0, 0, 0)
river = (138, 202, 238)

# Define the river tiles
river_tiles = [
    (0, 3),
    (1, 3),
    (2, 3),
    (3, 3),
    (3, 2),
    (4, 2),
    (4, 1),
    (4, 0),
    (5, 0),
    (6, 0),
    (7, 0),
    (8, 0),
    (12, 0),
    (12, 1),
    (12, 2),
    (13, 2),
    (13, 3),
    (14, 3),
    (15, 3),
    (15, 4),
    (14, 4),
    (14, 5),
    (14, 6),
    (13, 6),
    (12, 6),
    (12, 7),
    (12, 8),
    (11, 8),
    (10, 8),
    (9, 8),
    (8, 8),
    (7, 8),
    (6, 8),
    (6, 7),
    (5, 7),
    (4, 7),
    (3, 7),
    (3, 6),
    (2, 6),
    (1, 6),
    (0, 6),
]

# Temple tiles, with treasure
temple_with_treasure = pygame.image.load("temple_with_treasure.png")
temple_with_treasure = pygame.transform.scale(
    temple_with_treasure, (tile_size, tile_size)
)

temple_with_treasure_tiles = [
    (1, 1),
    (5, 2),
    (5, 9),
    (1, 7),
    (10, 0),
    (10, 10),
    (15, 1),
    (5, 2),
    (13, 4),
    (14, 8),
    (8, 6),
]

# Load the leader token images
leader_tokens = {
    "black": pygame.image.load("black_leader.png"),
    "blue": pygame.image.load("blue_leader.png"),
    "red": pygame.image.load("red_leader.png"),
    "green": pygame.image.load("green_leader.png"),
}

# Resize leader tokens
for color in leader_tokens:
    leader_tokens[color] = pygame.transform.scale(leader_tokens[color], (70, 70))

# Calculate the x and y coordinates for the player spaces
player_space_width = 570
player_space_height = 160
player_space_x1 = (window_width - player_space_width * 2 - 50) // 2
player_space_x2 = player_space_x1 + player_space_width + 50
player_space_y = window_height - player_space_height - 20

leader_positions = {
    "black": [player_space_x1 + 10, player_space_y + 10],
    "blue": [player_space_x1 + 90, player_space_y + 10],
    "red": [player_space_x1 + 170, player_space_y + 10],
    "green": [player_space_x1 + 250, player_space_y + 10],
}

leader_dragging = {color: False for color in leader_tokens}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for color, pos in leader_positions.items():
                    if (
                        pos[0]
                        <= event.pos[0]
                        <= pos[0] + leader_tokens[color].get_width()
                        and pos[1]
                        <= event.pos[1]
                        <= pos[1] + leader_tokens[color].get_height()
                    ):
                        leader_dragging[color] = True
                        mouse_x, mouse_y = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for color in leader_dragging:
                    leader_dragging[color] = False
        elif event.type == pygame.MOUSEMOTION:
            for color, dragging in leader_dragging.items():
                if dragging:
                    mouse_x, mouse_y = event.pos
                    leader_positions[color] = [
                        mouse_x - leader_tokens[color].get_width() // 2,
                        mouse_y - leader_tokens[color].get_height() // 2,
                    ]

    # Draw the grid
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

    # Draw a border around the entire grid
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

    # Draw the two rectangles for the player spaces
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

    # Draw the leader tokens for Player 1
    for color, pos in leader_positions.items():
        screen.blit(leader_tokens[color], pos)

    # Update the display
    pygame.display.flip()
