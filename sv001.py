import pygame
import numpy as np
import sys
import random
import time
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
PIXEL_SIZE = 10
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Setup the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sun Voyage")
clock = pygame.time.Clock()

# Font setup
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 28)

# Sound effects
def create_tone(frequency, duration=0.3, volume=0.5, is_enemy=False):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(frequency * t * 2 * np.pi)
    
    if is_enemy:
        # Add some noise for enemy sounds
        noise = np.random.normal(0, 0.1, wave.shape)
        wave = wave + noise
        wave = np.clip(wave, -1, 1)
    
    wave = (wave * 32767 * volume).astype(np.int16)
    sound = pygame.sndarray.make_sound(wave)
    return sound

# Create various tones
player_tones = {
    "blast": create_tone(440),  # A4
    "forcefield": create_tone(523.25),  # C5
    "fission": create_tone(659.25),  # E5
    "fusion": create_tone(783.99)  # G5
}

enemy_tones = {
    "attack": create_tone(415.30, is_enemy=True),  # G#4
    "defend": create_tone(493.88, is_enemy=True),  # B4
    "special": create_tone(622.25, is_enemy=True),  # D#5
    "heal": create_tone(739.99, is_enemy=True)  # F#5
}

# Create the title music
def create_title_music():
    notes = [
        (392.00, 0.5),  # G4
        (440.00, 0.5),  # A4
        (493.88, 0.5),  # B4
        (523.25, 1.0),  # C5
        (493.88, 0.5),  # B4
        (440.00, 0.5),  # A4
        (392.00, 1.0),  # G4
        (440.00, 0.5),  # A4
        (493.88, 0.5),  # B4
        (523.25, 1.0),  # C5
        (587.33, 1.0),  # D5
        (659.25, 2.0),  # E5
    ]
    
    sample_rate = 44100
    audio_data = np.array([], dtype=np.int16)
    
    for frequency, duration in notes:
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        note = np.sin(frequency * t * 2 * np.pi)
        note = (note * 32767 * 0.5).astype(np.int16)
        audio_data = np.append(audio_data, note)
    
    sound = pygame.sndarray.make_sound(audio_data)
    return sound

# Create ending music (more melodic and peaceful)
def create_ending_music():
    notes = [
        (523.25, 0.5),  # C5
        (587.33, 0.5),  # D5
        (659.25, 1.0),  # E5
        (698.46, 1.0),  # F5
        (783.99, 1.0),  # G5
        (880.00, 1.0),  # A5
        (987.77, 1.5),  # B5
        (1046.50, 2.0), # C6
    ]
    
    sample_rate = 44100
    audio_data = np.array([], dtype=np.int16)
    
    for frequency, duration in notes:
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        note = np.sin(frequency * t * 2 * np.pi)
        
        # Add harmonics for a richer tone
        harmonic = np.sin(2 * frequency * t * 2 * np.pi) * 0.3
        note = note + harmonic
        
        note = (note * 32767 * 0.5).astype(np.int16)
        audio_data = np.append(audio_data, note)
    
    sound = pygame.sndarray.make_sound(audio_data)
    return sound

title_music = create_title_music()
ending_music = create_ending_music()

# Game states
TITLE_SCREEN = 0
NAME_INPUT = 1
INTRO_SCREEN = 2
BATTLE_SCREEN = 3
ENDING_SCREEN = 4

