import json
import random
import time
import os
import pygame

# Initialize pygame
pygame.init()

# Screen setup
BASE_WIDTH, BASE_HEIGHT = 160, 120
SCALE = 5
WIDTH, HEIGHT = BASE_WIDTH * SCALE, BASE_HEIGHT * SCALE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lost in the Woods")

# Fonts and colors
font = pygame.font.SysFont("Courier New", 18)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SKY = (90, 140, 200)
FOREST = (30, 70, 50)
GROUND = (50, 110, 70)
STONE = (80, 80, 90)
FIRE = (240, 140, 40)

# Game state
base_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
inventory = []
skills = []
current_scene = "hub"
player_pos = [80, 60]
health = 10
max_health = 10
gold = 100
shrines_completed = 0
guardian_health = 0
demon_health = 0
ganondorf_health = 0
player_attack_ready = True
last_attack_time = 0
attack_cooldown = 500  # milliseconds

# NPCs and interaction rectangles
VILLAGER1_RECT = pygame.Rect(30, 66, 16, 24)
VILLAGER2_RECT = pygame.Rect(130, 66, 16, 24)
SHOP_NPC_RECT = pygame.Rect(80, 66, 16, 24)
TRIAL_ENTER_RECT = pygame.Rect(145, 52, 10, 20)
TEMPLE_NPC_RECT = pygame.Rect(80, 50, 16, 24)
OPEN_WORLD_PORTAL_RECT = pygame.Rect(10, 50, 16, 24)
ENEMY_RECT = pygame.Rect(100, 60, 16, 24)
OPTIONAL_SHRINE_RECT = pygame.Rect(50, 40, 16, 24)

# Define new portal rectangles
GUARDIAN_PORTAL_RECT = pygame.Rect(30, 30, 16, 24)
GANONDORF_PORTAL_RECT = pygame.Rect(70, 30, 16, 24)

MANDATORY_SHRINE1_RECT = pygame.Rect(20, 50, 10, 20)
MANDATORY_SHRINE2_RECT = pygame.Rect(60, 50, 10, 20)
MANDATORY_SHRINE3_RECT = pygame.Rect(100, 50, 10, 20)
POTION_SHOP_RECT = pygame.Rect(80, 66, 16, 24)

# Track completed shrines
completed_shrines = set()

# Add tutorial text
TUTORIAL_TEXT = (
    "Controls:\n"
    "- WASD or Arrow Keys: Move\n"
    "- E: Interact\n"
    "- I: View Inventory\n"
    "- S: Save Game\n"
    "- P: Go to Open World\n"
    "- T: Fight Guardian (requires Master Sword)\n"
    "- G: Fight Ganondorf (requires defeating Guardian)\n"
    "- U: View this tutorial\n"
)

def set_scene(name, spawn=None):
    global current_scene, player_pos
    current_scene = name
    if spawn:
        player_pos[0], player_pos[1] = spawn

def save_game(filename="savegame.json"):
    global inventory, skills, health, gold, shrines_completed
    data = {
        "inventory": inventory,
        "skills": skills,
        "health": health,
        "max_health": max_health,
        "gold": gold,
        "shrines_completed": shrines_completed,
        "current_scene": current_scene,
        "player_pos": player_pos,
    }
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Save failed: {e}")
        return False

def load_game(filename="savegame.json"):
    global inventory, skills, health, gold, shrines_completed, current_scene, player_pos
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        inventory = data.get("inventory", [])
        skills = data.get("skills", [])
        health = data.get("health", 10)
        gold = data.get("gold", 100)
        shrines_completed = data.get("shrines_completed", 0)
        current_scene = data.get("current_scene", "hub")
        player_pos = data.get("player_pos", [80, 60])
        return True
    except Exception as e:
        print(f"Load failed: {e}")
        return False

def draw_text(text):
    render_scene()
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, HEIGHT - 170, WIDTH, 170))
    lines = text.split("\n")
    for i, line in enumerate(lines):
        rendered = font.render(line, True, WHITE)
        screen.blit(rendered, (20, HEIGHT - 160 + i * 24))
    pygame.display.flip()

