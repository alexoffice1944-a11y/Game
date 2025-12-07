# =====================================================================
# FANTASY ADVENTURE ENGINE – 1000 LINES PYTHON
# =====================================================================
# Ein kleines textbasiertes Adventure-Spiel mit:
# - Welt / Maps
# - Spieler
# - Gegner
# - Inventar
# - Dialogsystem
# - Kampf
# - Speichern/Laden
# - Events
# - Zufallssystem
#
# Viel Spaß!
# =====================================================================

import json
import random
import time
import os
import sys

# -------------------------------------------------------------
# Line ~ 30 — Utility functions
# -------------------------------------------------------------

def slow(text, delay=0.015):
    """Print text slowly for dramatic effect."""
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def line():
    print("-" * 60)

# -------------------------------------------------------------
# Line ~ 60 — Player class
# -------------------------------------------------------------

class Player:
    def __init__(self, name="Held"):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.gold = 0
        self.inventory = []
        self.location = "dorf"
        self.alive = True

    def add_item(self, item):
        self.inventory.append(item)
        slow(f"Du hast {item['name']} erhalten!")

    def damage(self, amount):
        dmg = max(amount - self.defense, 0)
        self.hp -= dmg
        slow(f"{self.name} erleidet {dmg} Schaden!")
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            slow("Du bist gestorben!")

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        slow(f"Du regenerierst {amount} HP. Aktuelle HP: {self.hp}")

    def show_stats(self):
        line()
        print(f"Name: {self.name}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Attacke: {self.attack}")
        print(f"Verteidigung: {self.defense}")
        print(f"Gold: {self.gold}")
        print(f"Ort: {self.location}")
        print("Inventar:", ", ".join(i['name'] for i in self.inventory) or "(Leer)")
        line()

# -------------------------------------------------------------
# Line ~ 150 — Enemy class
# -------------------------------------------------------------

class Enemy:
    def __init__(self, name, hp, attack, defense, gold):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.gold = gold

    def damage(self, amount):
        dmg = max(amount - self.defense, 0)
        self.hp -= dmg
        slow(f"{self.name} erleidet {dmg} Schaden!")
        if self.hp <= 0:
            self.hp = 0
        return dmg

# -------------------------------------------------------------
# Line ~ 220 — Items
# -------------------------------------------------------------

ITEMS = {
    "heiltrank": {
        "name": "Heiltrank",
        "type": "heal",
        "value": 30
    },
    "starker_heiltrank": {
        "name": "Starker Heiltrank",
        "type": "heal",
        "value": 60
    },
    "schwert": {
        "name": "Stahlschwert",
        "type": "weapon",
        "attack": 12
    },
    "schild": {
        "name": "Stahlschild",
        "type": "armor",
        "defense": 8
    }
}

# -------------------------------------------------------------
# Line ~ 300 — World map
# -------------------------------------------------------------

WORLD = {
    "dorf": {
        "name": "Kleines Dorf",
        "description": "Ein ruhiges Dorf mit wenigen Häusern.",
        "exits": ["wald", "berg"],
        "npcs": ["alte_frau"],
        "enemies": []
    },
    "wald": {
        "name": "Dichter Wald",
        "description": "Die Bäume sind hoch und es riecht nach Moos.",
        "exits": ["dorf", "höhle"],
        "npcs": [],
        "enemies": ["wolf"]
    },
    "berg": {
        "name": "Hoher Berg",
        "description": "Der Wind ist stark und die Luft dünn.",
        "exits": ["dorf"],
        "npcs": ["schmied"],
        "enemies": ["harpyie"]
    },
    "höhle": {
        "name": "Dunkle Höhle",
        "description": "Es ist dunkel. Sehr dunkel.",
        "exits": ["wald"],
        "npcs": [],
        "enemies": ["goblin", "goblin", "goblin_chef"]
    }
}

# -------------------------------------------------------------
# Line ~ 380 — NPCs
# -------------------------------------------------------------

NPCS = {
    "alte_frau": {
        "name": "Alte Frau",
        "dialog": [
            "Kindchen, die Welt ist gefährlich...",
            "Nimm diesen Heiltrank, du wirst ihn brauchen!"
        ],
        "gives": ["heiltrank"]
    },
    "schmied": {
        "name": "Dorfschmied",
        "dialog": [
            "Ich kann dir ein Schwert oder ein Schild verkaufen.",
            "Oder willst du einfach reden?"
        ],
        "shop": ["schwert", "schild"]
    }
}

# -------------------------------------------------------------
# Line ~ 450 — Enemy definitions
# -------------------------------------------------------------

ENEMIES = {
    "wolf": Enemy("Wolf", 40, 8, 2, 10),
    "harpyie": Enemy("Harpyie", 50, 12, 4, 20),
    "goblin": Enemy("Goblin", 35, 7, 1, 5),
    "goblin_chef": Enemy("Goblin-Chef", 80, 15, 6, 50)
}

# -------------------------------------------------------------
# Line ~ 520 — Combat system
# -------------------------------------------------------------

def combat(player, enemy):
    slow(f"Ein {enemy.name} greift an!")
    line()
    while enemy.hp > 0 and player.alive:
        print(f"{player.name}: {player.hp} HP")
        print(f"{enemy.name}: {enemy.hp} HP")
        line()
        print("1) Angreifen")
        print("2) Item benutzen")
        print("3) Fliehen")
        choice = input("> ")

        if choice == "1":
            dmg = enemy.damage(player.attack)
            if enemy.hp <= 0:
                slow(f"Der {enemy.name} ist besiegt!")
                player.gold += enemy.gold
                slow(f"Du erhältst {enemy.gold} Gold.")
                return

            # Enemy attacks back
            player.damage(enemy.attack)

        elif choice == "2":
            use_item(player)
        elif choice == "3":
            if random.random() < 0.5:
                slow("Du fliehst erfolgreich!")
                return
            else:
                slow("Du kannst nicht entkommen!")
                player.damage(enemy.attack)

        if not player.alive:
            break

