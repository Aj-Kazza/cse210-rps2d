from ssl import CERT_NONE
import pygame
import os
import random
import sys



pygame.init()
from pygame.locals import *
from pygame import mixer
mixer.init()

WIDTH, HEIGHT = 500, 640
BOTTOM = 300
CENTER_X, CENTER_Y = ((WIDTH / 3) - 50), ((HEIGHT / 4) - 40)

WINDOWS = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPS 2D Demo")
DEFAULT_DECK = ["rock", "paper", "scissors", "lizard", "spock"]


#Useful pictures
BG = pygame.image.load(os.path.join("rps2d/assets/bg/grass.png")).convert_alpha()
panel = pygame.image.load(os.path.join('rps2d/assets/bg/half-thing.png')).convert_alpha()
scroll = pygame.image.load(os.path.join('rps2d/assets/ui/scroll.png')).convert_alpha()
arrow = pygame.image.load(os.path.join('rps2d/assets/ui/arrow.png')).convert_alpha()
click = pygame.image.load(os.path.join('rps2d/assets/ui/click.png')).convert_alpha()
win = pygame.image.load(os.path.join('rps2d/assets/ui/win.png')).convert_alpha()
lose = pygame.image.load(os.path.join('rps2d/assets/ui/lose.png')).convert_alpha()
menubg = pygame.image.load(os.path.join("rps2d/assets/bg/mainmenu.png")).convert_alpha()
title = pygame.image.load(os.path.join("rps2d/assets/ui/title.png")).convert_alpha()
instructions = pygame.image.load(os.path.join("rps2d/assets/bg/howto.png")).convert_alpha()
loadingscreen = pygame.image.load(os.path.join("rps2d/assets/bg/loadingscreen.png")).convert_alpha()

#music & sfx
sfx_hit = pygame.mixer.Sound('rps2d/assets/sfx/hit.ogg')
sfx_playerhit = pygame.mixer.Sound('rps2d/assets/sfx/playerhit.ogg')
sfx_draw = pygame.mixer.Sound('rps2d/assets/sfx/error.ogg')


#level soundtrack
grassland = 'rps2d/assets/sfx/grassland.ogg'
mainmenu = 'rps2d/assets/sfx/main.ogg'




action_cooldown = 0
action_wait = 90


attack = False
clicked = False


font = pygame.font.SysFont('Agency FB', 30)

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
gray = (106, 129, 119)
blueish = (0, 184, 255)

def drawBG(bg):
    WINDOWS.blit(bg, (0,0))

def drawScroll(x,y):
    WINDOWS.blit(scroll, (x,y))

def drawPanel():
    WINDOWS.blit(panel, (0, 500))

def load_image(dirr=None, name="None"):
    if dirr == None:
        image = pygame.image.load(name)
        return image
    else:
        image = pygame.image.load(dirr + "/" + name)
        return image


class ATK_Display():
    def __init__(self, x=0, y=0):
        block = load_image("rps2d/assets/ui", "block.png")
        block_win = load_image("rps2d/assets/ui", "block_1.png")
        block_draw = load_image("rps2d/assets/ui", "block_2.png")
        self.image_2 = pygame.transform.scale(block_win, (120, 120))
        self.image_3 = pygame.transform.scale(block_draw, (120, 120))
        self.image = pygame.transform.scale(block, (120, 120))
        self.dispimage = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        

    def draw(self, window):
        window.blit(self.dispimage, self.rect.center)

    def reset(self):
        self.dispimage = self.image

    def win(self):
        self.dispimage = self.image_2

    def tie(self):
        self.dispimage = self.image_3


class ATK_pop():
    def __init__(self, attack, x=0, y=0):
        img = load_image("rps2d/assets/ui", f"{attack}.png")
        self.image = pygame.transform.scale(img, (120, 120))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def draw(self, window):
        window.blit(self.image, self.rect.center)


class Label:
    def __init__(self, x, y, color, font, text=''):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color


    def draw(self, window):
        img = font.render(self.text, True, self.color)
        window.blit(img, (self.x, self.y))

    def __repr__(self):
        return self._text

class Text(Label):
    def __init__(self, x, y, color, font):
        super().__init__(x, y, color, font)
    def draw(self, window, turn):
        img = font.render(f"{turn._name.upper()} CHOSE {turn._attack}", True, self.color)
        window.blit(img, (self.x, self.y))
        
        
