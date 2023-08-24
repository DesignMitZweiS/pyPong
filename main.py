""" pyPong - A simple pong game made with pygame """
import random
import pygame as pg
import settings

# Initialize pyGame
pg.init()

# Set up the ball
ball_pos = [400, 300]
ball_vel = [3, 3]

# Set up the player and CPU paddles
player_pos = [0, 300]
cpu_pos = [780, 300]

ball_rect = pg.Rect(ball_pos[0],
                    ball_pos[1],
                    settings.BALL_SIZE,
                    settings.BALL_SIZE
                    )

player_rect = pg.Rect(player_pos[0],
                      player_pos[1],
                      settings.PADDLE_WIDTH,
                      settings.PADDLE_HEIGHT
                      )

cpu_rect = pg.Rect(cpu_pos[0],
                   cpu_pos[1],
                   settings.PADDLE_WIDTH,
                   settings.PADDLE_HEIGHT
                   )

player_score = 0
cpu_score = 0
has_cpu_hit_ball = False
is_game_over = False

# Set up the clock
clock = pg.time.Clock()

hit_sound = pg.mixer.Sound(settings.SOUNDS + 'ball.wav')
bounce_sound = pg.mixer.Sound(settings.SOUNDS + 'wall_hit.wav')
pg.mixer.Sound.set_volume(hit_sound, 0.2)
pg.mixer.Sound.set_volume(bounce_sound, 0.4)


# Set up a timer to update the CPU paddle's position every 100 milliseconds
UPDATE_cpu_pos = pg.USEREVENT + 1
pg.time.set_timer(UPDATE_cpu_pos, 100)
cpu_target_y = 0


def show_winner_text(who_won):
    """ shows the winner of the game, either player or cpu """
    winner_text = font.render(who_won+" wins!", True, settings.WHITE)
    screen.blit(
        winner_text, (settings.PLAYABLE_AREA[0]/2-150,
                      settings.PLAYABLE_AREA[1]/2-40)
    )


def draw_dotted_line(surface,
                     color,
                     start_pos,
                     end_pos,
                     width=1,
                     dot_length=10,
                     gap_length=5
                     ):
    """ draws a dotted line on the screen """
    distance = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
    length = pg.math.Vector2(distance).length()
    dot_distance = dot_length + gap_length
    dots = int(length / dot_distance)

    for i in range(dots):
        start = (start_pos[0]+i*distance[0]/dots,
                 start_pos[1]+i*distance[1]/dots
                 )
        end = (start_pos[0]+(i+0.5)*distance[0]/dots,
               start_pos[1]+(i+0.5)*distance[1]/dots
               )
        pg.draw.line(surface, color, start, end, width)


def reset_ball():
    """ resets the ball to the middle of the screen and waits 1 second """
    ball_vel[1] += (random.random()-0.15)
    ball_vel[0] = -ball_vel[0]
    pg.time.delay(1000)


def draw_score():
    """ draws the score of player and cpu """
    player_score_text = font.render(str(player_score), True, settings.WHITE)
    cpu_score_text = font.render(str(cpu_score), True, settings.WHITE)
    screen.blit(player_score_text, (settings.PLAYABLE_AREA[0]/4, 10))
    screen.blit(cpu_score_text, (settings.PLAYABLE_AREA[0]*3/4, 10))
    return cpu_score_text


# Set up the display
screen = pg.display.set_mode(settings.PLAYABLE_AREA)
pg.display.set_caption("My Pong")

# Load the font
font = pg.font.Font(None, settings.FONT_SIZE)

# hide mouse pointer
pg.mouse.set_visible(False)

# Game loop
move_up = False
move_down = False