def talk(text):
    draw_text(text)
    waiting = True
    clock = pygame.time.Clock()
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(30)

def render_scene():
    draw_background(current_scene)
    draw_link(player_pos[0], player_pos[1])
    draw_ui()
    scaled = pygame.transform.scale(base_surface, (WIDTH, HEIGHT))
    screen.blit(scaled, (0, 0))

def draw_ui():
    # Draw hearts at top
    for i in range(max_health):
        x = 5 + i * 8
        if i < health:
            pygame.draw.rect(base_surface, RED, pygame.Rect(x, 5, 6, 6))
        else:
            pygame.draw.rect(base_surface, (80, 80, 80), pygame.Rect(x, 5, 6, 6))
    # Draw gold counter
    gold_text = f"G:{gold}"
    font_small = pygame.font.SysFont("Courier New", 12)
    rendered = font_small.render(gold_text, True, (255, 215, 0))
    # Can't directly blit to base_surface in this context, so we'll draw it in main loop

def draw_background(scene):
    base_surface.fill(SKY)
    pygame.draw.rect(base_surface, GROUND, pygame.Rect(0, BASE_HEIGHT - 36, BASE_WIDTH, 36))

    if scene == "hub":
        # Draw NPCs and shrines in hub
        pygame.draw.rect(base_surface, (150, 100, 80), VILLAGER1_RECT)  # Villager 1
        pygame.draw.rect(base_surface, (150, 100, 80), VILLAGER2_RECT)  # Villager 2
        pygame.draw.rect(base_surface, (200, 180, 100), POTION_SHOP_RECT)  # Potion shop
        pygame.draw.rect(base_surface, (200, 200, 200), MANDATORY_SHRINE1_RECT)  # Mandatory shrine 1
        pygame.draw.rect(base_surface, (200, 200, 200), MANDATORY_SHRINE2_RECT)  # Mandatory shrine 2
        pygame.draw.rect(base_surface, (200, 200, 200), MANDATORY_SHRINE3_RECT)  # Mandatory shrine 3
        pygame.draw.rect(base_surface, (100, 100, 250), pygame.Rect(10, 100, 16, 24))  # Portal to open world
        if shrines_completed >= 3:
            pygame.draw.rect(base_surface, (250, 100, 100), GUARDIAN_PORTAL_RECT)  # Portal to Guardian
        if "Guardian Defeated" in inventory:
            pygame.draw.rect(base_surface, (150, 50, 250), GANONDORF_PORTAL_RECT)  # Portal to Ganondorf

    elif scene == "open_world":
        # Draw open world elements
        pygame.draw.rect(base_surface, (100, 100, 250), OPEN_WORLD_PORTAL_RECT)  # Portal back to hub
        pygame.draw.rect(base_surface, (200, 50, 50), ENEMY_RECT)  # Enemy
        pygame.draw.rect(base_surface, (150, 200, 200), OPTIONAL_SHRINE_RECT)  # Optional shrine

def draw_link(x, y):
    # Draw Link sprite - green tunic with blonde hair
    pygame.draw.rect(base_surface, (255, 255, 0), pygame.Rect(x + 4, y + 1, 8, 3))
    pygame.draw.rect(base_surface, (200, 160, 120), pygame.Rect(x + 3, y + 4, 10, 6))
    pygame.draw.rect(base_surface, (0, 0, 0), pygame.Rect(x + 5, y + 5, 2, 2))
    pygame.draw.rect(base_surface, (0, 0, 0), pygame.Rect(x + 10, y + 5, 2, 2))
    pygame.draw.rect(base_surface, (50, 150, 50), pygame.Rect(x + 2, y + 10, 12, 8))
    pygame.draw.rect(base_surface, (200, 160, 120), pygame.Rect(x, y + 10, 2, 6))
    pygame.draw.rect(base_surface, (200, 160, 120), pygame.Rect(x + 14, y + 10, 2, 6))
    pygame.draw.rect(base_surface, (120, 80, 40), pygame.Rect(x + 3, y + 18, 10, 4))

def update_movement():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_pos[0] = max(0, player_pos[0] - 1)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_pos[0] = min(BASE_WIDTH - 16, player_pos[0] + 1)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_pos[1] = max(0, player_pos[1] - 1)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_pos[1] = min(BASE_HEIGHT - 24, player_pos[1] + 1)

