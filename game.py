import pygame
import sys
from pygame.math import Vector2
import math
import random


pygame.init()

okno = pygame.display.set_mode((720, 500))
framy = pygame.time.Clock()
#titulek okna
pygame.display.set_caption("Tower Defense")

screenwidth = 720
screenheight = 500


class Button():
    def __init__(self, x, y, img):
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.last_clicked = 0

    def draw(self, povrch):
        pos = pygame.mouse.get_pos()
        akce = False
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]== 1 and self.clicked == False:
                akce = True
                self.clicked = True
                self.last_clicked = pygame.time.get_ticks()

        if pygame.mouse.get_pressed()[0]==0:
            self.clicked = False
        povrch.blit(self.image, self.rect)
        return akce

class World():
    def __init__(self, data, data2, map_image, vlny, player_health, penize):
        self.vlna = 1
        self.health = player_health
        self.penize = penize
        self.waypoints1 = data
        self.waypoints2 = data2
        self.image = map_image
        self.enemy_list = []
        self.spawned_enemies = 0
        self.vlny = vlny
        self.killed_enemies = 0
        self.missed_enemies = 0

    def process_enemies(self):
        enemies = self.vlny[self.vlna - 1]
        for enemy_type in enemies:
            enemies_to_spawn = enemies[enemy_type]
            for enemy in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)
        random.shuffle(self.enemy_list)

    def draw(self, surface):
        surface.blit(self.image, (0,0))

    def check_vlna_done(self):
        if len(self.enemy_list) == (self.killed_enemies + self.missed_enemies):
            return True
        
    def dalsi_vlna(self):
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, waypoints, enemy_sheets, enemy, mapa):
        pygame.sprite.Sprite.__init__(self)
        self.waypoints = waypoints
        self.pos = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.sheet = enemy_sheets.get(f"{enemy}").get("sheet")
        self.speed = enemy_sheets.get(f"{enemy}").get("speed")
        self.hp = enemy_sheets.get(f"{enemy}").get("hp")
        self.damage = enemy_sheets.get(f"{enemy}").get("damage")
        self.angle = 0
        self.frame = 0
        self.cas = pygame.time.get_ticks()
        self.animace = self.load_animace()
        self.origo_image = self.animace[self.frame]
        self.image = pygame.transform.rotate(self.origo_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.mapa = mapa
        self.enemy = enemy
        self.projectile = False
        
        

    def update(self, stop, speed_koef):
        if stop:
            pass
        else:
            if self.hp <=0:
                self.check_alive()
            self.move(speed_koef)
            self.pohyb(speed_koef)
            self.rotate()
        

    def load_animace(self):
        vyska = 50
        sirka = 50
        animace = []
        for i in range(8):
            temp_img = self.sheet.subsurface(i*sirka, 0, sirka, vyska)
            animace.append(temp_img)
        return animace
    
    def move(self, speed_koef):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        #konec cesty
        else:
            self.kill()
            player_dmg.play()
            self.mapa.health = max(self.mapa.health - self.damage, 0)
            self.mapa.missed_enemies += 1


        dist = self.movement.length()
        if dist >= self.speed*speed_koef:
            self.pos += self.movement.normalize() * self.speed*speed_koef
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint +=1


    def rotate(self):
        dist = self.target - self.pos
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))-90
        self.image = pygame.transform.rotate(self.origo_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def pohyb(self, speed_koef):
        self.origo_image = self.animace[self.frame]
        if pygame.time.get_ticks() - self.cas > 30*(self.speed*speed_koef//2):
            self.cas = pygame.time.get_ticks()
            self.frame +=1
            if self.frame >=8:
                self.frame = 0

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.origo_image, self.angle-90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)

    def check_alive(self):
        if not self.projectile:
            self.kill()
            enemy_kill.play()
            self.mapa.penize += enemy_sheets.get(f"{self.enemy}").get("kill")
            self.mapa.killed_enemies += 1
        else:
            pass

class Projectile(pygame.sprite.Sprite):
    def __init__(self, target, pos, speed, image, angle):
        pygame.sprite.Sprite.__init__(self)
        self.target = target
        self.pos = pos
        self.speed = speed
        self.image = image
        self.angle = angle

    def move(self, speed_koef):
        self.movement = self.target.pos - self.pos
        
        
        dist = self.movement.length()
        if dist >= self.speed*speed_koef:
            self.pos += self.movement.normalize() * self.speed*speed_koef
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            #konec cesty    
            self.kill()

    def rotate(self):
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        surface.blit(self.image, self.rect)

    def update(self, stop, speed_koef):
        if stop:
            pass
        else:
            self.move(speed_koef)
            self.rotate()

class Vez(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y, vez_typ, typ):
        pygame.sprite.Sprite.__init__(self)
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.x = (tile_x +0.5)*50
        self.y = (tile_y +0.5)*50

        self.typ = typ
        self.upgrade_level = 1
        self.sheet = vez_typ[self.upgrade_level-1].get("sheet")
        self.animace = self.load_animace()
        self.frame = 0
        self.cas = pygame.time.get_ticks()
        self.vez_typ = vez_typ
        self.range = vez_typ[self.upgrade_level-1].get("range")
        self.cooldown = vez_typ[self.upgrade_level-1].get("cooldown")
        self.posledni_strela = pygame.time.get_ticks()
        self.selected = False
        self.target = None
        self.damage = vez_typ[self.upgrade_level-1].get("damage")
        self.projectile = vez_typ[self.upgrade_level - 1].get("projectile")
        self.sound = vez_typ[self.upgrade_level - 1].get("sound")
        self.sell = self.vez_typ[self.upgrade_level-1].get("cena") * 0.75

        self.angle = 90
        self.original_image = self.animace[self.frame]
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        
        #range
        self.range_img = pygame.Surface((self.range*2, self.range*2))
        self.range_img.fill((0,0,0))
        self.range_img.set_colorkey((0,0,0))
        pygame.draw.circle(self.range_img, "grey100", (self.range, self.range), self.range)
        self.range_img.set_alpha(100)
        self.range_rect = self.range_img.get_rect()
        self.range_rect.center = self.rect.center


    def load_animace(self):
        vyska = 50
        sirka = 45
        animace = []
        for i in range(8):
            temp_img = self.sheet.subsurface(i*sirka, 0, sirka, vyska)
            animace.append(temp_img)
        return animace
    
    def strelba(self):
        self.original_image = self.animace[self.frame]
        if pygame.time.get_ticks() - self.cas > 30:
            self.cas = pygame.time.get_ticks()
            self.frame +=1
            if self.frame >=8:
                self.frame = 0
                self.posledni_strela = pygame.time.get_ticks()
                self.target = None

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle-90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_img, self.range_rect)
            
    def pick_target(self, enemy_group):
        x_dist = 0
        y_dist = 0
        for enemy in enemy_group:
            if self.target == None:
                if enemy.hp > 0:
                    x_dist = enemy.pos[0] - self.x
                    y_dist = enemy.pos[1] - self.y
                    dist = math.sqrt(x_dist**2 + y_dist**2)
                    if dist < self.range:
                        self.target = enemy
                        self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                        #strela = Projectile(enemy,(self.x, self.y),10,self.projectile, self.angle)
                        #projectile_group.add(strela)
                        self.sound.play()
                        self.target.hp -= self.damage

    def upgrade(self):
        self.upgrade_level += 1
        self.range = self.vez_typ[self.upgrade_level-1].get("range")
        self.cooldown = self.vez_typ[self.upgrade_level-1].get("cooldown")
        self.sheet = self.vez_typ[self.upgrade_level-1].get("sheet")
        self.animace = self.load_animace()
        self.strelba()

        #range_up
        self.range_img = pygame.Surface((self.range*2, self.range*2))
        self.range_img.fill((0,0,0))
        self.range_img.set_colorkey((0,0,0))
        pygame.draw.circle(self.range_img, "grey100", (self.range, self.range), self.range)
        self.range_img.set_alpha(100)
        self.range_rect = self.range_img.get_rect()
        self.range_rect.center = self.rect.center
                
    
    def update(self, enemy_group, stop, speed_koef):
        if stop:
            pass
        elif self.target:
            self.strelba()
        else:    
            if pygame.time.get_ticks() - self.posledni_strela>self.cooldown/speed_koef:
                self.pick_target(enemy_group)



