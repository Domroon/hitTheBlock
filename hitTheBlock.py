import pygame as pg
from pygame.math import Vector2
from pygame.sprite import GroupSingle, Sprite
from pygame.sprite import Group
from pygame import Surface
from random import randint

TOP_BAR_HEIGHT = 40
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 720 + TOP_BAR_HEIGHT
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

HITBLOCK_WIDTH = SCREEN_WIDTH / 10
HITBLOCK_HEIGHT = SCREEN_HEIGHT / 10
GAP_SIZE = SCREEN_WIDTH / 50


class Ball(Sprite):
    def __init__(self, color=(255, 255, 255), size=[20, 20], start_pos=[SCREEN_WIDTH/2, SCREEN_HEIGHT/1.5], angle=randint(200, 340), velocity=7):
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


class Borders(Sprite):
    def __init__(self, border_thickness=10, shift_down=0, shift_right=0):
        super().__init__()
        self.top = Border((255, 0, 0), (SCREEN_WIDTH, border_thickness), (shift_right, shift_down))
        self.right = Border((0, 255, 0), (10, SCREEN_HEIGHT - 2*border_thickness), (SCREEN_WIDTH - border_thickness + shift_right, border_thickness + shift_down))
        self.bottom = Border((0, 0, 255), (SCREEN_WIDTH, border_thickness), (shift_right, SCREEN_HEIGHT - border_thickness + shift_down))
        self.left = Border((0, 255, 255), (border_thickness, SCREEN_HEIGHT - 2* border_thickness), (shift_right, border_thickness + shift_down))
        self.right_left_group = Group(self.right, self.left)
        self.top_bottom_group = Group(self.top, self.bottom)


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
    def __init__(self, shift_up=0, length=80, width=20, middle_color=(255, 0, 255), side_color=(255, 0, 0)):
        super().__init__()
        self.side_length = length / 2
        self.middle = SimpleKeeper(middle_color, [length, width], [WINDOW_WIDTH/2, WINDOW_HEIGHT - width - shift_up])
        self.left = SimpleKeeper(side_color, [length/4, width], [self.middle.rect.x - self.side_length/4, WINDOW_HEIGHT - width - shift_up]) 
        self.right = SimpleKeeper(side_color, [length/4, width], [self.middle.rect.x + length + self.side_length/4, WINDOW_HEIGHT - width - shift_up]) 

        self.group = Group()
        self.group.add(self.left, self.middle, self.right)


class HitBlock(Sprite):
    def __init__(self, width=HITBLOCK_WIDTH, height=HITBLOCK_HEIGHT, pos=[WINDOW_WIDTH/10, WINDOW_HEIGHT/10], color=(255, 255, 255), number=str(randint(1, 10))):
        super().__init__()
        self.number = number
        self.color = color
        self.image = Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.inner_image = Surface([width/1.2, height/1.2])
        self.inner_image.fill((0, 0, 0))
        self.inner_width = width/2
        self.inner_height = height/2
        self.inner_rect = self.inner_image.get_rect(center=[width/2, height/2])
        self.image.blit(self.inner_image, self.inner_rect)
        self.font = pg.freetype.Font(None, SCREEN_HEIGHT/25)
        # self.font_rect = self.font.get_rect(self.number)
        self.font_image, self.font_rect = self.font.render(self.number, self.color)
        self.font_rect.center =  [self.inner_width, self.inner_height]
        self.font.render_to(self.image, self.font_rect, self.number, self.color)

    def decrease_number(self):
        self.number = str(int(self.number) - 1)
        self.image.blit(self.inner_image, self.inner_rect)
        self.font.render_to(self.image, self.font_rect, self.number, self.color)


class Score(Sprite):
    def __init__(self, number='0', color=(255, 255, 255)):
        super().__init__()
        self.number = number
        self.color = color
        self.font = self.font = pg.freetype.Font(None, TOP_BAR_HEIGHT/1.5)
        self.image, self.rect = self.font.render(self.number, self.color)
        self.rect.center = [WINDOW_WIDTH/2, TOP_BAR_HEIGHT/2]

    def increase(self):
        self.number = str(int(self.number) + 1)
        self.image.blit(self.image, self.rect)
        self.image, self.rect = self.font.render(self.number, self.color)
        self.rect.center = [WINDOW_WIDTH/2, TOP_BAR_HEIGHT/2]
        print(self.number)


