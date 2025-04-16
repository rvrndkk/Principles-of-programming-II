import pygame
import random
import psycopg2
import time

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="3799979"
    )

def userr(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM snake_users WHERE username = %s", (username,))
    user = cur.fetchone()
    if user:
        user_id = user[0]
        cur.execute("SELECT MAX(level) FROM snake_scores WHERE user_id = %s", (user_id,))
        level = cur.fetchone()[0] or 1
    else:
        cur.execute("INSERT INTO snake_users(username) VALUES (%s) RETURNING id", (username,))
        user_id = cur.fetchone()[0]
        level = 1
        conn.commit()
    cur.close()
    conn.close()
    return user_id, level

def save_score(user_id, score, level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO snake_scores(user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
    conn.commit()
    cur.close()
    conn.close()


pygame.init()

GRID_SIZE = 20
snake_col = (0, 255, 0)
food_col = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]
bg = (0, 0, 0)
txt_col = (255, 255, 255)
eda_timer = 5000

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Snake")
font = pygame.font.SysFont("Verdana", 20)


username = input("Enter username: ")
user_id, level = userr(username)
score = 0
speed = 10 + (level - 1) * 2

class Food:
    def __init__(self):
        self.position = self.generate_position()
        self.weight = random.randint(1, 3)
        self.color = food_col[self.weight - 1]
        self.spawn_time = pygame.time.get_ticks()

    def generate_position(self):
        return (
            random.randint(0, (600 // GRID_SIZE) - 1) * GRID_SIZE,
            random.randint(0, (400 // GRID_SIZE) - 1) * GRID_SIZE
        )

    def is_expired(self):
        return (pygame.time.get_ticks() - self.spawn_time) > eda_timer

snake = [(100, 100)]
snake_dir = (GRID_SIZE, 0)
foods = [Food()]
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(bg)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != (0, GRID_SIZE):
                snake_dir = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN and snake_dir != (0, -GRID_SIZE):
                snake_dir = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT and snake_dir != (GRID_SIZE, 0):
                snake_dir = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT and snake_dir != (-GRID_SIZE, 0):
                snake_dir = (GRID_SIZE, 0)
            elif event.key == pygame.K_p:
                save_score(user_id, score, level)
                print("Game paused.")
                time.sleep(2)

    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    if new_head[0] < 0 or new_head[0] >= 600 or new_head[1] < 0 or new_head[1] >= 400 or new_head in snake:
        save_score(user_id, score, level)
        print("Game Over!")
        break

    snake.insert(0, new_head)
    food_eaten = None
    for food in foods:
        if new_head == food.position:
            score += food.weight
            if score % 5 == 0:
                level += 1
                speed += 2
            food_eaten = food
            break

    if food_eaten:
        foods.remove(food_eaten)
        foods.append(Food())
    else:
        snake.pop()

    current_time = pygame.time.get_ticks()
    foods = [food for food in foods if not food.is_expired()]
    if len(foods) < 1:
        foods.append(Food())

    for food in foods:
        time_left = 1 - min(1, (current_time - food.spawn_time) / eda_timer)
        color = tuple(int(c * time_left) for c in food.color)
        pygame.draw.rect(screen, color, (food.position[0], food.position[1], GRID_SIZE, GRID_SIZE))

    for segment in snake:
        pygame.draw.rect(screen, snake_col, (segment[0], segment[1], GRID_SIZE, GRID_SIZE))

    screen.blit(font.render(f"Score: {score}", True, txt_col), (10, 10))
    screen.blit(font.render(f"Level: {level}", True, txt_col), (10, 30))
    pygame.display.update()
    clock.tick(speed)

pygame.quit()