class Health:
    def __init__(self, person, x=0, y=0):
        self._x = x
        self._y = y
        self.hearts = person.hp
        img = pygame.image.load(os.path.join("rps2d/assets/ui/hp.png"))
        self._image = pygame.transform.scale(img, (30, 30))

    def draw(self, window):
        x = self._x
        y = self._y
        for i in range(self.hearts):
            window.blit(self._image, (self._x + (i * 30), self._y))

    def get_hearts(self, person):
        self.hearts = person.hp


class Attacks:
    def __init__(self, name, x=0, y=0):
        self.name = name
        self._x = x
        self._y = y
        self._image = load_image("rps2d/assets/ui", f"{self.name}.png")
        self.rect = self._image.get_rect()
        self.rect.center = (x + 50,y + 50)


    def draw(self, window):
        window.blit(self._image, (self._x, self._y))

class Character:
    def __init__(self):
        self._name = "Player"
        self._deck = ["rock", "paper", "scissors", "lizard", "spock"]
        self._maxhp = 3
        self.hp = self._maxhp
        self._sprite = ""
        self.attack = ""
        self.alive = True

    def setattack(self, attack):
        self.attack = attack
    
    def get_attack(self):
        return self.attack

    def reset(self):
        self.hp = self._maxhp
        self.alive = True

    def getname(self):
        return self._name

class LoadingMan:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
        self.animation = []
        self.index = 0
        self.update_time = pygame.time.get_ticks()
        for i in range(4):
            img = pygame.image.load(f'rps2d/assets/ui/loading/{i}.png')
            self.animation.append(img)
        self.image = self.animation[self.index]


    def update(self):
        cooldown = 100

        self.image = self.animation[self.index]
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.index += 1
        if self.index >= len(self.animation):
            self.index = 0

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

class Enemy(Character):
    def __init__(self, x, y, name, deck, hp):
        super().__init__()
        self._x = x
        self._y = y        
        self._name = name
        self._maxhp = hp
        self.hp = hp
        self._deck = deck
        self.animations = []
        self.index = 0
        self.action = 0 #0:idle 1:attack 2:hurt 3:dead
        self.update_time = pygame.time.get_ticks()
        self.attacking = True
        self._attacks = ""

        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'rps2d/assets/enemies/{name}/idle/{i}.png')
            temp_list.append(img)
        self.animations.append(temp_list)
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'rps2d/assets/enemies/{name}/attack/{i}.png')
            temp_list.append(img)
        self.animations.append(temp_list)
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'rps2d/assets/enemies/{name}/hit/{i}.png')
            temp_list.append(img)
        self.animations.append(temp_list)
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'rps2d/assets/enemies/{name}/ded/{i}.png')
            temp_list.append(img)
        self.animations.append(temp_list)

        self.image = self.animations[self.action][self.index]

    def setattack(self):
        self._attacks = random.choice(self._deck)

    def update(self):
        cooldown = 100
        self.image = self.animations[self.action][self.index]
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.index += 1
        if self.index >= len(self.animations[self.action]):
            if self.action == 3:
                self.index = len(self.animations[self.action]) - 1
                self.alive = False
            else:
                self.idle()
    
    def draw(self):
        WINDOWS.blit(self.image, (self._x, self._y))

    def idle(self):
        self.action = 0
        self.index = 0
        self.update_time = pygame.time.get_ticks()

    def pew(self):
        self.action = 1
        self.index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.index = 0
        self.update_time = pygame.time.get_ticks()

    def ded(self):
        self.action = 3
        self.index = 0
        self.update_time = pygame.time.get_ticks()

    def get_attack(self):
        return self._attacks

