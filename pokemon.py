import pygame
from pygame.locals import *
import time
import math
import random
import requests
import io
from urllib.request import urlopen

pygame.init()

# Configurações da Tela
game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption("Pokemon Battle")

# Cores
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

base_url = 'https://pokeapi.co/api/v2'

class Move():
    def __init__(self, url):
        req = requests.get(url)
        self.data = req.json()

        self.name = self.data['name']
        self.power = self.data['power']
        self.type = self.data['type']['name']

class Pokemon(pygame.sprite.Sprite):

    def __init__(self, name, level, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Baixa informações do Pokémon
        req = requests.get(f'{base_url}/pokemon/{name.lower()}')
        self.data = req.json()

        self.name = name
        self.level = level

        self.x = x
        self.y = y

        self.num_potions = 3 

        stats = self.data['stats']
        for stat in stats:
            if stat['stat']['name'] == 'hp':
                self.current_hp = stat['base_stat'] + self.level 
                self.max_hp = stat['base_stat'] + self.level
            elif stat['stat']['name'] == 'attack':
                self.attack = stat['base_stat'] 
            elif stat['stat']['name'] == 'defense':
                self.defense = stat['base_stat'] 
            elif stat['stat']['name'] == 'speed':
                self.speed = stat['base_stat']
        
        self.type = [] 
        for i in range(len(self.data['types'])):
            type_info = self.data['types'][i]
            self.type.append(type_info['type']['name'])

        self.width = 150

        self.set_sprite('front_default')

    def perform_attack(self, other, move):
        
        display_menssage(f"{self.name} used {move.name}!")
        time.sleep(2)

        # Cálculo do dano
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power 

        if move.type in self.type:
            damage *= 1.75

        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5

        damage = math.floor(damage)

        other.take_damage(damage)
    
    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def use_potion(self):
        if self.num_potions > 0:
            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp

            self.num_potions -= 1

    def set_sprite(self, side):
        image = self.data['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()

        scale = self.width / self.image.get_width()
        new_width = int(self.image.get_width() * scale)
        new_height = int(self.image.get_height() * scale)
        
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def set_moves(self):
        self.moves = []

        for i in range(len(self.data['moves'])):
            
            move_data = self.data['moves'][i]
            versions = move_data['version_group_details']
            
            for j in range(len(versions)):
                version = versions[j]

                if version['version_group']['name'] != 'red-blue':
                    continue

                learn_method = version['move_learn_method']['name']
                if learn_method != 'level-up':
                    continue

                level_learned = version['level_learned_at']
                
                if self.level >= level_learned:
                    move_url = move_data['move']['url']
                    move = Move(move_url)

                    if move.power is not None:
                        self.moves.append(move)

        if len(self.moves) > 4:
            self.moves = random.sample(self.moves, 4)

    def draw(self, alpha=255):
        sprite = self.image.copy()
        transparent = (255, 255, 255, alpha)
        sprite.fill(transparent, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))

    def draw_hp(self):
        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, red, bar)

        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, green, bar) 

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y - 30
        game.blit(text, text_rect)

    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

def display_menssage(message):
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    
    pygame.display.update()

def create_button(width, height, left, top, text_cx, text_cy, label):
    mouse_cursor = pygame.mouse.get_pos()
    button = Rect(left, top, width, height)

    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)

    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)

    return button    

# --- INÍCIO DO JOGO ---

level = 30

# Linha 1 (Topo)
bulbasaur = Pokemon('Bulbasaur', level, 25, 50)
charmander = Pokemon('Charmander', level, 175, 50)
squirtle = Pokemon('Squirtle', level, 325, 50)

# Linha 2 (Meio)
pikachu = Pokemon('Pikachu', level, 25, 200)
jigglypuff = Pokemon('Jigglypuff', level, 175, 200)
gengar = Pokemon('Gengar', level, 325, 200)

# Linha 3 (Baixo)
eevee = Pokemon('Eevee', level, 25, 350)
machop = Pokemon('Machop', level, 175, 350)
psyduck = Pokemon('Psyduck', level, 325, 350)

pokemons = [bulbasaur, charmander, squirtle, pikachu, jigglypuff, gengar, eevee, machop, psyduck]

player_pokemon = None
rival_pokemon = None

# Game loop
game_status = 'select pokemon'

