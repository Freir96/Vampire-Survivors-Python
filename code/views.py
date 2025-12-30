import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


class State:
    def __init__(self, game):
        self.game = game

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class MainMenuView(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 50)
        self.options = ["Start Game", "Settings", "Skill Tree", "Quit"]
        self.selected_index = 0

    def update(self, dt):
        # Handling continuous press might be too fast, stick to events in main or handle here?
        # Ideally input handling should be decoupled or passed in.
        # But for now, we'll check specific keys or rely on a centralized event handler calling a method on state.
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.select_option()

    def select_option(self):
        option = self.options[self.selected_index]
        if option == "Start Game":
            self.game.change_state("game")
        elif option == "Settings":
            self.game.change_state("settings")
        elif option == "Skill Tree":
            self.game.change_state("skill_tree")
        elif option == "Quit":
            self.game.running = False

    def draw(self, surface):
        surface.fill("black")
        # Draw Title
        title_surf = self.font.render("Vampire Survivor Clone", True, "red")
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 100))
        surface.blit(title_surf, title_rect)

        # Draw Options
        for index, option in enumerate(self.options):
            color = "white" if index == self.selected_index else "grey"
            text_surf = self.font.render(option, True, color)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, 250 + index * 60))
            surface.blit(text_surf, text_rect)


class SettingsView(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 40)
        self.options = ["Music Volume", "SFX Volume", "Back"]
        self.selected_index = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)

            elif event.key == pygame.K_LEFT:
                self.adjust_volume(-0.1)
            elif event.key == pygame.K_RIGHT:
                self.adjust_volume(0.1)

            elif event.key == pygame.K_RETURN:
                if self.options[self.selected_index] == "Back":
                    self.game.change_state("main_menu")
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state("main_menu")

    def adjust_volume(self, amount):
        option = self.options[self.selected_index]
        if option == "Music Volume":
            self.game.music_volume = max(0.0, min(1.0, self.game.music_volume + amount))
        if option == "Music Volume":
            self.game.music_volume = max(0.0, min(1.0, self.game.music_volume + amount))
        elif option == "SFX Volume":
            self.game.sfx_volume = max(0.0, min(1.0, self.game.sfx_volume + amount))
        self.game.save_settings()

    def draw(self, surface):
        surface.fill("navy")

        # Title
        title_surf = self.font.render("Settings", True, "white")
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 100))
        surface.blit(title_surf, title_rect)

        # Options
        for index, option in enumerate(self.options):
            color = "white" if index == self.selected_index else "grey"

            if option == "Music Volume":
                text = f"{option}: {int(self.game.music_volume * 100)}%"
            elif option == "SFX Volume":
                text = f"{option}: {int(self.game.sfx_volume * 100)}%"
            else:
                text = option

            text_surf = self.font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, 250 + index * 60))
            surface.blit(text_surf, text_rect)

        help_surf = self.font.render(
            "Use Arrow Keys to Navigate and Adjust", True, "white"
        )
        help_rect = help_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
        surface.blit(help_surf, help_rect)


class SkillTreeView(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 40)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("main_menu")

    def draw(self, surface):
        surface.fill("darkgreen")
        text_surf = self.font.render("Skill Tree - Press ESC to return", True, "white")
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        surface.blit(text_surf, text_rect)


class DeathView(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 50)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_state("main_menu")

    def draw(self, surface):
        surface.fill("darkred")
        text_surf = self.font.render(
            "You Died! Press SPACE to return to Menu", True, "white"
        )
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        surface.blit(text_surf, text_rect)


class ShopView(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 40)
        self.options = [
            {"name": "Heal (50 pts)", "cost": 50, "action": "heal"},
            {"name": "Max HP (+20) (100 pts)", "cost": 100, "action": "max_hp"},
            {"name": "Speed (+50) (80 pts)", "cost": 80, "action": "speed"},
            {"name": "Next Level", "cost": 0, "action": "next_level"},
        ]
        self.selected_index = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.select_option()

    def select_option(self):
        option = self.options[self.selected_index]

        if option["action"] == "next_level":
            self.game.current_level_index += 1
            from levels import LEVEL_DATA  # Deferred import

            # Check if game clear
            if self.game.current_level_index >= len(LEVEL_DATA):
                print("Game Complete!")  # Placeholder for Win Screen
                self.game.change_state("main_menu")
            else:
                self.game.change_state("game")
            return

        if self.game.points >= option["cost"]:
            if option["action"] == "heal":
                self.game.player_stats["max_hp"] = self.game.player_stats[
                    "max_hp"
                ]  # Just refreshing stats? No, Player is recreated.
                # Actually, player instance is gone when we left GameView.
                # So we just update stats. Heal doesn't really work here unless we track current HP separate from max.
                # For simplicity, next level starts with full HP based on Max HP.
                # So "Heal" is useless if we reset HP every level.
                # Let's change Heal to something else or assume HP is persistent?
                # My plan said "Player Recreated".
                # Let's change "Heal" to "Damage (+5) (150 pts)"
                pass
            elif option["action"] == "max_hp":
                self.game.points -= option["cost"]
                self.game.player_stats["max_hp"] += 20
            elif option["action"] == "speed":
                self.game.points -= option["cost"]
                self.game.player_stats["speed"] += 50
        else:
            # Maybe play "cannot buy" sound
            pass

    def draw(self, surface):
        surface.fill("indigo")

        # Title
        title_surf = self.font.render(
            f"Shop - Points: {self.game.points}", True, "gold"
        )
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 100))
        surface.blit(title_surf, title_rect)

        # Options
        for index, option in enumerate(self.options):
            color = "white" if index == self.selected_index else "grey"
            if self.game.points < option["cost"]:
                color = "red" if index == self.selected_index else "darkred"

            text_surf = self.font.render(option["name"], True, color)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, 250 + index * 60))
            surface.blit(text_surf, text_rect)
