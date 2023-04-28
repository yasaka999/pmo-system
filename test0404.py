# 导入必要的模块
import pygame
import random

# 初始化pygame
pygame.init()

# 设置游戏界面大小、背景颜色和标题
screen_width = 480
screen_height = 480
bg_color = (255, 255, 255)
caption = '贪食蛇'
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption(caption)

# 定义颜色变量
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
black = pygame.Color(0, 0, 0)

# 定义游戏结束函数
def game_over():
    pygame.quit()
    exit()

# 定义主函数
def main():
    # 初始化变量
    snake_position = [100, 100]
    snake_body = [[100, 100], [90, 100], [80, 100]]
    food_position = [300, 300]
    food_spawned = 1
    direction = 'RIGHT'
    change_to = direction
    score = 0

    # 定义游戏循环
    while True:
        # 检测按键事件
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'
                if event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                if event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        # 判断蛇头是否与食物重合
        if snake_position == food_position:
            food_spawned = 0
            score += 1
        else:
            snake_body.pop()

        # 重新生成食物
        if not food_spawned:
            food_position = [random.randrange(1, screen_width // 10) * 10,
                             random.randrange(1, screen_height // 10) * 10]
            food_spawned = 1