def roam_until_interact(target_rect):
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    talk(f"Inventory: {', '.join(inventory)}\nGold: {gold}\nShrines: {shrines_completed}/3")
                if event.key == pygame.K_s:
                    save_game()
                    talk("Game saved!")
                if event.key == pygame.K_e:
                    player_rect = pygame.Rect(player_pos[0], player_pos[1], 16, 24)
                    if player_rect.colliderect(target_rect):
                        return
        update_movement()
        render_scene()
        pygame.display.flip()
        clock.tick(60)

def get_input(prompt):
    user_text = ""
    clock = pygame.time.Clock()
    while True:
        draw_text(prompt + "\n" + user_text)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return user_text.strip().lower()
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode
        clock.tick(30)

def battle(enemy_name, enemy_health):
    global health, player_attack_ready, last_attack_time
    health_damage_taken = 0
    
    while True:
        draw_text(f"{enemy_name} - HP: {enemy_health}\nYour HP: {health}\n\nPress SPACE to attack\nPress P to use potion")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Player attacks
                    damage = random.randint(2, 5)
                    enemy_health -= damage
                    talk(f"You attack for {damage} damage!")
                    if enemy_health <= 0:
                        talk(f"You defeated {enemy_name}!")
                        return True
                    # Enemy attacks back
                    enemy_damage = random.randint(1, 3)
                    health -= enemy_damage
                    talk(f"{enemy_name} attacks for {enemy_damage} damage!")
                    if health <= 0:
                        talk("You were defeated!")
                        return False
                if event.key == pygame.K_p:
                    health = min(health + 3, max_health)
                    talk("You used a potion!")
                    enemy_damage = random.randint(1, 3)
                    health -= enemy_damage
                    talk(f"{enemy_name} attacks for {enemy_damage} damage!")
                    if health <= 0:
                        talk("You were defeated!")
                        return False

def shrine_battle(shrine_num):
    global shrines_completed, health
    enemy_name = f"Shrine {shrine_num} Guardian"
    if battle(enemy_name, 8):
        shrines_completed += 1
        talk(f"Shrine {shrine_num} complete! ({shrines_completed}/3)")
        if shrines_completed == 3:
            talk("All shrines complete! Master Sword unlocked!")
            if "Master Sword" not in inventory:
                inventory.append("Master Sword")
        return True
    return False

# ===== START GAME MENU =====
draw_text("LOST IN THE WOODS\n\nPress any key to start\nPress L to load game\nPress U for tutorial")
waiting = True
clock = pygame.time.Clock()

while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l and os.path.exists("savegame.json"):
                if load_game():
                    draw_text("Game loaded!")
                    waiting = False
                    break
            elif event.key == pygame.K_u:
                talk(TUTORIAL_TEXT)  # Show tutorial when 'U' is pressed
            else:
                draw_text("Tutorial:\n- WASD to move\n- E to interact\n- I for inventory\n- S to save\n\nComplete 3 shrines to get Master Sword\nThen defeat Ganondorf!")
                waiting = False
    clock.tick(30)

