import pygame as pg
import random
import settings


is_Game_Over = False

# Set up the ball
ball_pos = [400, 300]
ball_vel = [3, 3]
ball_rect = pg.Rect(ball_pos[0], ball_pos[1], 20, 20)


# Set up the paddles
player_Pos = [0, 300]
player_rect = pg.Rect(player_Pos[0], player_Pos[1], 20, 100)
player_Vel = 0.5
player_score = 0

cpu_Pos = [780, 300]
cpu_rect = pg.Rect(cpu_Pos[0], cpu_Pos[1], 20, 100)
cpu_Vel = 6
cpu_score = 0
has_cpu_hit_ball = False


# Reduce the height of the player and CPU hitboxes by 4 pixels
player_rect.height -= 4
player_rect.top += 2
cpu_rect.height -= 4
cpu_rect.top += 2


# Initialize pg
pg.init()

# Set up the clock
clock = pg.time.Clock()

hit_sound = pg.mixer.Sound(settings.SOUNDS + 'ball.wav')
bounce_sound = pg.mixer.Sound(settings.SOUNDS + 'wall_hit.wav')
pg.mixer.Sound.set_volume(hit_sound, 0.2)
pg.mixer.Sound.set_volume(bounce_sound, 0.4)


# Set up a timer to update the CPU paddle's position every 100 milliseconds
UPDATE_CPU_POS = pg.USEREVENT + 1
pg.time.set_timer(UPDATE_CPU_POS, 100)
cpu_target_y = 0


def draw_dotted_line(surface, color, start_pos, end_pos, width=1, dot_length=10, gap_length=5):
    distance = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
    length = pg.math.Vector2(distance).length()
    angle = pg.math.Vector2(distance).angle_to((1, 0))
    dot_distance = dot_length + gap_length
    dots = int(length / dot_distance)

    for i in range(dots):
        start = (start_pos[0] + i * distance[0] / dots,
                 start_pos[1] + i * distance[1] / dots)
        end = (start_pos[0] + (i + 0.5) * distance[0] / dots,
               start_pos[1] + (i + 0.5) * distance[1] / dots)
        pg.draw.line(surface, color, start, end, width)

# Draw the Scores


def draw_score():
    player_score_text = font.render(str(player_score), True, settings.WHITE)
    cpu_score_text = font.render(str(cpu_score), True, settings.WHITE)
    screen.blit(player_score_text, (settings.PLAYABLE_AREA[0] / 4, 10))
    screen.blit(cpu_score_text, (settings.PLAYABLE_AREA[0] * 3 / 4, 10))
    return cpu_score_text


# Set up the display
screen = pg.display.set_mode(settings.PLAYABLE_AREA)
pg.display.set_caption("My Pong")


# Load the font
font = pg.font.Font(None, settings.FONT_SIZE)

# Game loop
move_up = False
move_down = False

running = 1

# hide mouse pointer
pg.mouse.set_visible(False)


