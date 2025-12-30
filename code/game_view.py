from settings import WINDOW_WIDTH
import pygame
from os.path import join
from os import walk
from random import choice
from pytmx.util_pygame import load_pygame

from settings import TILE_SIZE
from views import State
from player import Player
from sprites import Bullet, Enemy, Sprite, CollisionSprite
from groups import AllSprites
from levels import LEVEL_DATA


class GameView(State):
    def __init__(self, game):
        super().__init__(game)

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 500

        # Level & Wave Management
        self.level_data = LEVEL_DATA[
            min(self.game.current_level_index, len(LEVEL_DATA) - 1)
        ]
        self.current_wave_index = 0
        self.wave_start_time = pygame.time.get_ticks()
        self.last_spawn_time = 0
        self.spawn_positions = []

        # Audio
        self.shoot_sound = pygame.mixer.Sound(join("audio", "shoot.wav"))
        self.shoot_sound.set_volume(self.game.sfx_volume)
        self.impact_sound = pygame.mixer.Sound(join("audio", "impact.ogg"))
        self.impact_sound.set_volume(self.game.sfx_volume)
        self.music = pygame.mixer.Sound(join("audio", "music.wav"))
        self.music.set_volume(self.game.music_volume)
        # self.music.play(loops = -1)

        # setup
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(
            join("images", "gun", "bullet.png")
        ).convert_alpha()

        folders = list(walk(join("images", "enemies")))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join("images", "enemies", folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(
                    file_names, key=lambda name: int(name.split(".")[0])
                ):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def setup(self):
        map = load_pygame(join("data", "maps", "world.tmx"))

        for x, y, image in map.get_layer_by_name("Ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name("Objects"):
            CollisionSprite(
                (obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites)
            )

        for obj in map.get_layer_by_name("Collisions"):
            CollisionSprite(
                (obj.x, obj.y),
                pygame.Surface((obj.width, obj.height)),
                self.collision_sprites,
            )

        for obj in map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites,
                    self.game.player_stats,
                )
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def gun_shoot(self):
        if self.can_shoot:
            self.shoot_sound.play()
            directions = [
                (1, 0),
                (1, 1),
                (0, 1),
                (-1, 1),
                (-1, 0),
                (-1, -1),
                (0, -1),
                (1, -1),
            ]
            for dx, dy in directions:
                dir = pygame.Vector2(dx, dy).normalize()
                Bullet(
                    self.bullet_surf,
                    self.player.rect.center,
                    dir,
                    (self.all_sprites, self.bullet_sprites),
                )

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
        else:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    bullet, self.enemy_sprites, False, pygame.sprite.collide_mask
                )
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                        self.game.points += sprite.xp_value
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(
            self.player, self.enemy_sprites, False, pygame.sprite.collide_mask
        ):
            if self.player.vulnerable:
                self.player.hp -= 10
                self.player.vulnerable = False
                self.player.hurt_time = pygame.time.get_ticks()
                self.impact_sound.play()

            if self.player.hp <= 0:
                self.game.change_state("death")

    def wave_manager(self):
        # Check if all waves are done
        if self.current_wave_index >= len(self.level_data.waves):
            # Check if all enemies are dead
            if not self.enemy_sprites:
                self.game.change_state("shop")
            return

        current_wave = self.level_data.waves[self.current_wave_index]
        current_time = pygame.time.get_ticks()

        # Check wave duration
        if current_time - self.wave_start_time >= current_wave.duration * 1000:
            self.current_wave_index += 1
            self.wave_start_time = pygame.time.get_ticks()
            if self.current_wave_index < len(self.level_data.waves):
                print(f"Starting Wave {self.current_wave_index + 1}")
            return

        # Spawn enemies
        if current_time - self.last_spawn_time >= current_wave.spawn_interval:
            self.last_spawn_time = current_time
            for _ in range(current_wave.spawn_amount):
                Enemy(
                    choice(self.spawn_positions),
                    self.enemy_frames[current_wave.enemy_type],
                    (self.all_sprites, self.enemy_sprites),
                    self.player,
                    self.collision_sprites,
                )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("main_menu")

    def update(self, dt):
        self.gun_shoot()
        self.all_sprites.update(dt)
        self.bullet_collision()
        self.player_collision()
        self.wave_manager()

    def draw(self, surface):
        surface.fill("black")
        self.all_sprites.draw(self.player.rect.center)

        # Health Bar
        health_bar_width = 200
        health_bar_height = 20
        health_ratio = self.player.hp / self.player.max_hp

        bar_rect = pygame.Rect(10, 10, health_bar_width, health_bar_height)
        fill_rect = pygame.Rect(
            10, 10, health_bar_width * health_ratio, health_bar_height
        )

        pygame.draw.rect(surface, "red", bar_rect)
        pygame.draw.rect(surface, "green", fill_rect)

        # Draw Wave Info
        font = pygame.font.Font(None, 30)

        # Calculate time remaining in current wave
        if self.current_wave_index < len(self.level_data.waves):
            current_wave = self.level_data.waves[self.current_wave_index]
            time_elapsed_ms = pygame.time.get_ticks() - self.wave_start_time
            time_remaining_s = max(0, current_wave.duration - time_elapsed_ms // 1000)
            wave_text = f"Wave {self.current_wave_index + 1}/{len(self.level_data.waves)} - Time: {time_remaining_s}"
        else:
            wave_text = "Wave Complete - Clear Enemies!"

        text_surf = font.render(wave_text, True, "white")
        surface.blit(text_surf, (WINDOW_WIDTH // 2 - text_surf.get_width() // 2, 50))

        # Draw Points
        points_text = font.render(f"Points: {self.game.points}", True, "gold")
        surface.blit(points_text, (10, 40))
