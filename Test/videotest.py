import pygame
import subprocess
from videosprite import VideoSprite

# Window size
WINDOW_WIDTH    = 600
WINDOW_HEIGHT   = 400
WINDOW_SURFACE  = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE

DARK_BLUE = (   3,   5,  54)

### initialisation
pygame.init()
pygame.mixer.init()
#window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
window = pygame.display.set_mode(size=(1920, 1080), display=0, flags=pygame.FULLSCREEN)
pygame.display.set_caption("Video Sprite")

### Create Video Area
video_sprite1 = VideoSprite( pygame.Rect( 100, 100, 320, 240 ), 'video.mp4' )
video_sprite2 = VideoSprite( pygame.Rect( 100, 100, 160,  90 ), 'video.mp4' )  # 640x360
#sprite_group = pygame.sprite.GroupSingle()
sprite_group = pygame.sprite.Group()
sprite_group.add( video_sprite1 )
sprite_group.add( video_sprite2 )

### Main Loop
clock = pygame.time.Clock()
done = False
while not done:

    # Handle user-input
    for event in pygame.event.get():
        if ( event.type == pygame.QUIT ):
            done = True
        elif ( event.type == pygame.MOUSEBUTTONUP ):
            # On mouse-click
            pass

    # Movement keys
    keys = pygame.key.get_pressed()
    if ( keys[pygame.K_UP] ):
        video_sprite2.rect.y -= 10
    if ( keys[pygame.K_DOWN] ):
        video_sprite2.rect.y += 10
    if ( keys[pygame.K_LEFT] ):
        video_sprite2.rect.x -= 10
    if ( keys[pygame.K_RIGHT] ):
        video_sprite2.rect.x += 10
    

    # Update the window, but not more than 60fps
    sprite_group.update()
    window.fill( DARK_BLUE )
    sprite_group.draw( window )
    pygame.display.flip()

    # Clamp FPS
    clock.tick_busy_loop(25)  # matching my video file

pygame.quit()