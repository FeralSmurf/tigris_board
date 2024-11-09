import pygame
import sys

# initialize pygame
pygame.init()

# set the dimensions of the grid
grid_width = 16
grid_height = 11

# set the size of each tile
tile_size = 70

# calculate the size of the window
screen_width = grid_width * tile_size
screen_height = grid_height * tile_size + 150 # leave some space for the pieces
window_width = screen_width + 100 # extra space
window_height = screen_height + 100 # extra space

# create a window with the correct size
screen = pygame.display.set_mode((window_width, window_height))

# set the title of the window
pygame.display.set_caption("Tigris and Euphrates")

# define some colors
desert = (233, 200, 144)
black = (0, 0, 0)
river = (138, 202, 238)

# define the river tiles
river_tiles = [(0,3), (1,3), (2,3), (3,3), (3,2), (4,2), (4,1), (4,0), (5,0), (6,0), (7,0), (8,0), (12,0), (12,1), (12,2), (13,2), (13,3), (14,3), (15,3), (15,4), (14,4), (14,5), (14,6), (13,6), (12,6), (12,7), (12,8), (11,8), (10,8), (9,8), (8,8), (7,8), (6,8), (6,7), (5,7), (4,7), (3,7), (3,6), (2,6), (1,6), (0,6)]

# tenmple tiles, with treasure
temple_with_treasure = pygame.image.load("temple_with_treasure.png")
temple_with_treasure = pygame.transform.scale(temple_with_treasure, (tile_size, tile_size))

temple_with_treasure_tiles = [(1,1), (5,2), (5,9), (1,7), (10,0), (10,10), (15,1), (5,2), (13,4), (14,8), (8,6)]


# Calculate the x and y coordinates for the player spaces
player_space_width = 570
player_space_height = 160
player_space_x1 = (window_width - player_space_width * 2 - 50) // 2
player_space_x2 = player_space_x1 + player_space_width + 50
player_space_y = window_height - player_space_height - 20

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

 # Draw the grid
    screen.fill(desert)
    for x in range(grid_width):
        for y in range(grid_height):
            pygame.draw.rect(screen, black, ((window_width - screen_width) // 2 + x * tile_size, (window_height - screen_height) // 2 + y * tile_size, tile_size, tile_size), 1)
            if (x, y) in river_tiles:
                pygame.draw.rect(screen, river,((window_width - screen_width) // 2 + x * tile_size + 1, (window_height - screen_height) // 2 + y * tile_size + 1, tile_size - 2, tile_size - 2))
            elif (x, y) in temple_with_treasure_tiles:
                screen.blit(temple_with_treasure, ((window_width - screen_width) // 2 + x * tile_size, (window_height - screen_height) // 2 + y * tile_size))
    
    # Draw a border around the entire grid
    pygame.draw.rect(screen, black, ((window_width - screen_width) // 2 - 1, (window_height - screen_height) // 2, screen_width + 2, grid_height * tile_size), 2)
    
    # Draw the two rectangles for the player spaces
    pygame.draw.rect(screen, black, (player_space_x1, player_space_y, player_space_width, player_space_height), 2)
    pygame.draw.rect(screen, black, (player_space_x2, player_space_y, player_space_width, player_space_height), 2)
    
    # Update the display
    pygame.display.flip()