while game_status != 'quit':
    
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit' 

        if event.type == KEYDOWN:
            if event.key == K_y: 
                # Reinicia com todos os 9 Pokémons
                bulbasaur = Pokemon('Bulbasaur', level, 25, 50)
                charmander = Pokemon('Charmander', level, 175, 50)
                squirtle = Pokemon('Squirtle', level, 325, 50)
                pikachu = Pokemon('Pikachu', level, 25, 200)
                jigglypuff = Pokemon('Jigglypuff', level, 175, 200)
                gengar = Pokemon('Gengar', level, 325, 200)
                eevee = Pokemon('Eevee', level, 25, 350)
                machop = Pokemon('Machop', level, 175, 350)
                psyduck = Pokemon('Psyduck', level, 325, 350)

                pokemons = [bulbasaur, charmander, squirtle, pikachu, jigglypuff, gengar, eevee, machop, psyduck]
                game_status = 'select pokemon'

            elif event.key == K_n:
                game_status = 'quit'

        if event.type == MOUSEBUTTONDOWN:
            mouse_click = event.pos

            if game_status == 'select pokemon':
                for i in range(len(pokemons)):
                    if pokemons[i].get_rect().collidepoint(mouse_click):
                        
                        player_pokemon = pokemons[i]
                        rival_pokemon = pokemons[(i + 1) % len(pokemons)]

                        rival_pokemon.level = int(rival_pokemon.level * .75)

                        player_pokemon.hp_x = 275
                        player_pokemon.hp_y = 250
                        rival_pokemon.hp_x = 50
                        rival_pokemon.hp_y = 50

                        game_status = 'prebattle'
            
            elif game_status == 'player turn':
                
                fight_rect = Rect(10, 350, 240, 140)
                potion_rect = Rect(250, 350, 240, 140)

                if fight_rect.collidepoint(mouse_click):
                    game_status = 'player move'

                if potion_rect.collidepoint(mouse_click):
                    if player_pokemon.num_potions == 0:
                        display_menssage("No more potions left!")
                        time.sleep(2)
                        game_status = 'player move'
                    else:
                        player_pokemon.use_potion()
                        display_menssage(f"{player_pokemon.name} used a potion!")
                        time.sleep(2)
                        game_status = 'rival turn'

            elif game_status == 'player move':
                for i in range(len(player_pokemon.moves)):
                    button_width = 240
                    button_height = 70
                    left = 10 + i % 2 * button_width
                    top = 350 + i // 2 * button_height
                    
                    button_rect = Rect(left, top, button_width, button_height)

                    if button_rect.collidepoint(mouse_click):
                        move = player_pokemon.moves[i]
                        
                        player_pokemon.perform_attack(rival_pokemon, move)

                        if rival_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'
                    
    # Desenho da tela (Renderização)
    if game_status == 'select pokemon':
        game.fill(white)

        for pokemon in pokemons:
            pokemon.draw()

        mouse_cursor = pygame.mouse.get_pos()
        for pokemon in pokemons:
            if pokemon.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, black, pokemon.get_rect(), 2)

        pygame.display.update()    

    if game_status == 'prebattle':
        game.fill(white)

        player_pokemon.draw()
        pygame.display.update()

        player_pokemon.set_moves()
        rival_pokemon.set_moves()

        player_pokemon.x = 10 
        player_pokemon.y = 100
        
        rival_pokemon.x = 280 
        rival_pokemon.y = 10 

        player_pokemon.width = 300
        rival_pokemon.width = 300
        
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')

        game_status = 'start battle'

    if game_status == 'start battle':
        
        alpha = 0
        while alpha < 255:
            game.fill(white)

            rival_pokemon.draw(alpha)
            display_menssage(f"Rival sent out {rival_pokemon.name}!")
            alpha += .4 

            pygame.display.update()

        time.sleep(1)

        alpha = 0
        while alpha < 255:
            game.fill(white)

            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_menssage(f"Go! {player_pokemon.name}!")
            alpha += .4 

            pygame.display.update()

        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        if rival_pokemon.speed > player_pokemon.speed:
            game_status = 'rival turn'
        else:
            game_status = 'player turn'

        pygame.display.update()

        time.sleep(1)

    if game_status == 'player turn':

        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        create_button(240, 140, 10, 350, 130, 412, 'fight')
        create_button(240, 140, 250, 350, 370, 412, f'Use Potion ({player_pokemon.num_potions})')

        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        pygame.display.update()

    if game_status == 'player move':

        game.fill(white)
        player_pokemon.draw()   
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()

        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            create_button(button_width, button_height, left, top, text_center_x, text_center_y, move.name.capitalize())

        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        pygame.display.update()

    if game_status == 'rival turn':
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        display_menssage("Rival's turn...")
        pygame.display.update()
        time.sleep(1)

        if len(rival_pokemon.moves) > 0:
            rival_move = random.choice(rival_pokemon.moves)
            rival_pokemon.perform_attack(player_pokemon, rival_move)
            
            if player_pokemon.current_hp == 0:
                game_status = 'fainted'
            else:
                game_status = 'player turn'
        else:
             game_status = 'player turn'

    if game_status == 'fainted':
        alpha = 255
        while alpha > 0:

            game.fill(white)

            player_pokemon.draw_hp()
            rival_pokemon.draw_hp()

            if rival_pokemon.current_hp == 0:
                rival_pokemon.draw(alpha)
                player_pokemon.draw()
                display_menssage(f"{rival_pokemon.name} fainted!")

            else:
                player_pokemon.draw(alpha)
                rival_pokemon.draw()
                display_menssage(f"{player_pokemon.name} fainted!")
            alpha -= .4

            pygame.display.update()

        game_status = 'game over'

    if game_status == 'game over':

        display_menssage('Play again (y/n)?')
        pygame.display.update()

pygame.quit()