class Podstavec(pygame.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y):
        pygame.sprite.Sprite.__init__(self)
        self.x = (tile_x +0.5)*50
        self.y = (tile_y +0.5)*50
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)



#load obrazku enemaku
rytir_image = pygame.image.load("nepratele/rytir_sheet.png").convert_alpha()
kouzelnik_sheet = pygame.image.load("nepratele/kouzelnik_sheet.png").convert_alpha()
skorpion_sheet = pygame.image.load("nepratele/scorpio_sheet.png").convert_alpha()
troll_sheet = pygame.image.load("nepratele/troll-move.png").convert_alpha()
gargant1_sheet = pygame.image.load("nepratele/gargant-lord-move.png").convert_alpha()
gargant2_sheet = pygame.image.load("nepratele/gargant-berserker-move.png").convert_alpha()
gargant3_sheet = pygame.image.load("nepratele/gargant-boss-move.png").convert_alpha()
drak_sheet = pygame.image.load("nepratele/drak_sprite.png").convert_alpha()

enemy_sheets = {
    "rytir": {
        "speed": 2,
        "hp": 100,
        "sheet": rytir_image,
        "kill": 10,
        "damage": 5
    },
    "kouzelnik":{
        "speed": 2,
        "hp": 200,
        "sheet": kouzelnik_sheet,
        "kill": 20,
        "damage": 7
    },
    "skorpion":{
        "speed": 4,
        "hp": 75,
        "sheet": skorpion_sheet,
        "kill": 10,
        "damage": 2
    },
    "troll":{
        "speed": 1,
        "hp": 2000,
        "sheet": troll_sheet,
        "kill": 200,
        "damage": 30
    },
    "gargant1":{
        "speed": 1.5,
        "hp": 750,
        "sheet": gargant1_sheet,
        "kill": 100,
        "damage": 20
    },
    "gargant2":{
        "speed": 1.5,
        "hp": 1250,
        "sheet": gargant2_sheet,
        "kill": 150,
        "damage": 25
    },
    "gargant3":{
        "speed": 1.5,
        "hp": 1750,
        "sheet": gargant3_sheet,
        "kill": 250,
        "damage": 40
    },
    "drak":{
        "speed": 1,
        "hp": 3000,
        "sheet": drak_sheet,
        "kill": 500,
        "damage": 50
    },
}

#hudba
hudba1 = pygame.mixer.music.load("hudba/gamemusic-6082.mp3")
pygame.mixer.music.play(-1)
#sound
game_over_sound = pygame.mixer.Sound("hudba/game-over-arcade-6435.mp3")
level_complete = pygame.mixer.Sound("hudba/purchase-succesful-ingame-230550.mp3")
exploze = pygame.mixer.Sound("hudba/retro-game-sfx-explosion-104422.mp3")
player_dmg = pygame.mixer.Sound("hudba/damage-40114.mp3")
win = pygame.mixer.Sound("hudba/winbanjo-96336.mp3")
button_sound = pygame.mixer.Sound("hudba/menu-selection-102220.mp3")
mg_sound = pygame.mixer.Sound("hudba/machine-gun-burst-43670.mp3")
mg_sound.set_volume(0.25)
kanon_sound = pygame.mixer.Sound("hudba/gun-shot-6178.mp3")
kanon_sound.set_volume(0.25)
ms_sound = pygame.mixer.Sound("hudba/missile-blast-2-95177.mp3")
ms_sound.set_volume(0.5)
enemy_kill = pygame.mixer.Sound("hudba/monster-attack-47786.mp3")
enemy_kill.set_volume(0.5)

#grupy
enemy_group = pygame.sprite.Group()
vez_group = pygame.sprite.Group()
podstavec_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
#load obrazku vez
podstavec_img = pygame.image.load("turrets/PNG/Tower.50.png").convert_alpha()
kanon1_sheet = pygame.image.load("turrets/PNG/kanon.50.sheet.png").convert_alpha()
kanon2_sheet = pygame.image.load("turrets/PNG/kanon2_sheet.png").convert_alpha()
kanon3_sheet = pygame.image.load("turrets/PNG/kanon3_sheet.png").convert_alpha()

mg1_sheet = pygame.image.load("turrets/PNG/mg1_sheet.png").convert_alpha()
mg2_sheet = pygame.image.load("turrets/PNG/mg2_sheet.png").convert_alpha()
mg3_sheet = pygame.image.load("turrets/PNG/mg3_sheet.png").convert_alpha()

ms1_sheet = pygame.image.load("turrets/PNG/ms1_sheet.png").convert_alpha()
ms2_sheet = pygame.image.load("turrets/PNG/ms2_sheet.png").convert_alpha()
ms3_sheet = pygame.image.load("turrets/PNG/ms3_sheet.png").convert_alpha()

bullet_img = pygame.image.load("turrets/PNG/Bullet_MG_20.png").convert_alpha()
missile_img = pygame.image.load("turrets/PNG/Missile_27.png").convert_alpha()

#obrazek pro kurzor
kurzor_kanon = pygame.image.load("turrets/PNG/kanon_kurzor.50.png").convert_alpha()
kurzor_mg = pygame.image.load("turrets/PNG/mg_kurzor.50.png").convert_alpha()
kurzor_miss = pygame.image.load("turrets/PNG/ml_kurzor.50.png").convert_alpha()

#load mapy
map_image1 = pygame.image.load("mapy/level1.500.png").convert_alpha()
map_image2 = pygame.image.load("mapy/level2.500.png").convert_alpha()
map_image3 = pygame.image.load("mapy/level3.500.png").convert_alpha()

#buttony img
buy_vez_img = pygame.image.load("buttons/buy_turret.png").convert_alpha()
cancel_img = pygame.image.load("buttons/cancel.png").convert_alpha()
upgrade_img = pygame.image.load("buttons/upgrade_turret.png").convert_alpha()
play_img = pygame.image.load("buttons/play_button.png").convert_alpha()
pause_img = pygame.image.load("buttons/pause_button.png").convert_alpha()
menu_img = pygame.image.load("buttons/menu.png").convert_alpha()
music_img = pygame.image.load("buttons/music.png").convert_alpha()
sound_on_img = pygame.image.load("buttons/sound_on.png").convert_alpha()
sound_off_img = pygame.image.load("buttons/sound_off.png").convert_alpha()
speed_up_img = pygame.image.load("buttons/speed_up.png").convert_alpha()
speed_down_img = pygame.image.load("buttons/speed_down.png").convert_alpha()
hint_img = pygame.image.load("buttons/hint.png").convert_alpha()
play_start_img = pygame.image.load("buttons/play.png").convert_alpha()
music_off_img = pygame.image.load("buttons/music_off.png").convert_alpha()
restart_img = pygame.image.load("buttons/restart.png").convert_alpha()
heart_img = pygame.image.load("buttons/heart.png").convert_alpha()
coin_img = pygame.image.load("buttons/coin.png").convert_alpha()
zombie_img = pygame.image.load("buttons/zombie.png").convert_alpha()
menu_big_img = pygame.image.load("buttons/menu_big.png").convert_alpha()
sell_img = pygame.image.load("buttons/sell.png").convert_alpha()
coin_small_img = pygame.image.load("buttons/coin.20.png").convert_alpha()
coin_rect = coin_small_img.get_rect()
level1_img = pygame.image.load("buttons/level1.png").convert_alpha()
level2_img = pygame.image.load("buttons/level2.png").convert_alpha()
level3_img = pygame.image.load("buttons/level3.png").convert_alpha()

