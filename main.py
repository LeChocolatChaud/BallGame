import pygame
import os
from math import sqrt, sin, pi

# init pygame

pygame.init()

pygame.display.set_caption("Multilayer Maze")
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True

# init lvls

lvls = []

for lvl_file in os.listdir("levels"):
  with open(f"levels/{lvl_file}", "r") as file:
    data = file.read()
    layers = data.split("\n\n")
    lvl = []
    for layer in layers:
      layer = layer.split("\n")
      lvl.append(layer)
    lvls.append(lvl)
    print(f"Loaded {lvl_file}")

# init game vars

ball_pos = (1, 1)
selected_lvl = 1
mouse_prev_pressed = pygame.mouse.get_pressed()
key_press_cd = 0
direction = "up"
layer_direction = "lower"
animate_layer = False
animate = False
COOLDOWN = 10
BALL_RADIUS = 16
DOT_RADIUS = 5
STANDARD_OFFSET = sqrt(BALL_RADIUS ** 2 - DOT_RADIUS ** 2)
stage = "menu"
ball_depth = 0
maze_inited = False

# game util funcs

def place_center(screen, object, pos):
  screen.blit(
      object,
      (pos[0] - object.get_width() // 2, pos[1] - object.get_height() // 2))

# main loop

while running:

  # events, used for close window only
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  # game stages

  if stage == "menu":
    screen.fill("black")

    # main title
    title_font = pygame.font.SysFont("Arial Black", 60)
    title = title_font.render(f"BALL MAZE", True, "white")
    place_center(screen, title, (300, 100))

    # select level title
    font = pygame.font.SysFont("Arial", 30)
    select_lvl_title = font.render(f"Select level", True, "white")
    place_center(screen, select_lvl_title, (300, 250))
    # left choice triangle
    pygame.draw.polygon(screen, "white", [(225, 325), (250, 315), (250, 335)])
    # right choice triangle
    pygame.draw.polygon(screen, "white", [(375, 325), (350, 315), (350, 335)])

    lvl_number_text = font.render(f"{selected_lvl}", True, "white")
    place_center(screen, lvl_number_text, (300, 325))

    # start button
    pygame.draw.rect(screen, "white", (250, 400, 100, 40), border_radius=10)
    start_text = font.render(f"Start", True, "black")
    place_center(screen, start_text, (300, 420))

    pygame.display.flip()

    # mouse
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    if not mouse_pressed[0] and mouse_prev_pressed:
      # prev lvl
      if 225 < mouse_pos[0] < 250 and 315 < mouse_pos[1] < 335:
        if selected_lvl > 1:
          selected_lvl -= 1
      # next lvl
      elif 350 < mouse_pos[0] < 375 and 315 < mouse_pos[1] < 335:
        if len(lvls) > selected_lvl:
          selected_lvl += 1
      # start game
      elif 250 < mouse_pos[0] < 350 and 400 < mouse_pos[1] < 440:
        maze_inited = False
        stage = "game"
        continue

    mouse_prev_pressed = mouse_pressed[0]

  if stage == "game":
    # init maze
    if not maze_inited:
      lvl_index = selected_lvl - 1

      lvl = lvls[lvl_index]

      def find_ball_pos(lvl):
        for i, layer in enumerate(lvl):
          for y, row in enumerate(layer):
            for x, cell in enumerate(row):
              if cell == "o":
                return (x, y), i
        return None

      possible_pos = find_ball_pos(lvl)
      if possible_pos:
        ball_pos = possible_pos[0]
        ball_depth = possible_pos[1]

      maze_inited = True

    # init current layer
    layer = lvl[ball_depth]
    has_next_layer = ball_depth < len(lvl) - 1
    has_prev_layer = ball_depth > 0

    def can_go_next_layer(x, y):
      if has_next_layer:
        next_layer = lvl[ball_depth + 1]
        if next_layer[y][x] == " ":
          return True
      return False

    def can_go_prev_layer(x, y):
      if has_prev_layer:
        prev_layer = lvl[ball_depth - 1]
        if prev_layer[y][x] == " ":
          return True
      return False

    # draw map without ball
    def generate_layer_map(screen: pygame.Surface):
      # draw maze
      screen.fill("black")

      for y, row in enumerate(layer):
        for x, cell in enumerate(row):
          if cell == "#":
            pygame.draw.rect(screen, "darkgray", (x * 40, y * 40, 40, 40))
          if cell == "x":
            pygame.draw.circle(screen, "green", (x * 40 + 20, y * 40 + 20), 16)
          if cell == " ":
            if can_go_next_layer(x, y):
              pygame.draw.rect(screen, "orange", (x * 40, y * 40, 40, 40))

      # draw depth (segmented lines)
      if ball_depth > 0:
        prev_layer = lvl[ball_depth - 1]
        for y, row in enumerate(prev_layer):
          for x, cell in enumerate(row):
            if cell == "#":
              if x > 0 and prev_layer[y][x - 1] != "#":
                pygame.draw.line(screen, "lightgray", (x * 40, y * 40),
                                 (x * 40, y * 40 + 5), 3)
                pygame.draw.line(screen, "lightgray", (x * 40, y * 40 + 15),
                                 (x * 40, y * 40 + 25), 3)
                pygame.draw.line(screen, "lightgray", (x * 40, y * 40 + 35),
                                 (x * 40, y * 40 + 40), 3)
              if x < 14 and prev_layer[y][x + 1] != "#":
                pygame.draw.line(screen, "lightgray", (x * 40 + 40, y * 40),
                                 (x * 40 + 40, y * 40 + 5), 3)
                pygame.draw.line(screen, "lightgray",
                                 (x * 40 + 40, y * 40 + 15),
                                 (x * 40 + 40, y * 40 + 25), 3)
                pygame.draw.line(screen, "lightgray",
                                 (x * 40 + 40, y * 40 + 35),
                                 (x * 40 + 40, y * 40 + 40), 3)
              if y > 0 and prev_layer[y - 1][x] != "#":
                pygame.draw.line(screen, "lightgray", (x * 40, y * 40),
                                 (x * 40 + 5, y * 40), 3)
                pygame.draw.line(screen, "lightgray", (x * 40 + 15, y * 40),
                                 (x * 40 + 25, y * 40), 3)
                pygame.draw.line(screen, "lightgray", (x * 40 + 35, y * 40),
                                 (x * 40 + 40, y * 40), 3)
              if y < 14 and prev_layer[y + 1][x] != "#":
                pygame.draw.line(screen, "lightgray", (x * 40, y * 40 + 40),
                                 (x * 40 + 5, y * 40 + 40), 3)
                pygame.draw.line(screen, "lightgray",
                                 (x * 40 + 15, y * 40 + 40),
                                 (x * 40 + 25, y * 40 + 40), 3)
                pygame.draw.line(screen, "lightgray",
                                 (x * 40 + 35, y * 40 + 40),
                                 (x * 40 + 40, y * 40 + 40), 3)

      return screen.copy()

    # draw depth move
    if animate_layer and key_press_cd > 0:
      current_layer_map = generate_layer_map(screen.copy())
      screen.fill("black")
      animation_frame = 10 - key_press_cd
      if layer_direction == "lower":
        prev_layer_map.set_alpha(int(255 - animation_frame * 25.5))
        place_center(
            screen,
            pygame.transform.scale(
                current_layer_map,
                (500 + animation_frame * 10, 500 + animation_frame * 10)),
            (300, 300))
        place_center(
            screen,
            pygame.transform.scale(
                prev_layer_map,
                (600 + animation_frame * 10, 600 + animation_frame * 10)),
            (300, 300))
      if layer_direction == "upper":
        current_layer_map.set_alpha(int(animation_frame * 25.5))
        place_center(
            screen,
            pygame.transform.scale(
                prev_layer_map,
                (600 - animation_frame * 10, 600 - animation_frame * 10)),
            (300, 300))
        place_center(
            screen,
            pygame.transform.scale(
                current_layer_map,
                (700 - animation_frame * 10, 700 - animation_frame * 10)),
            (300, 300))
    else:
      animate_layer = False
      prev_layer_map = generate_layer_map(screen)

    # draw ball
    def get_ball_draw_center():
      if animate and key_press_cd > 0:
        animation_frame = 10 - key_press_cd
        if direction == "up":
          return (ball_pos[0] * 40 + 20, ball_pos[1] * 40 + 60 - animation_frame * 4)
        if direction == "down":
          return (ball_pos[0] * 40 + 20, ball_pos[1] * 40 - 20 + animation_frame * 4)
        if direction == "right":
          return (ball_pos[0] * 40 - 20 + animation_frame * 4, ball_pos[1] * 40 + 20)
        if direction == "left":
          return (ball_pos[0] * 40 + 60 - animation_frame * 4, ball_pos[1] * 40 + 20)
      return (ball_pos[0] * 40 + 20, ball_pos[1] * 40 + 20)

    # order: top, left, bottom, right, center, back
    def calc_dot_centers():
      x, y = get_ball_draw_center()
      if animate and key_press_cd > 0:
        animation_frame = 10 - key_press_cd
        offset = abs(STANDARD_OFFSET * sin(animation_frame * 0.05 * pi))
        if direction == "up":
          left = (x - STANDARD_OFFSET, y)
          right = (x + STANDARD_OFFSET, y)
          top = (x, y - offset)
          bottom = None
          center = (x, y + STANDARD_OFFSET - offset)
          back = (x, y - STANDARD_OFFSET + offset)
          if animation_frame > 2:
            back = None
          if animation_frame > 4:
            bottom = (x, y + offset)
        elif direction == "down":
          left = (x - STANDARD_OFFSET, y)
          right = (x + STANDARD_OFFSET, y)
          top = None
          bottom = (x, y + offset)
          center = (x, y - STANDARD_OFFSET + offset)
          back = (x, y + STANDARD_OFFSET - offset)
          if animation_frame > 2:
            back = None
          if animation_frame > 4:
            top = (x, y - offset)
        elif direction == "right":
          top = (x, y - STANDARD_OFFSET)
          bottom = (x, y + STANDARD_OFFSET)
          left = None
          right = (x + offset, y)
          center = (x - STANDARD_OFFSET + offset, y)
          back = (x + STANDARD_OFFSET - offset, y)
          if animation_frame > 2:
            back = None
          if animation_frame > 4:
            left = (x - offset, y)
        elif direction == "left":
          top = (x, y - STANDARD_OFFSET)
          bottom = (x, y + STANDARD_OFFSET)
          left = (x - offset, y)
          right = None
          center = (x + STANDARD_OFFSET - offset, y)
          back = (x - STANDARD_OFFSET + offset, y)
          if animation_frame > 2:
            back = None
          if animation_frame > 4:
            right = (x + offset, y)
        return (top, left, bottom, right, center, back)
      top = (x, y - STANDARD_OFFSET)
      left = (x - STANDARD_OFFSET, y)
      bottom = (x, y + STANDARD_OFFSET)
      right = (x + STANDARD_OFFSET, y)
      center = (x, y)
      back = None
      return (top, left, bottom, right, center, back)

    ball_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    ball_center = get_ball_draw_center()
    pygame.draw.circle(ball_surface, "dodgerblue", ball_center, BALL_RADIUS)
    ball_mask = pygame.mask.from_surface(ball_surface.copy())
    dots_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for center in calc_dot_centers():
      if center:
        pygame.draw.circle(dots_surface, "white", center, DOT_RADIUS)
    dots_mask = pygame.mask.from_surface(dots_surface)
    final_dot_mask = ball_mask.overlap_mask(dots_mask, (0, 0))
    screen.blit(ball_surface, (0, 0))
    screen.blit(final_dot_mask.to_surface(surface=ball_surface, setcolor="white", unsetcolor=(0, 0, 0, 0)), (0, 0))

    if not animate or key_press_cd <= 0:
      animate = False
    
    # draw hint
    if selected_lvl == 1 and find_ball_pos(lvl) == (ball_pos, ball_depth):
      pygame.draw.rect(screen, "salmon", (170, 280, 260, 40), border_radius=10)
      hint_font = pygame.font.SysFont("Arial", 24)
      hint_text = hint_font.render("Use arrow keys to navigate", True, "white")
      place_center(screen, hint_text, (300, 300))
    if selected_lvl == 2 and find_ball_pos(lvl) == (ball_pos, ball_depth):
      pygame.draw.rect(screen,
                       "salmon", (100, 240, 400, 120),
                       border_radius=10)
      hint_font = pygame.font.SysFont("Arial", 24)
      hint_text_1 = hint_font.render("Orange tiles are tunnels between layers",
                                     True, "white")
      hint_text_2 = hint_font.render("Gray boxes show paths of upper layer",
                                     True, "white")
      hint_text_3 = hint_font.render("Use A and Z to go between layers", True,
                                     "white")
      place_center(screen, hint_text_1, (300, 260))
      place_center(screen, hint_text_2, (300, 300))
      place_center(screen, hint_text_3, (300, 340))

    pygame.display.flip()

    # move ball

    x, y = ball_pos

    # check for win condition
    if key_press_cd == 0 and layer[y][x] == "x":
      stage = "win"
      continue

    key_pressed = pygame.key.get_pressed()

    if key_press_cd == 0:
      if key_pressed[pygame.K_LEFT] and x > 0 and layer[y][x - 1] != "#":
        x -= 1
        animate = True
        direction = "left"
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_RIGHT] and x < 14 and layer[y][x + 1] != "#":
        x += 1
        animate = True
        direction = "right"
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_UP] and y > 0 and layer[y - 1][x] != "#":
        y -= 1
        animate = True
        direction = "up"
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_DOWN] and y < 14 and layer[y + 1][x] != "#":
        y += 1
        animate = True
        direction = "down"
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_a] and can_go_next_layer(x, y):
        ball_depth += 1
        animate_layer = True
        layer_direction = "lower"
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_z] and can_go_prev_layer(x, y):
        ball_depth -= 1
        animate_layer = True
        layer_direction = "upper"
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_ESCAPE]:
        stage = "pause"
        continue

    ball_pos = (x, y)

    if key_press_cd > 0:
      key_press_cd -= 1

  if stage == "pause":
    # dialog
    pygame.draw.rect(screen, "white", (200, 200, 200, 200), border_radius=10)
    pygame.draw.rect(screen, "gray", (200, 200, 200, 200), 3)

    # pause text
    font = pygame.font.SysFont("Arial", 36)
    pause_text = font.render("Paused", True, "red")
    place_center(screen, pause_text, (300, 250))

    # resume button
    pygame.draw.rect(screen, "darkgray", (250, 280, 100, 40), border_radius=10)
    font = pygame.font.SysFont("Arial", 24)
    resume_text = font.render("Resume", True, "white")
    place_center(screen, resume_text, (300, 300))

    # menu button
    pygame.draw.rect(screen, "darkgray", (250, 330, 100, 40), border_radius=10)
    font = pygame.font.SysFont("Arial", 24)
    menu_text = font.render("Menu", True, "white")
    place_center(screen, menu_text, (300, 350))

    pygame.display.flip()

    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0] and not mouse_prev_pressed:
      mouse_pos = pygame.mouse.get_pos()
      if 200 <= mouse_pos[0] <= 400 and 280 <= mouse_pos[1] <= 320:
        stage = "game"
        continue
      elif 200 <= mouse_pos[0] <= 400 and 330 <= mouse_pos[1] <= 370:
        stage = "menu"
        continue

    mouse_prev_pressed = mouse_pressed[0]

  if stage == "win":
    # dialog
    pygame.draw.rect(screen, "white", (200, 200, 200, 200), border_radius=10)
    pygame.draw.rect(screen, "gray", (200, 200, 200, 200), 3)

    # win text
    font = pygame.font.SysFont("Arial", 36)
    win_text = font.render("You win!", True, "darkgreen")
    place_center(screen, win_text, (300, 250))

    has_next_lvl = len(lvls) > selected_lvl

    if has_next_lvl:
      # next level button
      pygame.draw.rect(screen,
                       "darkgreen", (250, 280, 100, 40),
                       border_radius=10)
      font = pygame.font.SysFont("Arial", 20)
      resume_text = font.render("Next level", True, "white")
      place_center(screen, resume_text, (300, 300))

      # menu button
      pygame.draw.rect(screen,
                       "darkgray", (250, 330, 100, 40),
                       border_radius=10)
      font = pygame.font.SysFont("Arial", 24)
      menu_text = font.render("Menu", True, "white")
      place_center(screen, menu_text, (300, 350))

    else:
      # menu button
      pygame.draw.rect(screen,
                       "darkgreen", (250, 300, 100, 40),
                       border_radius=10)
      font = pygame.font.SysFont("Arial", 24)
      menu_text = font.render("Menu", True, "white")
      place_center(screen, menu_text, (300, 320))

    pygame.display.flip()

    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0] and not mouse_prev_pressed:
      mouse_pos = pygame.mouse.get_pos()
      if has_next_lvl:
        if 200 <= mouse_pos[0] <= 400 and 280 <= mouse_pos[1] <= 320:
          selected_lvl += 1
          maze_inited = False
          stage = "game"
          continue
        elif 200 <= mouse_pos[0] <= 400 and 330 <= mouse_pos[1] <= 370:
          stage = "menu"
          continue
      else:
        if 200 <= mouse_pos[0] <= 400 and 300 <= mouse_pos[1] <= 340:
          stage = "menu"
          continue

    mouse_prev_pressed = mouse_pressed[0]

    key_pressed = pygame.key.get_pressed()

    if key_pressed[pygame.K_SPACE]:
      if has_next_lvl:
        selected_lvl += 1
        maze_inited = False
        stage = "game"
        continue
      else:
        stage = "menu"
        continue

  clock.tick(60)  # limits FPS to 60

pygame.quit()
