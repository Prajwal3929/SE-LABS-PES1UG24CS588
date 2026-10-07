import os
import pygame
from .player import Player
from .obstacle import Obstacle

# Color Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (20, 24, 38)
GROUND_COLOR = (70, 80, 95)
PLAYER_COLOR = (0, 200, 255)
PLAYER_BORDER = (0, 140, 220)
OBSTACLE_COLOR = (240, 70, 70)
OBSTACLE_BORDER = (180, 40, 40)
TEXT_COLOR = (240, 245, 250)
ACCENT_COLOR = (255, 215, 0)
CARD_BG = (35, 42, 60, 230)

DIFFICULTIES = {
    "Easy": {
        "start_speed": 4.5,
        "spawn_interval": 85,
        "speed_increase": 0.0015,
        "max_speed": 9.0
    },
    "Medium": {
        "start_speed": 6.0,
        "spawn_interval": 70,
        "speed_increase": 0.003,
        "max_speed": 12.0
    },
    "Hard": {
        "start_speed": 8.5,
        "spawn_interval": 50,
        "speed_increase": 0.005,
        "max_speed": 15.0
    }
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 50

        self.player = Player(80, self.ground_y)

        # State management
        self.state = "MENU"  # MENU, PLAYING, GAME_OVER
        self.difficulty = "Medium"
        
        self.high_score = 0
        self.score = 0
        self.distance = 0
        
        # Setup fonts
        self.title_font = pygame.font.SysFont("Arial", 38, bold=True)
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18)

        # Task 4: Audio Setup
        self.sounds = {}
        self._init_sounds()

        # Apply default difficulty settings
        self.reset_game(self.difficulty)
        self.state = "MENU"

    def _init_sounds(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            sound_files = {
                "jump": "assets/sounds/jump.wav",
                "score": "assets/sounds/score.wav",
                "game_over": "assets/sounds/game_over.wav"
            }
            
            for key, path in sound_files.items():
                if os.path.exists(path):
                    self.sounds[key] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Audio system notice: {e}")

    def play_sound(self, name):
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    def reset_game(self, difficulty="Medium"):
        self.difficulty = difficulty
        config = DIFFICULTIES[self.difficulty]

        self.speed = config["start_speed"]
        self.speed_increase_per_frame = config["speed_increase"]
        self.max_speed = config["max_speed"]
        self.spawn_interval = config["spawn_interval"]

        self._spawn_timer = 0
        self.obstacles = []
        self.player.reset()
        self.score = 0
        self.distance = 0
        self.state = "PLAYING"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "MENU":
                if event.key == pygame.K_e:
                    self.reset_game("Easy")
                elif event.key == pygame.K_m:
                    self.reset_game("Medium")
                elif event.key == pygame.K_h:
                    self.reset_game("Hard")
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.reset_game(self.difficulty)
                    
            elif self.state == "PLAYING":
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.player.jump():
                        self.play_sound("jump")

            elif self.state == "GAME_OVER":
                if event.key == pygame.K_e:
                    self.reset_game("Easy")
                elif event.key == pygame.K_m:
                    self.reset_game("Medium")
                elif event.key == pygame.K_h:
                    self.reset_game("Hard")
                elif event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    self.reset_game(self.difficulty)
                elif event.key == pygame.K_q:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.state in ("MENU", "GAME_OVER"):
                for diff, rect in self.diff_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self.reset_game(diff)
                        return
                if self.state == "GAME_OVER" and getattr(self, "replay_rect", None) and self.replay_rect.collidepoint(mouse_pos):
                    self.reset_game(self.difficulty)

    def handle_input(self):
        pass

    def check_swept_collision(self, player, obstacle):
        """
        Task 1: Continuous Swept Bounding Box Collision Detection
        Checks if player box intersects obstacle's path moved during the frame.
        """
        p_rect = player.rect()

        # Vertical overlap check
        if p_rect.bottom <= obstacle.y or p_rect.top >= obstacle.y + obstacle.height:
            return False

        # Swept horizontal interval covered by obstacle this frame
        swept_left = min(obstacle.prev_x, obstacle.x)
        swept_right = max(obstacle.prev_x + obstacle.width, obstacle.x + obstacle.width)

        # Check overlap with player horizontal range
        player_left = player.x
        player_right = player.x + player.width

        return (swept_right >= player_left) and (swept_left <= player_right)

    def update(self):
        if self.state != "PLAYING":
            return

        # Task 1: Cap max speed to remain fair & physics-stable
        if self.speed < self.max_speed:
            self.speed = min(self.max_speed, self.speed + self.speed_increase_per_frame)

        self.player.update()

        # Obstacle spawning
        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(Obstacle(self.width, self.ground_y, self.speed))

        # Update obstacle positions
        for obstacle in self.obstacles:
            obstacle.speed = self.speed
            obstacle.move()

        # Task 1: Continuous collision check
        for obstacle in self.obstacles:
            if self.check_swept_collision(self.player, obstacle):
                self.state = "GAME_OVER"
                if self.score > self.high_score:
                    self.high_score = self.score
                self.play_sound("game_over")
                return

        # Task 4: Scoring check with sound
        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1
                self.play_sound("score")

        # Cleanup offscreen obstacles
        self.obstacles = [o for o in self.obstacles if not o.off_screen()]
        self.distance += self.speed

    def render(self, screen):
        # Draw background and ground
        screen.fill(DARK_BG)
        pygame.draw.rect(screen, GROUND_COLOR, (0, self.ground_y, self.width, self.height - self.ground_y))
        pygame.draw.line(screen, ACCENT_COLOR, (0, self.ground_y), (self.width, self.ground_y), 3)

        # Draw Player
        p_rect = self.player.rect()
        pygame.draw.rect(screen, PLAYER_COLOR, p_rect, border_radius=4)
        pygame.draw.rect(screen, PLAYER_BORDER, p_rect, width=2, border_radius=4)

        # Draw Obstacles
        for obstacle in self.obstacles:
            o_rect = obstacle.rect()
            pygame.draw.rect(screen, OBSTACLE_COLOR, o_rect, border_radius=3)
            pygame.draw.rect(screen, OBSTACLE_BORDER, o_rect, width=2, border_radius=3)

        # Draw Score HUD
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        high_text = self.small_font.render(f"High: {self.high_score}", True, ACCENT_COLOR)
        diff_text = self.small_font.render(f"Mode: {self.difficulty}", True, TEXT_COLOR)
        
        screen.blit(score_text, (15, 10))
        screen.blit(high_text, (15, 40))
        screen.blit(diff_text, (self.width - 120, 15))

        # Task 2 & Task 3: Menu and Game Over Screens
        if self.state == "MENU":
            self.render_menu_screen(screen)
        elif self.state == "GAME_OVER":
            self.render_game_over_screen(screen)

    def render_menu_screen(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 210))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("ENDLESS RUNNER", True, ACCENT_COLOR)
        subtitle = self.small_font.render("Press SPACE to Start or Select Difficulty:", True, TEXT_COLOR)
        
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))
        screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 120))

        self.diff_rects = {}
        diffs = ["Easy", "Medium", "Hard"]
        btn_width, btn_height = 130, 45
        start_x = self.width // 2 - (len(diffs) * (btn_width + 15)) // 2

        for i, diff in enumerate(diffs):
            x = start_x + i * (btn_width + 15)
            y = 170
            rect = pygame.Rect(x, y, btn_width, btn_height)
            self.diff_rects[diff] = rect
            
            is_active = (self.difficulty == diff)
            bg_col = (50, 120, 200) if is_active else (40, 50, 70)
            border_col = ACCENT_COLOR if is_active else (80, 90, 110)

            pygame.draw.rect(screen, bg_col, rect, border_radius=6)
            pygame.draw.rect(screen, border_col, rect, width=2 if not is_active else 3, border_radius=6)

            txt = self.font.render(f"[{diff[0]}] {diff}", True, WHITE)
            screen.blit(txt, (x + btn_width//2 - txt.get_width()//2, y + btn_height//2 - txt.get_height()//2))

        controls_txt = self.small_font.render("Controls: SPACE / UP / W to Jump | Q to Quit", True, (170, 185, 200))
        screen.blit(controls_txt, (self.width // 2 - controls_txt.get_width() // 2, 280))

    def render_game_over_screen(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((15, 10, 15, 215))
        screen.blit(overlay, (0, 0))

        # Game Over Card
        card = pygame.Rect(self.width // 2 - 220, 30, 440, 340)
        card_surface = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
        card_surface.fill(CARD_BG)
        screen.blit(card_surface, (card.x, card.y))
        pygame.draw.rect(screen, OBSTACLE_COLOR, card, width=2, border_radius=10)

        go_title = self.title_font.render("GAME OVER", True, OBSTACLE_COLOR)
        score_info = self.font.render(f"Final Score: {self.score}   |   Best: {self.high_score}", True, TEXT_COLOR)
        screen.blit(go_title, (self.width // 2 - go_title.get_width() // 2, 50))
        screen.blit(score_info, (self.width // 2 - score_info.get_width() // 2, 105))

        # Difficulty Selection Buttons
        prompt = self.small_font.render("Select Difficulty to Play Again:", True, (200, 210, 225))
        screen.blit(prompt, (self.width // 2 - prompt.get_width() // 2, 155))

        self.diff_rects = {}
        diffs = ["Easy", "Medium", "Hard"]
        btn_width, btn_height = 110, 40
        start_x = self.width // 2 - (len(diffs) * (btn_width + 12)) // 2

        for i, diff in enumerate(diffs):
            x = start_x + i * (btn_width + 12)
            y = 190
            rect = pygame.Rect(x, y, btn_width, btn_height)
            self.diff_rects[diff] = rect
            
            is_active = (self.difficulty == diff)
            bg_col = (0, 150, 120) if is_active else (45, 55, 75)
            border_col = ACCENT_COLOR if is_active else (80, 95, 115)

            pygame.draw.rect(screen, bg_col, rect, border_radius=6)
            pygame.draw.rect(screen, border_col, rect, width=2 if not is_active else 3, border_radius=6)

            txt = self.font.render(f"[{diff[0]}] {diff}", True, WHITE)
            screen.blit(txt, (x + btn_width//2 - txt.get_width()//2, y + btn_height//2 - txt.get_height()//2))

        # Replay and Quit Instructions
        replay_rect = pygame.Rect(self.width // 2 - 120, 255, 240, 40)
        self.replay_rect = replay_rect
        pygame.draw.rect(screen, (30, 140, 70), replay_rect, border_radius=6)
        pygame.draw.rect(screen, ACCENT_COLOR, replay_rect, width=2, border_radius=6)

        replay_txt = self.font.render("Press R to Replay", True, WHITE)
        screen.blit(replay_txt, (replay_rect.x + replay_rect.width//2 - replay_txt.get_width()//2, 
                                 replay_rect.y + replay_rect.height//2 - replay_txt.get_height()//2))

        quit_txt = self.small_font.render("Press Q to Quit Game", True, (180, 190, 200))
        screen.blit(quit_txt, (self.width // 2 - quit_txt.get_width() // 2, 315))