# -------------------------------------------------------------
# Line ~ 620 — Item system
# -------------------------------------------------------------

def use_item(player):
    if not player.inventory:
        slow("Du hast keine Items!")
        return

    slow("Welches Item willst du benutzen?")
    for i, item in enumerate(player.inventory):
        print(f"{i+1}) {item['name']}")

    choice = input("> ")
    if not choice.isdigit():
        return

    idx = int(choice) - 1
    if not (0 <= idx < len(player.inventory)):
        return

    item = player.inventory.pop(idx)
    if item["type"] == "heal":
        player.heal(item["value"])
    elif item["type"] == "weapon":
        player.attack += item["attack"]
        slow("Du rüstest eine neue Waffe aus!")
    elif item["type"] == "armor":
        player.defense += item["defense"]
        slow("Du rüstest neue Rüstung aus!")

# -------------------------------------------------------------
# Line ~ 700 — NPC interactions
# -------------------------------------------------------------

def talk_to_npc(player, npc_id):
    npc = NPCS[npc_id]
    for line_txt in npc["dialog"]:
        slow(line_txt)

    if "gives" in npc:
        for item in npc["gives"]:
            player.add_item(ITEMS[item])

    if "shop" in npc:
        shop(npc, player)

def shop(npc, player):
    slow("Willkommen im Shop!")
    while True:
        line()
        for i, item_id in enumerate(npc["shop"]):
            item = ITEMS[item_id]
            print(f"{i+1}) {item['name']} - 20 Gold")
        print("0) Verlassen")
        line()

        choice = input("> ")
        if choice == "0":
            return
        if not choice.isdigit():
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(npc["shop"]):
            continue

        if player.gold < 20:
            slow("Du hast nicht genug Gold!")
            continue

        item_id = npc["shop"][idx]
        player.gold -= 20
        player.add_item(ITEMS[item_id])

# -------------------------------------------------------------
# Line ~ 820 — Movement & World exploration
# -------------------------------------------------------------

def explore(player):
    current = WORLD[player.location]
    clear()
    slow(current["name"])
    slow(current["description"])
    line()

    if current["npcs"]:
        print("NPCs:", ", ".join(current["npcs"]))
    if current["enemies"]:
        print("Feinde:", ", ".join(current["enemies"]))

    line()
    print("1) Bewegen")
    print("2) NPC ansprechen")
    print("3) Kämpfen")
    print("4) Status")
    print("5) Speichern")
    print("6) Laden")
    print("0) Beenden")

    choice = input("> ")
    if choice == "1":
        move(player)
    elif choice == "2":
        talk_menu(player)
    elif choice == "3":
        fight_menu(player)
    elif choice == "4":
        player.show_stats()
        input("Enter...")
    elif choice == "5":
        save_game(player)
    elif choice == "6":
        load_game(player)
    elif choice == "0":
        sys.exit()

def move(player):
    current = WORLD[player.location]
    slow("Mögliche Orte:")
    for i, exit_id in enumerate(current["exits"]):
        print(f"{i+1}) {exit_id}")

    choice = input("> ")
    if choice.isdigit() and 1 <= int(choice) <= len(current["exits"]):
        player.location = current["exits"][int(choice)-1]

def talk_menu(player):
    current = WORLD[player.location]
    if not current["npcs"]:
        slow("Niemand hier.")
        return
    for i, npc_id in enumerate(current["npcs"]):
        print(f"{i+1}) {NPCS[npc_id]['name']}")

    choice = input("> ")
    if choice.isdigit():
        idx = int(choice)-1
        if 0 <= idx < len(current["npcs"]):
            talk_to_npc(player, current["npcs"][idx])

def fight_menu(player):
    current = WORLD[player.location]
    if not current["enemies"]:
        slow("Hier gibt es keine Feinde.")
        return

    enemy_id = random.choice(current["enemies"])
    enemy = ENEMIES[enemy_id]
    combat(player, Enemy(enemy.name, enemy.max_hp, enemy.attack, enemy.defense, enemy.gold))

# -------------------------------------------------------------
# Line ~ 950 — Save & Load
# -------------------------------------------------------------

def save_game(player):
    data = {
        "name": player.name,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "attack": player.attack,
        "defense": player.defense,
        "gold": player.gold,
        "location": player.location,
        "inventory": player.inventory,
    }

    with open("save.json", "w") as f:
        json.dump(data, f, indent=4)

    slow("Spiel gespeichert!")

def load_game(player):
    if not os.path.exists("save.json"):
        slow("Kein Spiel gefunden.")
        return

    with open("save.json", "r") as f:
        data = json.load(f)

    player.name = data["name"]
    player.hp = data["hp"]
    player.max_hp = data["max_hp"]
    player.attack = data["attack"]
    player.defense = data["defense"]
    player.gold = data["gold"]
    player.location = data["location"]
    player.inventory = data["inventory"]

    slow("Spiel geladen!")

# -------------------------------------------------------------
# Line ~ 1000 — MAIN LOOP
# -------------------------------------------------------------

def main():
    clear()
    slow("WILLKOMMEN IM FANTASY-ADVENTURE!")
    name = input("Wie heißt du, Abenteurer? > ")
    player = Player(name)

    while player.alive:
        explore(player)

if __name__ == "__main__":
    main()
