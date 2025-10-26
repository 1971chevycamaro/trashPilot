import pygame
import class_messaging as messaging
import sys
pygame.init()
sm = messaging.SubMaster('modelV2')
W, H = 400, 400
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

# wheel = pygame.font.SysFont("segoeuisymbol", 300)  # large font
wheel = pygame.image.load("assets/steeringwheel.svg")   
wheel = pygame.transform.smoothscale(wheel, (300, 300))
symbol = "⎉"

angle = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # This triggers when you click the window's X
            running = False
    if sm.updated():
        curv = sm.data()['action'][0]
        # Render and rotate
        # text = wheel.render(symbol, True, (255, 255, 255))
        # text = text.subsurface(text.get_bounding_rect())
        rotated = pygame.transform.rotate(wheel, curv*-3000)
        rect = rotated.get_rect(center=(W//2, H//2))

        screen.fill((30, 30, 30))
        screen.blit(rotated, rect)
        pygame.display.flip()
        clock.tick(60)

pygame.quit()