start_img = pygame.image.load("buttons/start_screen.png").convert_alpha()
start_rect = start_img.get_rect()
kanon_menu_img = pygame.image.load("turrets/PNG/kanon_menu.png").convert_alpha()
mg_menu_img = pygame.image.load("turrets/PNG/mg_menu.png").convert_alpha()
ms_menu_img = pygame.image.load("turrets/PNG/ms_menu.png").convert_alpha()
kanon_menu_rect = kanon_menu_img.get_rect()
mg_menu_rect = mg_menu_img.get_rect()
ms_menu_rect = ms_menu_img.get_rect()
kanon_menu_rect.center = (610, 115)
mg_menu_rect.center = (610, 195)
ms_menu_rect.center = (610, 275)
#buttony
vez1_button = Button(510, 120, buy_vez_img)
cancel_button = Button(580, 120, cancel_img)
upgrade1_button = Button(570, 120, upgrade_img)
sell1_button = Button(510, 120, sell_img)

vez2_button = Button(510, 200, buy_vez_img)
cancel2_button = Button(580, 200, cancel_img)
upgrade2_button = Button(570, 200, upgrade_img)
sell2_button = Button(510, 200, sell_img)

vez3_button = Button(510, 280, buy_vez_img)
cancel3_button = Button(580, 280, cancel_img)
upgrade3_button = Button(570, 280, upgrade_img)
sell3_button = Button(510, 280, sell_img)

play_button = Button(510,360, play_img)
menu_button = Button(650, 430, menu_img)
sound_on_button = Button(580, 430, sound_on_img)
sound_off_button = Button(580, 430, sound_off_img)
speed_up_button = Button(650, 360, speed_up_img)
speed_down_button = Button(580, 360, speed_down_img)
hint_button = Button(580, 430, hint_img)
music_on_button = Button(510, 430, music_img)
music_off_button = Button(510, 430, music_off_img)
pause_button = Button(510,360, pause_img)
start_button = Button(305,300, play_start_img)
restart_button = Button(170, 220, restart_img)

sound_on_button2 = Button(90,430, sound_on_img)
sound_off_button2 = Button(90,430, sound_off_img)
music_on_button2 = Button(20,430, music_img)
music_off_button2 = Button(20,430, music_off_img)
menu_button2 = Button(10,10, menu_img)

level1_button = Button(80,80, level1_img)
level2_button = Button(290,80, level2_img)
level3_button = Button(500,80, level3_img)

sound_on_button3 = Button(10,370, sound_on_img)
sound_off_button3 = Button(10,370, sound_off_img)
music_on_button3 = Button(10,430, music_img)
music_off_button3 = Button(10,430, music_off_img)

heart_button = Button(510, 10, heart_img)
coin_button = Button(580, 10, coin_img)
zombie_button = Button(660, 10, zombie_img)

menu_big_button = Button(205, 280, menu_big_img)
# font
text_font = pygame.font.SysFont("Consolas", 24, bold = True)
large_font = pygame.font.SysFont("Consolas", 36, bold = True)
small_font = pygame.font.SysFont("Consolas", 16, bold = True)



#ruzne veze
kanon1_data = [
    {
        #1
        "range": 90,
        "cooldown": 1500,
        "damage": 75,
        "sheet": kanon1_sheet,
        "cena": 100,
        "projectile": bullet_img,
        "sound": kanon_sound,
    },
    {
        #2
        "range": 110,
        "cooldown": 1200,
        "damage": 125,
        "sheet": kanon2_sheet,
        "cena": 150,
        "projectile": bullet_img,
        "sound": kanon_sound,
    },
    {
        #3
        "range": 125,
        "cooldown": 1000,
        "damage": 175,
        "sheet": kanon3_sheet,
        "cena": 200,
        "projectile": bullet_img,
        "sound": kanon_sound
    },
    {
        #4
        "range": 150,
        "cooldown": 800,
        "damage": 225,
        "sheet": kanon3_sheet,
        "cena": 400,
        "projectile": bullet_img,
        "sound": kanon_sound
    }
]
kanon2_data = [
    {
        #1
        "range": 90,
        "cooldown": 1000,
        "damage": 50,
        "sheet": mg1_sheet,
        "cena": 200,
        "projectile": bullet_img,
        "sound": mg_sound
    },
    {
        #2
        "range": 100,
        "cooldown": 800,
        "damage": 75,
        "sheet": mg2_sheet,
        "cena": 250,
        "projectile": bullet_img,
        "sound": mg_sound
    },
    {
        #3
        "range": 110,
        "cooldown": 600,
        "damage": 125,
        "sheet": mg3_sheet,
        "cena": 300,
        "projectile": bullet_img,
        "sound": mg_sound
    },
    {
        #4
        "range": 120,
        "cooldown": 400,
        "damage": 200,
        "sheet": mg3_sheet,
        "cena": 500,
        "projectile": bullet_img,
        "sound": mg_sound
    }
]
kanon3_data = [
    {
        #1
        "range": 150,
        "cooldown": 2000,
        "damage": 200,
        "sheet": ms1_sheet,
        "cena": 300,
        "projectile": missile_img,
        "sound": ms_sound
    },
    {
        #2
        "range": 175,
        "cooldown": 2000,
        "damage": 250,
        "sheet": ms2_sheet,
        "cena": 350,
        "projectile": missile_img,
        "sound": mg_sound
    },
    {
        #3
        "range": 210,
        "cooldown": 2000,
        "damage": 300,
        "sheet": ms3_sheet,
        "cena": 400,
        "projectile": missile_img,
        "sound": mg_sound
    },
    {
        #4
        "range": 250,
        "cooldown": 2000,
        "damage": 350,
        "sheet": ms3_sheet,
        "cena": 600,
        "projectile": missile_img,
        "sound": mg_sound
    }
]


def quit_game():
    pygame.quit()
    sys.exit()

def mute_hudba():
    pygame.mixer.music.pause()
    return

def play_hudba():
    pygame.mixer.music.unpause()
    return

def mute_sound():
    game_over_sound.set_volume(0)
    level_complete.set_volume(0)
    exploze.set_volume(0)
    player_dmg.set_volume(0)
    win.set_volume(0)
    button_sound.set_volume(0)
    mg_sound.set_volume(0)
    kanon_sound.set_volume(0)
    kanon_sound.set_volume(0)
    ms_sound.set_volume(0)
    enemy_kill.set_volume(0)
    return

def play_sound():
    game_over_sound.set_volume(1)
    level_complete.set_volume(1)
    exploze.set_volume(1)
    player_dmg.set_volume(1)
    win.set_volume(1)
    button_sound.set_volume(1)
    mg_sound.set_volume(0.25)
    kanon_sound.set_volume(0.25)
    ms_sound.set_volume(0.5)
    enemy_kill.set_volume(0.5)
    

def draw_text(text, font, text_col, x ,y):
    img = font.render(text, True, text_col)
    okno.blit(img, (x,y))

def create_vez1(mouse_pos, mapa_placing, mapa):
    mys_x = mouse_pos[0]//50
    mys_y = mouse_pos[1]//50
    tile_num = mys_y*10+mys_x
    if mapa_placing[tile_num] ==0:
        volno = True
        for vez in vez_group:
            if (mys_x, mys_y)==(vez.tile_x, vez.tile_y):
                volno = False
        if volno == True and mapa.penize >= kanon1_data[0].get("cena"):
            nova_vez = Vez(mys_x, mys_y, kanon1_data, 1)
            vez_group.add(nova_vez)
            podstavec = Podstavec(podstavec_img, mys_x, mys_y)
            podstavec_group.add(podstavec)
            mapa.penize -= kanon1_data[0].get("cena")

def create_vez2(mouse_pos, mapa_placing, mapa):
    mys_x = mouse_pos[0]//50
    mys_y = mouse_pos[1]//50
    tile_num = mys_y*10+mys_x
    if mapa_placing[tile_num] ==0:
        volno = True
        for vez in vez_group:
            if (mys_x, mys_y)==(vez.tile_x, vez.tile_y):
                volno = False
        if volno == True and mapa.penize >= kanon2_data[0].get("cena"):
            nova_vez = Vez(mys_x, mys_y, kanon2_data, 2)
            vez_group.add(nova_vez)
            podstavec = Podstavec(podstavec_img, mys_x, mys_y)
            podstavec_group.add(podstavec)
            mapa.penize -= kanon2_data[0].get("cena")

