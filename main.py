import pygame, random, sys, neat, os, datetime, pickle
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from scripts.paddle import Paddle
from scripts.ball import Ball
from scripts.button import Button
from scripts.game import Game
from scripts.aitrain import GameAI

# Constants and the window initiliser
WIDTH, HEIGHT=1280, 720
WINDOW=pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

PADDLE_WIDTH, PADDLE_HEIGHT='20', '70'
BALL_RADIUS='7'
PADDLE_VELOCITY='15'
BALL_VELOCITY='10'

FPS=60

BLACK=(0,0,0)
GRAY=(64,64,64)
LAV_BLUE=(191,225,255)
RED=(255,0,0)

WINNING_SCORE=15

# Fonts
TITLE_FONT=pygame.font.SysFont('comicsans', 86)
OPTIONS_FONT=pygame.font.SysFont('comicsans', 26)
TEXT_FONT=pygame.font.SysFont('comicsans', 56)
BACK_FONT=pygame.font.SysFont('comicsans', 16)
SCORE_FONT=pygame.font.SysFont('comicsans', 26)
WIN_FONT=pygame.font.SysFont('comicsans', 40)

# Get working directory
cwd=os.getcwd()

# Create directories to store logs of games for analysis, if not exist
if not os.path.exists(cwd+"/data/pvp_logs"):
    os.makedirs(cwd+"/data/pvp_logs")
if not os.path.exists(cwd+"/data/ai_vs_hardcode_logs"):
    os.makedirs(cwd+"/data/ai_vs_hardcode_logs")
if not os.path.exists(cwd+"/data/ai_vs_ai_logs"):
    os.makedirs(cwd+"/data/ai_vs_ai_logs")

## AUXILIARY FUNCTIONS

# Function to get the model from the explorer window
def select_model():
    root = tk.Tk()
    root.withdraw()
    filename=filedialog.askopenfilename(initialdir=cwd+'/models', title='Select a model', filetypes=(('model files', '*.pickle'), ('all files', '*.*')))
    return filename

## Function taken from tutorial with small edits
# Function that iterates through every combination of genomes when we train ai vs ai
def eval_genomes1(genomes, config):
    global LAV_BLUE, WIDTH, HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, BALL_RADIUS, PADDLE_VELOCITY, BALL_VELOCITY
    for i, (genome_id1, genome1) in enumerate(genomes):
        genome1.fitness = 0
        for genome_id2, genome2 in genomes[min(i+1, len(genomes) - 1):]:
            genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
            pong = GameAI(LAV_BLUE, WINDOW, WIDTH, HEIGHT, int(PADDLE_WIDTH), int(PADDLE_HEIGHT), int(BALL_RADIUS), int(PADDLE_VELOCITY), int(BALL_VELOCITY))

            menu_quit = pong.train_ai_vs_ai(genome1, genome2, config, activation)
            
            if menu_quit:
                main_menu()

## Function based on previous function, edited to work on hardcoded paddle
# Function that iterates through every genomes when we train ai vs hardcoded
def eval_genomes2(genomes, config):
    global LAV_BLUE, WIDTH, HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, BALL_RADIUS, PADDLE_VELOCITY, BALL_VELOCITY
    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        pong = GameAI(LAV_BLUE, WINDOW, WIDTH, HEIGHT, int(PADDLE_WIDTH), int(PADDLE_HEIGHT), int(BALL_RADIUS), int(PADDLE_VELOCITY), int(BALL_VELOCITY))

        menu_quit = pong.train_ai_vs_hardcode(genome, config, activation)
            
        if menu_quit:
            main_menu()

## Function taken from tutorial with small edits
# Function that runs neat algorithm to create new models
def run_neat(config, n, hardcoded=False):
    # Defining algorithm
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    if hardcoded:
        winner = p.run(eval_genomes2, int(n))
    else:   
        winner = p.run(eval_genomes1, int(n))
    # Save model to a pickle file
    date=datetime.datetime.now()
    if mode=='hardcoded':
        with open("models/neat-"+n+'gen-'+activation+"-hardcoded"+f"-{date:%Y-%m-%d_%H-%M-%S}.pickle", "wb") as f:
            pickle.dump(winner, f)
    else:
        with open("models/neat-"+n+'gen-'+activation+f"-{date:%Y-%m-%d_%H-%M-%S}.pickle", "wb") as f:
            pickle.dump(winner, f)
    main_menu()