class RPS: 
    def __init__(self, player, enemy):
        self.rand = f"{enemy}"
        self.answer = f"{player}"
        self.run = 0
        self.message = ""
        self.victor = 0

        
        
    def check(self):
        if self.answer == self.rand:
            self.message = "Its a Tie! Go again."
            self.victor = 2
            
        elif self.answer == "rock":
            if self.rand == "scissors":
                self.message = "Rock crushes Scissors"
                self.victor = 0
            elif self.rand == "paper": 
                self.message = "Paper covers Rock"
                self.victor = 1
            elif self.rand == "lizard":
                self.message = "Rock crushes Lizard"
                self.victor = 0
            elif self.rand == "spock":
                self.message = "Spock melts rock"
                self.victor = 1    
                       
        elif self.answer == "paper":
            if self.rand == "rock":
                self.message = "Paper covers Rock"
                self.victor = 0
            elif self.rand == "scissors":
                self.message = "Scissors cuts Paper"
                self.victor = 1
            elif self.rand == "lizard":
                self.message = "Lizard eats paper"
                self.victor = 1
            elif self.rand == "spock":
                self.message = "The truth disproves Spock"
                self.victor = 0
                
        elif self.answer == "scissors":
            if self.rand == "paper":
                self.message = "Scissors cuts Paper"
                self.victor = 0
            elif self.rand == "rock":
                self.message = "Rock crushes Scissors"
                self.victor = 1
            elif self.rand == "lizard":
                self.message = "Scissors stab lizard"
                self.victor = 0
            elif self.rand == "spock":
                self.message = "do you think scissors can hurt spock?"
                self.victor = 1           
        
        elif self.answer == "lizard":
            if self.rand == "paper":
                self.message = "Lizard eats Paper"
                self.victor = 0
            elif self.rand == "rock":
                self.message = "Rock Smashes Lizard"
                self.victor = 1
            elif self.rand == "Scissors":
                self.message = "Scissors Stab Lizard"
                self.victor = 1
            elif self.rand == "spock":
                self.message = "Lizard Poisons Spock"
                self.victor = 0
        
        elif self.answer == "spock":
            if self.rand == "paper":
                self.message = "The truth disproves Spock"
                self.victor = 1
            elif self.rand == "rock":
                self.message = "Spock Destroys Rock"
                self.victor = 0
            elif self.rand == "scissors":
                self.message = "do you think scissors can hurt spock?"
                self.victor = 0
            elif self.rand == "lizard":
                self.message = "Lizard Poisons Spock"
                self.victor = 1
        

