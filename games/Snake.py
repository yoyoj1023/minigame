import pygame
import sys
import random

# =======================
#     Data Classes
# =======================

class Player:
    def __init__(self, name="Hero", hp=50, atk=10, gold=50):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.gold = gold
        # Default inventory with 1 "Healing Potion"
        self.inventory = {"Healing Potion": 1}

    def is_alive(self):
        return self.hp > 0

class Monster:
    def __init__(self, name, hp, atk, gold_drop):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.gold_drop = gold_drop

    def is_alive(self):
        return self.hp > 0

# =======================
#      Game Settings
# =======================

pygame.init()

# Window size: 5x5 tiles, each tile is 64x64, plus an info panel at the bottom
TILE_SIZE = 64
MAP_WIDTH = 5
MAP_HEIGHT = 5

INFO_PANEL_HEIGHT = 120
WINDOW_WIDTH = MAP_WIDTH * TILE_SIZE
WINDOW_HEIGHT = MAP_HEIGHT * TILE_SIZE + INFO_PANEL_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame RPG Example (English Version)")

# Font (use a default system font)
font = pygame.font.SysFont(None, 24)

# Colors (R, G, B)
COLOR_BG       = (30, 30, 30)      # Background
COLOR_TEXT     = (220, 220, 220)   # General text
COLOR_PLAYER   = (0, 255, 0)       # Player marker
COLOR_TOWN     = (100, 149, 237)   # Town tile
COLOR_DUNGEON  = (139, 69, 19)     # Dungeon tile
COLOR_EMPTY    = (60, 60, 60)      # Empty tile
COLOR_MONSTER  = (255, 0, 0)       # Monster indicator (battle)

clock = pygame.time.Clock()

# =======================
#      Map & Entities
# =======================