while running:
    clock.tick(144)

    # Handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = 0
        elif event.type == UPDATE_CPU_POS:
            # Update the CPU paddle's position
            cpu_target_y = ball_rect.centery
            cpu_target_y += random.randint(-50, 50)

        elif event.type == pg.KEYDOWN:
            # restart game if space is pressed
            if event.key == pg.K_SPACE and is_Game_Over:
                ball_vel = [3, 3]
                cpu_Vel = 5
                ball_rect = pg.Rect(ball_pos[0], ball_pos[1], 20, 20)
                player_score = 0
                cpu_score = 0
                is_Game_Over = False
                screen.fill((settings.BLACK))

            if event.key == pg.K_UP:
                move_up = True
            elif event.key == pg.K_DOWN:
                move_down = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                move_up = False
            elif event.key == pg.K_DOWN:
                move_down = False

    # Move the player paddle
    if move_up:
        player_rect.move_ip(0, -10 * player_Vel)

        if player_rect.top < 0:
            player_rect.top = 0

    elif move_down:
        player_rect.move_ip(0, 10 * player_Vel)

        if player_rect.bottom > settings.PLAYABLE_AREA[1]:
            player_rect.bottom = settings.PLAYABLE_AREA[1]

    # Update the ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Move the CPU paddle to track the ball
    if ball_pos[0] > (settings.PLAYABLE_AREA[0] / 2) + 50 and not has_cpu_hit_ball:
        if cpu_rect.centery < cpu_target_y:
            cpu_rect.centery += cpu_Vel

        elif cpu_rect.centery > cpu_target_y:
            cpu_rect.centery -= cpu_Vel

            if cpu_rect.top < 0:
                cpu_rect.top = 0

            elif cpu_rect.bottom > settings.PLAYABLE_AREA[1]:
                cpu_rect.bottom = settings.PLAYABLE_AREA[1]

    # Check if the ball hits upper or lower walls
    if ball_rect.top < 0:
        ball_pos[1] = ball_rect.height / 2
        ball_vel[1] = -ball_vel[1]
        bounce_sound.play()

    elif ball_rect.bottom > settings.PLAYABLE_AREA[1]:
        ball_pos[1] = settings.PLAYABLE_AREA[1] - ball_rect.height / 2
        ball_vel[1] = -ball_vel[1]
        bounce_sound.play()

    # ball starts in the middle of the screen
    ball_rect.center = ball_pos

    # Check for collisions with the side walls
    if ball_rect.left < 0:
        if not cpu_score == 10:
            cpu_score += 1
        ball_pos = [settings.PLAYABLE_AREA[0] /
                    2, settings.PLAYABLE_AREA[1] / 2]
        ball_vel[0] = -ball_vel[0]

    elif ball_rect.right > settings.PLAYABLE_AREA[0]:
        if not player_score == 10:
            player_score += 1

        ball_pos = [settings.PLAYABLE_AREA[0] /
                    2, settings.PLAYABLE_AREA[1] / 2]
        ball_vel[0] = -ball_vel[0]
        has_cpu_hit_ball = False

    # Check for collisions with the player paddle
    if ball_rect.colliderect(player_rect):
        hit_sound.play()
        has_cpu_hit_ball = False
        ball_vel[1] += random.random() - 0.25

        if ball_rect.bottom >= player_rect.top and ball_rect.top <= player_rect.bottom:
            ball_vel[0] = abs(-ball_vel[0])
        elif ball_rect.left <= player_rect.right:
            ball_vel[1] = -ball_vel[1]

    # Check for collisions with the CPU paddle
    if ball_rect.colliderect(cpu_rect):
        hit_sound.play()
        has_cpu_hit_ball = True
        ball_vel[1] += random.random() - 0.25
        if ball_rect.bottom >= cpu_rect.top and ball_rect.top <= cpu_rect.bottom:
            ball_vel[0] = -abs(ball_vel[0])
        elif ball_rect.right >= cpu_rect.left:  # and ball_rect.left <= cpu_rect.right:
            ball_vel[1] = -ball_vel[1]

    # Draw to the screen
    screen.fill((settings.BLACK))

    # draw dotted line in the middle of the screen
    draw_dotted_line(screen, settings.WHITE, (settings.PLAYABLE_AREA[0] / 2, 0), (
        settings.PLAYABLE_AREA[0] / 2, settings.PLAYABLE_AREA[1] + 15), width=10, dot_length=10, gap_length=20)

    pg.draw.rect(screen, settings.WHITE, ball_rect)
    pg.draw.rect(screen, settings.WHITE, player_rect)
    pg.draw.rect(screen, settings.WHITE, cpu_rect)

    draw_score()

    # if either player has 15 points then show the winner
    if player_score == 10 or cpu_score == 10:
        # stop the ball
        ball_vel = [0, 0]
        cpu_Vel = 0
        # remove ball
        ball_rect = pg.Rect(0, 0, 0, 0)
        is_Game_Over = True

        screen.fill((settings.BLACK))
        draw_score()
        if player_score == 10:
            winner_text = font.render("Player Wins!", True, settings.WHITE)
            screen.blit(
                winner_text, (settings.PLAYABLE_AREA[0] / 2 - 150, settings.PLAYABLE_AREA[1] / 2 - 40))
        elif cpu_score == 10:
            winner_text = font.render("CPU Wins!", True, settings.WHITE)
            screen.blit(
                winner_text, (settings.PLAYABLE_AREA[0] / 2 - 150, settings.PLAYABLE_AREA[1] / 2 - 40))

    # Update the display
    # pg.display.flip()
    pg.display.update()
    # pg.time.delay(10)

# Quit pg
pg.quit()
