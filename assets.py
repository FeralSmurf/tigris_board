import pygame
from config import tile_size

# Load and scale temple with treasure image
temple_with_treasure = pygame.image.load("temple_with_treasure.bmp")
temple_with_treasure = pygame.transform.scale(temple_with_treasure, (tile_size, tile_size))

# Load and scale leader tokens
leader_tokens = {
    "black": pygame.image.load("black_leader_1.bmp"),
    "blue": pygame.image.load("blue_leader_1.bmp"),
    "red": pygame.image.load("red_leader_1.bmp"),
    "green": pygame.image.load("green_leader_1.bmp"),
}

for color in leader_tokens:
    leader_tokens[color] = pygame.transform.scale(leader_tokens[color], (tile_size, tile_size))

# Load and scale other tokens
other_tokens = {
    "market": pygame.image.load("market.bmp"),
    "city": pygame.image.load("city.bmp"),
    "farm": pygame.image.load("farm.bmp"),
    "temple": pygame.image.load("temple.bmp"),
}

for token in other_tokens:
    other_tokens[token] = pygame.transform.scale(other_tokens[token], (tile_size, tile_size))
