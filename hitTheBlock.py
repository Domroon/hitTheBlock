import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Sprite
from pygame.sprite import Group
from pygame import Surface
from random import randint


class Block(Sprite):
    def __init__(self, color, size, start_pos, angle, velocity):
        super().__init__()
        self.image = Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.angle = angle
        self.pos = Vector2(start_pos)
        self.velocity = velocity
    
    def update(self):
        self.pos += Vector2(1, 0).rotate(self.angle) * self.velocity
        self.rect.center = self.pos


class Border(Sprite):
    def __init__(self, color, size, pos):
        super().__init__()

        self.image = Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)


class SimpleKeeper(Sprite):
    def __init__(self, color:tuple, size:list, pos:list):
        super().__init__()
        self.image = Surface(size)
        self.image.fill(color)
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, direction:str, velocity:int):
        if direction == 'right':
            self.pos[0] += velocity
        elif direction == 'left':
            self.pos[0] -= velocity
        self.rect.center = self.pos


class Keeper(Sprite):
    def __init__(self, screen_width, screen_height, length=80, width=20, middle_color=(0, 0, 255), side_color=(255, 0, 0)):
        super().__init__()
        self.side_length = length / 2
        self.middle = SimpleKeeper((255, 0, 0), [length, width], [screen_width/2, screen_height - width])
        self.left = SimpleKeeper((0, 255, 255), [length/4, width], [self.middle.rect.x - self.side_length/4, screen_height - width]) 
        self.right = SimpleKeeper((0, 255, 255), [length/4, width], [self.middle.rect.x + length + self.side_length/4, screen_height - width]) 

        self.group = Group()
        self.group.add(self.left, self.middle, self.right)


def main():
    pg.init()
    try:
        screen_width = 720
        screen_height = 720

        rect_width = 20
        rect_height = 20

        window = pg.display.set_mode((screen_width, screen_height))
        pg.display.set_caption("Test")

        background = Surface((screen_width, screen_width))
        
        top_border = Border((255, 0, 0), (720, 10), (0, 0))
        right_border = Border((0, 255, 0), (10, 700), (710, 10))
        bottom_border = Border((0, 0, 255), (720, 10), (0, 710))
        left_border = Border((0, 255, 255), (10, 700), (0, 10))

        right_left_borders = Group()
        right_left_borders.add(right_border, left_border)

        top_bottom_borders = Group()
        top_bottom_borders.add(top_border, bottom_border)

        block_group = Group()
        block = Block((255, 255, 255), [rect_width, rect_height], [randint(0, screen_width), randint(0, screen_height)], randint(12, 340), randint(5, 5))
        
        keeper = Keeper(screen_width, screen_height)

        clock = pg.time.Clock()
        fps = 120

        while True:
            for event in pg.event.get():
                #print(event)
                if event.type == pg.QUIT:
                    return

            # COLLISIONS
            keeper_collide_left = pg.sprite.collide_rect(keeper.left, left_border)
            keeper_collide_right = pg.sprite.collide_rect(keeper.right, right_border)

            if pg.sprite.spritecollide(block, right_left_borders, False):
                block.angle += 180 - 2 * (block.angle + randint(0, 3))
            if pg.sprite.collide_rect(block, top_border):
                block.angle += 360 - 2 * (block.angle + randint(0, 3))
            if pg.sprite.collide_rect(block, bottom_border):
                # block.velocity = 0
                block_group.remove(block)
                # block.angle += 360 - 2 * block.angle + randint(0, 2)
                # print('hit BOTTOM')
            if pg.sprite.collide_rect(block, keeper.left):
                # block.angle += 360 - 2 * block.angle
                block.angle = 250
            if pg.sprite.collide_rect(block, keeper.middle):
                # block.angle += 360 - 2 * block.angle
                block.angle = 270 + randint(-5, 5)
            if pg.sprite.collide_rect(block, keeper.right):
                block.angle = 290

            # KEY PRESSES
            keys = pg.key.get_pressed()

            if keys[pg.K_SPACE] and not block_group:
                block = Block((255, 255, 255), [rect_width, rect_height], [randint(0, screen_width), randint(0, screen_height)], randint(12, 340), randint(7, 7))
                block_group.add(block)

            if keys[pg.K_RIGHT] and not keeper_collide_right:
                keeper.group.update('right', 4)
            elif keys[pg.K_LEFT] and not keeper_collide_left:
                keeper.group.update('left', 4)
            
            window.blit(background, (0, 0))

            right_left_borders.draw(window)
            top_bottom_borders.draw(window)

            block_group.draw(window)
            block_group.update()

            keeper.group.draw(window)

            

            pg.display.update()
            clock.tick(fps)

    finally:
        pg.quit()


if __name__ == '__main__':
    main()