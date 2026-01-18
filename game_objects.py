import pygame
from assets import leader_tokens
from config import window_height, player_space_height, player_space_width

class Tile:
    def __init__(self, tile_type, image):
        self.tile_type = tile_type
        self.image = image
        self.rect = self.image.get_rect()

class Player:
    def __init__(self, name, player_space_x):
        self.name = name
        self.score = {"red": 0, "blue": 0, "green": 0, "black": 0}
        self.hand = []
        self.leaders = {
            "black": Tile("black_leader", leader_tokens["black"].copy()),
            "blue": Tile("blue_leader", leader_tokens["blue"].copy()),
            "red": Tile("red_leader", leader_tokens["red"].copy()),
            "green": Tile("green_leader", leader_tokens["green"].copy()),
        }

        if self.name == "Player 2":
            for leader in self.leaders.values():
                darken_surface = pygame.Surface(leader.image.get_size(), flags=pygame.SRCALPHA)
                darken_surface.fill((0, 0, 0, 50))  # Black with 50 alpha
                leader.image.blit(darken_surface, (0, 0))

        self.player_space_x = player_space_x
        self.place_leaders()

    def place_leaders(self):
        y_pos = window_height - player_space_height - 20 + 10 # top of player space + 10px padding
        x_start = self.player_space_x + (player_space_width - (4 * 70 + 3 * 10)) // 2 # Center the leaders block
        self.leaders["black"].rect.topleft = (x_start, y_pos)
        self.leaders["blue"].rect.topleft = (x_start + 80, y_pos)
        self.leaders["red"].rect.topleft = (x_start + 160, y_pos)
        self.leaders["green"].rect.topleft = (x_start + 240, y_pos)

    def draw_hand(self, tile_bag):
        for _ in range(6):
            if tile_bag:
                self.hand.append(tile_bag.pop())
        self.arrange_hand()

    def arrange_hand(self):
        y_pos = window_height - player_space_height - 20 + 10 + 70 + 10 # under leaders
        x_start = self.player_space_x + (player_space_width - (6 * 70 + 5 * 10)) // 2 # Center the hand block
        for i, tile in enumerate(self.hand):
            tile.rect.topleft = (x_start + i * 80, y_pos)

    def refill_hand(self, tile_bag):
        needed = 6 - len(self.hand)
        for _ in range(needed):
            if tile_bag:
                self.hand.append(tile_bag.pop())
        self.arrange_hand()