def create_vez3(mouse_pos, mapa_placing, mapa):
    mys_x = mouse_pos[0]//50
    mys_y = mouse_pos[1]//50
    tile_num = mys_y*10+mys_x
    if mapa_placing[tile_num] ==0:
        volno = True
        for vez in vez_group:
            if (mys_x, mys_y)==(vez.tile_x, vez.tile_y):
                volno = False
        if volno == True and mapa.penize >= kanon3_data[0].get("cena"):
            nova_vez = Vez(mys_x, mys_y, kanon3_data, 3)
            vez_group.add(nova_vez)
            podstavec = Podstavec(podstavec_img, mys_x, mys_y)
            podstavec_group.add(podstavec)
            mapa.penize -= kanon3_data[0].get("cena")

def select_turret(mouse_pos, previous_selected):
    mys_x = mouse_pos[0]//50
    mys_y = mouse_pos[1]//50    
    for vez in vez_group:
        if (mys_x, mys_y)==(vez.tile_x, vez.tile_y) and vez != previous_selected:
            return vez

def clear_selection():
    for vez in vez_group:
        vez.selected = False           


def level_1():
    #variables
    buying_vez1 = False
    buying_vez2 = False
    buying_vez3 = False
    selected_turret = None
    previous_selected = None
    playing = False
    stop = False
    konec = False
    vysledek = False
    global hudba
    global zvuk
    last_enemy_spawn = pygame.time.get_ticks()
    spawn_cooldown = 400
    player_health = 100
    penize = 600
    speed_koef = 1
    konec_sound = 0

    mapa_data = [
            (175,0),
            (175,75),
            (375.2, 75),
            (375.2, 224.8),
            (124.5, 224.8),
            (124.5, 375.6),
            (375.8, 375.6),
            (375.8, 500)
        ]
    
    mapa_placing = [1,1,0,1,0,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0,1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1,0,0,0,0,0,1,1,
                        0,0,1,0,0,0,0,0,1,1,
                        0,0,1,1,1,1,1,1,1,1,
                        0,0,0,0,0,0,0,1,0,0,
                        0,0,0,0,0,0,0,1,0,0]
    
    upgrade_buttony = {
        "1": upgrade1_button,
        "2": upgrade2_button,
        "3": upgrade3_button,
        "11": 110,
        "21": 190,
        "31": 270
    }
    
    vlny = [
            {
               #1
               "rytir": 8,
               "skorpion": 0,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0, 
               "gargant2": 0,
               "gargant3": 0,
                "drak": 0
            },
            {
               #2
               "rytir": 15,
               "skorpion": 2,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0,
            },
            {
               #3
               "rytir": 20,
               "skorpion": 5,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #4
               "rytir": 30,
               "skorpion": 10,
               "kouzelnik": 5,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #5
               "rytir": 40,
               "skorpion": 10,
               "kouzelnik": 15,
               "troll": 0,
               "gargant1": 1,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #6
               "rytir": 40,
               "skorpion": 30,
               "kouzelnik": 15,
               "troll": 0,
               "gargant1": 2,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #7
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 20,
               "troll": 0,
               "gargant1": 3,
               "gargant2":1,
                "gargant3":0,
                "drak":0
            },
            {
               #8
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 25,
               "troll": 1,
               "gargant1": 5,
               "gargant2":3,
                "gargant3":0,
                "drak":0
            },
            {
               #9
               "rytir": 50,
               "skorpion":40,
               "kouzelnik": 30,
               "troll": 3,
               "gargant1": 7,
               "gargant2":5,
                "gargant3":0,
                "drak":0
            },
            {
               #10
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 5,
               "gargant1": 10,
               "gargant2": 7,
                "gargant3": 2,
                "drak":0
            },
            {
               #11
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 1,
               "gargant1": 7,
               "gargant2":7,
                "gargant3":1,
                "drak":0
            },
            {
               #12
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 10,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":10,
                "drak":0
            },
            {
               #13
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 15,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":10,
                "drak":0
            },
            {
               #14
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 40,
               "troll": 20,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":13,
                "drak":0
            },
            {
               #15
               "rytir": 70,
               "skorpion": 80,
               "kouzelnik": 60,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":1
            },
            {
               #16
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik":40,
               "troll": 20,
               "gargant1": 0,
               "gargant2":20,
                "gargant3":13,
                "drak":0
            },
            {
               #17
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 40,
               "troll": 20,
               "gargant1": 30,
               "gargant2":20,
                "gargant3":15,
                "drak":0
            },
            {
               #18
               "rytir": 50,
               "skorpion": 60,
               "kouzelnik": 50,
               "troll": 25,
               "gargant1": 30,
               "gargant2":20,
                "gargant3":20,
                "drak":0
            },
            {
               #19
               "rytir": 50,
               "skorpion": 60,
               "kouzelnik": 50,
               "troll": 25,
               "gargant1": 30,
               "gargant2":25,
                "gargant3":25,
                "drak":2
            },
            {
               #20
               "rytir": 70,
               "skorpion": 100,
               "kouzelnik": 70,
               "troll": 30,
               "gargant1": 35,
               "gargant2":30,
                "gargant3":30,
                "drak":10
            },

        ]

    vlny_reward = [300,300,300,300,500,300,300,300,300,500,500,500,500,500,750,750,750,750,750,1000]
    
    mapa = World(mapa_data, mapa_data, map_image1, vlny, player_health, penize)
    mapa.process_enemies()


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0]<=500 and mouse_pos[1]<= 500:
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    if buying_vez1:
                        create_vez1(mouse_pos, mapa_placing, mapa)
                    elif buying_vez2:
                        create_vez2(mouse_pos, mapa_placing, mapa)
                    elif buying_vez3:
                        create_vez3(mouse_pos, mapa_placing, mapa)
                    else:
                        selected_turret = select_turret(mouse_pos, previous_selected)
                        previous_selected = selected_turret
                    

        #update
        if konec == False:
            if mapa.health <=0:
                konec = True
            if mapa.vlna == len(vlny):
                konec = True
                vysledek = True 
            enemy_group.update(stop, speed_koef)
            vez_group.update(enemy_group, stop, speed_koef)
            projectile_group.update(stop, speed_koef)
            #highlight vybrany turrety
            if selected_turret:
                selected_turret.selected = True

        #draw        
        mapa.draw(okno)
        pygame.draw.rect(okno,"maroon",(500,0,220,500))
        pygame.draw.rect(okno,"grey0",(500,0,220,500), 2)
        okno.blit(kanon_menu_img, kanon_menu_rect)
        okno.blit(mg_menu_img, mg_menu_rect)
        okno.blit(ms_menu_img, ms_menu_rect)
        podstavec_group.draw(okno)
        enemy_group.draw(okno)
        projectile_group.draw(okno)
        for vez in vez_group:
            vez.draw(okno)
        if heart_button.draw(okno):
            #sound efekt easter egg
            pass
        draw_text(str(mapa.health), text_font, "grey100", 540, 15)
        if coin_button.draw(okno):
            #se ea
            pass
        draw_text(str(mapa.penize), text_font, "grey100", 610, 15)
        if zombie_button.draw(okno):
            #se ea
            pass
        draw_text(str(mapa.vlna), text_font, "grey100", 690, 15)

        if konec == False:
            if playing == False or stop == True:
                if play_button.draw(okno):
                    button_sound.play()
                    playing = True
                    stop = False
            else:
                if pause_button.draw(okno):
                    button_sound.play()
                    stop = True
                #spawn
                if pygame.time.get_ticks() - last_enemy_spawn > spawn_cooldown/speed_koef:
                    if mapa.spawned_enemies < len(mapa.enemy_list):
                        typ = mapa.enemy_list[mapa.spawned_enemies]
                        rytir = Enemy(mapa.waypoints1, enemy_sheets, typ, mapa)
                        enemy_group.add(rytir)
                        mapa.spawned_enemies += 1
                        last_enemy_spawn = pygame.time.get_ticks()

            if mapa.check_vlna_done():
                mapa.vlna += 1
                mapa.penize += vlny_reward[mapa.vlna-1]
                playing = False
                stop = True
                last_enemy_spawn = pygame.time.get_ticks()
                mapa.dalsi_vlna()
                mapa.process_enemies()

            #kupovani vezi
            if selected_turret is not None and selected_turret.typ ==1:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 102)
                coin_rect.center = (520, 110)
                okno.blit(coin_small_img, coin_rect)
                if sell1_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon1_data[0].get("cena")}", small_font, "grey100", 530, 102)
                coin_rect.center = (520, 110)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell1_button.last_clicked > 100 and vez1_button.draw(okno):
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = True    


            if buying_vez1 == True:
                kurzor_img = kurzor_kanon.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)

                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_kanon, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel_button.draw(okno):
                    button_sound.play()
                    buying_vez1 = False
            
            
            if selected_turret is not None and  selected_turret.typ ==2:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 182)
                coin_rect.center = (520, 190)
                okno.blit(coin_small_img, coin_rect)
                if sell2_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon2_data[0].get("cena")}", small_font, "grey100", 530, 182)
                coin_rect.center = (520, 190)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell2_button.last_clicked > 100 and vez2_button.draw(okno):
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = True
                    buying_vez1 = False
                    buying_vez3 = False 

            if buying_vez2 == True:
                kurzor_img = kurzor_mg.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)
                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_mg, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel2_button.draw(okno):
                    button_sound.play()
                    buying_vez2 = False
            
            
            if selected_turret is not None and  selected_turret.typ == 3:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 262)
                coin_rect.center = (520, 270)
                okno.blit(coin_small_img, coin_rect)
                
                if sell3_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon3_data[0].get("cena")}", small_font, "grey100", 530, 262)
                coin_rect.center = (520, 270)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell3_button.last_clicked > 100 and vez3_button.draw(okno):
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez3 = True
                    buying_vez2 = False
                    buying_vez1 = False
            
            if buying_vez3 == True:
                kurzor_img = kurzor_miss.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)
                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_miss, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel3_button.draw(okno):
                    button_sound.play()
                    buying_vez3 = False
            
            if selected_turret:
                if selected_turret.upgrade_level < 4 and selected_turret.vez_typ[selected_turret.upgrade_level].get("cena") <= mapa.penize :
                    coin_rect.center = (580, upgrade_buttony.get(f"{selected_turret.typ}1"))
                    draw_text(f"{int(selected_turret.vez_typ[selected_turret.upgrade_level - 1].get("cena"))}", small_font, "grey100", 590, coin_rect.centery-8)
                    okno.blit(coin_small_img, coin_rect)
                    if upgrade_buttony.get(f"{selected_turret.typ}").draw(okno):       
                        mapa.penize -= selected_turret.vez_typ[selected_turret.upgrade_level].get("cena")
                        selected_turret.upgrade()
        else:
            pygame.draw.rect (okno, "maroon", (50,150,400,200), border_radius = 30)
            if vysledek == False:
                draw_text("GAME OVER", large_font, "grey0", 163,170)
                if konec_sound == 0:
                    game_over_sound.play()
                    konec_sound +=1
            else:
                draw_text("YOU WIN", large_font, "grey0", 185,170)
                if konec_sound == 0:
                    win.play()
                    konec_sound +=1
            if restart_button.draw(okno):
                enemy_group.empty()
                vez_group.empty()
                podstavec_group.empty()
                level_1()
            if menu_big_button.draw(okno):
                vyber_levelu()

        

        if menu_button.draw(okno):
            button_sound.play()
            vyber_levelu()
        if hudba:
            #hrat hudbu
            if music_off_button.draw(okno):
                button_sound.play()
                mute_hudba()
                hudba = False
        else:
            if music_on_button.draw(okno):
                button_sound.play()
                play_hudba()
                hudba = True
        if zvuk:
            #hrat hudbu
            if sound_off_button.draw(okno):
                mute_sound()
                zvuk = False
        else:
            if sound_on_button.draw(okno):
                play_sound()
                zvuk = True
        if speed_koef <= 1:
            if speed_up_button.draw(okno):
                button_sound.play()
                speed_koef +=0.5
        if speed_koef >=1:
            if speed_down_button.draw(okno):
                button_sound.play()
                speed_koef-=0.5
        #jeste hint button



        pygame.display.update()
        pygame.display.flip()
        framy.tick(60)


