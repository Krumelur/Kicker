import string
from typing import List
import pygame
import pygame_menu
import pygame.freetype
from pygame import Surface
import os
from helpers import *
import sys
from gpio import GPIOBase, RaspberryPiGPIO, MockGPIO


# *** Game Field Info ***
#
# Resolution of screen: 1920x1080
#
# Top border: 22px (covered by the table)
# Bottom border: 0px
# Left border: 2px (covered by the table)
# Right border: 8px (covered by the table)
#
# Effective resolution: 1910x1058
# Top left corner: X = 2, Y = 22
# Center line vertical X: 953
# Center line horizontal Y: 548
#
# Torsensoren
# Tor1 GRÜN GPIO6
# Tor2 GRÜN GPIO27
#
# Taster
# Taster1 ORANGE GPIO26
# Taster2 ORANGE GPIO5
# Taster3 ORANGE GPIO17
# Taster4 GELB GPIO19
# Taster5 BRAUN GPIO13


def main() -> None:
	current_gamefield_surface: Surface = None
	current_gamefield_filenameinfo : FilenameInfo = None
	screen: Surface
	background_offset: pygame.Vector2 = pygame.Vector2(2, 22)
	score_player1: int = 0
	score_player2: int = 0
	score_surface: Surface = Surface((0, 0))
	score_border_distance_y = 70
	score_updated_ticks: int = -sys.maxsize - 1
	score_visibility_seconds: int = 5
	gpio: GPIOBase = None

	message_surface: Surface = Surface((0, 0))
	message_updated_ticks: int = -sys.maxsize - 1
	message_visibility_seconds: int = 5

	def on_goal_player1(channel) -> None:
		print("Pin", channel, "changed to high")
		on_update_score_player1(score_player1 + 1)

	def on_goal_player2(channel) -> None:
		print("Pin", channel, "changed to high")
		on_update_score_player2(score_player2 + 1)

	def on_button_1(channel) -> None:
		"""
		Button 1: show score
		"""
		print("Pin", channel, "changed to high")
		update_score(score_player1, score_player2)

	def on_button_2(channel) -> None:
		"""
		Button 2: cycle themes
		"""
		nonlocal current_gamefield_filenameinfo
		current_index : int = game_fields.index(current_gamefield_filenameinfo)
		current_index = (current_index + 1) % len(game_fields)
		current_gamefield_filenameinfo = game_fields[current_index]

		print("Pin", channel, "changed to high")
		on_game_field_selected(current_gamefield_filenameinfo.title, current_gamefield_filenameinfo.filename)
	
	def on_button_5(channel) -> None:
		"""
		Button 5: restart game
		"""
		print("Pin", channel, "changed to high")
		on_new_game()

	def initialize_gpio() -> None:
		nonlocal gpio
		if sys.platform == "darwin":
			gpio = MockGPIO()
		else:
			gpio = RaspberryPiGPIO()

		gpio.add_event_detect(27, on_goal_player1, 2000)
		gpio.add_event_detect(6, on_goal_player2, 2000)
		gpio.add_event_detect(5, on_button_1, 1000)
		gpio.add_event_detect(17, on_button_2, 500)
		gpio.add_event_detect(26, on_button_5, 1000)

	def on_game_field_selected(title, filename : string):
		print(f"Selected {title} with filename {filename}")
		nonlocal current_gamefield_surface
		current_gamefield_surface = pygame.image.load(filename)

	def on_new_game():
		pygame.mouse.set_visible(False)
		score_player1 = 0
		score_player2 = 0
		update_score(score_player1, score_player2)
		on_close_main_menu()
		ambient_sound = pygame.mixer.Sound(
			get_full_path("assets/sounds/Final Match Ambience.mp3")
		)
		ambient_sound.play()
		update_message("Anpfiff!")

	def on_update_score_player1(value, **kwargs):
		nonlocal score_player2
		update_score(value, score_player2)
		update_message("Tor Team Blau!")

	def on_update_score_player2(value, **kwargs):
		nonlocal score_player1
		update_score(score_player1, value)
		update_message("Tor Team Schwarz!")

	def on_close_main_menu():
		main_menu.disable()

	def update_score(score1: int, score2: int) -> None:
		nonlocal score_player1
		nonlocal score_player2
		score_player1 = score1
		score_player2 = score2

		score = f"{score1}  :  {score2}"

		shadow_offset = 2
		font_size = 160

		(text_surface1, text_rect1) = score_font.render(
			text=score, fgcolor=(0, 0, 0), bgcolor=None, size=font_size
		)
		(text_surface2, text_rect2) = score_font.render(
			text=score, fgcolor=(255, 255, 255), bgcolor=None, size=font_size
		)

		nonlocal score_surface
		score_surface = Surface(
			(text_rect1.width + shadow_offset, text_rect1.height + shadow_offset),
			pygame.SRCALPHA,
		)
		score_surface.blit(text_surface1, (0, 0))
		score_surface.blit(text_surface2, (shadow_offset, shadow_offset))

		nonlocal score_updated_ticks
		score_updated_ticks = pygame.time.get_ticks()

	def update_message(text: string) -> None:
		shadow_offset = 2
		font_size = 100

		(text_surface1, text_rect1) = message_font.render(
			text, fgcolor=(0, 0, 0), bgcolor=None, size=font_size
		)
		(text_surface2, text_rect2) = message_font.render(
			text, fgcolor=(255, 255, 255), bgcolor=None, size=font_size
		)

		nonlocal message_surface
		message_surface = Surface(
			(text_rect1.width + shadow_offset, text_rect1.height + shadow_offset),
			pygame.SRCALPHA,
		)
		message_surface.blit(text_surface1, (0, 0))
		message_surface.blit(text_surface2, (shadow_offset, shadow_offset))

		nonlocal message_updated_ticks
		message_updated_ticks = pygame.time.get_ticks()

	pygame.init()
	pygame.display.set_caption("Foosion")

	message_font = pygame.freetype.Font(
		get_full_path("assets/fonts/soccer-league/SoccerLeague.ttf")
	)
	score_font = pygame.freetype.Font(
		get_full_path("assets/fonts/soccer-scoreboard/Soccer Scoreboard.otf")
	)

	screen: Surface = None
	# On Mac run in windowed mode, on Raspberry run in fullscreen
	if sys.platform == "darwin":
		screen = pygame.display.set_mode((1920, 1080))
	else:
		screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

	# Load default game field.
	game_fields : List[FilenameInfo] = get_game_fields()
	on_game_field_selected(game_fields[0].title, game_fields[0].filename)

	# Create settings menu (show using F10).
	menu_theme = pygame_menu.themes.THEME_DEFAULT.set_background_color_opacity(0.9)
	main_menu = pygame_menu.Menu("Foosion - Einstellungen", 600, 400, theme=menu_theme)
	main_menu.add.selector("Feld: ", game_fields, 0, onchange=on_game_field_selected)
	main_menu.add.range_slider(
		"<- Punkte Spieler 1",
		0,
		(0, 10),
		1,
		rangeslider_id="score_player1",
		value_format=lambda x: str(int(x)),
		onchange=on_update_score_player1,
	)
	main_menu.add.range_slider(
		"Punkte Spieler 2 ->",
		0,
		(0, 10),
		1,
		rangeslider_id="score_player2",
		value_format=lambda x: str(int(x)),
		onchange=on_update_score_player2,
	)
	main_menu.add.button("Neues Spiel", on_new_game).set_alignment(
		pygame_menu.locals.ALIGN_CENTER
	)
	main_menu.add.button("Zurück", on_close_main_menu).set_alignment(
		pygame_menu.locals.ALIGN_CENTER
	)
	main_menu.disable()

	screen_center_x = screen.get_width() / 2
	screen_center_y = screen.get_height() / 2
	screen_height = screen.get_height()

	initialize_gpio()
	on_new_game()

	is_running = True
	while is_running:
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				is_running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_F10:
					main_menu.enable()
				elif event.key == pygame.K_ESCAPE:
					on_close_main_menu()
				elif event.key == pygame.K_1:
					on_update_score_player1(score_player1 + 1)
				elif event.key == pygame.K_2:
					on_update_score_player2(score_player2 + 1)

		# Display gamefield background
		if current_gamefield_surface is not None:
			screen.fill((0, 0, 0))
			screen.blit(current_gamefield_surface, background_offset)
			screen.fill((0, 0, 0), pygame.Rect(0, 0, 1920, background_offset.y))

		# Display score
		if pygame.time.get_ticks() - score_updated_ticks < score_visibility_seconds * 1000:
			screen.blit(score_surface, (screen_center_x - score_surface.get_width() / 2, background_offset.y + score_border_distance_y))
			screen.blit(pygame.transform.rotate(score_surface, 180), (screen_center_x - score_surface.get_width() / 2,screen_height- score_surface.get_height()- score_border_distance_y))

		# Display message
		if pygame.time.get_ticks() - message_updated_ticks < message_visibility_seconds * 1000:
			screen.blit(pygame.transform.rotate(message_surface, 90), (390, screen_center_y - message_surface.get_width() / 2))
			screen.blit(pygame.transform.rotate(message_surface, 270), (1450, screen_center_y - message_surface.get_width() / 2))

		if main_menu.is_enabled():
			main_menu.update(events)
			if main_menu.is_enabled():
				main_menu.draw(screen)

		if score_player1 >= 10:
			update_score(score_player1, score_player2)
			update_message("Team Blau gewinnt!")
		if score_player2 >= 10:
			update_score(score_player1, score_player2)
			update_message("Team Schwarz gewinnt!")

		pygame.display.flip()
		pygame.time.Clock().tick(30)

	gpio.cleanup()
	pygame.quit()


if __name__ == "__main__":
	main()