# Player class
class Player:
    def __init__(self, name="Sun"):
        self.name = name
        self.max_health = 100
        self.health = 100
        self.power = 20
        self.defense = 10
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        self.victories = 0
    
    def attack(self):
        return random.randint(int(self.power * 0.8), int(self.power * 1.2))
    
    def defend(self):
        return self.defense * 2
    
    def fission(self):
        # Powerful attack that costs health
        cost = int(self.max_health * 0.1)
        self.health = max(1, self.health - cost)
        return random.randint(int(self.power * 1.5), int(self.power * 2.0))
    
    def fusion(self):
        # Heal self
        heal_amount = int(self.max_health * 0.3)
        self.health = min(self.max_health, self.health + heal_amount)
        return heal_amount
    
    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= self.exp_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        self.max_health += 20
        self.health = self.max_health
        self.power += 5
        self.defense += 3
        return True
        
    def draw(self, screen):
        # Draw the sun (player)
        sun_radius = 50
        pygame.draw.circle(screen, YELLOW, (WIDTH // 2, HEIGHT - 100), sun_radius)
        
        # Draw some "rays" for the sun
        for i in range(8):
            angle = i * np.pi / 4
            x1 = WIDTH // 2 + int(sun_radius * np.cos(angle))
            y1 = HEIGHT - 100 + int(sun_radius * np.sin(angle))
            x2 = WIDTH // 2 + int((sun_radius + 20) * np.cos(angle))
            y2 = HEIGHT - 100 + int((sun_radius + 20) * np.sin(angle))
            pygame.draw.line(screen, ORANGE, (x1, y1), (x2, y2), 3)
        
        # Draw health bar
        health_percentage = self.health / self.max_health
        pygame.draw.rect(screen, RED, (WIDTH // 2 - 100, HEIGHT - 20, 200, 15))
        pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 100, HEIGHT - 20, int(200 * health_percentage), 15))
        
        # Draw player name and health
        name_text = font_small.render(f"{self.name} - Level {self.level}", True, WHITE)
        health_text = font_small.render(f"HP: {self.health}/{self.max_health}", True, WHITE)
        screen.blit(name_text, (WIDTH // 2 - 100, HEIGHT - 40))
        screen.blit(health_text, (WIDTH // 2 + 30, HEIGHT - 40))

# Enemy class
class Enemy:
    def __init__(self, level):
        self.types = [
            {"name": "Planet", "color": BLUE, "radius": 40},
            {"name": "Comet", "color": WHITE, "radius": 30},
            {"name": "Black Hole", "color": PURPLE, "radius": 35},
            {"name": "Meteor", "color": ORANGE, "radius": 25},
            {"name": "Nebula", "color": (138, 43, 226), "radius": 45},
            {"name": "Neutron Star", "color": (0, 191, 255), "radius": 30},
            {"name": "Supernova", "color": (255, 69, 0), "radius": 50},
            {"name": "Asteroid", "color": (169, 169, 169), "radius": 35}
        ]
        
        self.type = random.choice(self.types)
        self.name = self.type["name"]
        self.color = self.type["color"]
        self.radius = self.type["radius"]
        
        # Scale difficulty with player level
        level_factor = 0.8 + (level * 0.2)
        self.max_health = int(80 * level_factor)
        self.health = self.max_health
        self.power = int(15 * level_factor)
        self.defense = int(8 * level_factor)
        self.exp_reward = int(50 * level_factor)
        
        # Special attributes based on enemy type
        if self.name == "Black Hole":
            self.power *= 1.5
            self.defense *= 0.7
        elif self.name == "Neutron Star":
            self.power *= 1.2
            self.max_health *= 1.2
            self.health = self.max_health
        elif self.name == "Supernova":
            self.power *= 2
            self.max_health *= 0.8
            self.health = self.max_health
            self.defense *= 0.5
    
    def choose_action(self):
        # AI for enemy actions
        if self.health < self.max_health * 0.3:
            # Low health, 50% chance to heal
            if random.random() < 0.5:
                return "heal"
        
        if self.health < self.max_health * 0.5:
            # Medium health, 30% chance to defend, 10% chance to heal
            rand = random.random()
            if rand < 0.3:
                return "defend"
            elif rand < 0.4:
                return "heal"
        
        # Otherwise mostly attack, sometimes use special
        if random.random() < 0.7:
            return "attack"
        else:
            return "special"
    
    def attack(self):
        return random.randint(int(self.power * 0.8), int(self.power * 1.2))
    
    def defend(self):
        return self.defense * 2
    
    def special(self):
        # Special attack based on enemy type
        if self.name == "Black Hole":
            return random.randint(int(self.power * 1.5), int(self.power * 2.0))
        elif self.name == "Supernova":
            return random.randint(int(self.power * 1.8), int(self.power * 2.2))
        else:
            return random.randint(int(self.power * 1.3), int(self.power * 1.7))
    
    def heal(self):
        heal_amount = int(self.max_health * 0.2)
        self.health = min(self.max_health, self.health + heal_amount)
        return heal_amount
    
    def draw(self, screen, flash=False):
        # Draw the enemy based on its type
        if flash:
            color = WHITE  # Flash white when hit
        else:
            color = self.color
        
        if self.name == "Planet":
            pygame.draw.circle(screen, color, (WIDTH // 2, 100), self.radius)
            # Draw some details on the planet
            pygame.draw.arc(screen, (200, 200, 200), (WIDTH // 2 - self.radius, 100 - self.radius, 
                                                     self.radius * 2, self.radius * 2), 
                           0, np.pi / 2, 2)
        
        elif self.name == "Comet":
            # Draw comet head
            pygame.draw.circle(screen, color, (WIDTH // 2, 100), self.radius)
            # Draw comet tail
            points = [
                (WIDTH // 2, 100 - self.radius),
                (WIDTH // 2 - self.radius * 2, 100 - self.radius * 2),
                (WIDTH // 2, 100 + self.radius)
            ]
            pygame.draw.polygon(screen, color, points)
        
        elif self.name == "Black Hole":
            # Outer ring
            pygame.draw.circle(screen, (100, 0, 100), (WIDTH // 2, 100), self.radius + 10)
            # Inner black hole
            pygame.draw.circle(screen, BLACK, (WIDTH // 2, 100), self.radius)
            # Draw some "gravitational lensing" effect
            for i in range(8):
                angle = i * np.pi / 4
                x1 = WIDTH // 2 + int((self.radius + 10) * np.cos(angle))
                y1 = 100 + int((self.radius + 10) * np.sin(angle))
                x2 = WIDTH // 2 + int((self.radius + 30) * np.cos(angle))
                y2 = 100 + int((self.radius + 30) * np.sin(angle))
                pygame.draw.line(screen, PURPLE, (x1, y1), (x2, y2), 2)
        
        elif self.name == "Meteor":
            # Draw irregular meteor shape
            points = []
            for i in range(8):
                angle = i * np.pi / 4
                r = self.radius * (0.8 + random.random() * 0.4)
                x = WIDTH // 2 + int(r * np.cos(angle))
                y = 100 + int(r * np.sin(angle))
                points.append((x, y))
            pygame.draw.polygon(screen, color, points)
            
            # Draw some meteor details
            for _ in range(5):
                x = WIDTH // 2 + random.randint(-self.radius//2, self.radius//2)
                y = 100 + random.randint(-self.radius//2, self.radius//2)
                pygame.draw.circle(screen, (100, 100, 100), (x, y), 3)
        
        elif self.name == "Nebula":
            # Create a cloud-like shape for the nebula
            center_x, center_y = WIDTH // 2, 100
            
            # Draw several overlapping circles for cloud effect
            for offset_x, offset_y, size in [
                (-10, -10, 0.7),
                (10, -15, 0.8),
                (15, 5, 0.75),
                (-5, 10, 0.9),
                (0, 0, 1)
            ]:
                pygame.draw.circle(
                    screen, 
                    color, 
                    (center_x + offset_x, center_y + offset_y), 
                    int(self.radius * size)
                )
                
            # Add some stars inside the nebula
            for _ in range(10):
                x = center_x + random.randint(-self.radius, self.radius)
                y = center_y + random.randint(-self.radius, self.radius)
                # Only draw if point is roughly inside the nebula
                if (x - center_x)**2 + (y - center_y)**2 < self.radius**2:
                    pygame.draw.circle(screen, WHITE, (x, y), 2)
        
        elif self.name == "Neutron Star":
            # Draw the star
            pygame.draw.circle(screen, color, (WIDTH // 2, 100), self.radius)
            
            # Draw pulsing rings
            for i in range(3):
                ring_radius = self.radius + 10 + (i * 10)
                pygame.draw.circle(screen, color, (WIDTH // 2, 100), ring_radius, 2)
            
            # Draw core
            pygame.draw.circle(screen, WHITE, (WIDTH // 2, 100), self.radius // 2)
        
        elif self.name == "Supernova":
            # Draw the expanding explosion
            for i in range(3):
                explosion_radius = self.radius - (i * 10)
                color_val = min(255, 150 + i * 50)
                explosion_color = (color_val, 100 - i * 30, 0)
                pygame.draw.circle(screen, explosion_color, (WIDTH // 2, 100), explosion_radius)
            
            # Draw some explosion rays
            for i in range(12):
                angle = i * np.pi / 6
                x1 = WIDTH // 2 + int(self.radius * np.cos(angle))
                y1 = 100 + int(self.radius * np.sin(angle))
                x2 = WIDTH // 2 + int((self.radius + 30) * np.cos(angle))
                y2 = 100 + int((self.radius + 30) * np.sin(angle))
                pygame.draw.line(screen, (255, 200, 0), (x1, y1), (x2, y2), 3)
        
        elif self.name == "Asteroid":
            # Draw irregular asteroid shape
            points = []
            for i in range(10):
                angle = i * np.pi / 5
                r = self.radius * (0.8 + random.random() * 0.4)
                x = WIDTH // 2 + int(r * np.cos(angle))
                y = 100 + int(r * np.sin(angle))
                points.append((x, y))
            pygame.draw.polygon(screen, color, points)
            
            # Draw some crater details
            for _ in range(4):
                x = WIDTH // 2 + random.randint(-self.radius//2, self.radius//2)
                y = 100 + random.randint(-self.radius//2, self.radius//2)
                crater_size = random.randint(4, 8)
                pygame.draw.circle(screen, (50, 50, 50), (x, y), crater_size)
                pygame.draw.circle(screen, (30, 30, 30), (x, y), crater_size - 2)
        
        # Draw health bar
        health_percentage = self.health / self.max_health
        pygame.draw.rect(screen, RED, (WIDTH // 2 - 100, 30, 200, 15))
        pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 100, 30, int(200 * health_percentage), 15))
        
        # Draw enemy name and health
        name_text = font_small.render(self.name, True, WHITE)
        health_text = font_small.render(f"HP: {self.health}/{self.max_health}", True, WHITE)
        screen.blit(name_text, (WIDTH // 2 - 100, 10))
        screen.blit(health_text, (WIDTH // 2 + 30, 10))

# Battle system class
class BattleSystem:
    def __init__(self, player):
        self.player = player
        self.enemy = None
        self.state = "player_turn"  # "player_turn", "enemy_turn", "win", "lose"
        self.message = ""
        self.flash_timer = 0
        self.flash_target = None  # "player" or "enemy"
        self.animation_frame = 0
        
        # Make the battle log text area
        self.log_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 50, 400, 100)
        
        # Menu items
        self.menu_items = ["Blast", "Forcefield", "Fission", "Fusion"]
        self.selected_item = 0
        
        # Animation elements for the space background
        self.stars = []
        self.reset_stars()
    
    def reset_stars(self):
        self.stars = []
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.uniform(0.5, 2.0)
            size = random.randint(1, 3)
            self.stars.append({"x": x, "y": y, "speed": speed, "size": size})
    
    def new_battle(self):
        self.enemy = Enemy(self.player.level)
        self.state = "player_turn"
        self.message = f"A {self.enemy.name} appears in space!"
        self.selected_item = 0
        self.animation_frame = 0
    
    def update(self):
        # Update animations
        self.animation_frame += 1
        
        # Update star positions
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] > HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, WIDTH)
        
        # Update flash effect
        if self.flash_timer > 0:
            self.flash_timer -= 1
    
    def player_action(self, action):
        if self.state != "player_turn":
            return
        
        if action == "Blast":
            damage = self.player.attack()
            self.enemy.health = max(0, self.enemy.health - damage)
            self.message = f"{self.player.name} blasts the {self.enemy.name} for {damage} damage!"
            player_tones["blast"].play()
            
        elif action == "Forcefield":
            defense_bonus = self.player.defend()
            self.message = f"{self.player.name} creates a forcefield, increasing defense by {defense_bonus}!"
            player_tones["forcefield"].play()
            
        elif action == "Fission":
            damage = self.player.fission()
            self.enemy.health = max(0, self.enemy.health - damage)
            self.message = f"{self.player.name} releases fission energy for {damage} damage!"
            player_tones["fission"].play()
            
        elif action == "Fusion":
            heal_amount = self.player.fusion()
            self.message = f"{self.player.name} uses fusion to restore {heal_amount} health!"
            player_tones["fusion"].play()
        
        # Flash effect for enemy
        self.flash_timer = 15
        self.flash_target = "enemy"
        
        # Check win condition
        if self.enemy.health <= 0:
            self.state = "win"
            self.message = f"You defeated the {self.enemy.name}!"
            exp_gained = self.enemy.exp_reward
            self.player.gain_experience(exp_gained)
            self.player.victories += 1
            
            if self.player.victories >= 10:  # Win game after 10 victories
                return "game_won"
            
            return
        
        # Switch to enemy turn after a delay
        pygame.time.delay(500)
        self.state = "enemy_turn"
    
    def enemy_action(self):
        if self.state != "enemy_turn":
            return
        
        action = self.enemy.choose_action()
        
        if action == "attack":
            damage = self.enemy.attack()
            self.player.health = max(0, self.player.health - damage)
            self.message = f"The {self.enemy.name} attacks for {damage} damage!"
            enemy_tones["attack"].play()
            
        elif action == "defend":
            defense_bonus = self.enemy.defend()
            self.message = f"The {self.enemy.name} strengthens its defenses!"
            enemy_tones["defend"].play()
            
        elif action == "special":
            damage = self.enemy.special()
            self.player.health = max(0, self.player.health - damage)
            
            # Special message based on enemy type
            if self.enemy.name == "Black Hole":
                self.message = f"The Black Hole generates gravitational forces for {damage} damage!"
            elif self.enemy.name == "Supernova":
                self.message = f"The Supernova explodes with energy for {damage} damage!"
            else:
                self.message = f"The {self.enemy.name} unleashes a cosmic attack for {damage} damage!"
                
            enemy_tones["special"].play()
            
        elif action == "heal":
            heal_amount = self.enemy.heal()
            self.message = f"The {self.enemy.name} absorbs cosmic energy and recovers {heal_amount} health!"
            enemy_tones["heal"].play()
        
        # Flash effect for player
        self.flash_timer = 15
        self.flash_target = "player"
        
        # Check lose condition
        if self.player.health <= 0:
            self.state = "lose"
            self.message = "You have been defeated!"
            return
        
        # Switch back to player turn after a delay
        pygame.time.delay(500)
        self.state = "player_turn"
    
    def draw(self, screen):
        # Draw stars in the background
        for star in self.stars:
            pygame.draw.circle(screen, WHITE, (int(star["x"]), int(star["y"])), star["size"])
        
        # Draw player and enemy
        should_flash_player = self.flash_timer > 0 and self.flash_target == "player"
        should_flash_enemy = self.flash_timer > 0 and self.flash_target == "enemy"
        
        self.player.draw(screen)
        if self.enemy:
            self.enemy.draw(screen, should_flash_enemy)
        
        # Draw battle log
        pygame.draw.rect(screen, (0, 0, 50), self.log_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 255), self.log_rect, 2, border_radius=5)
        
        # Wrap text to fit in the battle log
        wrapped_text = []
        words = self.message.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            text_width, _ = font_small.size(test_line)
            if text_width < self.log_rect.width - 20:
                line = test_line
            else:
                wrapped_text.append(line)
                line = word + " "
        wrapped_text.append(line)
        
        for i, line in enumerate(wrapped_text):
            text_surface = font_small.render(line, True, WHITE)
            screen.blit(text_surface, (self.log_rect.x + 10, self.log_rect.y + 10 + i * 25))
        
        # Draw menu if it's player's turn
        if self.state == "player_turn":
            menu_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 80, 200, 30)
            for i, item in enumerate(self.menu_items):
                item_rect = pygame.Rect(menu_rect.x, menu_rect.y + i * 30, menu_rect.width, 25)
                
                # Highlight selected item
                if i == self.selected_item:
                    pygame.draw.rect(screen, BLUE, item_rect, border_radius=3)
                else:
                    pygame.draw.rect(screen, (50, 50, 50), item_rect, border_radius=3)
                
                text = font_small.render(item, True, WHITE)
                screen.blit(text, (item_rect.x + 10, item_rect.y + 5))
        
        # Draw status messages for win/lose
        if self.state == "win":
            # Show level up message if applicable
            if self.player.experience >= self.player.exp_to_next_level:
                level_up_text = font_medium.render(f"Level Up! {self.player.name} is now level {self.player.level}!", True, YELLOW)
                screen.blit(level_up_text, (WIDTH // 2 - level_up_text.get_width() // 2, HEIGHT // 2 + 80))
                
                stats_text = font_small.render("Power and Defense increased!", True, WHITE)
                screen.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 120))
            
            # Press space to continue
            continue_text = font_small.render("Press Space to continue", True, WHITE)
            screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 150))
            
        elif self.state == "lose":
            game_over_text = font_medium.render("Game Over", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 + 80))
            
            restart_text = font_small.render("Press Space to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 120))

# Title screen animation
class TitleScreen:
    def __init__(self):
        self.angle = 0
        self.stars = []
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.uniform(0.2, 1.0)
            size = random.randint(1, 3)
            self.stars.append({"x": x, "y": y, "speed": speed, "size": size})
    
    def update(self):
        self.angle += 0.01
        
        # Update star positions
        for star in self.stars:
            star["x"] -= star["speed"]
            if star["x"] < 0:
                star["x"] = WIDTH
star["x"] = WIDTH
                star["y"] = random.randint(0, HEIGHT)
    
    def draw(self, screen):
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(screen, WHITE, (int(star["x"]), int(star["y"])), star["size"])
        
        # Draw animated sun
        sun_x = 320
        sun_y = 240
        sun_radius = 40
        
        # Draw the sun
        pygame.draw.circle(screen, YELLOW, (sun_x, sun_y), sun_radius)
        
        # Draw rotating rays
        for i in range(8):
            angle = self.angle + (i * np.pi / 4)
            x1 = sun_x + int(sun_radius * np.cos(angle))
            y1 = sun_y + int(sun_radius * np.sin(angle))
            x2 = sun_x + int((sun_radius + 20) * np.cos(angle))
            y2 = sun_y + int((sun_radius + 20) * np.sin(angle))
            pygame.draw.line(screen, ORANGE, (x1, y1), (x2, y2), 3)
        
        # Draw title
        title_text = font_large.render("Sun Voyage", True, YELLOW)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw press space message
        if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking effect
            press_text = font_medium.render("Press Space to Play", True, WHITE)
            screen.blit(press_text, (WIDTH // 2 - press_text.get_width() // 2, 400))

# Name input screen
class NameInputScreen:
    def __init__(self):
        self.name = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.stars = []
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.uniform(0.1, 0.5)
            size = random.randint(1, 3)
            self.stars.append({"x": x, "y": y, "speed": speed, "size": size})
    
    def update(self):
        # Cursor blinking
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
        
        # Update star positions
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] > HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, WIDTH)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "done"
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.unicode.isalnum() or event.unicode.isspace():
                if len(self.name) < 15:  # Limit name length
                    self.name += event.unicode
        return None
    
    def draw(self, screen):
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(screen, WHITE, (int(star["x"]), int(star["y"])), star["size"])
        
        # Draw title
        title_text = font_medium.render("Enter Your Name:", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 200))
        
        # Draw name input box
        input_rect = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)
        pygame.draw.rect(screen, (50, 50, 100), input_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 200), input_rect, 2, border_radius=5)
        
        # Draw name and cursor
        display_name = self.name
        if self.cursor_visible:
            display_name += "|"
        
        if not display_name:
            display_name = "Sun"  # Default name
            name_text = font_medium.render(display_name, True, (150, 150, 150))  # Grayed out
        else:
            name_text = font_medium.render(display_name, True, WHITE)
        
        screen.blit(name_text, (input_rect.x + 10, input_rect.y + 10))
        
        # Draw instructions
        instr_text = font_small.render("Press Enter to confirm", True, WHITE)
        screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, 320))

# Intro screen
class IntroScreen:
    def __init__(self, player_name):
        self.player_name = player_name if player_name else "Sun"
        self.timer = 0
        self.done = False
        self.stars = []
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.uniform(0.1, 0.5)
            size = random.randint(1, 3)
            self.stars.append({"x": x, "y": y, "speed": speed, "size": size})
    
    def update(self):
        self.timer += 1
        if self.timer > 180:  # Show for 3 seconds
            self.done = True
        
        # Update star positions
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] > HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, WIDTH)
    
    def draw(self, screen):
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(screen, WHITE, (int(star["x"]), int(star["y"])), star["size"])
        
        # Draw text
        text1 = font_medium.render(f"You are {self.player_name}", True, WHITE)
        text2 = font_medium.render("on drift in endless space.", True, WHITE)
        text3 = font_medium.render("You fight to survive.", True, WHITE)
        
        screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, 200))
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, 250))
        screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, 300))

# End screen
class EndingScreen:
    def __init__(self):
        self.timer = 0
        self.flower_stage = 0
        self.stars = []
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.uniform(0.1, 0.3)
            size = random.randint(1, 3)
            self.stars.append({"x": x, "y": y, "speed": speed, "size": size})
    
    def update(self):
        self.timer += 1
        if self.timer % 60 == 0 and self.flower_stage < 5:
            self.flower_stage += 1
        
        # Update star positions
        for star in self.stars:
            star["x"] += star["speed"] * np.cos(star["y"] * 0.01)
            star["y"] += star["speed"] * np.sin(star["x"] * 0.01)
            if star["y"] < 0 or star["y"] > HEIGHT or star["x"] < 0 or star["x"] > WIDTH:
                star["x"] = random.randint(0, WIDTH)
                star["y"] = random.randint(0, HEIGHT)
    
    def draw(self, screen):
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(screen, WHITE, (int(star["x"]), int(star["y"])), star["size"])
        
        # Draw text
        text = font_medium.render("You reached a perfect galaxy", True, WHITE)
        text2 = font_medium.render("where you stay and create life.", True, WHITE)
        
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, 150))
        
        # Draw flower animation based on stage
        flower_x, flower_y = WIDTH // 2, 350
        
        # Draw stem
        pygame.draw.rect(screen, GREEN, (flower_x - 5, flower_y, 10, 100))
        
        if self.flower_stage >= 1:
            # Draw leaves
            pygame.draw.ellipse(screen, GREEN, (flower_x - 30, flower_y + 60, 25, 15))
            pygame.draw.ellipse(screen, GREEN, (flower_x + 5, flower_y + 40, 25, 15))
        
        if self.flower_stage >= 2:
            # Draw bud
            pygame.draw.circle(screen, (0, 100, 0), (flower_x, flower_y), 15)
        
        if self.flower_stage >= 3:
            # Draw opening bud
            pygame.draw.circle(screen, (200, 100, 200), (flower_x, flower_y), 20)
            pygame.draw.circle(screen, (0, 100, 0), (flower_x, flower_y), 15)
        
        if self.flower_stage >= 4:
            # Draw half-bloomed flower
            for i in range(8):
                angle = i * np.pi / 4
                petal_x = flower_x + int(25 * np.cos(angle))
                petal_y = flower_y + int(25 * np.sin(angle))
                pygame.draw.circle(screen, (200, 100, 200), (petal_x, petal_y), 10)
            pygame.draw.circle(screen, (255, 255, 0), (flower_x, flower_y), 10)
        
        if self.flower_stage >= 5:
            # Draw fully bloomed flower
            for i in range(8):
                angle = i * np.pi / 4
                petal_x = flower_x + int(30 * np.cos(angle))
                petal_y = flower_y + int(30 * np.sin(angle))
                pygame.draw.circle(screen, (255, 100, 255), (petal_x, petal_y), 15)
            pygame.draw.circle(screen, (255, 255, 0), (flower_x, flower_y), 12)
        
        # Draw "Press Space to return to title" text
        if self.timer > 300:  # After 5 seconds
            if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking effect
                restart_text = font_small.render("Press Space to return to title", True, WHITE)
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 500))

# Main game loop
def main():
    # Initialize game state
    game_state = TITLE_SCREEN
    title_screen = TitleScreen()
    name_input = NameInputScreen()
    intro_screen = None
    battle_system = None
    ending_screen = None
    player = None
    
    # Music flags
    title_music_playing = False
    ending_music_playing = False
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle key presses based on game state
            if event.type == pygame.KEYDOWN:
                if game_state == TITLE_SCREEN:
                    if event.key == pygame.K_SPACE:
                        game_state = NAME_INPUT
                        if title_music_playing:
                            title_music.stop()
                            title_music_playing = False
                
                elif game_state == NAME_INPUT:
                    result = name_input.handle_event(event)
                    if result == "done":
                        player_name = name_input.name if name_input.name else "Sun"
                        player = Player(player_name)
                        intro_screen = IntroScreen(player_name)
                        game_state = INTRO_SCREEN
                
                elif game_state == INTRO_SCREEN:
                    # Skip intro with any key
                    if intro_screen.timer > 60:  # Allow skipping after 1 second
                        battle_system = BattleSystem(player)
                        battle_system.new_battle()
                        game_state = BATTLE_SCREEN
                
                elif game_state == BATTLE_SCREEN:
                    if battle_system.state == "player_turn":
                        if event.key == pygame.K_UP:
                            battle_system.selected_item = (battle_system.selected_item - 1) % len(battle_system.menu_items)
                        elif event.key == pygame.K_DOWN:
                            battle_system.selected_item = (battle_system.selected_item + 1) % len(battle_system.menu_items)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            selected_action = battle_system.menu_items[battle_system.selected_item]
                            result = battle_system.player_action(selected_action)
                            if result == "game_won":
                                ending_screen = EndingScreen()
                                game_state = ENDING_SCREEN
                        
                    elif battle_system.state == "win":
                        if event.key == pygame.K_SPACE:
                            battle_system.new_battle()
                    
                    elif battle_system.state == "lose":
                        if event.key == pygame.K_SPACE:
                            # Reset game
                            player = Player(player.name)
                            battle_system = BattleSystem(player)
                            battle_system.new_battle()
                
                elif game_state == ENDING_SCREEN:
                    if event.key == pygame.K_SPACE and ending_screen.timer > 300:
                        game_state = TITLE_SCREEN
                        title_screen = TitleScreen()
                        if ending_music_playing:
                            ending_music.stop()
                            ending_music_playing = False
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Update and draw based on game state
        if game_state == TITLE_SCREEN:
            # Play title music if not already playing
            if not title_music_playing:
                title_music.play(-1)  # Loop the music
                title_music_playing = True
            
            title_screen.update()
            title_screen.draw(screen)
        
        elif game_state == NAME_INPUT:
            name_input.update()
            name_input.draw(screen)
        
        elif game_state == INTRO_SCREEN:
            intro_screen.update()
            intro_screen.draw(screen)
            
            if intro_screen.done:
                battle_system = BattleSystem(player)
                battle_system.new_battle()
                game_state = BATTLE_SCREEN
        
        elif game_state == BATTLE_SCREEN:
            battle_system.update()
            battle_system.draw(screen)
            
            if battle_system.state == "enemy_turn":
                battle_system.enemy_action()
        
        elif game_state == ENDING_SCREEN:
            # Play ending music if not already playing
            if not ending_music_playing:
                ending_music.play(-1)  # Loop the music
                ending_music_playing = True
                
            ending_screen.update()
            ending_screen.draw(screen)
        
        # Update the display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Clean up pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()