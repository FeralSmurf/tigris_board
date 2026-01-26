import pygame
from config import tile_size

# Load and scale monument with treasure image
monument_with_treasure = pygame.image.load("temple_with_treasure.bmp")
monument_with_treasure = pygame.transform.scale(monument_with_treasure, (tile_size, tile_size))
monument_without_treasure = pygame.image.load("temple_without_treasure.bmp")
monument_without_treasure = pygame.transform.scale(monument_without_treasure, (tile_size, tile_size))

# Load and scale leader tokens
leader_tokens = {
    "black": pygame.image.load("black_leader_1.bmp"),
    "blue": pygame.image.load("blue_leader_1.bmp"),
    "red": pygame.image.load("red_leader_1.bmp"),
    "green": pygame.image.load("green_leader_1.bmp"),
}

for color in leader_tokens:
    leader_tokens[color] = pygame.transform.scale(leader_tokens[color], (tile_size, tile_size))

leader_tokens_p2 = {
    "black": pygame.image.load("black_leader_2.bmp"),
    "blue": pygame.image.load("blue_leader_2.bmp"),
    "red": pygame.image.load("red_leader_2.bmp"),
    "green": pygame.image.load("green_leader_2.bmp"),
}

for color in leader_tokens_p2:
    leader_tokens_p2[color] = pygame.transform.scale(leader_tokens_p2[color], (tile_size, tile_size))

# Load and scale other tokens
other_tokens = {
    "market": pygame.image.load("market.bmp"),
    "city": pygame.image.load("city.bmp"),
    "farm": pygame.image.load("farm.bmp"),
    "monument": pygame.image.load("temple.bmp"),
}

for token in other_tokens:
    other_tokens[token] = pygame.transform.scale(other_tokens[token], (tile_size, tile_size))

# Load and scale specific monument images
monument_images = {}
specific_monuments = [
    ("blue", "black"), ("blue", "green"), ("red", "black"),
    ("red", "green"), ("green", "blue"), ("green", "black")
]

for c1, c2 in specific_monuments:
    sorted_key = tuple(sorted((c1, c2))) # Ensure key is always sorted alphabetically
    try:
        # Assuming filenames are consistent: monument_color1_color2.bmp
        filename = f"monument_{c1}_{c2}.bmp"
        img = pygame.image.load(filename)
        monument_images[sorted_key] = pygame.transform.scale(img, (tile_size * 2, tile_size * 2))
    except pygame.error:
        # Try reversed filename if the first one fails
        filename = f"monument_{c2}_{c1}.bmp"
        img = pygame.image.load(filename)
        monument_images[sorted_key] = pygame.transform.scale(img, (tile_size * 2, tile_size * 2))

