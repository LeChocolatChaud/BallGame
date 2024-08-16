import pygame
from math import sqrt
from tkinter.filedialog import asksaveasfilename

pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

running = True

lvl = []
current_depth = 0
ball_pos = None
end_placed = False
cursor_pos = (0, 0)
key_press_cd = 0
key_prev_pressed = pygame.key.get_pressed()
stage = "edit"
update = False
press_length = {pygame.K_UP: 0, pygame.K_DOWN: 0, pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
COOLDOWN = 1
BALL_RADIUS = 16
DOT_RADIUS = 5
STANDARD_OFFSET = sqrt(BALL_RADIUS ** 2 - DOT_RADIUS ** 2)

def place_center(screen, object, pos):
  screen.blit(
      object,
      (pos[0] - object.get_width() // 2, pos[1] - object.get_height() // 2))

def add_layer(index = None):
  if index is None:
    index = len(lvl)
  new_layer = []
  new_layer.append("#" * 15)
  for _ in range(13):
    new_layer.append("#" + " " * 13 + "#")
  new_layer.append("#" * 15)
  lvl.insert(index, new_layer)

add_layer()

def save_level(lvl):
  with open(asksaveasfilename(defaultextension=".lvl"), "wb") as f:
    for layer in lvl:
      for row in layer:
        f.write(row.encode() + b'\n')
      f.write(b'\n')
    f.seek(-2, 2)
    f.truncate()

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  
  if stage == "edit":
    screen.fill("black")

    # init current layer
    layer = lvl[current_depth]
    has_next_layer = current_depth < len(lvl) - 1
    has_prev_layer = current_depth > 0

    def can_go_next_layer(x, y):
      if has_next_layer:
        next_layer = lvl[current_depth + 1]
        if next_layer[y][x] == " ":
          return True
      return False

    def can_go_prev_layer(x, y):
      if has_prev_layer:
        prev_layer = lvl[current_depth - 1]
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
      if current_depth > 0:
        prev_layer = lvl[current_depth - 1]
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
    
    generate_layer_map(screen)

    def draw_ball(screen: pygame.Surface, ball_pos):
      # draw ball
      def get_ball_draw_center():
        return (ball_pos[0] * 40 + 20, ball_pos[1] * 40 + 20)

      # order: top, left, bottom, right, center, back
      def calc_dot_centers():
        x, y = get_ball_draw_center()
        top = (x, y - STANDARD_OFFSET)
        left = (x - STANDARD_OFFSET, y)
        bottom = (x, y + STANDARD_OFFSET)
        right = (x + STANDARD_OFFSET, y)
        center = (x, y)
        return (top, left, bottom, right, center)

      ball_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
      ball_center = get_ball_draw_center()
      pygame.draw.circle(ball_surface, "dodgerblue", ball_center, BALL_RADIUS)
      ball_mask = pygame.mask.from_surface(ball_surface.copy())
      dots_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
      for center in calc_dot_centers():
        pygame.draw.circle(dots_surface, "white", center, DOT_RADIUS)
      dots_mask = pygame.mask.from_surface(dots_surface)
      final_dot_mask = ball_mask.overlap_mask(dots_mask, (0, 0))
      screen.blit(ball_surface, (0, 0))
      screen.blit(final_dot_mask.to_surface(surface=ball_surface, setcolor="white", unsetcolor=(0, 0, 0, 0)), (0, 0))

    if ball_pos and current_depth == ball_pos[2]:
      draw_ball(screen, ball_pos)

    # draw cursor
    pygame.draw.rect(screen, "white", (cursor_pos[0] * 40, cursor_pos[1] * 40, 40, 40), 3)

    # draw depth number
    font = pygame.font.SysFont("Arial", 24)
    depth_text = font.render("Depth: " + str(current_depth), True, "white")
    place_center(screen, depth_text, (700, 580))

    # draw hint
    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)
    tiny_font = pygame.font.SysFont("Arial", 12)

    equals_symbol = font.render("=", True, "white")
    
    def draw_key_outline(center_pos):
      pygame.draw.rect(screen, "darkgray", (center_pos[0] - 20, center_pos[1] - 20, 40, 40), border_radius=5)
      pygame.draw.rect(screen, "white", (center_pos[0] - 15, center_pos[1] - 20, 30, 35), border_radius=5)

    draw_key_outline((660, 60))
    wall_key_hint = tiny_font.render("Space", True, "black")
    place_center(screen, wall_key_hint, (660, 55))
    place_center(screen, equals_symbol, (700, 60))
    pygame.draw.rect(screen, "darkgray", (720, 40, 40, 40))

    draw_key_outline((660, 120))
    ball_key_hint = font.render("C", True, "black")
    place_center(screen, ball_key_hint, (660, 115))
    place_center(screen, equals_symbol, (700, 120))
    draw_ball(screen, (18, 2.5))

    draw_key_outline((660, 180))
    finish_key_hint = font.render("X", True, "black")
    place_center(screen, finish_key_hint, (660, 175))
    place_center(screen, equals_symbol, (700, 180))
    pygame.draw.circle(screen, "green", (740, 180), 16)

    draw_key_outline((640, 240))
    depth_down_key_hint = font.render("A", True, "black")
    place_center(screen, depth_down_key_hint, (640, 235))
    draw_key_outline((680, 240))
    depth_up_key_hint = font.render("Z", True, "black")
    place_center(screen, depth_up_key_hint, (680, 235))
    depth_hint = small_font.render("depth control", True, "white")
    place_center(screen, depth_hint, (745, 240))

    draw_key_outline((640, 300))
    add_lower_layer_key_hint = font.render("M", True, "black")
    place_center(screen, add_lower_layer_key_hint, (640, 295))
    draw_key_outline((680, 300))
    add_upper_layer_key_hint = font.render("K", True, "black")
    place_center(screen, add_upper_layer_key_hint, (680, 295))
    layers_hint_1 = small_font.render("add a", True, "white")
    place_center(screen, layers_hint_1, (745, 280))
    layers_hint_2 = small_font.render("lower/upper", True, "white")
    place_center(screen, layers_hint_2, (745, 300))
    layers_hint_3 = small_font.render("layer", True, "white")
    place_center(screen, layers_hint_3, (745, 320))

    draw_key_outline((660, 360))
    delete_layer_key_hint = small_font.render("Del", True, "black")
    place_center(screen, delete_layer_key_hint, (660, 355))
    delete_layer_hint_1 = small_font.render("delete current", True, "white")
    place_center(screen, delete_layer_hint_1, (745, 350))
    delete_layer_hint_2 = small_font.render("layer", True, "white")
    place_center(screen, delete_layer_hint_2, (745, 370))

    draw_key_outline((630, 420))
    ctrl_key_hint = small_font.render("Ctrl", True, "black")
    place_center(screen, ctrl_key_hint, (630, 415))
    plus_key_hint = font.render("+", True, "white")
    place_center(screen, plus_key_hint, (660, 417))
    draw_key_outline((690, 420))
    save_key_hint = font.render("S", True, "black")
    place_center(screen, save_key_hint, (690, 415))
    save_hint_1 = small_font.render("save level", True, "white")
    place_center(screen, save_hint_1, (750, 417))

    pygame.display.flip()

    # move ball

    x, y = cursor_pos

    key_pressed = pygame.key.get_pressed()
    if_pressed = lambda x: key_pressed[x] and not key_prev_pressed[x]
    if_pressed_or_held = lambda x: if_pressed(x) or press_length[x] > 10

    if key_press_cd == 0:
      if if_pressed_or_held(pygame.K_LEFT) and x > 0:
        x -= 1
        press_length[pygame.K_LEFT] = 0
        key_press_cd = COOLDOWN
      elif if_pressed_or_held(pygame.K_RIGHT) and x < 14:
        x += 1
        press_length[pygame.K_RIGHT] = 0
        key_press_cd = COOLDOWN
      elif if_pressed_or_held(pygame.K_UP) and y > 0:
        y -= 1
        press_length[pygame.K_UP] = 0
        key_press_cd = COOLDOWN
      elif if_pressed_or_held(pygame.K_DOWN) and y < 14:
        y += 1
        press_length[pygame.K_DOWN] = 0
        key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_a) and has_next_layer:
        current_depth += 1
        key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_z) and has_prev_layer:
        current_depth -= 1
        key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_SPACE):
        if layer[y][x] == "#":
          layer[y] = layer[y][:x] + " " + layer[y][x + 1:]
        else:
          if layer[y][x] == "o":
            ball_pos = None
          elif layer[y][x] == "x":
            end_placed = False
          layer[y] = layer[y][:x] + "#" + layer[y][x + 1:]
        update = True
        key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_c):
        if layer[y][x] == " " and not ball_pos:
          layer[y] = layer[y][:x] + "o" + layer[y][x + 1:]
          ball_pos = (x, y, current_depth)
          update = True
          key_press_cd = COOLDOWN
        elif layer[y][x] == "o" and ball_pos:
          layer[y] = layer[y][:x] + " " + layer[y][x + 1:]
          ball_pos = None
          update = True
          key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_x):
        if layer[y][x] == " " and not end_placed:
          layer[y] = layer[y][:x] + "x" + layer[y][x + 1:]
          end_placed = True
          update = True
          key_press_cd = COOLDOWN
        elif layer[y][x] == "x" and end_placed:
          layer[y] = layer[y][:x] + " " + layer[y][x + 1:]
          end_placed = False
          update = True
          key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_m):
        add_layer()
        current_depth += 1
        key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_k):
        add_layer(index=current_depth)
        key_press_cd = COOLDOWN
      elif if_pressed(pygame.K_DELETE):
        if len(lvl) > 1:
          stage = "danger"
          key_press_cd = 10
      elif if_pressed(pygame.K_s) and pygame.key.get_mods() & pygame.KMOD_CTRL:
        if not ball_pos or not end_placed:
          stage = "badlvl"
          key_press_cd = COOLDOWN
        else:
          save_level(lvl)
    
    for key in press_length:
      if key_pressed[key]:
        press_length[key] += 1
      else:
        press_length[key] = 0

    key_prev_pressed = key_pressed
    cursor_pos = (x, y)
    if update:
      update = False
      lvl[current_depth] = layer
  
  if stage == "danger":
    # dialog
    pygame.draw.rect(screen, "white", (200, 200, 200, 200), border_radius=10)
    pygame.draw.rect(screen, "gray", (200, 200, 200, 200), 3)

    # danger text
    font = pygame.font.SysFont("Arial", 30)
    danger_text = font.render("Delete layer", True, "red")
    place_center(screen, danger_text, (300, 250))

    # hint text
    font = pygame.font.SysFont("Arial", 24)
    hint_text_1 = font.render("Press delete again to", True, "red")
    place_center(screen, hint_text_1, (300, 300))
    hint_text_2 = font.render("delete the layer", True, "red")
    place_center(screen, hint_text_2, (300, 325))
    hint_text_3 = font.render("Press escape to cancel", True, "red")
    place_center(screen, hint_text_3, (300, 350))

    pygame.display.flip()

    key_pressed = pygame.key.get_pressed()
    if_pressed = lambda x: key_pressed[x] and not key_prev_pressed[x]

    if key_press_cd == 0:
      if if_pressed(pygame.K_DELETE):
        del lvl[current_depth]
        if current_depth == len(lvl):
          current_depth -= 1
        stage = "edit"
        continue
      elif if_pressed(pygame.K_ESCAPE):
        stage = "edit"
        continue
    
    key_prev_pressed = key_pressed
  
  if stage == "badlvl":
    # dialog
    pygame.draw.rect(screen, "white", (200, 200, 200, 200), border_radius=10)
    pygame.draw.rect(screen, "gray", (200, 200, 200, 200), 3)

    # bad level text
    font = pygame.font.SysFont("Arial", 30)
    badlvl_text = font.render("Bad level", True, "red")
    place_center(screen, badlvl_text, (300, 250))

    # hint text
    font = pygame.font.SysFont("Arial", 20)
    hint_text_1 = font.render("Place the ball and", True, "red")
    place_center(screen, hint_text_1, (300, 300))
    hint_text_2 = font.render("the end before saving", True, "red")
    place_center(screen, hint_text_2, (300, 325))
    hint_text_3 = font.render("Press escape to cancel", True, "red")
    place_center(screen, hint_text_3, (300, 350))

    pygame.display.flip()

    key_pressed = pygame.key.get_pressed()

    if key_press_cd == 0:
      if key_pressed[pygame.K_ESCAPE]:
        stage = "edit"
        continue

  if key_press_cd > 0:
    key_press_cd -= 1

  clock.tick(60)