### FOR VS_AI SCREEN

# Function that gets the name of model that you wanna play with and creates a game against that model
def play_p_vs_ai(config, filename):
    # Get corresponding activation function
    for function in ['relu', 'tanh']:
        if function in filename:
            activation=function
    # Load model
    with open(filename, "rb") as f:
        winner=pickle.load(f)
    # Get the network
    winner_net=neat.nn.FeedForwardNetwork.create(winner, config)

    pong=GameAI(LAV_BLUE, WINDOW, WIDTH, HEIGHT, int(PADDLE_WIDTH), int(PADDLE_HEIGHT), int(BALL_RADIUS), int(PADDLE_VELOCITY), int(BALL_VELOCITY))
    menu_quit=pong.test_p_vs_ai(winner_net, activation)
    if menu_quit:
        main_menu()

# Function that starts a game between two AI models
def ai_vs_ai(config1, config2, filename1, filename2, modelname1, modelname2):
    # Get two activation functions
    activation=[]
    for filename in [filename1, filename2]:
        for function in ['relu', 'tanh']:
            if function in filename:
                activation.append(function)
    # Load models
    with open(filename1, "rb") as f:
        winner1=pickle.load(f)
    with open(filename2, "rb") as f:
        winner2=pickle.load(f)
    # Create neural networks
    winner_net1=neat.nn.FeedForwardNetwork.create(winner1, config1)
    winner_net2=neat.nn.FeedForwardNetwork.create(winner2, config2)

    pong=GameAI(LAV_BLUE, WINDOW, WIDTH, HEIGHT, int(PADDLE_WIDTH), int(PADDLE_HEIGHT), int(BALL_RADIUS), int(PADDLE_VELOCITY), int(BALL_VELOCITY))
    menu_quit=pong.test_ai_vs_ai([winner_net1, winner_net2], activation, modelname1, modelname2)
    if menu_quit:
        main_menu()

# Function that starts a game between model and hardcoded paddle
def ai_vs_hardcoded(config, filename, modelname):
    for function in ['relu', 'tanh']:
        if function in filename:
            activation=function
    with open(filename, "rb") as f:
        winner=pickle.load(f)
    winner_net=neat.nn.FeedForwardNetwork.create(winner, config)
    pong=GameAI(LAV_BLUE, WINDOW, WIDTH, HEIGHT, int(PADDLE_WIDTH), int(PADDLE_HEIGHT), int(BALL_RADIUS), int(PADDLE_VELOCITY), int(BALL_VELOCITY))
    menu_quit=pong.test_ai_vs_hardcode(winner_net, activation, modelname)
    if menu_quit:
        main_menu()


