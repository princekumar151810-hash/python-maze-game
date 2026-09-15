import pygame
import sys
import cv2
import numpy as np
import os
import random

pygame.init()

CELL_SIZE = 30
GRID_SIZE = 20
WALL_SIZE = 4

WIDTH = CELL_SIZE * GRID_SIZE
HEIGHT = CELL_SIZE * GRID_SIZE + 40
GAME_HEIGHT = CELL_SIZE * GRID_SIZE
BALL_SIZE = 10
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SCORE_BG = (240, 240, 240)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Maze Escape")
clock = pygame.time.Clock()


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)

    def move(self, dx, dy, walls):
        if dx != 0:
            next_x = self.x + dx * self.speed
            test_rect = pygame.Rect(next_x, self.y, BALL_SIZE, BALL_SIZE)

            if not any(test_rect.colliderect(wall.rect) for wall in walls):
                self.x = next_x

        if dy != 0:
            next_y = self.y + dy * self.speed
            test_rect = pygame.Rect(self.x, next_y, BALL_SIZE, BALL_SIZE)

            if not any(test_rect.colliderect(wall.rect) for wall in walls):
                self.y = next_y

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self):
        pygame.draw.circle(
            screen,
            RED,
            (int(self.x + BALL_SIZE / 2), int(self.y + BALL_SIZE / 2)),
            BALL_SIZE // 2
        )


class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self):
        pygame.draw.rect(screen, BLACK, self.rect)


class Game:
    def __init__(self):
        self.ball = Ball(CELL_SIZE // 2, CELL_SIZE // 2)
        self.walls = []

        self.goal = pygame.Rect(
            WIDTH - CELL_SIZE + 5,
            HEIGHT - CELL_SIZE + 5 - 40,
            CELL_SIZE - 10,
            CELL_SIZE - 10
        )

        self.font = pygame.font.Font(None, 36)

        self.load_maze()

        # Background music
        music_file = os.path.join("assets", "game_music.mp3")

        if os.path.exists(music_file):
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
        else:
            print("Warning: Music file not found!")

    def load_maze(self):
        self.walls = []

        # Maze images are inside assets folder
        maze_file = os.path.join("assets", "maze6.png")

        maze_img = cv2.imread(maze_file, cv2.IMREAD_GRAYSCALE)

        if maze_img is None:
            print(f"Error: Could not load maze image {maze_file}")
            return

        maze_img = cv2.resize(
            maze_img,
            (WIDTH, GAME_HEIGHT)
        )

        _, maze_binary = cv2.threshold(
            maze_img,
            127,
            255,
            cv2.THRESH_BINARY
        )

        wall_padding = 1

        for y in range(GAME_HEIGHT):
            for x in range(WIDTH):
                if maze_binary[y, x] == 0:
                    self.walls.append(
                        Wall(
                            x,
                            y,
                            WALL_SIZE + wall_padding,
                            WALL_SIZE + wall_padding
                        )
                    )

    def load_random_maze(self):
        self.walls = []

        maze_number = random.randint(0, 9)

        maze_file = os.path.join(
            "assets",
            f"maze{maze_number}.png"
        )

        print(f"Loading maze {maze_number}")

        maze_img = cv2.imread(
            maze_file,
            cv2.IMREAD_GRAYSCALE
        )

        if maze_img is None:
            print(f"Error: Could not load maze image {maze_file}")
            return

        maze_img = cv2.resize(
            maze_img,
            (WIDTH, GAME_HEIGHT)
        )

        _, maze_binary = cv2.threshold(
            maze_img,
            127,
            255,
            cv2.THRESH_BINARY
        )

        wall_padding = 1

        for y in range(GAME_HEIGHT):
            for x in range(WIDTH):
                if maze_binary[y, x] == 0:
                    self.walls.append(
                        Wall(
                            x,
                            y,
                            WALL_SIZE + wall_padding,
                            WALL_SIZE + wall_padding
                        )
                    )

    def draw_score(self, maze_completed):
        score_rect = pygame.Rect(
            0,
            GAME_HEIGHT,
            WIDTH,
            40
        )

        pygame.draw.rect(
            screen,
            SCORE_BG,
            score_rect
        )

        pygame.draw.line(
            screen,
            BLACK,
            (0, GAME_HEIGHT),
            (WIDTH, GAME_HEIGHT),
            2
        )

        text = self.font.render(
            f"Mazes Completed: {maze_completed}",
            True,
            BLACK
        )

        text_rect = text.get_rect(
            center=(WIDTH // 2, GAME_HEIGHT + 20)
        )

        screen.blit(text, text_rect)

    def reset_ball(self):
        self.ball.x = CELL_SIZE // 2
        self.ball.y = CELL_SIZE // 2

        self.ball.rect.x = self.ball.x
        self.ball.rect.y = self.ball.y

    def run(self):
        running = True
        maze_completed = 0

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            dx = (
                keys[pygame.K_RIGHT]
                - keys[pygame.K_LEFT]
            )

            dy = (
                keys[pygame.K_DOWN]
                - keys[pygame.K_UP]
            )

            self.ball.move(
                dx,
                dy,
                self.walls
            )

            if self.ball.rect.colliderect(self.goal):

                maze_completed += 1

                print(
                    f"Maze {maze_completed} completed! "
                    "Loading next maze..."
                )

                self.load_random_maze()
                self.reset_ball()

            screen.fill(WHITE)

            pygame.draw.rect(
                screen,
                GREEN,
                self.goal
            )

            self.ball.draw()

            for wall in self.walls:
                wall.draw()

            self.draw_score(
                maze_completed
            )

            pygame.display.flip()

            clock.tick(FPS)

        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()