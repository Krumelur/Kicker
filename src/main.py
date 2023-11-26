from typing import List
import pygame
import pygame_menu
from pygame import Surface
import os
import os
from helpers import *

		
def main() -> None:
	current_gamefield : Surface = None
	screen : Surface
	background_offset : pygame.Vector2 = pygame.Vector2(0, 0)
	border_right_rect : pygame.Rect

	def on_game_field_selected(title, filename):
		print(f"Selected {title} with filename {filename}")
		nonlocal current_gamefield
		current_gamefield = pygame.image.load(filename)

	def close_main_menu():
		main_menu.close()
		main_menu.disable()

	def on_update_offset_x(value, **kwargs):
		nonlocal background_offset
		print(f"X Offset: {value}")
		background_offset.x = value

	def on_update_offset_y(value, **kwargs):
		nonlocal background_offset
		print(f"Y Offset: {value}")
		background_offset.y = value

	def on_update_side_border(value, **kwargs):
		nonlocal border_right_rect
		print(f"Border: {value}")
		border_right_rect.height = value

	pygame.init()
	pygame.display.set_caption("Foosion")

	screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	#screen = pygame.display.set_mode((800, 600))

	border_right_rect = pygame.Rect(0, 0, pygame.display.get_window_size()[0], 0)

	menu_theme = pygame_menu.themes.THEME_DEFAULT.set_background_color_opacity(0.9)

	debug_menu = pygame_menu.Menu('Debug', 600, 300, theme=menu_theme)
	debug_menu.add.range_slider('X-Offset', 0, (-100, 100), 1, rangeslider_id='x_offset', value_format=lambda x: str(int(x)), onchange=on_update_offset_x)
	debug_menu.add.range_slider('Y-Offset', 0, (-100, 100), 1, rangeslider_id='y_offset', value_format=lambda x: str(int(x)), onchange=on_update_offset_y)
	debug_menu.add.range_slider('Rand', 0, (0, 100), 1, rangeslider_id='border', value_format=lambda x: str(int(x)), onchange=on_update_side_border)

	main_menu = pygame_menu.Menu('Foosion - Einstellungen', 600, 300, theme=menu_theme)

	main_menu.add.selector('Feld: ', get_game_fields(), onchange=on_game_field_selected).set_alignment(pygame_menu.locals.ALIGN_LEFT)
	main_menu.add.button('Debug', debug_menu).set_alignment(pygame_menu.locals.ALIGN_CENTER)
	main_menu.add.button('<- Zurück', close_main_menu).set_alignment(pygame_menu.locals.ALIGN_CENTER)


	is_running = True
	while is_running:
		
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				is_running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					main_menu.enable()

		if current_gamefield is not None:
			scaled_gamefield = pygame.transform.scale(current_gamefield, screen.get_size())
			screen.fill((0, 0, 0))
			screen.blit(scaled_gamefield, background_offset)
			screen.fill((0, 0, 0), border_right_rect)

		if main_menu.is_enabled():
			main_menu.update(events)
			if main_menu.is_enabled():
				main_menu.draw(screen)

		pygame.display.flip()

	# pygame.quit()
	def get_fields() -> List[str]:
		directory = "assets/fields"
		filenames = os.listdir(directory)
		return filenames

if __name__ == "__main__":
	main()