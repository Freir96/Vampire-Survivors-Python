from settings import WINDOW_WIDTH, WINDOW_HEIGHT
import pygame
import json
from os.path import join


from views import MainMenuView, SettingsView, SkillTreeView, DeathView
from game_view import GameView


class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Survivor")
        self.clock = pygame.time.Clock()
        self.running = True

        # Settings
        self.music_volume = 0.5
        self.sfx_volume = 0.1
        self.load_settings()

        # Player Data Persistence
        self.points = 0
        self.player_stats = {
            "max_hp": 100,
            "speed": 500,
            "damage": 10,  # Not used yet but good to have
        }
        self.current_level_index = 0

        # States
        self.states = {
            "main_menu": MainMenuView(self),
            "settings": SettingsView(self),
            "skill_tree": SkillTreeView(self),
            "death": DeathView(self),
            "game": None,
            "shop": None,  # Shop created on demand
        }

        self.state = self.states["main_menu"]

    def load_settings(self):
        try:
            with open(join("data", "settings.json"), "r") as f:
                data = json.load(f)
                self.music_volume = data.get("music_volume", 0.5)
                self.sfx_volume = data.get("sfx_volume", 0.1)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_settings(self):
        data = {"music_volume": self.music_volume, "sfx_volume": self.sfx_volume}
        with open(join("data", "settings.json"), "w") as f:
            json.dump(data, f)

    def change_state(self, state_name):
        if state_name == "game":
            self.state = GameView(self)
        elif state_name == "shop":
            from views import (
                ShopView,
            )  # Avoid circular import if possible, or move imports

            self.state = ShopView(self)
        elif state_name in self.states:
            self.state = self.states[state_name]

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if hasattr(self.state, "handle_event"):
                    self.state.handle_event(event)

            # update
            self.state.update(dt)

            # draw
            self.state.draw(self.display_surface)
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