## GAME ITSELF
# Main menu (the idea on how to organise main menu was inspired from youtube video mentioned in acknowledgements)
def main_menu():
    # Define title
    MENU_TEXT = TITLE_FONT.render("PONG GAME", 1, BLACK)
    MENU_RECT = MENU_TEXT.get_rect(center=(WIDTH//2, 100))
    # Define buttons
    PVP_BUTTON = Button(image=None, pos=(WIDTH//4, 250), text_input="PVP", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    TRAINAI_BUTTON = Button(image=None, pos=(WIDTH//2, 250), text_input="TRAIN AI", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    VSAI_BUTTON = Button(image=None, pos=(3*WIDTH//4, 250), text_input="VS AI", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    OPTIONS_BUTTON = Button(image=None, pos=(WIDTH//2, 400), text_input="OPTIONS", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    QUIT_BUTTON = Button(image=None, pos=(WIDTH//2, 550), text_input="QUIT", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    
    while True:
        WINDOW.fill(LAV_BLUE)
        # Get mouse position
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        # Show title
        WINDOW.blit(MENU_TEXT, MENU_RECT)
        # Create and update buttons when hovered
        for button in [PVP_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON, TRAINAI_BUTTON, VSAI_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WINDOW)
        # Get events
        for event in pygame.event.get():
            # If player clicks red cross to quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # If player clicks something
            if event.type == pygame.MOUSEBUTTONDOWN:
                # START PVP GAME
                if PVP_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pvp()
                # TRAIN AI SCREEN
                if TRAINAI_BUTTON.checkForInput(MENU_MOUSE_POS):
                    screen_train_ai()
                # VS AI SCREEN
                if VSAI_BUTTON.checkForInput(MENU_MOUSE_POS):
                    # Define buttons
                    P_VS_AI_BUTTON = Button(image=None, pos=(WIDTH//2, 400), text_input="PLAYER VS AI", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
                    AI_VS_AI_BUTTON = Button(image=None, pos=(WIDTH//2, 300), text_input="AI VS AI", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
                    AI_VS_HARDCODE_BUTTON = Button(image=None, pos=(WIDTH//2, 200), text_input="AI VS HARDCODED", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
                    BACK_BUTTON = Button(image=None, pos=(WIDTH//2, 550), text_input="BACK", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
                    while True:
                        WINDOW.fill(LAV_BLUE)
                        # Get mouse position
                        VSAI_MOUSE_POS = pygame.mouse.get_pos()
                        # Make and update buttons
                        for button in [P_VS_AI_BUTTON, AI_VS_AI_BUTTON, AI_VS_HARDCODE_BUTTON, BACK_BUTTON]:
                            button.changeColor(VSAI_MOUSE_POS)
                            button.update(WINDOW)
                        # Get events
                        for event in pygame.event.get():
                            # Exit when quit red cross clicked
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            # Take to other screens when clicked
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if P_VS_AI_BUTTON.checkForInput(VSAI_MOUSE_POS):
                                    screen_p_vs_ai()
                                if AI_VS_AI_BUTTON.checkForInput(VSAI_MOUSE_POS):
                                    screen_ai_vs_ai()
                                if AI_VS_HARDCODE_BUTTON.checkForInput(VSAI_MOUSE_POS):
                                    screen_p_vs_ai(is_hardcoded=True)
                                if BACK_BUTTON.checkForInput(VSAI_MOUSE_POS):
                                    main_menu()
                        pygame.display.update()
                # Take to options screen
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                # Quit button
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

# PVP GAME
def pvp():
    run=True
    # Define game
    game=Game(LAV_BLUE, WINDOW, WIDTH, HEIGHT, int(PADDLE_WIDTH), int(PADDLE_HEIGHT), int(BALL_RADIUS), int(PADDLE_VELOCITY), int(BALL_VELOCITY))
    # Define back button
    BACK_BUTTON = Button(image=None, pos=(50, HEIGHT-20), text_input="BACK", font=BACK_FONT, base_color=BLACK, hovering_color=GRAY)
    clock=pygame.time.Clock()
    date=datetime.datetime.now()
    # Create path to save logs
    path=cwd+'/data/pvp_logs/'+f"{date:%Y-%m-%d_%H-%M-%S}.csv"
    # Create dataframe to store data
    data=pd.DataFrame(columns=['total_hits','left_score','right_score'])
    while run:
        clock.tick(FPS)
        # Start game
        game_info=game.loop()
        # Get mouse position
        GAME_MOUSE_POS = pygame.mouse.get_pos()
        # Get events
        for event in pygame.event.get():
            # When user clicks red cross
            if event.type==pygame.QUIT:
                run=False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # When user clicks on back button
                if BACK_BUTTON.checkForInput(GAME_MOUSE_POS):
                    # Save current data to csv
                    row=[game_info[1].total_hits, game_info[1].left_score, game_info[1].right_score]
                    data.loc[len(data)] = row
                    data.to_csv(path, index=False)
                    # Reset game and return to menu
                    game.reset()
                    main_menu()
        
        # Get keybord keys pressed
        keys=pygame.key.get_pressed()
        # Move the left paddle
        if keys[pygame.K_w]:
            game.move_paddle(left=True, up=True)
        elif keys[pygame.K_s]:
            game.move_paddle(left=True, up=False)
        # Move the right paddle
        if keys[pygame.K_UP]:
            game.move_paddle(left=False, up=True)
        elif keys[pygame.K_DOWN]:
            game.move_paddle(left=False, up=False)
        
        # If round has finished save data to csv
        if game.round_finish:
            row=[game_info[1].total_hits, game_info[1].left_score, game_info[1].right_score]
            data.loc[len(data)] = row
            data.to_csv(path, index=False)
        # Define win variable
        won=False
        # If someone won then set won to True and define winning text
        if game.left_score>=WINNING_SCORE:
            won=True
            win_text="Player 1 won"
        elif game.right_score>=WINNING_SCORE:
            won=True
            win_text="Player 2 won"
        # End game if won
        if won:
            # Show winning text for 1 second
            text=WIN_FONT.render(win_text, 1, BLACK)
            WINDOW.blit(text, (WIDTH//2-text.get_width()//2, HEIGHT//2-text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(1000)
            # Reset game
            game.reset()
        # Draw game
        game.draw(True, True)
        # Draw back button
        BACK_BUTTON.changeColor(GAME_MOUSE_POS)
        BACK_BUTTON.update(WINDOW)
        pygame.display.update()
    pygame.quit()

# SCREEN TO TRAIN AI, AND CONFIGURE WANTED VARIABLES
def screen_train_ai():
    # Define default values
    global activation, mode
    n='20'
    activation='relu'
    mode='itself'
    active=False
    # Get current path for config path
    local_dir = os.path.dirname(__file__)
    # Define buttons for back and play action
    TRAIN_AI_BACK_BUTTON = Button(image=None, pos=(WIDTH//4+60, HEIGHT-50), text_input="BACK", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    TRAIN_AI_PLAY_BUTTON = Button(image=None, pos=(3*WIDTH//4-60, HEIGHT-50), text_input="PLAY", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    # Create input rectangle for the number of generations
    input_rects=[pygame.Rect(WIDTH//2+60, 200, 140, 32)]
    # Define texts that will be on the screen
    parameters_text=[OPTIONS_FONT.render('Number of generations', 1, BLACK), OPTIONS_FONT.render('Activation function:', 1, BLACK), OPTIONS_FONT.render('Mode:', 1, BLACK)]
    while True:
        WINDOW.fill(LAV_BLUE)
        # Get mouse position
        TRAIN_AI_MOUSE_POS = pygame.mouse.get_pos()
        # Render the number of generations variable
        parameters=[OPTIONS_FONT.render(str(n), 1, BLACK)]
        # Draw the rectangle with variable
        pygame.draw.rect(WINDOW, BLACK, input_rects[0], 2)
        WINDOW.blit(parameters[0], (input_rects[0].centerx-parameters[0].get_width()//2, input_rects[0].y-3))
        # Show the text on the screen
        WINDOW.blit(parameters_text[0], (WIDTH//4, 200))
        WINDOW.blit(parameters_text[1], (WIDTH//4, 300))
        WINDOW.blit(parameters_text[2], (WIDTH//4, 400))
        # If activation function is relu then change the colour of the button to red
        if activation=='relu':
            RELU_BUTTON = Button(image=None, pos=(WIDTH//2, 320), text_input="relu", font=OPTIONS_FONT, base_color=RED, hovering_color=GRAY)
            TANH_BUTTON = Button(image=None, pos=(WIDTH//2+100, 320), text_input="tanh", font=OPTIONS_FONT, base_color=BLACK, hovering_color=GRAY)
        # If activation function is tanh then change the colour of the button to red
        if activation=='tanh':
            TANH_BUTTON = Button(image=None, pos=(WIDTH//2+100, 320), text_input="tanh", font=OPTIONS_FONT, base_color=RED, hovering_color=GRAY)
            RELU_BUTTON = Button(image=None, pos=(WIDTH//2, 320), text_input="relu", font=OPTIONS_FONT, base_color=BLACK, hovering_color=GRAY)
        # If mode is set to vs itself then change the colour of the button to red
        if mode=='itself':
            ITSELF_BUTTON = Button(image=None, pos=(WIDTH//2-100, 420), text_input="vs itself", font=OPTIONS_FONT, base_color=RED, hovering_color=GRAY)
            HARDCODED_BUTTON = Button(image=None, pos=(WIDTH//2+90, 420), text_input="vs hardcoded", font=OPTIONS_FONT, base_color=BLACK, hovering_color=GRAY)
        # If mode is set to vs hardcoded then change the colour of the button to red
        if mode=='hardcoded':
            HARDCODED_BUTTON = Button(image=None, pos=(WIDTH//2+90, 420), text_input="vs hardcoded", font=OPTIONS_FONT, base_color=RED, hovering_color=GRAY)
            ITSELF_BUTTON = Button(image=None, pos=(WIDTH//2-100, 420), text_input="vs itself", font=OPTIONS_FONT, base_color=BLACK, hovering_color=GRAY)
        # Show buttons
        for button in [TRAIN_AI_BACK_BUTTON, TRAIN_AI_PLAY_BUTTON, RELU_BUTTON, TANH_BUTTON, ITSELF_BUTTON, HARDCODED_BUTTON]:
            button.changeColor(TRAIN_AI_MOUSE_POS)
            button.update(WINDOW)
        # Check click events
        for event in pygame.event.get():
            # Quitting
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Pressed back button
                if TRAIN_AI_BACK_BUTTON.checkForInput(TRAIN_AI_MOUSE_POS):
                    main_menu()
                # Pressed play button
                if TRAIN_AI_PLAY_BUTTON.checkForInput(TRAIN_AI_MOUSE_POS):
                    config_path = os.path.join(local_dir, 'config_'+activation+'.txt')
                    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
                    # Train mode itself
                    if mode=='itself':
                        run_neat(config, n)
                    # Train hardcoded mode
                    else:
                        run_neat(config, n, True)
                # Clicked on input box for generation number
                if input_rects[0].collidepoint(event.pos):
                    active=True
                # Clicked on relu
                if RELU_BUTTON.checkForInput(TRAIN_AI_MOUSE_POS):
                    activation='relu'
                # Clicked on tanh
                if TANH_BUTTON.checkForInput(TRAIN_AI_MOUSE_POS):
                    activation='tanh'
                if ITSELF_BUTTON.checkForInput(TRAIN_AI_MOUSE_POS):
                    mode='itself'
                if HARDCODED_BUTTON.checkForInput(TRAIN_AI_MOUSE_POS):
                    mode='hardcoded'
            # Change number of generations
            if event.type == pygame.KEYDOWN and active:
                if event.key==pygame.K_BACKSPACE:
                    n=n[:-1]
                if event.unicode.isdigit():
                    n=n+event.unicode
        pygame.display.update()
    
# SCREEN TO LOAD MODELS FOR AI VS AI 
def screen_ai_vs_ai():
    # Strings for the name of the models
    loaded_model1='model 1: '
    loaded_model2='model 2: '
    model1_name=''
    model2_name=''
    # Define buttons on the screen
    AI_VS_AI_BACK_BUTTON = Button(image=None, pos=(WIDTH//4+60, HEIGHT-100), text_input="BACK", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    AI_VS_AI_PLAY_BUTTON = Button(image=None, pos=(3*WIDTH//4-60, HEIGHT-100), text_input="PLAY", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    LOAD_MODEL1_BUTTON = Button(image=None, pos=(WIDTH//2, 100), text_input="LOAD MODEL 1", font=TITLE_FONT, base_color=BLACK, hovering_color=GRAY)
    LOAD_MODEL2_BUTTON = Button(image=None, pos=(WIDTH//2, 300), text_input="LOAD MODEL 2", font=TITLE_FONT, base_color=BLACK, hovering_color=GRAY)
    # Get local path for config file
    local_dir = os.path.dirname(__file__)
    while True:
        WINDOW.fill(LAV_BLUE)
        AI_VS_AI_MOUSE_POS = pygame.mouse.get_pos()
        # Render texts and rectangles where they are placed
        MODEL1_TEXT = OPTIONS_FONT.render(loaded_model1, 1, BLACK)
        MODEL1_RECT = MODEL1_TEXT.get_rect(center=(WIDTH//2, 400))
        MODEL2_TEXT = OPTIONS_FONT.render(loaded_model2, 1, BLACK)
        MODEL2_RECT = MODEL2_TEXT.get_rect(center=(WIDTH//2, 500))
        # Show text and respective rectangles on the screen
        WINDOW.blit(MODEL1_TEXT, MODEL1_RECT)
        WINDOW.blit(MODEL2_TEXT, MODEL2_RECT)
        # Show and update buttons
        for button in [AI_VS_AI_BACK_BUTTON, LOAD_MODEL1_BUTTON, LOAD_MODEL2_BUTTON, AI_VS_AI_PLAY_BUTTON]:
            button.changeColor(AI_VS_AI_MOUSE_POS)
            button.update(WINDOW)
        # Get events for clicking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Back button clicked
                if AI_VS_AI_BACK_BUTTON.checkForInput(AI_VS_AI_MOUSE_POS):
                    main_menu()
                # Clicked button to load first model
                if LOAD_MODEL1_BUTTON.checkForInput(AI_VS_AI_MOUSE_POS):
                    model1_path=select_model()
                    if model1_path!='':
                        # Remove .pickle ending
                        model1_name=model1_path.rsplit('/', 1)[1][:-7]
                        loaded_model1='model 1: '+model1_name
                # Clicked button to load second model
                if LOAD_MODEL2_BUTTON.checkForInput(AI_VS_AI_MOUSE_POS):
                    model2_path=select_model()
                    if model2_path!='':
                        # Remove .pickle ending
                        model2_name=model2_path.rsplit('/', 1)[1][:-7]
                        loaded_model2='model 2: '+model2_name
                # Clicked button to play
                if AI_VS_AI_PLAY_BUTTON.checkForInput(AI_VS_AI_MOUSE_POS):
                    # Check if both models are loaded
                    if model1_name!='' and model2_name!='':  
                        if 'relu' in model1_name:
                            config_path = os.path.join(local_dir, 'config_relu.txt')
                            config1 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
                        if 'tanh' in model1_name:
                            config_path = os.path.join(local_dir, 'config_tanh.txt')
                            config1 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
                        if 'relu' in model2_name:
                            config_path = os.path.join(local_dir, 'config_relu.txt')
                            config2 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
                        if 'tanh' in model2_name:
                            config_path = os.path.join(local_dir, 'config_tanh.txt')
                            config2 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
                        ai_vs_ai(config1, config2, model1_path, model2_path, model1_name, model2_name)
                    # Otherwise do nothing
                    else:
                        pass   
        pygame.display.update()

# SCREEN FOR PLAYER VS AI (AND AI VS HARDCODED WHEN is_hardcoded=True)
def screen_p_vs_ai(is_hardcoded=False):
    # Variable for loaded model
    loaded_model='model: '
    model_name=''
    # Define buttons
    P_VS_AI_BACK_BUTTON = Button(image=None, pos=(WIDTH//4+60, HEIGHT-100), text_input="BACK", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    P_VS_AI_PLAY_BUTTON = Button(image=None, pos=(3*WIDTH//4-60, HEIGHT-100), text_input="PLAY", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    LOAD_MODEL_BUTTON = Button(image=None, pos=(WIDTH//2, 200), text_input="LOAD MODEL", font=TITLE_FONT, base_color=BLACK, hovering_color=GRAY)
    # Get local directory for config path
    local_dir = os.path.dirname(__file__)
    while True:
        WINDOW.fill(LAV_BLUE)
        # Get mouse position
        P_VS_AI_MOUSE_POS = pygame.mouse.get_pos()
        # Render and show model name
        MODEL_TEXT = OPTIONS_FONT.render(loaded_model, 1, BLACK)
        MODEL_RECT = MODEL_TEXT.get_rect(center=(WIDTH//2, 400))
        WINDOW.blit(MODEL_TEXT, MODEL_RECT)
        # Update buttons when hovered
        for button in [P_VS_AI_BACK_BUTTON, LOAD_MODEL_BUTTON, P_VS_AI_PLAY_BUTTON]:
            button.changeColor(P_VS_AI_MOUSE_POS)
            button.update(WINDOW)
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # When clicked something
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Back button clicked
                if P_VS_AI_BACK_BUTTON.checkForInput(P_VS_AI_MOUSE_POS):
                    main_menu()
                # Load model button clicked
                if LOAD_MODEL_BUTTON.checkForInput(P_VS_AI_MOUSE_POS):
                    model_path=select_model()
                    if model_path!='':
                        # Remove .pickle ending
                        model_name=model_path.rsplit('/', 1)[1][:-7]
                        loaded_model='model: '+model_name
                # Play button clicked
                if P_VS_AI_PLAY_BUTTON.checkForInput(P_VS_AI_MOUSE_POS):
                    # Check if any model is loaded
                    if model_name!='':
                        if 'relu' in model_name:
                            config_path = os.path.join(local_dir, 'config_relu.txt')
                            config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
                            # Check if ai vs hardcoded chosen
                            if is_hardcoded:
                                ai_vs_hardcoded(config, model_path, model_name)
                            else:
                                play_p_vs_ai(config, model_path)
                        if 'tanh' in model_name:
                            config_path = os.path.join(local_dir, 'config_tanh.txt')
                            config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
                            if is_hardcoded:
                                ai_vs_hardcoded(config, model_path, model_name)
                            else:
                                play_p_vs_ai(config, model_path)
                    else:
                        pass
        pygame.display.update()

# OPTIONS SCREEN
def options():
    global PADDLE_WIDTH, PADDLE_HEIGHT, BALL_RADIUS, PADDLE_VELOCITY, BALL_VELOCITY
    # Get all the input rectangles for variables
    input_rects=[pygame.Rect(WIDTH//2+60, 100, 140, 32), pygame.Rect(WIDTH//2+60, 200, 140, 32), pygame.Rect(WIDTH//2+60, 300, 140, 32), pygame.Rect(WIDTH//2+60, 400, 140, 32), pygame.Rect(WIDTH//2+60, 500, 140, 32)]
    # Get text that explains variable
    parameters_text=[OPTIONS_FONT.render('PADDLE WIDTH', 1, BLACK), OPTIONS_FONT.render('PADDLE HEIGHT', 1, BLACK), OPTIONS_FONT.render('BALL RADIUS', 1, BLACK), OPTIONS_FONT.render('PADDLE VELOCITY', 1, BLACK),OPTIONS_FONT.render('BALL VELOCITY', 1, BLACK)]
    # Get recommended value text
    recommended_text=[OPTIONS_FONT.render('Recommend 10-20', 1, BLACK), OPTIONS_FONT.render('Recommend 50-90', 1, BLACK), OPTIONS_FONT.render('Recommend 5-8', 1, BLACK), OPTIONS_FONT.render('Recommend 10-20', 1, BLACK),OPTIONS_FONT.render('Recommend: 7-12', 1, BLACK)]
    # List that will determine if textbox is active
    active=[False, False, False, False, False]
    # Define buttons
    OPTIONS_BACK_BUTTON = Button(image=None, pos=(WIDTH//4+60, HEIGHT-50), text_input="BACK", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    OPTIONS_DEFAULT_BUTTON = Button(image=None, pos=(3*WIDTH//4-60, HEIGHT-50), text_input="DEFAULT", font=TEXT_FONT, base_color=BLACK, hovering_color=GRAY)
    while True:
        WINDOW.fill(LAV_BLUE)
        # Get mouse position
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        # Show and update buttons
        for button in [OPTIONS_BACK_BUTTON, OPTIONS_DEFAULT_BUTTON]:
            button.changeColor(OPTIONS_MOUSE_POS)
            button.update(WINDOW)
        # Render variables
        parameters=[OPTIONS_FONT.render(str(PADDLE_WIDTH), 1, BLACK), OPTIONS_FONT.render(str(PADDLE_HEIGHT), 1, BLACK), OPTIONS_FONT.render(str(BALL_RADIUS), 1, BLACK), OPTIONS_FONT.render(str(PADDLE_VELOCITY), 1, BLACK),OPTIONS_FONT.render(str(BALL_VELOCITY), 1, BLACK)]
        # Show variables, names of the variables and recommended values
        for i in range(len(input_rects)):
            pygame.draw.rect(WINDOW, BLACK, input_rects[i], 2)
            WINDOW.blit(parameters[i], (input_rects[i].centerx-parameters[i].get_width()//2, input_rects[i].y-3))
            WINDOW.blit(parameters_text[i], (WIDTH//4, 100*i+100))
            WINDOW.blit(recommended_text[i], (input_rects[i].x+input_rects[i].width+10, 100*i+100-3))
        # Get events
        for event in pygame.event.get():
            # Quitting
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Mouse clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Back button clicked
                if OPTIONS_BACK_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
                # Default options button clicked
                if OPTIONS_DEFAULT_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    PADDLE_WIDTH='20'
                    PADDLE_HEIGHT='70'
                    BALL_RADIUS='7'
                    PADDLE_VELOCITY='15'
                    BALL_VELOCITY='10'
            if event.type==pygame.MOUSEBUTTONDOWN:
                # If clicked anywhere then every textbox is off
                active=[False, False, False, False, False]
                # Except when it collides with any of the textboxes
                if input_rects[0].collidepoint(event.pos):
                    active[0]=True
                if input_rects[1].collidepoint(event.pos):
                    active[1]=True
                if input_rects[2].collidepoint(event.pos):
                    active[2]=True
                if input_rects[3].collidepoint(event.pos):
                    active[3]=True
                if input_rects[4].collidepoint(event.pos):
                    active[4]=True
            # Paddle width option case
            if event.type == pygame.KEYDOWN and active[0]:
                if event.key==pygame.K_BACKSPACE:
                    PADDLE_WIDTH=PADDLE_WIDTH[:-1]
                if event.unicode.isdigit():
                    PADDLE_WIDTH=PADDLE_WIDTH+event.unicode
            # Paddle height option case
            if event.type == pygame.KEYDOWN and active[1]:
                if event.key==pygame.K_BACKSPACE:
                    PADDLE_HEIGHT=PADDLE_HEIGHT[:-1]
                if event.unicode.isdigit():
                    PADDLE_HEIGHT=PADDLE_HEIGHT+event.unicode
            # Ball radius option case
            if event.type == pygame.KEYDOWN and active[2]:
                if event.key==pygame.K_BACKSPACE:
                    BALL_RADIUS=BALL_RADIUS[:-1]
                if event.unicode.isdigit():
                    BALL_RADIUS=BALL_RADIUS+event.unicode
            # Paddle velocity option case
            if event.type == pygame.KEYDOWN and active[3]:
                if event.key==pygame.K_BACKSPACE:
                    PADDLE_VELOCITY=PADDLE_VELOCITY[:-1]
                if event.unicode.isdigit():
                    PADDLE_VELOCITY=PADDLE_VELOCITY+event.unicode
            # Ball velocity option case
            if event.type == pygame.KEYDOWN and active[4]:
                if event.key==pygame.K_BACKSPACE:
                    BALL_VELOCITY=BALL_VELOCITY[:-1]
                if event.unicode.isdigit():
                    BALL_VELOCITY=BALL_VELOCITY+event.unicode
        pygame.display.update()

if __name__=='__main__':
    main_menu()
    