def game():

    #animation controller variables
    action_cooldown = 0
    display_atk = 100
    calc_atk = 50
    calc = 0
    FPS = 60

    #loop controller variables
    game_over = 0
    gameOn = True

    enemylist = ["default", "birb", "coco"]
    opponent = random.choice(enemylist)

    enemy = Enemy(CENTER_X, CENTER_Y + 60, opponent, DEFAULT_DECK, 3)
    player = Character()
    clock = pygame.time.Clock()
    rock = Attacks("rock", -15, HEIGHT - 125)
    paper = Attacks("paper", 88, HEIGHT - 125)
    scissors = Attacks("scissors", 188, HEIGHT - 125)
    lizard = Attacks("lizard", 288, HEIGHT - 125)
    spock = Attacks("spock", 388, HEIGHT - 125)
    rps = [rock, paper, scissors, lizard, spock]
    enemystat = Label(50, 30, gray, font, f"{enemy._name.upper()}")
    playerstat = Label(CENTER_X + 140, 420, gray, font, f"PLAYER")
    enemyhp = Health(enemy, CENTER_X + 35, 60)
    playerhp = Health(player, WIDTH - 125, 450)
    eblock = ATK_Display(WIDTH - 130, 10)
    pblock = ATK_Display(10, 380)
    
        
        
    while gameOn:
        clock.tick(FPS)

        

        

        drawBG(BG)

        drawPanel()


        drawScroll(CENTER_X - 110, 10)
        
        
        drawScroll(CENTER_X + 90, 400)
        
        for i in rps:
            i.draw(WINDOWS)
        enemy.update()
        enemy.draw()


        pygame.mouse.set_visible(True)

        if game_over == 0:


            enemystat.draw(WINDOWS)
            enemyhp.draw(WINDOWS)
            
            eblock.draw(WINDOWS)
            pblock.draw(WINDOWS)

            playerstat.draw(WINDOWS)
            playerhp.draw(WINDOWS)



            attack = False
            pygame.mouse.set_visible(True)
            pos = pygame.mouse.get_pos()
            if rock.rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                WINDOWS.blit(arrow, (pos))
                if clicked == True:
                    player.setattack("rock")
                    attack = True
                    WINDOWS.blit(click, (pos))
            elif paper.rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                WINDOWS.blit(arrow, (pos))
                if clicked == True:
                    player.setattack("paper")
                    attack = True
                    WINDOWS.blit(click, (pos))
            elif scissors.rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                WINDOWS.blit(arrow, (pos))
                if clicked == True:
                    player.setattack("scissors")
                    attack = True
                    WINDOWS.blit(click, (pos))
            elif lizard.rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                WINDOWS.blit(arrow, (pos))
                if clicked == True:
                    player.setattack("lizard")
                    attack = True
                    WINDOWS.blit(click, (pos))
            elif spock.rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                WINDOWS.blit(arrow, (pos))
                if clicked == True:
                    player.setattack("spock")
                    attack = True
                    WINDOWS.blit(click, (pos))
                    sfx_blip.play()

            if attack == True:
                calc = calc + 1
                enemy.setattack()

            
            if calc != 0:
                patk = player.get_attack()
                pchoice = ATK_pop(patk, 10, 380)
                pchoice.draw(WINDOWS)
                
                eatk = enemy.get_attack()
                echoice = ATK_pop(eatk, WIDTH - 130, 10)
                echoice.draw(WINDOWS)
                
                thing = RPS(player.get_attack(), enemy.get_attack())
                thing.check()
                if thing.victor == 0:
                    action_cooldown = action_cooldown + 1
                    if action_cooldown >= calc_atk:
                        pblock.win()
                        action_cooldown = action_cooldown + 1
                        if action_cooldown >= display_atk:
                            sfx_hit.play()
                            enemy.hp -= 1
                            if enemy.hp > 0:
                                enemy.hurt()
                            else:
                                enemy.ded()
                                enemy.alive = False
                                game_over = 1
                            enemyhp.get_hearts(enemy)
                            action_cooldown = 0
                            calc = 0
                            pblock.reset()

                elif thing.victor == 1:
                    action_cooldown = action_cooldown + 1
                    if action_cooldown >= calc_atk:
                        eblock.win()
                        action_cooldown = action_cooldown + 1
                        if action_cooldown >= display_atk:
                            enemy.pew()
                            player.hp -= 1
                            if player.hp > 0:
                                game_over = 0
                            else:
                                game_over = -1
                            sfx_playerhit.play()
                            playerhp.get_hearts(player)
                            action_cooldown = 0
                            calc = 0
                            eblock.reset()

                elif thing.victor == 2:
                    action_cooldown = action_cooldown + 1
                    if action_cooldown >= calc_atk:
                        eblock.tie()
                        pblock.tie()
                        action_cooldown = action_cooldown + 1
                        if action_cooldown >= display_atk:
                            sfx_draw.play()
                            action_cooldown = 0
                            calc = 0
                            eblock.reset()
                            pblock.reset()
        if game_over != 0:
            if game_over == 1:
                WINDOWS.blit(win, (CENTER_X - 120, CENTER_Y - 100))
                retry = Attacks("retry1", 320, 360)
                leave = Attacks("leave1", 120, 360)
                retry.draw(WINDOWS)
                leave.draw(WINDOWS)
                pos = pygame.mouse.get_pos()
                if leave.rect.collidepoint(pos):
                    pygame.mouse.set_visible(False)
                    leave = Attacks("leave1_hover", 120, 360)
                    leave.draw(WINDOWS)
                    WINDOWS.blit(arrow, (pos))
                    if clicked == True:
                        WINDOWS.blit(click, (pos))
                        gameOn = False

                elif retry.rect.collidepoint(pos):
                    pygame.mouse.set_visible(False)
                    retry = Attacks("retry1_hover", 320, 360)
                    retry.draw(WINDOWS)
                    WINDOWS.blit(arrow, (pos))
                    if clicked == True:
                        attack = True
                        WINDOWS.blit(click, (pos))
                        game_over = 0
                        player.reset()
                        enemy.reset()
                        enemy.idle()
                        gameOn = False
                        adventuring()
            if game_over == -1:
                WINDOWS.blit(lose, (CENTER_X - 120, CENTER_Y - 100))
                retry = Attacks("retry1", 320, 360)
                leave = Attacks("leave1", 120, 360)
                retry.draw(WINDOWS)
                leave.draw(WINDOWS)
                pos = pygame.mouse.get_pos()
                if leave.rect.collidepoint(pos):
                    pygame.mouse.set_visible(False)
                    leave = Attacks("leave1_hover", 120, 360)
                    leave.draw(WINDOWS)
                    WINDOWS.blit(arrow, (pos))
                    if clicked == True:
                        WINDOWS.blit(click, (pos))
                        gameOn = False

                elif retry.rect.collidepoint(pos):
                    pygame.mouse.set_visible(False)
                    retry = Attacks("retry1_hover", 320, 360)
                    retry.draw(WINDOWS)
                    WINDOWS.blit(arrow, (pos))
                    if clicked == True:
                        attack = True
                        WINDOWS.blit(click, (pos))
                        game_over = 0
                        player.reset()
                        enemy.reset()
                        enemy.idle()
                        gameOn = False
                        adventuring()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                gameOn = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
            else:
                clicked = False

        pygame.display.update()

