import pygame
import config

def draw_undo_button(screen, mouse_pos):
    undo_button_rect = pygame.Rect(config.undo_button_x, config.undo_button_y, config.undo_button_width, config.undo_button_height)
    button_color = config.undo_button_hover_color if undo_button_rect.collidepoint(mouse_pos) else config.undo_button_color
    pygame.draw.rect(screen, button_color, undo_button_rect)

    undo_text = config.button_font.render("Undo", True, config.black)
    text_rect = undo_text.get_rect(center=undo_button_rect.center)
    screen.blit(undo_text, text_rect)
    return undo_button_rect

def draw_end_turn_button(screen, mouse_pos):
    end_turn_button_rect = pygame.Rect(config.end_turn_button_x, config.end_turn_button_y, config.end_turn_button_width, config.end_turn_button_height)
    end_turn_color = config.end_turn_button_hover_color if end_turn_button_rect.collidepoint(mouse_pos) else config.end_turn_button_color
    pygame.draw.rect(screen, end_turn_color, end_turn_button_rect)

    end_turn_text = config.button_font.render("End Turn", True, config.black)
    end_turn_text_rect = end_turn_text.get_rect(center=end_turn_button_rect.center)
    screen.blit(end_turn_text, end_turn_text_rect)
    return end_turn_button_rect

def draw_replace_button(screen, mouse_pos):
    replace_button_rect = pygame.Rect(config.replace_button_x, config.replace_button_y, config.replace_button_width, config.replace_button_height)
    replace_color = config.replace_button_hover_color if replace_button_rect.collidepoint(mouse_pos) else config.replace_button_color
    pygame.draw.rect(screen, replace_color, replace_button_rect)

    replace_text = config.button_font.render("Replace Tiles", True, config.black)
    replace_text_rect = replace_text.get_rect(center=replace_button_rect.center)
    screen.blit(replace_text, replace_text_rect)
    return replace_button_rect

def handle_monument_choice(mouse_pos, monument_rects):
    for i, rect in enumerate(monument_rects):
        if rect.collidepoint(mouse_pos):
            return i
    return None

def draw_commit_button(screen, mouse_pos):
    commit_button_rect = pygame.Rect(config.commit_button_x, config.commit_button_y, config.commit_button_width, config.commit_button_height)
    commit_color = config.commit_button_hover_color if commit_button_rect.collidepoint(mouse_pos) else config.commit_button_color
    pygame.draw.rect(screen, commit_color, commit_button_rect)

    commit_text = config.button_font.render("Commit", True, config.black)
    commit_text_rect = commit_text.get_rect(center=commit_button_rect.center)
    screen.blit(commit_text, commit_text_rect)
    return commit_button_rect