# ===== GAME LOOP =====
set_scene("hub", (80, 60))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                talk(f"Inventory: {', '.join(inventory)}\nHealth: {health}/{max_health}\nGold: {gold}\nShrines: {shrines_completed}/3")
            if event.key == pygame.K_s:
                save_game()
                talk("Game saved!")
            if event.key == pygame.K_p:
                set_scene("open_world", (20, 60))  # Pressing 'P' takes you to the open world
            if event.key == pygame.K_t and "Master Sword" in inventory:
                set_scene("temple", (20, 60))  # Pressing 'T' takes you to the Guardian if you have the Master Sword
                if battle("Guardian", 20):
                    talk("You defeated the Guardian!")
                    inventory.append("Guardian Defeated")
                else:
                    health = max_health
                    talk("You were defeated! Returning to hub...")
                set_scene("hub", (80, 60))
            if event.key == pygame.K_g and "Guardian Defeated" in inventory:
                set_scene("castle", (20, 60))  # Pressing 'G' takes you to fight Ganondorf after defeating the Guardian
                if battle("Ganondorf", 30):
                    talk("You defeated Ganondorf!")
                    talk("CONGRATULATIONS! You saved the realm!")
                    pygame.quit()
                    exit()
                else:
                    health = max_health
                    talk("You were defeated! Returning to hub...")
                set_scene("hub", (80, 60))
            if event.key == pygame.K_e:
                player_rect = pygame.Rect(player_pos[0], player_pos[1], 16, 24)

                if current_scene == "hub":
                    if player_rect.colliderect(VILLAGER1_RECT):
                        talk("Villager: Long ago, a hero saved this land with the Master Sword.")
                    elif player_rect.colliderect(VILLAGER2_RECT):
                        talk("Villager: Press 'G' to fight Ganondorf if you are ready!")
                    elif player_rect.colliderect(POTION_SHOP_RECT):
                        choice = get_input("Shop - Buy potion (10g)? (yes/no)")
                        if choice == "yes" and gold >= 10:
                            gold -= 10
                            health = min(health + 5, max_health)
                            talk("Potion purchased!")
                        elif choice == "yes":
                            talk("Not enough gold!")
                    elif player_rect.colliderect(MANDATORY_SHRINE1_RECT):
                        if 1 in completed_shrines:
                            talk("You have already completed Shrine 1.")
                        else:
                            choice = get_input("Enter Shrine 1? (yes/no)")
                            if choice == "yes":
                                set_scene("shrine1", (20, 80))
                                if not shrine_battle(1):
                                    health = max_health
                                    talk("You were defeated! Returning to hub...")
                                else:
                                    completed_shrines.add(1)
                                    if health == max_health:
                                        gold += 20  # Reward extra gold for full health
                                        talk("You completed Shrine 1 with full health! +20 gold")
                                set_scene("hub", (80, 60))
                    elif player_rect.colliderect(MANDATORY_SHRINE2_RECT):
                        if 2 in completed_shrines:
                            talk("You have already completed Shrine 2.")
                        else:
                            choice = get_input("Enter Shrine 2? (yes/no)")
                            if choice == "yes":
                                set_scene("shrine2", (20, 80))
                                if not shrine_battle(2):
                                    health = max_health
                                    talk("You were defeated! Returning to hub...")
                                else:
                                    completed_shrines.add(2)
                                    if health == max_health:
                                        gold += 20  # Reward extra gold for full health
                                        talk("You completed Shrine 2 with full health! +20 gold")
                                set_scene("hub", (80, 60))
                    elif player_rect.colliderect(MANDATORY_SHRINE3_RECT):
                        if 3 in completed_shrines:
                            talk("You have already completed Shrine 3.")
                        else:
                            choice = get_input("Enter Shrine 3? (yes/no)")
                            if choice == "yes":
                                set_scene("shrine3", (20, 80))
                                if not shrine_battle(3):
                                    health = max_health
                                    talk("You were defeated! Returning to hub...")
                                else:
                                    completed_shrines.add(3)
                                    if health == max_health:
                                        gold += 20  # Reward extra gold for full health
                                        talk("You completed Shrine 3 with full health! +20 gold")
                                set_scene("hub", (80, 60))

                elif current_scene == "open_world":
                    if player_rect.colliderect(OPEN_WORLD_PORTAL_RECT):
                        choice = get_input("Return to the hub? (yes/no)")
                        if choice == "yes":
                            set_scene("hub", (80, 60))
                    elif player_rect.colliderect(ENEMY_RECT):
                        if battle("Wild Beast", 10):
                            talk("You defeated the Wild Beast!")
                        else:
                            health = max_health
                            talk("You were defeated! Returning to hub...")
                            set_scene("hub", (80, 60))
                    elif player_rect.colliderect(OPTIONAL_SHRINE_RECT):
                        choice = get_input("Enter the optional shrine? (yes/no)")
                        if choice == "yes":
                            if shrine_battle("Optional Shrine"):
                                talk("Optional shrine completed!")

    update_movement()
    render_scene()
    pygame.display.flip()
    clock.tick(60)