def level_2():
    mapa_data = [
            (488, 450),
            (201,450),
            (201, 275),
            (101, 275),
            (101, 375),
            (201, 375),
            (201, 275),
            (475.5, 275),
            (475.5, 25),
            (325.5, 25),
            (325.5, 150),
            (175, 150),
            (175, 0)
        ]
    
    
    
    buying_vez1 = False
    buying_vez2 = False
    buying_vez3 = False
    selected_turret = None
    previous_selected = None
    playing = False
    stop = False
    konec = False
    vysledek = False
    global hudba
    global zvuk
    last_enemy_spawn = pygame.time.get_ticks()
    spawn_cooldown = 400
    player_health = 100
    penize = 600
    speed_koef = 1
    konec_sound = 0

    mapa_placing = [0,0,0,1,0,0,1,1,1,1,
                    1,0,0,1,0,0,1,0,0,1,
                    1,1,0,1,0,0,1,0,0,1,
                    1,1,0,1,1,1,1,0,0,1,
                    0,0,0,0,0,0,0,0,0,1,
                    0,0,1,1,1,1,1,1,1,1,
                    1,0,1,0,1,0,0,0,0,0,
                    1,1,1,1,1,0,0,0,0,0,
                    1,1,1,0,1,0,0,0,0,0,
                    1,1,1,1,1,1,1,1,1,1]
    
    upgrade_buttony = {
        "1": upgrade1_button,
        "2": upgrade2_button,
        "3": upgrade3_button,
        "11": 110,
        "21": 190,
        "31": 270
    }
    
    vlny = [
            {
               #1
               "rytir": 8,
               "skorpion": 0,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0, 
               "gargant2": 0,
               "gargant3": 0,
                "drak": 0
            },
            {
               #2
               "rytir": 15,
               "skorpion": 2,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0,
            },
            {
               #3
               "rytir": 20,
               "skorpion": 5,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #4
               "rytir": 30,
               "skorpion": 10,
               "kouzelnik": 5,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #5
               "rytir": 40,
               "skorpion": 10,
               "kouzelnik": 15,
               "troll": 0,
               "gargant1": 1,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #6
               "rytir": 40,
               "skorpion": 30,
               "kouzelnik": 15,
               "troll": 0,
               "gargant1": 2,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #7
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 20,
               "troll": 0,
               "gargant1": 3,
               "gargant2":1,
                "gargant3":0,
                "drak":0
            },
            {
               #8
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 25,
               "troll": 1,
               "gargant1": 5,
               "gargant2":3,
                "gargant3":0,
                "drak":0
            },
            {
               #9
               "rytir": 50,
               "skorpion":40,
               "kouzelnik": 30,
               "troll": 3,
               "gargant1": 7,
               "gargant2":5,
                "gargant3":0,
                "drak":0
            },
            {
               #10
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 5,
               "gargant1": 10,
               "gargant2": 7,
                "gargant3": 2,
                "drak":0
            },
            {
               #11
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 1,
               "gargant1": 7,
               "gargant2":7,
                "gargant3":1,
                "drak":0
            },
            {
               #12
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 10,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":10,
                "drak":0
            },
            {
               #13
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 15,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":10,
                "drak":0
            },
            {
               #14
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 40,
               "troll": 20,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":13,
                "drak":0
            },
            {
               #15
               "rytir": 70,
               "skorpion": 80,
               "kouzelnik": 60,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":1
            },
            {
               #16
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik":40,
               "troll": 20,
               "gargant1": 0,
               "gargant2":20,
                "gargant3":13,
                "drak":0
            },
            {
               #17
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 40,
               "troll": 20,
               "gargant1": 30,
               "gargant2":20,
                "gargant3":15,
                "drak":0
            },
            {
               #18
               "rytir": 50,
               "skorpion": 60,
               "kouzelnik": 50,
               "troll": 25,
               "gargant1": 30,
               "gargant2":20,
                "gargant3":20,
                "drak":0
            },
            {
               #19
               "rytir": 50,
               "skorpion": 60,
               "kouzelnik": 50,
               "troll": 25,
               "gargant1": 30,
               "gargant2":25,
                "gargant3":25,
                "drak":2
            },
            {
               #20
               "rytir": 70,
               "skorpion": 100,
               "kouzelnik": 70,
               "troll": 30,
               "gargant1": 35,
               "gargant2":30,
                "gargant3":30,
                "drak":10
            },

        ]
    vlny_reward = [300,300,300,300,500,300,300,300,300,500,500,500,500,500,750,750,750,750,750,1000]
    
    mapa = World(mapa_data, mapa_data, map_image2, vlny, player_health, penize)
    mapa.process_enemies()


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0]<=500 and mouse_pos[1]<= 500:
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    if buying_vez1:
                        create_vez1(mouse_pos, mapa_placing, mapa)
                    elif buying_vez2:
                        create_vez2(mouse_pos, mapa_placing, mapa)
                    elif buying_vez3:
                        create_vez3(mouse_pos, mapa_placing, mapa)
                    else:
                        selected_turret = select_turret(mouse_pos, previous_selected)
                        previous_selected = selected_turret
                    

        #update
        if konec == False:
            if mapa.health <=0:
                konec = True
            if mapa.vlna == len(vlny):
                konec = True
                vysledek = True 
            enemy_group.update(stop, speed_koef)
            vez_group.update(enemy_group, stop, speed_koef)
            projectile_group.update(stop, speed_koef)
            #highlight vybrany turrety
            if selected_turret:
                selected_turret.selected = True

        #draw        
        mapa.draw(okno)
        pygame.draw.rect(okno,"maroon",(500,0,220,500))
        pygame.draw.rect(okno,"grey0",(500,0,220,500), 2)
        okno.blit(kanon_menu_img, kanon_menu_rect)
        okno.blit(mg_menu_img, mg_menu_rect)
        okno.blit(ms_menu_img, ms_menu_rect)
        podstavec_group.draw(okno)
        podstavec_group.draw(okno)
        enemy_group.draw(okno)
        projectile_group.draw(okno)
        for vez in vez_group:
            vez.draw(okno)
        if heart_button.draw(okno):
            #sound efekt easter egg
            pass
        draw_text(str(mapa.health), text_font, "grey100", 540, 15)
        if coin_button.draw(okno):
            #se ea
            pass
        draw_text(str(mapa.penize), text_font, "grey100", 610, 15)
        if zombie_button.draw(okno):
            #se ea
            pass
        draw_text(str(mapa.vlna), text_font, "grey100", 690, 15)
    

        if konec == False:
            if playing == False or stop == True:
                if play_button.draw(okno):
                    button_sound.play()
                    playing = True
                    stop = False
            else:
                if pause_button.draw(okno):
                    button_sound.play()
                    stop = True
                #spawn
                if pygame.time.get_ticks() - last_enemy_spawn > spawn_cooldown/speed_koef:
                    if mapa.spawned_enemies < len(mapa.enemy_list):
                        typ = mapa.enemy_list[mapa.spawned_enemies]
                        rytir = Enemy(mapa.waypoints1, enemy_sheets, typ, mapa)
                        enemy_group.add(rytir)
                        mapa.spawned_enemies += 1
                        last_enemy_spawn = pygame.time.get_ticks()

            if mapa.check_vlna_done():
                mapa.vlna += 1
                mapa.penize += vlny_reward[mapa.vlna-1]
                playing = False
                stop = True
                last_enemy_spawn = pygame.time.get_ticks()
                mapa.dalsi_vlna()
                mapa.process_enemies()

            #kupovani vezi
            if selected_turret is not None and selected_turret.typ ==1:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 102)
                coin_rect.center = (520, 110)
                okno.blit(coin_small_img, coin_rect)
                if sell1_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon1_data[0].get("cena")}", small_font, "grey100", 530, 102)
                coin_rect.center = (520, 110)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell1_button.last_clicked > 100 and vez1_button.draw(okno):
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = True    


            if buying_vez1 == True:
                kurzor_img = kurzor_kanon.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)

                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_kanon, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel_button.draw(okno):
                    button_sound.play()
                    buying_vez1 = False
            
            
            if selected_turret is not None and  selected_turret.typ ==2:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 182)
                coin_rect.center = (520, 190)
                okno.blit(coin_small_img, coin_rect)
                if sell2_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon2_data[0].get("cena")}", small_font, "grey100", 530, 182)
                coin_rect.center = (520, 190)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell2_button.last_clicked > 100 and vez2_button.draw(okno):
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = True
                    buying_vez1 = False
                    buying_vez3 = False 

            if buying_vez2 == True:
                kurzor_img = kurzor_mg.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)
                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_mg, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel2_button.draw(okno):
                    button_sound.play()
                    buying_vez2 = False
            
            
            if selected_turret is not None and  selected_turret.typ == 3:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 262)
                coin_rect.center = (520, 270)
                okno.blit(coin_small_img, coin_rect)
                
                if sell3_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon3_data[0].get("cena")}", small_font, "grey100", 530, 262)
                coin_rect.center = (520, 270)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell3_button.last_clicked > 100 and vez3_button.draw(okno):
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez3 = True
                    buying_vez2 = False
                    buying_vez1 = False
            
            if buying_vez3 == True:
                kurzor_img = kurzor_miss.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)
                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_miss, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel3_button.draw(okno):
                    button_sound.play()
                    buying_vez3 = False
            
            if selected_turret:
                if selected_turret.upgrade_level < 4 and selected_turret.vez_typ[selected_turret.upgrade_level].get("cena") <= mapa.penize :
                    coin_rect.center = (580, upgrade_buttony.get(f"{selected_turret.typ}1"))
                    draw_text(f"{int(selected_turret.vez_typ[selected_turret.upgrade_level - 1].get("cena"))}", small_font, "grey100", 590, coin_rect.centery-8)
                    okno.blit(coin_small_img, coin_rect)
                    if upgrade_buttony.get(f"{selected_turret.typ}").draw(okno):       
                        mapa.penize -= selected_turret.vez_typ[selected_turret.upgrade_level].get("cena")
                        selected_turret.upgrade()
        else:
            pygame.draw.rect (okno, "maroon", (50,150,400,200), border_radius = 30)
            if vysledek == False:
                draw_text("GAME OVER", large_font, "grey0", 163,170)
                if konec_sound == 0:
                    game_over_sound.play()
                    konec_sound +=1
            else:
                draw_text("YOU WIN", large_font, "grey0", 185,170)
                if konec_sound == 0:
                    win.play()
                    konec_sound +=1
            if restart_button.draw(okno):
                enemy_group.empty()
                vez_group.empty()
                podstavec_group.empty()
                level_2()
            if menu_big_button.draw(okno):
                vyber_levelu()

        

        if menu_button.draw(okno):
            button_sound.play()
            vyber_levelu()
        if hudba:
            #hrat hudbu
            if music_off_button.draw(okno):
                button_sound.play()
                mute_hudba()
                hudba = False
        else:
            if music_on_button.draw(okno):
                button_sound.play()
                play_hudba()
                hudba = True
        if zvuk:
            #hrat hudbu
            if sound_off_button.draw(okno):
                mute_sound()
                zvuk = False
        else:
            if sound_on_button.draw(okno):
                play_sound()
                zvuk = True
        if speed_koef <= 1:
            if speed_up_button.draw(okno):
                button_sound.play()
                speed_koef +=0.5
        if speed_koef >=1:
            if speed_down_button.draw(okno):
                button_sound.play()
                speed_koef-=0.5
        #jeste hint button



        
        
        pygame.display.update()
        pygame.display.flip()
        framy.tick(60)


