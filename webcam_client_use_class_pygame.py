# consumer_pygame.py
import pygame
from class_webcam_client import FrameClient
import sys

client = FrameClient()
h, w, _ = client.shape
screen = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            client.close()
            pygame.quit()
            sys.exit()


    surface = pygame.image.frombuffer(client.frameshm.buf, (w, h), "BGR")
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    clock.tick(30)