def howtoplay():
    pygame.display.set_caption("RPS2D Demo Intructions")
    learning = True

    while learning == True:
        drawBG(menubg)

        WINDOWS.blit(instructions, (0,0))
        back_button = Attacks("back", 220, HEIGHT - 80)
        back_button.draw(WINDOWS)

        
        pygame.mouse.set_visible(True)
        pos = pygame.mouse.get_pos()
        if back_button.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            back_button = Attacks("back_hover", 220, HEIGHT - 80)
            back_button.draw(WINDOWS)
            WINDOWS.blit(arrow, (pos))
            if clicked == True:
                back_button = Attacks("back_clicked", 220, HEIGHT - 80)
                back_button.draw(WINDOWS)
                WINDOWS.blit(click, (pos))
                learning = False




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                gameOn = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
            else:
                clicked = False

        pygame.display.update()

def adventuring():
    searching = True
    walking = 100
    looking = 50
    action_cooldown = 0

    FPS = 60

    clock = pygame.time.Clock()

    running = LoadingMan(CENTER_X, CENTER_Y)

    

    while searching == True:
        clock.tick(FPS)
        drawBG(loadingscreen)

        running.update()
        running.draw(WINDOWS)


        action_cooldown = action_cooldown + 1
        if action_cooldown >= looking:
            running.update()
            running.draw
            action_cooldown = action_cooldown + 1
            if action_cooldown >= walking:
                searching = False
                game()




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        pygame.display.update()

def  main():
    pygame.display.set_caption("RPS2D Demo")




    while True:
        drawBG(menubg)
        WINDOWS.blit(title, (CENTER_X, 30))
        play = Attacks("play", 190, CENTER_Y + 120)
        play.draw(WINDOWS)
        how = Attacks("how", 190, CENTER_Y + 220)
        how.draw(WINDOWS)
        leave_game = Attacks("exit", 190, CENTER_Y + 320)
        leave_game.draw(WINDOWS)

        pygame.mouse.set_visible(True)
        pos = pygame.mouse.get_pos()
        if play.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            play = Attacks("play_hover", 190, CENTER_Y + 120)
            play.draw(WINDOWS)
            WINDOWS.blit(arrow, (pos))
            if clicked == True:
                play = Attacks("play_clicked", 190, CENTER_Y + 120)
                play.draw(WINDOWS)
                WINDOWS.blit(click, (pos))
                adventuring()
        elif how.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            how = Attacks("how_hover", 190, CENTER_Y + 220)
            how.draw(WINDOWS)
            WINDOWS.blit(arrow, (pos))
            if clicked == True:
                how = Attacks("how_clicked", 190, CENTER_Y + 220)
                how.draw(WINDOWS)
                WINDOWS.blit(click, (pos))
                howtoplay()
        elif leave_game.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            leave_game = Attacks("exit_hover", 190, CENTER_Y + 320)
            leave_game.draw(WINDOWS)
            WINDOWS.blit(arrow, (pos))           
            if clicked == True:
                leave_game = Attacks("exit_clicked", 190, CENTER_Y + 320)
                leave_game.draw(WINDOWS)
                WINDOWS.blit(click, (pos))
                return False




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                gameOn = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
            else:
                clicked = False

        pygame.display.update()




main()