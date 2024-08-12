import pygame
import os

pygame.init()

pygame.display.set_caption("Multilayer Maze")
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True

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

ball_pos = (1, 1)
selected_lvl = 1
mouse_prev_pressed = pygame.mouse.get_pressed()
key_press_cd = 0
COOLDOWN = 10
stage = "menu"
ball_depth = 0
maze_inited = False

def place_center(screen, object, pos):
  screen.blit(
      object,
      (pos[0] - object.get_width() // 2, pos[1] - object.get_height() // 2))

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

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
      if 225 < mouse_pos[0] < 250 and 315 < mouse_pos[1] < 335:
        if selected_lvl > 1:
          selected_lvl -= 1
      elif 350 < mouse_pos[0] < 375 and 315 < mouse_pos[1] < 335:
        if len(lvls) > selected_lvl:
          selected_lvl += 1
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

    # draw maze

    screen.fill("black")

    for y, row in enumerate(layer):
      for x, cell in enumerate(row):
        if cell == "#":
          pygame.draw.rect(screen, "white", (x * 40, y * 40, 40, 40))
        if cell == "x":
          pygame.draw.circle(screen, "green", (x * 40 + 20, y * 40 + 20), 16)
        if cell == " ":
          if can_go_next_layer(x, y):
            pygame.draw.rect(screen, "orange", (x * 40, y * 40, 40, 40))

    # draw ball
    pygame.draw.circle(screen, "dodgerblue",
                       (ball_pos[0] * 40 + 20, ball_pos[1] * 40 + 20), 16)

    # draw depth
    if ball_depth > 0:
      prev_layer = lvl[ball_depth - 1]
      for y, row in enumerate(prev_layer):
        for x, cell in enumerate(row):
          if cell == "#":
            if x > 0 and prev_layer[y][x - 1] != "#":
              pygame.draw.line(screen, "gray", (x * 40, y * 40),
                               (x * 40, y * 40 + 5), 3)
              pygame.draw.line(screen, "gray", (x * 40, y * 40 + 15),
                               (x * 40, y * 40 + 25), 3)
              pygame.draw.line(screen, "gray", (x * 40, y * 40 + 35),
                               (x * 40, y * 40 + 40), 3)
            if x < 14 and prev_layer[y][x + 1] != "#":
              pygame.draw.line(screen, "gray", (x * 40 + 40, y * 40),
                               (x * 40 + 40, y * 40 + 5), 3)
              pygame.draw.line(screen, "gray", (x * 40 + 40, y * 40 + 15),
                               (x * 40 + 40, y * 40 + 25), 3)
              pygame.draw.line(screen, "gray", (x * 40 + 40, y * 40 + 35),
                               (x * 40 + 40, y * 40 + 40), 3)
            if y > 0 and prev_layer[y - 1][x] != "#":
              pygame.draw.line(screen, "gray", (x * 40, y * 40),
                               (x * 40 + 5, y * 40), 3)
              pygame.draw.line(screen, "gray", (x * 40 + 15, y * 40),
                               (x * 40 + 25, y * 40), 3)
              pygame.draw.line(screen, "gray", (x * 40 + 35, y * 40),
                               (x * 40 + 40, y * 40), 3)
            if y < 14 and prev_layer[y + 1][x] != "#":
              pygame.draw.line(screen, "gray", (x * 40, y * 40 + 40),
                               (x * 40 + 5, y * 40 + 40), 3)
              pygame.draw.line(screen, "gray", (x * 40 + 15, y * 40 + 40),
                               (x * 40 + 25, y * 40 + 40), 3)
              pygame.draw.line(screen, "gray", (x * 40 + 35, y * 40 + 40),
                               (x * 40 + 40, y * 40 + 40), 3)

    if selected_lvl == 1 and find_ball_pos(lvl) == (ball_pos, ball_depth):
      pygame.draw.rect(screen, "salmon", (170, 280, 260, 40), border_radius=10)
      hint_font = pygame.font.SysFont("Arial", 24)
      hint_text = hint_font.render("Use arrow keys to navigate", True, "white")
      place_center(screen, hint_text, (300, 300))
    if selected_lvl == 2 and find_ball_pos(lvl) == (ball_pos, ball_depth):
      pygame.draw.rect(screen, "salmon", (100, 240, 400, 120), border_radius=10)
      hint_font = pygame.font.SysFont("Arial", 24)
      hint_text_1 = hint_font.render("Orange tiles are tunnels between layers", True, "white")
      hint_text_2 = hint_font.render("Gray boxes show paths of upper layer", True, "white")
      hint_text_3 = hint_font.render("Use A and Z to go between layers", True, "white")
      place_center(screen, hint_text_1, (300, 260))
      place_center(screen, hint_text_2, (300, 300))
      place_center(screen, hint_text_3, (300, 340))

    pygame.display.flip()

    # move ball
    x, y = ball_pos

    # check for win condition
    if layer[y][x] == "x":
      stage = "win"
      continue

    key_pressed = pygame.key.get_pressed()

    if key_press_cd == 0:
      if key_pressed[pygame.K_LEFT] and x > 0 and layer[y][x - 1] != "#":
        x -= 1
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_RIGHT] and x < 14 and layer[y][x + 1] != "#":
        x += 1
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_UP] and y > 0 and layer[y - 1][x] != "#":
        y -= 1
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_DOWN] and y < 14 and layer[y + 1][x] != "#":
        y += 1
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_a] and can_go_next_layer(x, y):
        ball_depth += 1
        key_press_cd = COOLDOWN
      elif key_pressed[pygame.K_z] and can_go_prev_layer(x, y):
        ball_depth -= 1
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
    pygame.draw.rect(screen, "darkgray", (200, 200, 200, 200), 3)

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
    pygame.draw.rect(screen, "darkgray", (200, 200, 200, 200), 3)

    # win text
    font = pygame.font.SysFont("Arial", 36)
    win_text = font.render("You win!", True, "darkgreen")
    place_center(screen, win_text, (300, 250))

    if len(lvls) > selected_lvl:
      # next level button
      pygame.draw.rect(screen, "darkgreen", (250, 280, 100, 40), border_radius=10)
      font = pygame.font.SysFont("Arial", 20)
      resume_text = font.render("Next level", True, "white")
      place_center(screen, resume_text, (300, 300))

      # menu button
      pygame.draw.rect(screen, "darkgray", (250, 330, 100, 40), border_radius=10)
      font = pygame.font.SysFont("Arial", 24)
      menu_text = font.render("Menu", True, "white")
      place_center(screen, menu_text, (300, 350))
    
    else:
      # menu button
      pygame.draw.rect(screen, "darkgreen", (250, 300, 100, 40), border_radius=10)
      font = pygame.font.SysFont("Arial", 24)
      menu_text = font.render("Menu", True, "white")
      place_center(screen, menu_text, (300, 320))

    pygame.display.flip()

    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0] and not mouse_prev_pressed:
      mouse_pos = pygame.mouse.get_pos()
      if len(lvls) > selected_lvl:
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

  clock.tick(60)  # limits FPS to 60

pygame.quit()