def level_3():
    
   
        
    mapa_data1 = [
            (0,225),
            (75,225),
            (75,475),
            (225, 475),
            (225, 325.5),
            (374.4, 325.5),
            (374.4, 425.5),
            (485, 425.5),
            ]

    mapa_data2 = [
            (0, 225),
            (75, 225),
            (75, 75),
            (375.5, 75),
            (375.5, 425.5),
            (485, 425.5),
        ]
    buying_vez1 = False
    buying_vez2 = False
    buying_vez3 = False
    selected_turret = None
    previous_selected = None
    playing = False
    stop = False
    konec = False
    vysledek = False
    global hudba
    global zvuk
    last_enemy_spawn = pygame.time.get_ticks()
    spawn_cooldown = 400
    player_health = 100
    penize = 600
    speed_koef = 1
    konec_sound = 0
    mapa_placing = [0,0,1,1,1,1,1,1,1,0,
                    0,1,1,1,1,1,1,1,0,1,
                    0,1,0,0,0,0,0,1,0,1,
                    0,1,0,1,1,0,0,1,1,1,
                    1,1,0,1,1,0,0,1,1,1,
                    0,1,0,0,0,0,0,1,1,1,
                    0,1,1,1,1,1,1,1,0,1,
                    0,1,1,1,1,0,0,1,0,0,
                    0,1,1,1,1,0,0,1,1,1,
                    0,1,1,1,1,0,0,0,0,0]
    
    upgrade_buttony = {
        "1": upgrade1_button,
        "2": upgrade2_button,
        "3": upgrade3_button,
        "11": 110,
        "21": 190,
        "31": 270
    }
    
    vlny = [
            {
               #1
               "rytir": 8,
               "skorpion": 0,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0, 
               "gargant2": 0,
               "gargant3": 0,
                "drak": 0
            },
            {
               #2
               "rytir": 15,
               "skorpion": 2,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0,
            },
            {
               #3
               "rytir": 20,
               "skorpion": 5,
               "kouzelnik": 0,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #4
               "rytir": 30,
               "skorpion": 10,
               "kouzelnik": 5,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #5
               "rytir": 40,
               "skorpion": 10,
               "kouzelnik": 15,
               "troll": 0,
               "gargant1": 1,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #6
               "rytir": 40,
               "skorpion": 30,
               "kouzelnik": 15,
               "troll": 0,
               "gargant1": 2,
               "gargant2":0,
                "gargant3":0,
                "drak":0
            },
            {
               #7
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 20,
               "troll": 0,
               "gargant1": 3,
               "gargant2":1,
                "gargant3":0,
                "drak":0
            },
            {
               #8
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 25,
               "troll": 1,
               "gargant1": 5,
               "gargant2":3,
                "gargant3":0,
                "drak":0
            },
            {
               #9
               "rytir": 50,
               "skorpion":40,
               "kouzelnik": 30,
               "troll": 3,
               "gargant1": 7,
               "gargant2":5,
                "gargant3":0,
                "drak":0
            },
            {
               #10
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 5,
               "gargant1": 10,
               "gargant2": 7,
                "gargant3": 2,
                "drak":0
            },
            {
               #11
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 1,
               "gargant1": 7,
               "gargant2":7,
                "gargant3":1,
                "drak":0
            },
            {
               #12
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 10,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":10,
                "drak":0
            },
            {
               #13
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 30,
               "troll": 15,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":10,
                "drak":0
            },
            {
               #14
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 40,
               "troll": 20,
               "gargant1": 0,
               "gargant2":15,
                "gargant3":13,
                "drak":0
            },
            {
               #15
               "rytir": 70,
               "skorpion": 80,
               "kouzelnik": 60,
               "troll": 0,
               "gargant1": 0,
               "gargant2":0,
                "gargant3":0,
                "drak":1
            },
            {
               #16
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik":40,
               "troll": 20,
               "gargant1": 0,
               "gargant2":20,
                "gargant3":13,
                "drak":0
            },
            {
               #17
               "rytir": 50,
               "skorpion": 40,
               "kouzelnik": 40,
               "troll": 20,
               "gargant1": 30,
               "gargant2":20,
                "gargant3":15,
                "drak":0
            },
            {
               #18
               "rytir": 50,
               "skorpion": 60,
               "kouzelnik": 50,
               "troll": 25,
               "gargant1": 30,
               "gargant2":20,
                "gargant3":20,
                "drak":0
            },
            {
               #19
               "rytir": 50,
               "skorpion": 60,
               "kouzelnik": 50,
               "troll": 25,
               "gargant1": 30,
               "gargant2":25,
                "gargant3":25,
                "drak":2
            },
            {
               #20
               "rytir": 70,
               "skorpion": 100,
               "kouzelnik": 70,
               "troll": 30,
               "gargant1": 35,
               "gargant2":30,
                "gargant3":30,
                "drak":10
            },

        ]
    
    vlny_reward = [300,300,300,300,500,300,300,300,300,500,500,500,500,500,750,750,750,750,750,1000]
    
    mapa = World(mapa_data1, mapa_data2, map_image3, vlny, player_health, penize)
    mapa.process_enemies()


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0]<=500 and mouse_pos[1]<= 500:
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    if buying_vez1:
                        create_vez1(mouse_pos, mapa_placing, mapa)
                    elif buying_vez2:
                        create_vez2(mouse_pos, mapa_placing, mapa)
                    elif buying_vez3:
                        create_vez3(mouse_pos, mapa_placing, mapa)
                    else:
                        selected_turret = select_turret(mouse_pos, previous_selected)
                        previous_selected = selected_turret
                    

        #update
        if konec == False:
            if mapa.health <=0:
                konec = True
            if mapa.vlna == len(vlny):
                konec = True
                vysledek = True 
            enemy_group.update(stop, speed_koef)
            vez_group.update(enemy_group, stop, speed_koef)
            projectile_group.update(stop, speed_koef)
            #highlight vybrany turrety
            if selected_turret:
                selected_turret.selected = True

        #draw        
        mapa.draw(okno)
        pygame.draw.rect(okno,"maroon",(500,0,220,500))
        pygame.draw.rect(okno,"grey0",(500,0,220,500), 2)
        okno.blit(kanon_menu_img, kanon_menu_rect)
        okno.blit(mg_menu_img, mg_menu_rect)
        okno.blit(ms_menu_img, ms_menu_rect)
        podstavec_group.draw(okno)
        podstavec_group.draw(okno)
        enemy_group.draw(okno)
        projectile_group.draw(okno)
        for vez in vez_group:
            vez.draw(okno)
        if heart_button.draw(okno):
            #sound efekt easter egg
            pass
        draw_text(str(mapa.health), text_font, "grey100", 540, 15)
        if coin_button.draw(okno):
            #se ea
            pass
        draw_text(str(mapa.penize), text_font, "grey100", 610, 15)
        if zombie_button.draw(okno):
            #se ea
            pass
        draw_text(str(mapa.vlna), text_font, "grey100", 690, 15)
        #upgrade_button.draw(okno)
        #upgrade2_button.draw(okno)
        #upgrade3_button.draw(okno)

        if konec == False:
            if playing == False or stop == True:
                if play_button.draw(okno) and pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    button_sound.play()
                    playing = True
                    stop = False
            else:
                if pause_button.draw(okno):
                    button_sound.play()
                    stop = True
                #spawn
                if pygame.time.get_ticks() - last_enemy_spawn > spawn_cooldown/speed_koef:
                    if mapa.spawned_enemies < len(mapa.enemy_list):
                        typ = mapa.enemy_list[mapa.spawned_enemies]
                        cesta = random.randint(1,2)
                        if cesta ==1:   
                            rytir = Enemy(mapa.waypoints1, enemy_sheets, typ, mapa)
                        else:
                            rytir = Enemy(mapa.waypoints2, enemy_sheets, typ, mapa)
                        enemy_group.add(rytir)
                        mapa.spawned_enemies += 1
                        last_enemy_spawn = pygame.time.get_ticks()

            if mapa.check_vlna_done():
                mapa.vlna += 1
                mapa.penize += vlny_reward[mapa.vlna-1]
                playing = False
                stop = True
                last_enemy_spawn = pygame.time.get_ticks()
                mapa.dalsi_vlna()
                mapa.process_enemies()

            #kupovani vezi
            if selected_turret is not None and selected_turret.typ ==1:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 102)
                coin_rect.center = (520, 110)
                okno.blit(coin_small_img, coin_rect)
                if sell1_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon1_data[0].get("cena")}", small_font, "grey100", 530, 102)
                coin_rect.center = (520, 110)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell1_button.last_clicked > 100 and vez1_button.draw(okno) and pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = True    


            if buying_vez1 == True:
                kurzor_img = kurzor_kanon.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)

                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_kanon, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel_button.draw(okno):
                    button_sound.play()
                    buying_vez1 = False
            
            
            if selected_turret is not None and  selected_turret.typ ==2:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 182)
                coin_rect.center = (520, 190)
                okno.blit(coin_small_img, coin_rect)
                if sell2_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon2_data[0].get("cena")}", small_font, "grey100", 530, 182)
                coin_rect.center = (520, 190)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell2_button.last_clicked > 100 and vez2_button.draw(okno) and pygame.time.get_ticks() - level3_button.last_clicked > 100: 
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = True
                    buying_vez1 = False
                    buying_vez3 = False 

            if buying_vez2 == True:
                kurzor_img = kurzor_mg.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)
                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_mg, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel2_button.draw(okno):
                    button_sound.play()
                    buying_vez2 = False
            
            
            if selected_turret is not None and  selected_turret.typ == 3:
                draw_text(f"{int(selected_turret.sell)}", small_font, "grey100", 530, 262)
                coin_rect.center = (520, 270)
                okno.blit(coin_small_img, coin_rect)
                
                if sell3_button.draw(okno):
                    button_sound.play()
                    mapa.penize += int(selected_turret.sell)
                    for podstavec in podstavec_group:
                        if podstavec.x == selected_turret.x and podstavec.y == selected_turret.y:
                            podstavec.kill()
                            continue
                    selected_turret.kill()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez2 = False
                    buying_vez3 = False
                    buying_vez1 = False
            else:
                draw_text(f"{kanon3_data[0].get("cena")}", small_font, "grey100", 530, 262)
                coin_rect.center = (520, 270)
                okno.blit(coin_small_img, coin_rect)
                if pygame.time.get_ticks() - sell3_button.last_clicked > 100 and vez3_button.draw(okno) and pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    button_sound.play()
                    selected_turret = None
                    clear_selection()
                    previous_selected = None
                    buying_vez3 = True
                    buying_vez2 = False
                    buying_vez1 = False
            
            if buying_vez3 == True:
                kurzor_img = kurzor_miss.get_rect()
                kurzor_pos = pygame.mouse.get_pos()
                kurzor_img.center = (kurzor_pos[0]//50*50+25,kurzor_pos[1]//50*50+20)
                sqr_img = pygame.Surface((50, 50), pygame.SRCALPHA)
                sqr_img.fill((0,0,0,0))
                rect_pos = (0,0)
                rect_size = (50,50)
                if kurzor_pos[0]<=500:
                    if mapa_placing[kurzor_pos[0]//50+kurzor_pos[1]//50*10] == 0:
                        pygame.draw.rect(sqr_img, (50,205,50,100), pygame.Rect(rect_pos,rect_size))
                    
                    else:
                        pygame.draw.rect(sqr_img, (255,0,0,100), pygame.Rect(rect_pos,rect_size))   
                    okno.blit(kurzor_miss, kurzor_img)
                    okno.blit(sqr_img, (kurzor_pos[0] // 50 * 50, kurzor_pos[1] // 50 * 50)) 
                if cancel3_button.draw(okno):
                    button_sound.play()
                    buying_vez3 = False
            
            if selected_turret:
                if selected_turret.upgrade_level < 4 and selected_turret.vez_typ[selected_turret.upgrade_level].get("cena") <= mapa.penize :
                    coin_rect.center = (580, upgrade_buttony.get(f"{selected_turret.typ}1"))
                    draw_text(f"{int(selected_turret.vez_typ[selected_turret.upgrade_level - 1].get("cena"))}", small_font, "grey100", 590, coin_rect.centery-8)
                    okno.blit(coin_small_img, coin_rect)
                    if upgrade_buttony.get(f"{selected_turret.typ}").draw(okno):       
                        mapa.penize -= selected_turret.vez_typ[selected_turret.upgrade_level].get("cena")
                        selected_turret.upgrade()
        else:
            pygame.draw.rect (okno, "maroon", (50,150,400,200), border_radius = 30)
            if vysledek == False:
                draw_text("GAME OVER", large_font, "grey0", 163,170)
                if konec_sound == 0:
                    game_over_sound.play()
                    konec_sound +=1
            else:
                draw_text("YOU WIN", large_font, "grey0", 185,170)
                if konec_sound == 0:
                    win.play()
                    konec_sound +=1
            if restart_button.draw(okno):
                enemy_group.empty()
                vez_group.empty()
                podstavec_group.empty()
                level_3()
            if menu_big_button.draw(okno):
                vyber_levelu()

        

        if menu_button.draw(okno):
            if pygame.time.get_ticks() - level3_button.last_clicked > 100:
                button_sound.play()
                vyber_levelu()
        if hudba:
            #hrat hudbu
            if music_off_button.draw(okno):
                if pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    button_sound.play()
                    mute_hudba()
                    hudba = False
        else:
            if music_on_button.draw(okno):
                if pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    button_sound.play()
                    play_hudba()
                    hudba = True
        if zvuk:
            #hrat hudbu
            if sound_off_button.draw(okno):
                if pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    mute_sound()
                    zvuk = False
        else:
            if sound_on_button.draw(okno):
                if pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    play_sound()
                    zvuk = True
        if speed_koef <= 1:
            if speed_up_button.draw(okno):
                if pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    button_sound.play()
                    speed_koef +=0.5
        if speed_koef >=1:
            if speed_down_button.draw(okno):
                if pygame.time.get_ticks() - level3_button.last_clicked > 100:
                    button_sound.play()
                    speed_koef-=0.5
        #jeste hint buttonimage3)





        pygame.display.update()
        pygame.display.flip()
        framy.tick(60)


#vyber levelu
def vyber_levelu():
    enemy_group.empty()
    vez_group.empty()
    podstavec_group.empty()
    

    global zvuk
    global hudba

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
        
        okno.fill("maroon")
        if menu_button2.draw(okno):
            button_sound.play()
            main_menu()
        
        #button("1", 80,80, 200, 400, (255,0,0), (0,255,0), level_1)
        #button("2",290,80, 200, 400, (255,0,0), (0,255,0), level_2)
        #button("3", 500,80, 200, 400, (255,0,0), (0,255,0), level_3)
        if level1_button.draw(okno):
            if pygame.time.get_ticks() - start_button.last_clicked > 100 and pygame.time.get_ticks() - menu_big_button.last_clicked>100:
                button_sound.play()
                level_1()
        if level2_button.draw(okno):
            if pygame.time.get_ticks() - start_button.last_clicked > 100 and pygame.time.get_ticks() - menu_big_button.last_clicked>100:
                button_sound.play()
                level_2()
        if level3_button.draw(okno):
            if pygame.time.get_ticks() - start_button.last_clicked > 100 and pygame.time.get_ticks() - menu_button.last_clicked > 100:
                button_sound.play()
                level_3()

        if hudba:
            #hrat hudbu
            if music_off_button3.draw(okno):
                button_sound.play()
                hudba = False
                mute_hudba()
        else:
            if music_on_button3.draw(okno):
                button_sound.play()
                hudba = True
                play_hudba()
        if zvuk:
            #hrat hudbu
            if sound_off_button3.draw(okno):
                mute_sound()
                zvuk = False
        else:
            if sound_on_button3.draw(okno):
                play_sound()
                zvuk = True


        pygame.display.update()
        pygame.display.flip()
        framy.tick(60)

zvuk = True
hudba = True

def main_menu():
    global zvuk
    global hudba
    while True:

        for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   quit_game()


        okno.blit(start_img, start_rect)
        #hlavni menu
        if start_button.draw(okno):
            button_sound.play()
            vyber_levelu()
        if hudba:
            #hrat hudbu
            if music_off_button2.draw(okno):
                button_sound.play()
                hudba = False
                mute_hudba()
        else:
            if music_on_button2.draw(okno):
                button_sound.play()
                hudba = True
                play_hudba()
        if zvuk:
            #hrat hudbu
            if sound_off_button2.draw(okno):
                mute_sound()
                zvuk = False
        else:
            if sound_on_button2.draw(okno):
                play_hudba()
                zvuk = True
        pygame.display.update()

      #dat na listu
        pygame.display.flip()

        framy.tick(60)  


main_menu()
pygame.quit()