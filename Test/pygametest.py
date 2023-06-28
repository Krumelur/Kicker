import pygame

pygame.init()
image = "image.png"
screen = pygame.display.set_mode(size=(1920, 1080), display=0, flags=pygame.FULLSCREEN)
pygame.display.init()

background = pygame.image.load(image).convert()


screen.blit(background, (0,0))

pygame.display.update()

import time
time.sleep(10)

print("end")