# 5x5 grid: '.' for empty, 'T' for town, 'D' for dungeon
GAME_MAP = [
    ['.', 'T', '.', 'T', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', 'D', '.', '.'],
    ['.', '.', '.', '.', 'T'],
    ['.', '.', '.', '.', '.']
]

player_pos = [0, 0]  # Starting position (row, col)
player = Player()

SHOP_ITEMS = {
    "Healing Potion": 10,
    "Strong Potion": 25,
}

MONSTER_LIST = [
    Monster("Slime", 20, 5, 10),
    Monster("Goblin", 30, 8, 15),
    Monster("Bat", 15, 6, 8),
    Monster("Imp", 25, 7, 12),
]

# =======================
#     Game State Enum
# =======================
STATE_MAP = 0      # Moving on map
STATE_TOWN = 1     # In town (shop)
STATE_DUNGEON = 2  # In dungeon (chance to encounter monster)
STATE_BATTLE = 3   # In battle

game_state = STATE_MAP
current_monster = None

# Message lines to display at the bottom
message_lines = []
def add_message(text):
    """
    Add a text message to the message list.
    Keep only the last 5 messages to avoid overflow.
    """
    message_lines.append(text)
    if len(message_lines) > 5:
        message_lines.pop(0)

# =======================
#      Drawing Helpers
# =======================

def draw_map():
    """
    Draw the map tiles and the player marker.
    """
    for r in range(MAP_HEIGHT):
        for c in range(MAP_WIDTH):
            tile = GAME_MAP[r][c]
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            if tile == 'T':
                color = COLOR_TOWN
            elif tile == 'D':
                color = COLOR_DUNGEON
            else:
                color = COLOR_EMPTY
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    # Draw the player
    px = player_pos[1] * TILE_SIZE
    py = player_pos[0] * TILE_SIZE
    pygame.draw.rect(screen, COLOR_PLAYER, (px, py, TILE_SIZE, TILE_SIZE))

def draw_info_panel():
    """
    Draw the bottom info panel, including player's HP, gold, inventory, and messages.
    """
    panel_y = MAP_HEIGHT * TILE_SIZE
    panel_rect = (0, panel_y, WINDOW_WIDTH, INFO_PANEL_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)

    # Player info
    hp_text = f"HP: {player.hp}/{player.max_hp}"
    gold_text = f"GOLD: {player.gold}"
    inv_text = "INVENTORY: " + ", ".join([f"{k}x{v}" for k, v in player.inventory.items()])

    # Draw the text
    draw_text(hp_text, 10, panel_y + 10, COLOR_TEXT)
    draw_text(gold_text, 150, panel_y + 10, COLOR_TEXT)
    draw_text(inv_text, 10, panel_y + 35, COLOR_TEXT)

    # Draw the message lines
    line_y = panel_y + 60
    for line in message_lines:
        draw_text(line, 10, line_y, COLOR_TEXT)
        line_y += 20

def draw_battle(monster):
    """
    Draw a simple battle screen: monster in the center, both HP displayed.
    """
    pygame.draw.rect(screen, COLOR_BG, (0, 0, WINDOW_WIDTH, MAP_HEIGHT*TILE_SIZE))

    # Monster (red square)
    mx = WINDOW_WIDTH // 2 - TILE_SIZE // 2
    my = (MAP_HEIGHT * TILE_SIZE) // 2 - TILE_SIZE // 2
    pygame.draw.rect(screen, COLOR_MONSTER, (mx, my, TILE_SIZE, TILE_SIZE))

    # Monster info
    draw_text(f"{monster.name} HP: {monster.hp}/{monster.max_hp}", mx - 20, my - 30, COLOR_TEXT)
    # Player info
    draw_text(f"{player.name} HP: {player.hp}/{player.max_hp}", 10, 10, COLOR_TEXT)

def draw_text(text, x, y, color=(255,255,255)):
    """
    Render text at (x,y).
    """
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

# =======================
#       Game Logic
# =======================

def move_player(drow, dcol):
    """
    Attempt to move the player on the map.
    """
    new_r = player_pos[0] + drow
    new_c = player_pos[1] + dcol
    if 0 <= new_r < MAP_HEIGHT and 0 <= new_c < MAP_WIDTH:
        player_pos[0] = new_r
        player_pos[1] = new_c

def check_tile_event():
    """
    After moving, check the current tile and possibly change game state.
    """
    global game_state
    r, c = player_pos
    tile = GAME_MAP[r][c]
    if tile == 'T':
        add_message("You arrived at a Town. (Press 1/2 to buy items, ESC to leave)")
        game_state = STATE_TOWN
    elif tile == 'D':
        add_message("You stepped into a Dungeon...")
        game_state = STATE_DUNGEON
    else:
        game_state = STATE_MAP

def enter_dungeon():
    """
    In the dungeon: 80% chance to encounter a monster. If encountered, switch to battle.
    """
    global game_state, current_monster
    if random.random() < 0.8:
        current_monster = Monster(*random.choice([
            ("Slime", 20, 5, 10),
            ("Goblin", 30, 8, 15),
            ("Bat", 15, 6, 8),
            ("Imp", 25, 7, 12),
        ]))
        add_message(f"A wild {current_monster.name} appears! (Battle...)")
        game_state = STATE_BATTLE
    else:
        add_message("No monsters here...")
        game_state = STATE_MAP

def battle(monster, command):
    """
    Battle logic.
    command can be:
       '1' -> attack
       '2' -> use item
       '3' -> run away
    """
    global game_state

    if command == '1':
        # Attack
        damage_to_monster = player.atk
        monster.hp -= damage_to_monster
        add_message(f"You attacked {monster.name} for {damage_to_monster} damage.")

        # Monster counter-attack if it's still alive
        if monster.is_alive():
            damage_to_player = monster.atk
            player.hp -= damage_to_player
            add_message(f"{monster.name} hit you for {damage_to_player} damage.")

    elif command == '2':
        # Use item
        use_item_in_battle()
    elif command == '3':
        # Run away
        add_message("You successfully ran away!")
        game_state = STATE_MAP
        return

    # Check battle end conditions
    if not monster.is_alive():
        add_message(f"You defeated {monster.name} and gained {monster.gold_drop} gold!")
        player.gold += monster.gold_drop
        game_state = STATE_MAP
    elif not player.is_alive():
        add_message(f"You were defeated by {monster.name}...")
        # For simplicity, just switch back to map state
        # In a real game, you might end the game or reload from checkpoint
        game_state = STATE_MAP

def use_item_in_battle():
    """
    Example: tries to use a 'Strong Potion' if available, otherwise use a 'Healing Potion'.
    """
    if "Strong Potion" in player.inventory and player.inventory["Strong Potion"] > 0:
        heal_amount = 40
        player.hp = min(player.hp + heal_amount, player.max_hp)
        player.inventory["Strong Potion"] -= 1
        if player.inventory["Strong Potion"] <= 0:
            del player.inventory["Strong Potion"]
        add_message(f"You used a Strong Potion and restored {heal_amount} HP.")
    elif "Healing Potion" in player.inventory and player.inventory["Healing Potion"] > 0:
        heal_amount = 20
        player.hp = min(player.hp + heal_amount, player.max_hp)
        player.inventory["Healing Potion"] -= 1
        if player.inventory["Healing Potion"] <= 0:
            del player.inventory["Healing Potion"]
        add_message(f"You used a Healing Potion and restored {heal_amount} HP.")
    else:
        add_message("You have no potions to use!")

def buy_item(item_name):
    """
    Attempt to purchase an item in town.
    """
    price = SHOP_ITEMS[item_name]
    if player.gold >= price:
        player.gold -= price
        if item_name in player.inventory:
            player.inventory[item_name] += 1
        else:
            player.inventory[item_name] = 1
        add_message(f"You bought a {item_name} for {price} gold.")
    else:
        add_message("Not enough gold to buy this item.")

# =======================
#     Main Game Loop
# =======================
def main():
    global game_state

    add_message("Game start! Use WASD or arrow keys to move, Q to quit.")

    running = True
    while running:
        clock.tick(30)  # 30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Q to quit
                if event.key == pygame.K_q:
                    running = False

                # Handle states
                if game_state == STATE_MAP:
                    # Movement on the map
                    if event.key in (pygame.K_w, pygame.K_UP):
                        move_player(-1, 0)
                        check_tile_event()
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        move_player(1, 0)
                        check_tile_event()
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        move_player(0, -1)
                        check_tile_event()
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        move_player(0, 1)
                        check_tile_event()

                elif game_state == STATE_TOWN:
                    # Town shop: 1 -> Healing Potion, 2 -> Strong Potion, ESC -> leave
                    if event.key == pygame.K_1:
                        buy_item("Healing Potion")
                    elif event.key == pygame.K_2:
                        buy_item("Strong Potion")
                    elif event.key == pygame.K_ESCAPE:
                        add_message("You left the town.")
                        game_state = STATE_MAP

                elif game_state == STATE_DUNGEON:
                    # Trigger dungeon encounter once
                    enter_dungeon()

                elif game_state == STATE_BATTLE and current_monster:
                    # Battle commands: 1=Attack, 2=Use item, 3=Run
                    if event.key == pygame.K_1:
                        battle(current_monster, '1')
                    elif event.key == pygame.K_2:
                        battle(current_monster, '2')
                    elif event.key == pygame.K_3:
                        battle(current_monster, '3')

        # Drawing
        screen.fill(COLOR_BG)

        if game_state in (STATE_MAP, STATE_TOWN, STATE_DUNGEON):
            draw_map()
        elif game_state == STATE_BATTLE and current_monster:
            draw_battle(current_monster)

        draw_info_panel()
        pygame.display.flip()

        # Check if player is dead
        if player.hp <= 0:
            add_message("Your hero has fallen... Game Over.")
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
