import pygame
import random
import sys
import time

pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60

TARGET_SCORE = 200
POINTS_PER_CRYSTAL = 10

DIFFICULTTY_INCREASE_INTERVAL = 15.0
MAX_ASTEROID_SIZE = 160
MIN_ASTEROID_SIZE = 30

RES_SPACESHIP = "resources/spaceship.png"
RES_ASTEROID = "resources/asteroid.png"
RES_CRYSTAL = "resources/energy_crystal.png"
RES_BG = "resources/background.jpg"
RES_CRASH = "resources/clash_sound.wav" # game over
RES_BG_MUSIC = "resources/background_music.wav" # throughout the whole game

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Scavenger - Restart Enabled")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

try:
    spaceship_img_orig = pygame.image.load(RES_SPACESHIP).convert_alpha()
    asteroid_img_orig = pygame.image.load(RES_ASTEROID).convert_alpha()
    crystal_img_orig = pygame.image.load(RES_CRYSTAL).convert_alpha()
    background_img = pygame.image.load(RES_BG).convert()
    crash_sound = pygame.mixer.Sound(RES_CRASH)
    pygame.mixer.music.load(RES_BG_MUSIC)
except Exception as e:
    print("Error loading resources:", e)
    sys.exit()

BACKGROUND = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

font_small = pygame.font.Font(None, 28)
font_large = pygame.font.Font(None, 64)


def run_game():
    pygame.mixer.music.play(-1)

    # base speeds
    spaceship_speed = 5.0
    SPACESHIP = pygame.transform.scale(spaceship_img_orig, (56, 56))
    spaceship_rect = SPACESHIP.get_rect(center=(WIDTH // 2, HEIGHT - 80))

    asteroids = []
    crystals = []

    score = 0
    start_time = time.time()
    last_diff = start_time
    difficulty_level = 1

    asteroid_base_speed = 2.5
    crystal_speed = 2.0
    asteroid_spawn_chance = 0.03
    crystal_spawn_chance = 0.01

    running = True
    game_over_state = None  # "win" or "lose"
    freeze_timer_value = 0  # stops timer on win or lose

    def create_asteroid():
        # base range that shifts upward with difficulty
        base_min = MIN_ASTEROID_SIZE
        base_max = 60

        # gradual shift per difficulty
        shift = difficulty_level * 5

        # adjusted size range
        min_size = min(MAX_ASTEROID_SIZE, base_min + shift)
        max_size = min(MAX_ASTEROID_SIZE, base_max + shift)

        max_size = max(min_size + 1, max_size)

        size = random.randint(min_size, max_size)

        x = random.randint(0, WIDTH - size)
        y = random.randint(-220, -40)

        surf = pygame.transform.scale(asteroid_img_orig, (size, size))
        rect = surf.get_rect(topleft=(x, y))

        # gradual speed increase
        speed = asteroid_base_speed + (difficulty_level * 0.25)

        asteroids.append({"rect": rect, "surf": surf, "size": size, "speed": speed})

    def create_crystal():
        surf = pygame.transform.scale(crystal_img_orig, (28, 28))
        rect = surf.get_rect(
            topleft=(random.randint(0, WIDTH - 28), random.randint(-200, -40))
        )
        crystals.append({"rect": rect, "surf": surf})

    def draw_hud():
        # timer freezes on win/lose
        elapsed = freeze_timer_value if game_over_state else int(time.time() - start_time)

        for i, text in enumerate(
            [f"Score: {score}", f"Target: {TARGET_SCORE}", f"Time: {elapsed}s", f"Difficulty: {difficulty_level}"]
        ):
            surf = font_small.render(text, True, WHITE)
            screen.blit(surf, (10, 10 + 22 * i))

    def increase_difficulty():
        nonlocal difficulty_level, asteroid_base_speed
        difficulty_level += 1
        asteroid_base_speed += 0.5  # gradual increase

    while running:

        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ESC = quit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # R = restart only after game over or win
                if event.key == pygame.K_r and game_over_state:
                    return "restart"

        keys = pygame.key.get_pressed()
        if not game_over_state:
            # movement
            if keys[pygame.K_LEFT] and spaceship_rect.left > 0:
                spaceship_rect.x -= spaceship_speed
            if keys[pygame.K_RIGHT] and spaceship_rect.right < WIDTH:
                spaceship_rect.x += spaceship_speed
            if keys[pygame.K_UP] and spaceship_rect.top > 0:
                spaceship_rect.y -= spaceship_speed
            if keys[pygame.K_DOWN] and spaceship_rect.bottom < HEIGHT:
                spaceship_rect.y += spaceship_speed

        # difficulty increases over time
        now = time.time()
        if now - last_diff > DIFFICULTTY_INCREASE_INTERVAL:
            last_diff = now
            increase_difficulty()

        # spawn objects
        if random.random() < asteroid_spawn_chance:
            create_asteroid()
        if random.random() < crystal_spawn_chance:
            create_crystal()

        # update asteroids
        for ast in asteroids[:]:
            ast["rect"].y += ast["speed"]

            # gradual in-air growing
            if random.random() < 0.0008 * difficulty_level:
                if ast["size"] < MAX_ASTEROID_SIZE:
                    ast["size"] += 1
                    center = ast["rect"].center
                    ast["surf"] = pygame.transform.scale(asteroid_img_orig, (ast["size"], ast["size"]))
                    ast["rect"] = ast["surf"].get_rect(center=center)
                    ast["speed"] += 0.02  # small, gradual increase

            if ast["rect"].top > HEIGHT:
                asteroids.remove(ast)

            # collision = game over
            if not game_over_state and spaceship_rect.colliderect(ast["rect"]):
                pygame.mixer.music.fadeout(800)
                crash_sound.play()
                game_over_state = "lose"
                freeze_timer_value = int(time.time() - start_time)
                game_over_timer = time.time()

        # update crystals
        for c in crystals[:]:
            c["rect"].y += crystal_speed + difficulty_level * 0.1

            if c["rect"].top > HEIGHT:
                crystals.remove(c)

            elif not game_over_state and spaceship_rect.colliderect(c["rect"]):
                crystals.remove(c)
                score += POINTS_PER_CRYSTAL

        # win check
        if not game_over_state and score >= TARGET_SCORE:
            pygame.mixer.music.fadeout(800)
            success_sound.play()
            game_over_state = "win"
            freeze_timer_value = int(time.time() - start_time)
            game_over_timer = time.time()

        screen.blit(BACKGROUND, (0, 0))

        for ast in asteroids:
            screen.blit(ast["surf"], ast["rect"])
        for c in crystals:
            screen.blit(c["surf"], c["rect"])

        screen.blit(SPACESHIP, spaceship_rect)

        draw_hud()

        # Game Over / Win message
        if game_over_state:
            msg = "YOU WON!" if game_over_state == "win" else "GAME OVER"
            text = font_large.render(msg, True, WHITE)
            text2 = font_small.render("Press R to restart or ESC to quit", True, WHITE)

            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 10))

        pygame.display.flip()

    return None

while True:
    result = run_game()
    if result != "restart":
        break

pygame.quit()
sys.exit()
