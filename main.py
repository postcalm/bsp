import pygame
import pygame.gfxdraw
import time

from leaf import create_leaf
from misc import BLACK, GRAY, SCREEN, WIDTH, HEIGHT


RUNNING = True

pygame.init()
SCREEN.fill(BLACK)


def drop():
    global RUNNING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False


def main():
    leafs = create_leaf(WIDTH, HEIGHT)
    while RUNNING:
        drop()
        for leaf in leafs:
            pygame.gfxdraw.rectangle(
                SCREEN,
                pygame.Rect(leaf.x, leaf.y, leaf.width, leaf.height),
                GRAY
            )
            # pygame.display.flip()


if __name__ == '__main__':
    main()