running = 1
while running:
    # set FPS
    clock.tick(144)

    # Handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = 0
        elif event.type == UPDATE_cpu_pos:
            # Update the CPU paddle's position
            cpu_target_y = ball_rect.centery
            cpu_target_y += random.randint(-50, 50)

        elif event.type == pg.KEYDOWN:
            # restart game if space is pressed
            if event.key == pg.K_SPACE and is_game_over:
                ball_vel = [3, 3]
                settings.CPU_VEL = 5
                ball_rect = pg.Rect(ball_pos[0], ball_pos[1], 20, 20)
                player_score = 0
                cpu_score = 0
                is_game_over = False
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
        player_rect.move_ip(0, -10*settings.PLAYER_VEL)
        player_rect.top = max(0, player_rect.top)
    elif move_down:
        player_rect.move_ip(0, 10*settings.PLAYER_VEL)
        player_rect.bottom = min(settings.PLAYABLE_AREA[1], player_rect.bottom)

    # Update the ball's position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    ball_rect.center = ball_pos

    # Move the CPU paddle to track the ball
    if (ball_pos[0] > (settings.PLAYABLE_AREA[0]/2)+50 and
            not has_cpu_hit_ball):
        if cpu_rect.centery < cpu_target_y:
            cpu_rect.centery += settings.CPU_VEL
        elif cpu_rect.centery > cpu_target_y:
            cpu_rect.centery -= settings.CPU_VEL
            cpu_rect.top = max(0, cpu_rect.top)
            cpu_rect.bottom = min(settings.PLAYABLE_AREA[1], cpu_rect.bottom)

    # Check if the ball hits upper or lower walls
    if ball_rect.top < 0:
        ball_pos[1] = ball_rect.height/2
        ball_vel[1] = -ball_vel[1]
        bounce_sound.play()
    elif ball_rect.bottom > settings.PLAYABLE_AREA[1]:
        ball_pos[1] = settings.PLAYABLE_AREA[1] - ball_rect.height/2
        ball_vel[1] = -ball_vel[1]
        bounce_sound.play()

    # Check for collisions with the side walls
    if ball_rect.left < 0:
        if not cpu_score == 10:
            cpu_score += 1
        ball_pos = [settings.PLAYABLE_AREA[0]/2,
                    settings.PLAYABLE_AREA[1]/2
                    ]
        reset_ball()
    elif ball_rect.right >= settings.PLAYABLE_AREA[0]:
        if not player_score == 10:
            player_score += 1

        ball_pos = [settings.PLAYABLE_AREA[0]/2,
                    settings.PLAYABLE_AREA[1]/2
                    ]
        reset_ball()
        has_cpu_hit_ball = False

    # Play the hit sound if the ball hits a paddle
    if ball_rect.colliderect(player_rect) or ball_rect.colliderect(cpu_rect):
        hit_sound.play()

    # Check for collisions with the player paddle
    if ball_rect.colliderect(player_rect):
        has_cpu_hit_ball = False
        ball_vel[1] += (random.random()-0.15)

        if (ball_rect.bottom >= player_rect.top and
                ball_rect.top <= player_rect.bottom):
            ball_vel[0] = abs(-ball_vel[0])
        elif ball_rect.left <= player_rect.right:
            ball_vel[1] = -ball_vel[1]

    # Check for collisions with the CPU paddle
    if ball_rect.colliderect(cpu_rect):
        has_cpu_hit_ball = True
        ball_vel[1] += (random.random()-0.15)

        if (ball_rect.bottom >= cpu_rect.top and
                ball_rect.top <= cpu_rect.bottom):
            ball_vel[0] = -abs(ball_vel[0])
        elif ball_rect.right >= cpu_rect.left:
            ball_vel[1] = -ball_vel[1]

    # Draw to the screen
    screen.fill((settings.BLACK))
    draw_score()

    # draw dotted line in the middle of the screen
    draw_dotted_line(screen,
                     settings.WHITE,
                     (settings.PLAYABLE_AREA[0]/2, 0),
                     (settings.PLAYABLE_AREA[0]/2,
                      settings.PLAYABLE_AREA[1]+15),
                     width=10, dot_length=10, gap_length=20
                     )

    # draw the ball and paddles
    pg.draw.rect(screen, settings.WHITE, ball_rect)
    pg.draw.rect(screen, settings.WHITE, player_rect)
    pg.draw.rect(screen, settings.WHITE, cpu_rect)

    # if either player has 10 points then show the winner
    if player_score == 10 or cpu_score == 10:
        is_game_over = True
        # stop the ball
        ball_vel = [0, 0]
        settings.CPU_VEL = 0
        # remove ball
        ball_rect = pg.Rect(0, 0, 0, 0)
        screen.fill((settings.BLACK))
        draw_score()

        if player_score == 10:
            show_winner_text("Player")
        elif cpu_score == 10:
            show_winner_text("CPU")

    # Update the display
    pg.display.update()

# Quit pg
pg.quit()
