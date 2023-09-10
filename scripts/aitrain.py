from .game import Game
from .button import Button
import pygame, neat, random, datetime, os
import pandas as pd

# Define colours, fonts and constants
BLACK=(0,0,0)
GRAY=(64,64,64)
BACK_FONT=pygame.font.SysFont('comicsans', 16)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)
WIN_FONT=pygame.font.SysFont('comicsans', 40)
WINNING_SCORE=15

# Get working directory
cwd=os.getcwd()

# Auxiliary function
def sign(x):
    if x >= 0: 
        return 1
    else:
        return -1

# Class that will contain statistics for the whole game
class GameInformation:
    def __init__(self, left_hits, right_hits, left_score, right_score):
        self.left_hits = left_hits
        self.right_hits = right_hits
        self.left_score = left_score
        self.right_score = right_score
# Class that will contain statistics for the round
class RoundInformation:
    def __init__(self, total_hits, left_score, right_score):
        self.total_hits=total_hits
        self.left_score=left_score
        self.right_score=right_score

class GameAI:
    # Initilise class
    def __init__(self, colour, win, window_width, window_height, paddle_width, paddle_height, ball_radius, paddle_velocity, ball_velocity):
        self.colour=colour
        self.win = win
        self.window_width = window_width
        self.window_height = window_height
        self.paddle_width=paddle_width
        self.paddle_height=paddle_height
        self.ball_radius=ball_radius
        self.paddle_velocity=paddle_velocity
        self.ball_velocity=ball_velocity
        # Initilise game
        self.game=Game(self.colour, self.win, self.window_width, self.window_height, self.paddle_width, self.paddle_height, self.ball_radius, self.paddle_velocity, self.ball_velocity)
        self.left_paddle=self.game.left_paddle
        self.right_paddle=self.game.right_paddle
        self.ball=self.game.ball

        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
    # Method for the game between player and trained model
    def test_p_vs_ai(self, net, activation):
        clock = pygame.time.Clock()
        # Define button
        BACK_BUTTON = Button(image=None, pos=(50, self.window_height-20), text_input="BACK", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        run = True
        # Define values that will make game more difficult with every hit
        y_addifier=0.5
        total_hits=0
        while run:
            clock.tick(60)
            # Start game
            game_info = self.game.loop()
            # Get mouse postition
            GAME_MOUSE_POS = pygame.mouse.get_pos()
            # Get mouse click event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    quit()
                # If back button pressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(GAME_MOUSE_POS):
                        self.game.reset()
                        return True
            # Manage ai paddle movement
            self.ai_paddle_movement(net, activation)
            # Speed up the ball after every hit
            if total_hits<game_info[1].total_hits:
                self.ball.x_velocity=self.ball.x_velocity*1.01
                self.ball.y_velocity=self.ball.y_velocity+(sign(self.ball.y_velocity)*y_addifier)
                y_addifier+=0.1
                total_hits+=1
            # Reset the speed of the ball when end of round
            if self.game.round_finish:
                total_hits=0
                y_addifier=0.5
                self.ball.reset()
            # Move the player paddle
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.game.move_paddle(left=True, up=True)
            elif keys[pygame.K_s]:
                self.game.move_paddle(left=True, up=False)
            # Draw the game
            self.game.draw(draw_score=True, draw_hits=True, mode=1)
            # Draw and update the back buttons
            BACK_BUTTON.changeColor(GAME_MOUSE_POS)
            BACK_BUTTON.update(self.win)
            pygame.display.update()
    
    # Method for testing ai against hardcoded paddle
    def test_ai_vs_hardcode(self, net, activation, name1):
        clock = pygame.time.Clock()
        # Initilise variables and buttons
        FPS=60
        y_addifier=0.5
        BACK_BUTTON = Button(image=None, pos=(50, self.window_height-20), text_input="BACK", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        NORMAL_BUTTON = Button(image=None, pos=(220, self.window_height-20), text_input="NORMAL SPEED", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        FAST_BUTTON = Button(image=None, pos=(380, self.window_height-20), text_input="FAST", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        FASTEST_BUTTON = Button(image=None, pos=(500, self.window_height-20), text_input="FASTEST", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        total_hits=0
        # Create path for saving logs
        date=datetime.datetime.now()
        path=cwd+'/data/ai_vs_hardcode_logs/'+name1+f"_{date:%Y-%m-%d_%H-%M-%S}.csv"
        data=pd.DataFrame(columns=['total_hits','left_scored','right_scored'])
        run = True
        while run:
            # Adjust the speed according to FPS value
            clock.tick(FPS)
            game_info = self.game.loop()
            GAME_MOUSE_POS = pygame.mouse.get_pos()
            # Get events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    quit()
                # Back button pressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(GAME_MOUSE_POS):
                        self.game.reset()
                        return True
                    # Normal speed
                    if NORMAL_BUTTON.checkForInput(GAME_MOUSE_POS):
                        FPS=60
                    # Fast speed
                    if FAST_BUTTON.checkForInput(GAME_MOUSE_POS):
                        FPS=160
                    # Fastest speed
                    if FASTEST_BUTTON.checkForInput(GAME_MOUSE_POS):
                        FPS=300
            # Move AI paddle
            self.ai_paddle_movement(net, activation)
            # Move hardcoded paddle
            if self.ball.y>self.left_paddle.y+self.left_paddle.height//2:
                self.game.move_paddle(left=True, up=False)
            if self.ball.y<self.left_paddle.y+self.left_paddle.height//2:
                self.game.move_paddle(left=True, up=True)

            # Speed up the ball after every hit
            if total_hits<game_info[1].total_hits:
                self.ball.x_velocity=self.ball.x_velocity*1.01
                self.ball.y_velocity=self.ball.y_velocity+(sign(self.ball.y_velocity)*y_addifier)
                y_addifier+=0.1
                total_hits+=1  
            # Reset the speed of the ball when end of round
            if self.game.round_finish:
                total_hits=0
                y_addifier=0.5
                self.ball.reset()
                row=[game_info[1].total_hits, game_info[1].left_score, game_info[1].right_score]
                data.loc[len(data)] = row
                data.to_csv(path, index=False)
            # Check if someone won
            won=False
            if self.game.left_score>=WINNING_SCORE:
                won=True
                win_text="Hardcoded paddle won"
            elif self.game.right_score>=WINNING_SCORE:
                won=True
                win_text=name1+" won"
            # Show winning text and come back to main menu
            if won:
                text=WIN_FONT.render(win_text, 1, BLACK)
                self.win.blit(text, (self.window_width//2-text.get_width()//2, self.window_height//2-text.get_height()//2))
                pygame.display.update()
                pygame.time.delay(4000)
                self.game.reset()
                return True
            # Draw the game
            self.game.draw(name1, draw_score=True, draw_hits=True, mode=3)
            # Show and update buttons
            for button in [BACK_BUTTON, NORMAL_BUTTON, FAST_BUTTON, FASTEST_BUTTON]:
                button.changeColor(GAME_MOUSE_POS)
                button.update(self.win)
            pygame.display.update()
    
    # Method for ai vs ai game between two trained models
    def test_ai_vs_ai(self, nets, activations, name1, name2):
        clock = pygame.time.Clock()
        # Define buttons and variables
        FPS=60
        y_addifier=0.5
        BACK_BUTTON = Button(image=None, pos=(50, self.window_height-20), text_input="BACK", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        NORMAL_BUTTON = Button(image=None, pos=(220, self.window_height-20), text_input="NORMAL SPEED", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        FAST_BUTTON = Button(image=None, pos=(380, self.window_height-20), text_input="FAST", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        FASTEST_BUTTON = Button(image=None, pos=(500, self.window_height-20), text_input="FASTEST", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        total_hits=0
        run = True
        # Get path to save logs into
        date=datetime.datetime.now()
        path=cwd+'/data/ai_vs_ai_logs/'+name1+'_vs_'+name2+f"_{date:%Y-%m-%d_%H-%M-%S}.csv"
        data=pd.DataFrame(columns=['total_hits','left_scored','right_scored'])
        while run:
            clock.tick(FPS)
            game_info = self.game.loop()
            GAME_MOUSE_POS = pygame.mouse.get_pos()
            # Get events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    quit()
                # Something got clicked
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Back button clicked
                    if BACK_BUTTON.checkForInput(GAME_MOUSE_POS):
                        self.game.reset()
                        return True
                    # Speed buttons clicked
                    if NORMAL_BUTTON.checkForInput(GAME_MOUSE_POS):
                        FPS=60
                    if FAST_BUTTON.checkForInput(GAME_MOUSE_POS):
                        FPS=160
                    if FASTEST_BUTTON.checkForInput(GAME_MOUSE_POS):
                        FPS=300
            # Handle ai paddles movements
            self.ai_paddle_movement(nets[0], activations[0], left=True)
            self.ai_paddle_movement(nets[1], activations[1])

            # Speed up the ball after every hit
            if total_hits<game_info[1].total_hits:
                self.ball.x_velocity=self.ball.x_velocity*1.01
                self.ball.y_velocity=self.ball.y_velocity+(sign(self.ball.y_velocity)*y_addifier)
                y_addifier+=0.1
                total_hits+=1
            
            # Reset the speed of the ball when end of round
            if self.game.round_finish:
                total_hits=0
                y_addifier=0.5
                self.ball.reset()
                row=[game_info[1].total_hits, game_info[1].left_score, game_info[1].right_score]
                data.loc[len(data)] = row
                data.to_csv(path, index=False)
            
            # Check if someone won the game
            won=False
            if self.game.left_score>=WINNING_SCORE:
                won=True
                win_text=name1+" won"
            elif self.game.right_score>=WINNING_SCORE:
                won=True
                win_text=name2+" won"
            # If someone won then show winning text
            if won:
                text=WIN_FONT.render(win_text, 1, BLACK)
                self.win.blit(text, (self.window_width//2-text.get_width()//2, self.window_height//2-text.get_height()//2))
                pygame.display.update()
                pygame.time.delay(4000)
                self.game.reset()
                return True
            # Draw the game and buttons
            self.game.draw(name1, name2, draw_score=True, draw_hits=True, mode=2)
            for button in [BACK_BUTTON, NORMAL_BUTTON, FAST_BUTTON, FASTEST_BUTTON]:
                button.changeColor(GAME_MOUSE_POS)
                button.update(self.win)
            pygame.display.update()

    # Method to train AI when ai vs itself mode was chosen
    def train_ai_vs_ai(self, genome1, genome2, config, activation):
        clock = pygame.time.Clock()
        run = True
        # Create neural networks
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)
        self.genome1 = genome1
        self.genome2 = genome2
        # Define button
        BACK_BUTTON = Button(image=None, pos=(50, self.window_height-20), text_input="BACK", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        # Set number of hits after which the game restarts
        max_hits = 15
        while run:
            clock.tick(3000)
            # Start game
            game_info = self.game.loop()
            # Get events
            GAME_MOUSE_POS = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(GAME_MOUSE_POS):
                        self.game.reset()
                        return True
            # Apply rewards and penalties to genomes
            self.train_ai_paddles(net1, activation, net2)
            # Draw game
            self.game.draw(draw_score=False, draw_hits=True)
            # Display button
            BACK_BUTTON.changeColor(GAME_MOUSE_POS)
            BACK_BUTTON.update(self.win)
            pygame.display.update()
            # Update fitness if someone won or maximum number of hits reached
            if game_info[0].left_score == 1 or game_info[0].right_score == 1 or game_info[0].left_hits >= max_hits:
                self.calculate_fitness_ai(game_info)
                break

        return False

    # Method for training AI against hardcoded paddle
    def train_ai_vs_hardcode(self, genome, config, activation):
        clock = pygame.time.Clock()
        run = True
        # Create neural network
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome
        # Define button and maximum number of hits
        BACK_BUTTON = Button(image=None, pos=(50, self.window_height-20), text_input="BACK", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
        max_hits = 15
        while run:
            clock.tick(3000)
            # Run game
            game_info = self.game.loop()
            # Get clicking events
            GAME_MOUSE_POS = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(GAME_MOUSE_POS):
                        self.game.reset()
                        return True
            # Update rewards and penalties
            self.train_ai_paddles(net, activation)
            # Draw game and buttons
            self.game.draw(draw_score=False, draw_hits=True)
            BACK_BUTTON.changeColor(GAME_MOUSE_POS)
            BACK_BUTTON.update(self.win)
            pygame.display.update()
            # Update fitness after scoring a point or max number of hits reached
            if game_info[0].left_score == 1 or game_info[0].right_score == 1 or game_info[0].left_hits >= max_hits:
                self.calculate_fitness_hardcode(game_info)
                break

        return False

    # Method for movement of AI paddle WHEN TESTING (PLAYING AGAINST IT)
    def ai_paddle_movement(self, net, activation, left=False):
        if left:
            if activation=='relu':
                # Get the list with values of the output layer
                output = net.activate((self.left_paddle.y, abs(self.left_paddle.x - self.ball.x), self.ball.y))
                # Get the index of the highest value
                decision = output.index(max(output))
                # Dont move
                if decision==0:
                    pass
                # Move up
                if decision == 1:
                    self.game.move_paddle(left=True, up=True)
                # Move down
                elif decision == 2:
                    self.game.move_paddle(left=True, up=False)
            if activation=='tanh':
                # Get the value of the output
                output = net.activate((self.left_paddle.y, abs(self.left_paddle.x - self.ball.x), self.ball.y))[0]
                # Go up
                if output>0.9:
                    self.game.move_paddle(left=True, up=True)
                # Go down
                if output<-0.9:
                    self.game.move_paddle(left=True, up=False)
                # Stay the same
                if output>=-0.9 and output<=0.9:
                    pass
        else:
            if activation=='relu':
                # Get the list with values of the output layer
                output = net.activate((self.right_paddle.y, abs(self.right_paddle.x - self.ball.x), self.ball.y))
                # Get the index of the highest value
                decision = output.index(max(output))
                # Dont move
                if decision==0:
                    pass
                # Move up
                if decision == 1:
                    self.game.move_paddle(left=False, up=True)
                # Move down
                elif decision == 2:
                    self.game.move_paddle(left=False, up=False)
            if activation=='tanh':
                # Get the value of the output
                output = net.activate((self.right_paddle.y, abs(self.right_paddle.x - self.ball.x), self.ball.y))[0]
                # Go up
                if output>0.9:
                    self.game.move_paddle(left=False, up=True)
                # Go down
                if output<-0.9:
                    self.game.move_paddle(left=False, up=False)
                # Stay the same
                if output>=-0.9 and output<=0.9:
                    pass

    # Method for movement of AI paddle WHEN TRAINING
    def train_ai_paddles(self, net1, activation, net2=None):
        # Scenario when training against hardcoded
        if net2 is None:
            if activation=='relu':
                # Get output of the netowrk
                output=net1.activate((self.left_paddle.y, abs(self.left_paddle.x - self.ball.x), self.ball.y))
                # Derive decision
                decision=output.index(max(output))
                valid=True
                # Stay still
                if decision==0:
                    pass
                # Go up
                elif decision==1:
                    self.genome.fitness+=0.2
                    valid = self.game.move_paddle(left=True, up=True)
                # Go down
                elif decision==2:
                    self.genome.fitness+=0.2
                    valid = self.game.move_paddle(left=True, up=False)
                # If trying to go out of the borded then punish
                if not valid:
                    self.genome.fitness -= 1
                # Hardcoded paddle
                if self.ball.y>self.right_paddle.y+self.right_paddle.height//2:
                    self.game.move_paddle(left=False, up=False)
                if self.ball.y<self.right_paddle.y+self.right_paddle.height//2:
                    self.game.move_paddle(left=False, up=True)
            if activation=='tanh':
                # Get the output
                output=net1.activate((self.left_paddle.y, abs(self.left_paddle.x - self.ball.x), self.ball.y))[0]
                valid = True
                # Stay still
                if output>=-0.9 and output<=0.9:
                    pass
                # Go up
                elif output>0.9:
                    self.genome.fitness+=0.2
                    valid = self.game.move_paddle(left=True, up=True)
                # Go down
                elif output<-0.9:
                    self.genome.fitness+=0.2
                    valid = self.game.move_paddle(left=True, up=False)
                # If trying to go out of the borded then punish
                if not valid:
                    self.genome.fitness -= 1
                # Hardcoded paddle
                if self.ball.y>self.right_paddle.y+self.right_paddle.height//2:
                    self.game.move_paddle(left=False, up=False)
                if self.ball.y<self.right_paddle.y+self.right_paddle.height//2:
                    self.game.move_paddle(left=False, up=True)
        # Scenario when AI is trained vs AI
        else:
            players=[(self.genome1, net1, self.left_paddle, True), (self.genome2, net2, self.right_paddle, False)]
            if activation=='relu':
                # Iterate through each player
                for (genome, net, paddle, left) in players:
                    # Get the decision
                    output=net.activate((paddle.y, abs(paddle.x - self.ball.x), self.ball.y))
                    decision=output.index(max(output))
                    valid=True
                    # Stay still
                    if decision==0:
                        pass
                    # Gp up
                    elif decision==1:
                        genome.fitness+=0.2
                        valid = self.game.move_paddle(left=left, up=True)
                    # Go down
                    elif decision==2:
                        genome.fitness+=0.2
                        valid = self.game.move_paddle(left=left, up=False)
                    # If paddle tries to go out of the border then punish
                    if not valid:
                        genome.fitness -= 1
            if activation=='tanh':
                for (genome, net, paddle, left) in players:
                    # Get decision
                    output = net.activate((paddle.y, abs(paddle.x - self.ball.x), self.ball.y))[0]
                    valid = True
                    if output>=-0.9 and output<=0.9:
                        pass
                    elif output>0.9:
                        genome.fitness+=0.2
                        valid = self.game.move_paddle(left=left, up=True)
                    elif output<-0.9:
                        genome.fitness+=0.2
                        valid = self.game.move_paddle(left=left, up=False)
                    if not valid:
                        genome.fitness -= 1
    # Give 10 points reward for each hit and 1 additional point for win
    def calculate_fitness_ai(self, game_info):
        self.genome1.fitness += 10*game_info[0].left_hits+game_info[0].left_score
        self.genome2.fitness += 10*game_info[0].right_hits+game_info[0].right_score
    # Same as above but for hardcoded mode
    def calculate_fitness_hardcode(self, game_info):
        self.genome.fitness += 10*game_info[0].left_hits+game_info[0].left_score
