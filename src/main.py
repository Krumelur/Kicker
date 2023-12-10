import random
import string
from typing import List
import pygame
import pygame_menu
import pygame.freetype
from pygame import Surface
from helpers import *
import sys
import time

if is_raspberrypi():
	import RPi.GPIO as GPIO
	
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

PIN_GOAL1 = 6
PIN_GOAL2 = 27
PIN_BUTTON1 = 26
PIN_BUTTON2 = 5 
PIN_BUTTON3 = 17
PIN_BUTTON4 = 19
PIN_BUTTON5 = 13


def main() -> None:
	referee_surface: Surface = None
	referee_updated_ticks: int = -sys.maxsize - 1
	referee_visibility_seconds: int = 5

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
	
	message_surface: Surface = Surface((0, 0))
	message_updated_ticks: int = -sys.maxsize - 1
	message_visibility_seconds: int = 5
	
	last_goal_time:float = 0.0
	goal_debounce_seconds:float = 1.5

	last_button_press_time:float = 0.0
	button_debounce_seconds:float = 1.0

	should_process_goal_player1:bool = False
	should_process_goal_player2:bool = False

	is_match_over = False
	
	def update_referee_visual(action:str) -> None:
		nonlocal referee_surface, referee_updated_ticks
		referee_surface = pygame.image.load(get_full_path(f"assets/images/referee/{action}.png"))
		referee_updated_ticks = pygame.time.get_ticks()

	def handle_goal_player1(channel) -> None:
		nonlocal should_process_goal_player1
		should_process_goal_player1 = True

	def handle_goal_player2(channel) -> None:
		nonlocal should_process_goal_player2
		should_process_goal_player2 = True

	def on_goal_player1() -> None:
		nonlocal last_goal_time, goal_debounce_seconds
		
		if time.time() - last_goal_time <= goal_debounce_seconds:
			print("Ignoring goal - debounce time not reached.")
			return
		
		print("Detected goal player 1")
		
		last_goal_time = time.time()
		
		update_referee_visual("goal_player1")
		play_referee_sound("goal.wav")
		play_random_sound("goal")
		on_update_score_player1(score_player1 + 1)

	def on_goal_player2() -> None:
		nonlocal last_goal_time, goal_debounce_seconds
		
		if time.time() - last_goal_time <= goal_debounce_seconds:
			print("Ignoring goal - debounce time not reached.")
			return
		
		print("Detected goal player 2")
		
		last_goal_time = time.time()
		
		update_referee_visual("goal_player2")
		play_referee_sound("goal.wav")
		play_random_sound("goal")
		on_update_score_player2(score_player2 + 1)
	
	def should_handle_button_press() -> bool:
		nonlocal last_button_press_time, button_debounce_seconds
		if time.time() - last_button_press_time <= button_debounce_seconds:
			return False
		last_button_press_time = time.time()
		return True

	def on_button1() -> None:
		if not should_handle_button_press():
			return
		
		nonlocal score_player1, score_player2
		update_score(score_player1, score_player2)

	def on_button2() -> None:
		if not should_handle_button_press():
			return
		
		nonlocal current_gamefield_filenameinfo
		current_index : int = game_fields.index(current_gamefield_filenameinfo)
		current_index = (current_index + 1) % len(game_fields)
		current_gamefield_filenameinfo = game_fields[current_index]
		on_game_field_selected(current_gamefield_filenameinfo)

	def on_button3() -> None:
		if not should_handle_button_press():
			return
		on_goal_player1()

	def on_button4() -> None:
		if not should_handle_button_press():
			return
		on_goal_player2()
	
	def on_button5() -> None:
		if not should_handle_button_press():
			return
		restart_match()

	def initialize_gpio() -> None:
		if is_raspberrypi():
			GPIO.setmode(GPIO.BCM)

			# Taster1
			GPIO.setup(PIN_BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			
			# Taster2
			GPIO.setup(PIN_BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			
			# Taster3
			GPIO.setup(PIN_BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			
			# Taster4
			GPIO.setup(PIN_BUTTON4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

			# Taster5
			GPIO.setup(PIN_BUTTON5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

			# Tor1
			GPIO.setup(PIN_GOAL1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
			GPIO.add_event_detect(PIN_GOAL1, GPIO.RISING, callback=handle_goal_player1)
			
			# Tor2 
			GPIO.setup(PIN_GOAL2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
			GPIO.add_event_detect(PIN_GOAL2, GPIO.RISING, callback=handle_goal_player2)

	def on_game_field_selected(gamefield_filenameinfo: FilenameInfo):
		print(f"Selected {gamefield_filenameinfo.title} with filename {gamefield_filenameinfo.filename}")
		nonlocal current_gamefield_surface
		current_gamefield_surface = pygame.image.load(gamefield_filenameinfo.filename)

	def play_random_sound(kind:str):
		goal_sounds : List[FilenameInfo] = get_sounds(kind)
		random_goal_sound : FilenameInfo = random.choice(goal_sounds)
		fx = pygame.mixer.Sound(random_goal_sound.filename)
		fx.play()

	def play_referee_sound(filename:str):
		fx = pygame.mixer.Sound(get_full_path(f"assets/sounds/referee/{filename}"))
		fx.play()
	
	def restart_match():
		nonlocal is_match_over
		is_match_over = False
		pygame.mouse.set_visible(False)
		update_score(0, 0)
		on_close_main_menu()
		play_random_sound("ambience")
		play_referee_sound("kickoff.wav")
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

		score = f"{score1} : {score2}"

		shadow_offset = 2
		font_size = 160

		(text_surface1, text_rect1) = score_font.render(
			text=score, fgcolor=(0, 0, 0), bgcolor=None, size=font_size
		)
		(text_surface2, text_rect2) = score_font.render(
			text=score, fgcolor=(255, 255, 255), bgcolor=None, size=font_size
		)

		nonlocal score_surface

		if not score_surface is None:
			del score_surface
		
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
		
		if not message_surface is None:
			del message_surface
		
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
	if is_raspberrypi():
		screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode((1920, 1080))

	# Load default game field.
	game_fields : List[FilenameInfo] = get_game_fields()
	current_gamefield_filenameinfo = game_fields[0]
	on_game_field_selected(current_gamefield_filenameinfo)

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
	main_menu.add.button("Neues Spiel", restart_match).set_alignment(
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
	restart_match()
	
	clock = pygame.time.Clock()

	is_running = True
	
	try:
		while is_running:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					is_running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_F10:
						# Show settings menu
						main_menu.enable()
					elif event.key == pygame.K_ESCAPE:
						on_close_main_menu()
					elif event.key == pygame.K_1:
						# Score player 1
						on_goal_player1()
					elif event.key == pygame.K_2:
						# Score player 2
						on_goal_player2()
					elif event.key == pygame.K_t:
						# Toggle background
						on_button2()

			# Display gamefield background
			if current_gamefield_surface is not None:
				screen.fill((0, 0, 0))
				screen.blit(current_gamefield_surface, background_offset)
				screen.fill((0, 0, 0), pygame.Rect(0, 0, 1920, background_offset.y))

			# Display referee
			if referee_surface is not None and pygame.time.get_ticks() - referee_updated_ticks < referee_visibility_seconds * 1000:
				screen.blit(referee_surface, (screen_center_x - referee_surface.get_width() / 2, screen_center_y - referee_surface.get_height() / 2))
			else:
				referee_surface = None

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
				
			if score_player1 >= 10 and not is_match_over:
				is_match_over = True
				update_score(score_player1, score_player2)
				update_message("Team Blau gewinnt!")
				play_random_sound("match_over")
			if score_player2 >= 10 and not is_match_over:
				is_match_over = True
				update_score(score_player1, score_player2)
				update_message("Team Schwarz gewinnt!")
				play_random_sound("match_over")

			# Handle all input on main game loop to not update GFX on non-mein threads.
			if is_raspberrypi():
				if should_process_goal_player1 or GPIO.input(PIN_GOAL1) == GPIO.HIGH:
					should_process_goal_player1 = False
					on_goal_player1()
				elif should_process_goal_player2 or GPIO.input(PIN_GOAL2) == GPIO.HIGH:
					should_process_goal_player2 = False
					on_goal_player2()
				elif GPIO.input(PIN_BUTTON1) == GPIO.LOW:
					on_button1()
				elif GPIO.input(PIN_BUTTON2) == GPIO.LOW:
					on_button2()
				elif GPIO.input(PIN_BUTTON3) == GPIO.LOW:
					on_button3()
				elif GPIO.input(PIN_BUTTON4) == GPIO.LOW:
					on_button4()
				elif GPIO.input(PIN_BUTTON5) == GPIO.LOW:
					on_button5()

			pygame.display.flip()
			#pygame.time.Clock().tick(30)
			#clock.tick(30)
			#print(clock.get_fps())

			# if goal_sensor1.is_pressed: 
			# 	on_goal_player1()
			
			# if goal_sensor2.is_pressed: 
			# 	on_goal_player2()
	except:
		if is_raspberrypi():
			GPIO.cleanup()
		raise

	pygame.quit()
	if is_raspberrypi():
		GPIO.cleanup()

if __name__ == "__main__":
	main()
