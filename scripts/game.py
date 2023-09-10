from .paddle import Paddle
from .ball import Ball
import pygame
import random
pygame.init()

# Class that will hold the statistics about the game
class GameInformation:
    def __init__(self, left_hits, right_hits, left_score, right_score):
        self.left_hits = left_hits
        self.right_hits = right_hits
        self.left_score = left_score
        self.right_score = right_score
# Class that will hold statistics about the round
class RoundInformation:
    def __init__(self, total_hits, left_score, right_score):
        self.total_hits=total_hits
        self.left_score=left_score
        self.right_score=right_score
# Main game class
class Game:
    # Define fonts and colours
    SCORE_FONT=pygame.font.SysFont("comicsans", 26)
    SMALL_SCORE_FONT=pygame.font.SysFont("comicsans", 20)
    BLACK=(0, 0, 0)

    def __init__(self, colour, win, window_width, window_height, paddle_width, paddle_height, ball_radius, paddle_velocity, ball_velocity):
        # Get the parameters for game settings
        self.colour=colour
        self.window_width=window_width
        self.window_height=window_height
        self.paddle_width=paddle_width
        self.paddle_height=paddle_height
        self.ball_radius=ball_radius
        self.paddle_velocity=paddle_velocity
        self.ball_velocity=ball_velocity
        # Define paddles and ball
        self.left_paddle = Paddle(10, self.window_height//2-self.paddle_height//2, self.paddle_width, self.paddle_height, self.paddle_velocity)
        self.right_paddle = Paddle(self.window_width-10-self.paddle_width, self.window_height//2-self.paddle_height//2, self.paddle_width, self.paddle_height, self.paddle_velocity)
        self.ball = Ball(self.window_width // 2, self.window_height // 2, self.ball_radius, self.ball_velocity)
        # Initilise scores
        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
        self.win = win

    # Method for drawing the score
    def _draw_score(self, name1, name2, mode):
        # PVP MODE
        if mode==0:
            # Define left score variable
            left_score_text=self.SCORE_FONT.render(f"Player 1 score: {self.left_score}", 1, self.BLACK)
            # Define right score variable
            right_score_text=self.SCORE_FONT.render(f"Player 2 score: {self.right_score}", 1, self.BLACK)
        # P VS AI MODE
        if mode==1:
            # Define left score variable
            left_score_text=self.SCORE_FONT.render(f"Player 1 score: {self.left_score}", 1, self.BLACK)
            # Define right score variable
            right_score_text=self.SCORE_FONT.render(f"AI score: {self.right_score}", 1, self.BLACK)
        # AI VS AI MODE
        if mode==2:
            # Define left score variable
            left_score_text=self.SMALL_SCORE_FONT.render(f"{name1} score: {self.left_score}", 1, self.BLACK)
            # Define right score variable
            right_score_text=self.SMALL_SCORE_FONT.render(f"{name2} score: {self.right_score}", 1, self.BLACK)
        # AI VS HARDCODED MODE
        if mode==3:
            # Define left score variable
            right_score_text=self.SMALL_SCORE_FONT.render(f"{name1} score: {self.right_score}", 1, self.BLACK)
            # Define right score variable
            left_score_text=self.SMALL_SCORE_FONT.render(f"Hardcode paddle score: {self.left_score}", 1, self.BLACK)
        # Draw left score
        self.win.blit(left_score_text, (self.window_width//4-left_score_text.get_width()//2, 0))
        # Draw right score
        self.win.blit(right_score_text, (self.window_width*(3/4)-right_score_text.get_width()//2, 0))

    # Method to draw the number of hits in the middle
    def _draw_hits(self):
        # Define hits string variable
        hits_text = self.SCORE_FONT.render(f"Hits: {self.left_hits + self.right_hits}", 1, self.BLACK)
        # Draw hits score
        self.win.blit(hits_text, (self.window_width //2 - hits_text.get_width()//2, 0))

    # Method to draw the dotted line at top and bottom
    def _draw_divider(self):
        # Draw dotted line at the top
        for i in range(10, self.window_width, self.window_width//50):
            if i%2==1:
                continue
            pygame.draw.rect(self.win, self.BLACK, (i, 40, 10, 2))
        # Draw dotted line at the bottom
        for i in range(10, self.window_width, self.window_width//50):
            if i%2==1:
                continue
            pygame.draw.rect(self.win, self.BLACK, (i, self.window_height-40, 10, 2))

    # Method to handle collisions
    def _handle_collision(self):
        ball=self.ball
        left_paddle=self.left_paddle
        right_paddle=self.right_paddle
        # Check the ball colliding with the floor
        if ball.y+ball.radius>self.window_height-40 and ball.y_velocity>0:
            ball.y_velocity=ball.y_velocity*-1
        # Check the ball colliding with the ceilling
        elif ball.y-ball.radius<40 and ball.y_velocity<0:
            ball.y_velocity=ball.y_velocity*-1
        # Check colliding with left paddle
        if ball.x_velocity<0:
            # Check collision in terms of height of the paddle
            if ball.y>=left_paddle.y and ball.y<=left_paddle.y+left_paddle.height:
                # Check collision in terms of the right edge of the left paddle
                if ball.x-ball.radius<=left_paddle.x+left_paddle.width:
                    ball.x_velocity=ball.x_velocity*-1
                    # Calculate the displacement in terms of y coordinate between the ball and the paddle
                    middle_y=left_paddle.y+left_paddle.height/2
                    difference_in_y=ball.y-middle_y
                    # Get the reduction factor
                    reduction_factor=(left_paddle.height/2)/ball.MAX_VELOCITY
                    y_velocity=difference_in_y/reduction_factor
                    ball.y_velocity=y_velocity
                    # Increment hits
                    self.left_hits += 1
        # Check colliding with right paddle
        else:
            # Check collision in terms of height of the paddle
            if ball.y>=right_paddle.y and ball.y<=right_paddle.y+right_paddle.height:
                # Check collision in terms of the left edge of the right paddle
                if ball.x+ball.radius>=right_paddle.x:
                    ball.x_velocity=ball.x_velocity*-1
                    # Calculate the displacement in terms of y coordinate between the ball and the paddle
                    middle_y=right_paddle.y+right_paddle.height/2
                    difference_in_y=ball.y-middle_y
                    # Get the reduction factor
                    reduction_factor=(right_paddle.height/2)/ball.MAX_VELOCITY
                    y_velocity=difference_in_y/reduction_factor
                    ball.y_velocity=y_velocity
                    # Increment hits
                    self.right_hits += 1

    # Method to draw the game
    def draw(self, name1=None, name2=None, draw_score=True, draw_hits=False, mode=0):
        # Colour window
        self.win.fill(self.colour)
        self._draw_divider()
        if draw_score:
            self._draw_score(name1, name2, mode)
        if draw_hits:
            self._draw_hits()
        for paddle in [self.left_paddle, self.right_paddle]:
            paddle.draw(self.win)
        self.ball.draw(self.win)

    # Method to move the paddle, returns boolean indicating if it is possible to do the move
    def move_paddle(self, left=True, up=True):
        if left:
            # Check if the move is allowed
            if up and self.left_paddle.y - self.left_paddle.velocity < 40:
                return False
            if not up and self.left_paddle.y + self.paddle_height > self.window_height-50:
                return False
            # If so then move
            self.left_paddle.move(up)
        else:
            # Check if the move is allowed
            if up and self.right_paddle.y - self.right_paddle.velocity < 40:
                return False
            if not up and self.right_paddle.y + self.paddle_height > self.window_height-50:
                return False
            # If so then move
            self.right_paddle.move(up)
        return True

    # Executes single loop of the game, returns statistics of the game
    def loop(self):
        left_won=0
        right_won=0
        self.ball.move()
        self._handle_collision()
        self.round_finish=False
        self.total_hits=self.left_hits+self.right_hits
        # If ball crossed left side
        if self.ball.x<0:
            self.round_finish=True
            self.ball.reset()
            self.right_score+=1
            right_won=1
            self.total_hits=self.left_hits+self.right_hits
            self.left_hits=0
            self.right_hits=0
        # If ball crossed right side
        elif self.ball.x > self.window_width:
            self.round_finish=True
            self.ball.reset()
            self.left_score+=1
            left_won=1
            self.total_hits=self.left_hits+self.right_hits
            self.left_hits=0
            self.right_hits=0
        # Return game statistics
        game_info=GameInformation(self.left_hits, self.right_hits, self.left_score, self.right_score)
        round_info=RoundInformation(self.total_hits, left_won, right_won)
        return [game_info, round_info]

    # Method to reset game
    def reset(self):
        self.ball.reset()
        self.left_paddle.reset()
        self.right_paddle.reset()
        self.left_score=0
        self.right_score=0
        self.left_hits=0
        self.right_hits=0