def main():
    pg.init()
    try:
        window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption("HitTheBlock")

        # INIT SURFACES
        background = Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        top_bar = Surface((SCREEN_WIDTH, TOP_BAR_HEIGHT))
        top_bar.fill((255, 0, 255))
        screen = Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen_background = Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # INIT SPRITES
        borders = Borders(shift_down=TOP_BAR_HEIGHT)
        ball_group = Group()
        ball = None
        
        keeper = Keeper(shift_up=10)

        score = Score()
        score_group = GroupSingle(score)

        row = HITBLOCK_WIDTH - GAP_SIZE
        column = HITBLOCK_HEIGHT - GAP_SIZE + TOP_BAR_HEIGHT
        first_pos = [row, column]
        hitblocks = Group()
        hitblock_column_quantity = SCREEN_WIDTH/(HITBLOCK_WIDTH + GAP_SIZE)
        hitblock_row_quantity = (SCREEN_HEIGHT/2)/(HITBLOCK_HEIGHT+ GAP_SIZE)
        pos = first_pos
        for _ in range(0, int(hitblock_row_quantity)):
            for _ in range(0, int(hitblock_column_quantity)):
                hitblock = HitBlock(pos=pos, number=str(randint(1, 2)))
                hitblocks.add(hitblock)
                row += HITBLOCK_WIDTH + GAP_SIZE
                pos = [row, column]
            row = HITBLOCK_WIDTH - GAP_SIZE
            column += HITBLOCK_HEIGHT + GAP_SIZE
            pos = [row, column]

        clock = pg.time.Clock()
        fps = 120

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return

            # COLLISIONS
            keeper_collide_left = pg.sprite.collide_rect(keeper.left, borders.left)
            keeper_collide_right = pg.sprite.collide_rect(keeper.right, borders.right)
            if ball:
                if pg.sprite.spritecollide(ball, borders.right_left_group, False):
                    ball.angle += 180 - 2 * (ball.angle + randint(0, 3))
                if pg.sprite.collide_rect(ball, borders.top):
                    ball.angle += 360 - 2 * (ball.angle + randint(0, 3))
                if pg.sprite.collide_rect(ball, borders.bottom):
                    ball_group.remove(ball)
                    # ball.velocity = 0
                    # ball.angle += 360 - 2 * ball.angle + randint(0, 2)
                if pg.sprite.collide_rect(ball, keeper.left):
                    ball.angle = 250 + randint(-5, 5)
                if pg.sprite.collide_rect(ball, keeper.middle):
                    ball.angle = 270 + randint(-5, 5)
                if pg.sprite.collide_rect(ball, keeper.right):
                    ball.angle = 290 + randint(-5, 5)
                collided_hitblock = pg.sprite.spritecollide(ball, hitblocks, False)
                if collided_hitblock:
                    ball.angle += 180 + randint(-5, 5)
                    score.increase()
                    for hitblock in collided_hitblock:
                        hitblock.decrease_number()
                        if int(hitblock.number) == 0:
                            hitblocks.remove(hitblock)

            # KEY PRESSES
            keys = pg.key.get_pressed()

            if keys[pg.K_SPACE] and not ball_group:
                ball = Ball(angle=randint(250, 340))
                ball_group.add(ball)

            if keys[pg.K_RIGHT] and not keeper_collide_right:
                keeper.group.update('right', 4)
            elif keys[pg.K_LEFT] and not keeper_collide_left:
                keeper.group.update('left', 4)
            
            # DRAW
            window.blit(background, (0, 0))
            # window.blit(screen_background, [0, 0])
            borders.right_left_group.draw(window)

            borders.top_bottom_group.draw(window)    

            ball_group.draw(window)
            ball_group.update()

            hitblocks.draw(window)

            keeper.group.draw(window)

            score_group.draw(window)
            
            # window.blit(top, [0, TOP_BAR_HEIGHT])

            # window.blit(top_bar, [0, 0])
            
            pg.display.update()
            # pg.display.flip()
            clock.tick(fps)

    finally:
        pg.quit()


if __name__ == '__main__':
    main()