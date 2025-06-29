import pygame
import sys
import random
import time

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
GAME_WIDTH, GAME_HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = GAME_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE
BASE_FPS = 10  # 基础速度

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
DARK_GREEN = (0, 100, 0)
GRAY = (40, 40, 40)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (100, 180, 255)
DARK_BLUE = (30, 30, 70)
PANEL_BG = (40, 40, 80)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 180, 255)
GOLD = (255, 215, 0)

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 鼓励话语
ENCOURAGEMENTS = [
    "真棒！继续加油！",
    "干得漂亮！",
    "太厉害了！",
    "你是贪吃蛇大师！",
    "继续前进！",
    "完美表现！",
    "令人印象深刻！"
]

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.font = pygame.font.SysFont('microsoftyahei', 25)
        
    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                return self.action
        return None

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0
        self.speed_level = 2  # 初始速度级别 (1x)
        self.grow_to = 3
        self.last_move_time = time.time()
        self.last_encouragement_score = 0  # 上次显示鼓励语的分数
        self.boosted = False  # 是否处于加速状态
        self.boost_start_time = 0  # 加速开始时间
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        current_time = time.time()
        
        # 计算实际速度
        base_speeds = [0.5 * BASE_FPS, 0.75 * BASE_FPS, BASE_FPS, 1.5 * BASE_FPS, 2 * BASE_FPS]
        current_speed = base_speeds[self.speed_level]
        
        # 如果处于加速状态，速度翻倍
        if self.boosted:
            current_speed *= 2
        
        if current_time - self.last_move_time < 1.0 / current_speed:
            return False
            
        self.last_move_time = current_time
        head = self.get_head_position()
        x, y = self.direction
        new_x = head[0] + x
        new_y = head[1] + y
        new_position = (new_x, new_y)
        
        # 检查是否撞墙
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return True
            
        # 检查是否撞到自己
        if new_position in self.positions[1:]:
            return True
            
        self.positions.insert(0, new_position)
        
        if len(self.positions) > self.grow_to:
            self.positions.pop()
            
        return False
    
    def grow(self, points=10):
        self.grow_to += 1
        self.score += points
        
    def change_direction(self, direction):
        # 防止直接反向移动
        if (direction[0] * -1, direction[1] * -1) == self.direction:
            return
        self.direction = direction
        
    def increase_speed(self):
        if self.speed_level < 4:  # 最大速度级别为4 (2x)
            self.speed_level += 1
            
    def decrease_speed(self):
        if self.speed_level > 0:  # 最小速度级别为0 (0.5x)
            self.speed_level -= 1
            
    def get_speed_str(self):
        speeds = ["0.5x", "0.75x", "1x", "1.5x", "2x"]
        if self.boosted:
            return f"{speeds[self.speed_level]} → {float(speeds[self.speed_level][:-1]) * 2}x"
        return speeds[self.speed_level]
    
    def start_boost(self):
        self.boosted = True
        self.boost_start_time = time.time()
    
    def stop_boost(self):
        self.boosted = False
    
    def update_boost(self):
        # 如果加速超过0.5秒，自动停止加速
        if self.boosted and time.time() - self.boost_start_time > 0.5:
            self.boosted = False
            
    def draw(self, surface):
        for i, p in enumerate(self.positions):
            # 蛇头用不同颜色
            color = YELLOW if i == 0 else GREEN
            
            # 如果处于加速状态，使用更亮的颜色
            if self.boosted and i == 0:
                color = ORANGE
            elif self.boosted:
                color = LIGHT_BLUE
                
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, DARK_GREEN, rect, 1)
            
            # 绘制蛇眼睛
            if i == 0:
                eye_size = GRID_SIZE // 5
                # 根据方向确定眼睛位置
                if self.direction == UP:
                    left_eye = (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3)
                    right_eye = (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3)
                elif self.direction == DOWN:
                    left_eye = (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3)
                    right_eye = (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3)
                elif self.direction == LEFT:
                    left_eye = (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3)
                    right_eye = (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3)
                else:  # RIGHT
                    left_eye = (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3)
                    right_eye = (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3)
                
                pygame.draw.circle(surface, BLACK, left_eye, eye_size)
                pygame.draw.circle(surface, BLACK, right_eye, eye_size)

class Food:
    def __init__(self, is_golden=False):
        self.position = (0, 0)
        self.is_golden = is_golden
        self.spawn_time = 0
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        self.spawn_time = time.time()
        
    def draw(self, surface):
        color = GOLD if self.is_golden else RED
        border_color = (200, 170, 0) if self.is_golden else (200, 0, 0)
        
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, border_color, rect, 1)
        
        # 绘制苹果的茎和叶
        stem_rect = pygame.Rect((self.position[0] * GRID_SIZE + GRID_SIZE // 2 - 1, 
                                self.position[1] * GRID_SIZE - GRID_SIZE // 3), 
                               (2, GRID_SIZE // 3))
        stem_color = DARK_GREEN if not self.is_golden else (100, 80, 0)
        pygame.draw.rect(surface, stem_color, stem_rect)
        
        leaf_rect = pygame.Rect((self.position[0] * GRID_SIZE + GRID_SIZE // 2, 
                                self.position[1] * GRID_SIZE - GRID_SIZE // 3), 
                               (GRID_SIZE // 4, GRID_SIZE // 4))
        leaf_color = GREEN if not self.is_golden else (200, 180, 0)
        pygame.draw.ellipse(surface, leaf_color, leaf_rect)
        
        # 如果是金苹果，绘制闪光效果
        if self.is_golden:
            flash_rect = pygame.Rect((self.position[0] * GRID_SIZE - 2, 
                                     self.position[1] * GRID_SIZE - 2), 
                                    (GRID_SIZE + 4, GRID_SIZE + 4))
            pygame.draw.rect(surface, (255, 255, 200), flash_rect, 2, border_radius=3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("贪吃蛇小游戏")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('microsoftyahei', 20)
        self.medium_font = pygame.font.SysFont('microsoftyahei', 25)
        self.big_font = pygame.font.SysFont('microsoftyahei', 30)
        self.encourage_font = pygame.font.SysFont('microsoftyahei', 40, bold=True)
        self.title_font = pygame.font.SysFont('microsoftyahei', 60, bold=True)
        self.snake = Snake()
        self.food = Food()  # 普通食物
        self.golden_food = None  # 金色食物
        self.golden_food_duration = 5  # 金苹果持续时间(秒)
        
        # 鼓励系统
        self.encouragement_text = ""
        self.encouragement_timer = 0
        self.encouragement_duration = 1.0  # 鼓励语显示时间(秒)
        
        # 游戏状态
        self.game_over = False
        self.paused = False
        self.game_started = False
        self.show_help = False
        self.show_rules = False
        
        # 创建按钮
        self.start_button = Button(SCREEN_WIDTH//2 - 100, 250, 200, 50, "开始游戏", "start")
        self.help_button = Button(SCREEN_WIDTH//2 - 100, 320, 200, 50, "按键说明", "help")
        self.rules_button = Button(SCREEN_WIDTH//2 - 100, 390, 200, 50, "游戏规则", "rules")
        self.back_button = Button(SCREEN_WIDTH//2 - 100, 500, 200, 50, "返回主菜单", "back")
        
        # 金苹果生成相关
        self.golden_spawn_score = 100  # 初始金苹果生成分数
        self.golden_active = False  # 金苹果是否激活
        
        # 保存游戏状态
        self.saved_state = None
        
        # 键盘状态跟踪
        self.key_states = {
            pygame.K_UP: {'pressed': False, 'press_time': 0},
            pygame.K_DOWN: {'pressed': False, 'press_time': 0},
            pygame.K_LEFT: {'pressed': False, 'press_time': 0},
            pygame.K_RIGHT: {'pressed': False, 'press_time': 0}
        }
        
    def draw_grid(self):
        for x in range(0, GAME_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, GAME_HEIGHT), 1)
        for y in range(0, GAME_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (GAME_WIDTH, y), 1)
            
    def draw_score_panel(self):
        # 绘制右侧面板背景
        panel_rect = pygame.Rect(GAME_WIDTH, 0, SCREEN_WIDTH - GAME_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        
        # 绘制标题
        title_text = self.big_font.render("游戏状态", True, LIGHT_BLUE)
        self.screen.blit(title_text, (GAME_WIDTH + 40, 20))
        
        # 绘制分数信息
        score_text = self.medium_font.render(f'得分: {self.snake.score}', True, WHITE)
        speed_text = self.medium_font.render(f'速度: {self.snake.get_speed_str()}', True, WHITE)
        length_text = self.medium_font.render(f'长度: {self.snake.grow_to}', True, WHITE)
        
        self.screen.blit(score_text, (GAME_WIDTH + 40, 70))
        self.screen.blit(speed_text, (GAME_WIDTH + 40, 110))
        self.screen.blit(length_text, (GAME_WIDTH + 40, 150))
        
        # 绘制操作说明
        controls_title = self.big_font.render("操作说明", True, LIGHT_BLUE)
        self.screen.blit(controls_title, (GAME_WIDTH + 20, 200))
        
        controls = [
            "方向键: 控制蛇移动",
            "Q: 加速，E: 减速",
            "P: 暂停/继续",
            "R: 重新开始",
            "ESC: 返回主菜单",
            "长按方向键: 临时加速"
        ]
        
        for i, text in enumerate(controls):
            inst = self.medium_font.render(text, True, WHITE)
            self.screen.blit(inst, (GAME_WIDTH + 40, 240 + i * 35))
        
        # 绘制游戏提示
        tips_title = self.big_font.render("游戏提示", True, LIGHT_BLUE)
        self.screen.blit(tips_title, (GAME_WIDTH + 20, 440))
        
        tips = [
            "避免撞墙或撞到自己",
            "金色苹果=3倍分数",
            "长按方向键可加速",
            "速度越快难度越大",
        ]
        
        for i, text in enumerate(tips):
            tip = self.medium_font.render(text, True, YELLOW)
            self.screen.blit(tip, (GAME_WIDTH + 40, 480 + i * 30))
        
    def draw_game_over(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render('游戏结束!', True, RED)
        score_text = self.medium_font.render(f'最终得分: {self.snake.score}', True, WHITE)
        restart_text = self.medium_font.render('按 R 键重新开始', True, GREEN)
        menu_text = self.medium_font.render('按 ESC 返回主菜单', True, LIGHT_BLUE)
        
        self.screen.blit(game_over_text, (GAME_WIDTH // 2 - game_over_text.get_width() // 2, GAME_HEIGHT // 2 - 80))
        self.screen.blit(score_text, (GAME_WIDTH // 2 - score_text.get_width() // 2, GAME_HEIGHT // 2 - 20))
        self.screen.blit(restart_text, (GAME_WIDTH // 2 - restart_text.get_width() // 2, GAME_HEIGHT // 2 + 40))
        self.screen.blit(menu_text, (GAME_WIDTH // 2 - menu_text.get_width() // 2, GAME_HEIGHT // 2 + 100))
        
    def draw_pause(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0)) 
        
        pause_text = self.big_font.render('游戏暂停', True, YELLOW)
        continue_text = self.medium_font.render('按 P 键继续游戏', True, GREEN)
        menu_text = self.medium_font.render('按 ESC 返回主菜单', True, LIGHT_BLUE)
        
        self.screen.blit(pause_text, (GAME_WIDTH // 2 - pause_text.get_width() // 2, GAME_HEIGHT // 2 - 60))
        self.screen.blit(continue_text, (GAME_WIDTH // 2 - continue_text.get_width() // 2, GAME_HEIGHT // 2))
        self.screen.blit(menu_text, (GAME_WIDTH // 2 - menu_text.get_width() // 2, GAME_HEIGHT // 2 + 60))
        
    def draw_encouragement(self):
        if self.encouragement_timer > 0:
            # 计算透明度 (0-255)
            alpha = min(255, int(self.encouragement_timer * 510))
            
            # 创建文字表面
            text_surf = self.encourage_font.render(self.encouragement_text, True, (255, 255, 0))
            
            # 添加背景效果
            bg_rect = pygame.Rect(0, 0, text_surf.get_width() + 40, text_surf.get_height() + 20)
            bg_rect.center = (GAME_WIDTH // 2, GAME_HEIGHT // 2 - 100)
            
            # 绘制半透明背景
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, alpha//3), (0, 0, bg_rect.width, bg_rect.height), border_radius=10)
            pygame.draw.rect(bg_surf, (255, 215, 0, alpha), (0, 0, bg_rect.width, bg_rect.height), 3, border_radius=10)
            self.screen.blit(bg_surf, bg_rect)
            
            # 绘制文字
            text_rect = text_surf.get_rect(center=bg_rect.center)
            text_surf.set_alpha(alpha)
            self.screen.blit(text_surf, text_rect)
        
    def draw_start_screen(self):
        self.screen.fill(DARK_BLUE)
        
        # 绘制标题
        title_text = self.title_font.render("贪吃蛇游戏", True, GREEN)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - 50))
        
        # 绘制蛇的图案
        snake_positions = [
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20),
            (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20),
            (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 20),
            (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 20),
            (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 20),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        ]
        
        for i, pos in enumerate(snake_positions):
            color = YELLOW if i == len(snake_positions) - 1 else GREEN
            pygame.draw.rect(self.screen, color, (pos[0], pos[1], 20, 20))
            pygame.draw.rect(self.screen, DARK_GREEN, (pos[0], pos[1], 20, 20), 1)
        
        # 绘制食物
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH // 2 + 40, SCREEN_HEIGHT // 2 - 20, 20, 20))
        
        # 绘制金色苹果
        pygame.draw.rect(self.screen, GOLD, (SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 - 20, 20, 20))
        
        # 绘制按钮
        self.start_button.draw(self.screen)
        self.help_button.draw(self.screen)
        self.rules_button.draw(self.screen)
        
        # 绘制作者信息
        author_text = self.medium_font.render("Python贪吃蛇游戏   作者：贺巍", True, PURPLE)
        self.screen.blit(author_text, (SCREEN_WIDTH // 2 - author_text.get_width() // 2, SCREEN_HEIGHT - 40))
        
    def draw_help_screen(self):
        self.screen.fill(DARK_BLUE)
        
        # 绘制标题
        title_text = self.title_font.render("按键说明", True, GREEN)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # 绘制按键说明内容
        controls = [
            "方向键: 控制蛇的移动方向",
            "Q: 增加蛇的移动速度",
            "E: 减少蛇的移动速度",
            "P: 暂停/继续游戏",
            "R: 重新开始游戏",
            "ESC: 返回主菜单",
            "长按方向键: 临时加速"
        ]
        
        for i, text in enumerate(controls):
            inst = self.medium_font.render(text, True, LIGHT_BLUE)
            self.screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 150 + i * 50))
        
        # 绘制返回按钮
        self.back_button.draw(self.screen)
        
    def draw_rules_screen(self):
        self.screen.fill(DARK_BLUE)
        
        # 绘制标题
        title_text = self.title_font.render("游戏规则", True, GREEN)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # 绘制规则内容
        rules = [
            "1. 蛇撞墙或撞到自己游戏结束,长蛇建议使用较低速度",
            "2. 苹果会使蛇长度增加,每吃一个红苹果得10分",
            "3. 速度共有5个级别:- 0.5x, 0.75x, 1x, 1.5x, 2x",
            "4. 按Q键加速，按E键减速,长按方向键可临时加速",
            "5. 每获得100分，会出现一个金色苹果",
            "6. 金色苹果5秒后消失，吃掉得30分",
            "7. 每获得100分会受到鼓励哟(^▽^)！",
        ]
        
        for i, text in enumerate(rules):
            rule = self.medium_font.render(text, True, YELLOW)
            self.screen.blit(rule, (SCREEN_WIDTH // 2 - rule.get_width() // 2, 120 + i * 40))
        
        # 绘制返回按钮
        self.back_button.draw(self.screen)
        
    def spawn_golden_food(self):
        """在达到100分倍数时生成金色苹果"""
        if self.golden_food is None and self.snake.score >= self.golden_spawn_score:
            self.golden_food = Food(is_golden=True)
            self.golden_food.randomize_position()
            
            # 确保金苹果不在蛇身上
            while self.golden_food.position in self.snake.positions:
                self.golden_food.randomize_position()
                
            # 移除普通食物
            self.food.position = None
            
            # 设置下一个金苹果生成分数
            self.golden_spawn_score += 100
            self.golden_active = True
            
    def update_golden_food(self):
        """更新金色苹果状态"""
        if self.golden_food:
            # 检查金苹果是否过期
            current_time = time.time()
            if current_time - self.golden_food.spawn_time > self.golden_food_duration:
                self.golden_food = None
                self.golden_active = False
                
                # 重新生成普通食物
                self.food.randomize_position()
                while self.food.position in self.snake.positions:
                    self.food.randomize_position()
    
    def check_encouragement(self):
        """检查是否需要显示鼓励语"""
        if self.snake.score >= self.snake.last_encouragement_score + 100:
            self.snake.last_encouragement_score = self.snake.score
            self.encouragement_text = random.choice(ENCOURAGEMENTS)
            self.encouragement_timer = self.encouragement_duration
    
    def update_encouragement(self, dt):
        """更新鼓励语计时器"""
        if self.encouragement_timer > 0:
            self.encouragement_timer -= dt
            
    def save_game_state(self):
        """保存当前游戏状态"""
        return {
            'snake': {
                'positions': self.snake.positions.copy(),
                'direction': self.snake.direction,
                'score': self.snake.score,
                'speed_level': self.snake.speed_level,
                'grow_to': self.snake.grow_to,
                'last_encouragement_score': self.snake.last_encouragement_score,
                'boosted': self.snake.boosted,
                'boost_start_time': self.snake.boost_start_time
            },
            'food': self.food.position if self.food else None,
            'golden_food': self.golden_food.position if self.golden_food else None,
            'golden_spawn_score': self.golden_spawn_score,
            'golden_active': self.golden_active,
            'encouragement_text': self.encouragement_text,
            'encouragement_timer': self.encouragement_timer,
            'paused': self.paused
        }
    
    def restore_game_state(self, state):
        """恢复保存的游戏状态"""
        if state:
            # 恢复蛇的状态
            self.snake.positions = state['snake']['positions'].copy()
            self.snake.direction = state['snake']['direction']
            self.snake.score = state['snake']['score']
            self.snake.speed_level = state['snake']['speed_level']
            self.snake.grow_to = state['snake']['grow_to']
            self.snake.last_encouragement_score = state['snake']['last_encouragement_score']
            self.snake.boosted = state['snake']['boosted']
            self.snake.boost_start_time = state['snake']['boost_start_time']
            
            # 恢复食物状态
            if state['food']:
                self.food.position = state['food']
            else:
                self.food.randomize_position()
                
            # 恢复金苹果状态
            if state['golden_food']:
                self.golden_food = Food(is_golden=True)
                self.golden_food.position = state['golden_food']
            else:
                self.golden_food = None
                
            # 恢复其他状态
            self.golden_spawn_score = state['golden_spawn_score']
            self.golden_active = state['golden_active']
            self.encouragement_text = state['encouragement_text']
            self.encouragement_timer = state['encouragement_timer']
            self.paused = state['paused']
    
    def update_key_states(self):
        """更新按键状态并检测长按"""
        current_time = time.time()
        for key, state in self.key_states.items():
            if state['pressed']:
                # 检查是否长按超过0.2秒
                if current_time - state['press_time'] > 0.2:
                    # 启动加速
                    self.snake.start_boost()
    
    def run(self):
        last_time = time.time()
        
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            mouse_pos = pygame.mouse.get_pos()
            
            # 更新按钮悬停状态
            if not self.game_started and not self.show_help and not self.show_rules:
                # 主菜单状态
                self.start_button.check_hover(mouse_pos)
                self.help_button.check_hover(mouse_pos)
                self.rules_button.check_hover(mouse_pos)
            elif self.show_help:
                # 按键说明界面
                self.back_button.check_hover(mouse_pos)
            elif self.show_rules:
                # 游戏规则界面
                self.back_button.check_hover(mouse_pos)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_started:
                            if self.game_over:
                                # 游戏结束状态返回主菜单
                                self.game_started = False
                                self.game_over = False
                                self.paused = False
                                self.saved_state = None
                            else:
                                # 游戏进行中返回主菜单前保存状态
                                self.saved_state = self.save_game_state()
                                self.game_started = False
                        elif self.show_help:
                            self.show_help = False
                        elif self.show_rules:
                            self.show_rules = False
                        else:
                            # 在主菜单按ESC，不做任何操作（不退出）
                            pass
                    
                    # 处理游戏中的按键（包括暂停状态）
                    if self.game_started and not self.game_over:
                        # 记录按键按下时间（仅方向键）
                        if event.key in self.key_states:
                            self.key_states[event.key]['pressed'] = True
                            self.key_states[event.key]['press_time'] = time.time()
                            
                        # 处理方向键按下 - 立即改变方向（仅在非暂停状态）
                        if not self.paused:
                            if event.key == pygame.K_UP:
                                self.snake.change_direction(UP)
                            elif event.key == pygame.K_DOWN:
                                self.snake.change_direction(DOWN)
                            elif event.key == pygame.K_LEFT:
                                self.snake.change_direction(LEFT)
                            elif event.key == pygame.K_RIGHT:
                                self.snake.change_direction(RIGHT)
                        
                        # 处理其他功能键（无论是否暂停都应响应）
                        if event.key == pygame.K_q:
                            self.snake.increase_speed()
                        elif event.key == pygame.K_e:
                            self.snake.decrease_speed()
                        elif event.key == pygame.K_p:  # 将P键处理移出方向键条件块
                            # 切换暂停状态
                            self.paused = not self.paused
                        elif event.key == pygame.K_r:
                            self.snake.reset()
                            self.food.randomize_position()
                            self.golden_food = None
                            self.game_over = False
                            self.golden_spawn_score = 100
                            self.golden_active = False
                    
                    

                    if self.game_over and event.key == pygame.K_r:
                        self.snake.reset()
                        self.food.randomize_position()
                        self.golden_food = None
                        self.game_over = False
                        self.golden_spawn_score = 100
                        self.golden_active = False
                
                if event.type == pygame.KEYUP:
                    # 处理按键释放
                    if event.key in self.key_states:
                        self.key_states[event.key]['pressed'] = False
                        self.snake.stop_boost()
                
                # 处理按钮点击
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.game_started and not self.show_help and not self.show_rules:
                        # 主菜单按钮
                        if self.start_button.hovered:
                            self.game_started = True
                            
                            # 如果有保存的状态，则恢复游戏状态
                            if self.saved_state:
                                self.restore_game_state(self.saved_state)
                            else:
                                # 否则初始化新游戏
                                self.snake.reset()
                                self.food.randomize_position()
                                self.golden_food = None
                                self.golden_spawn_score = 100
                                self.golden_active = False
                                self.game_over = False
                                self.paused = False
                        elif self.help_button.hovered:
                            self.show_help = True
                        elif self.rules_button.hovered:
                            self.show_rules = True
                    elif self.show_help and self.back_button.hovered:
                        self.show_help = False
                    elif self.show_rules and self.back_button.hovered:
                        self.show_rules = False
            
            # 更新按键状态并检测长按
            if self.game_started and not self.paused and not self.game_over:
                self.update_key_states()
                self.snake.update_boost()
            
            # 绘制当前界面
            if self.show_help:
                self.draw_help_screen()
            elif self.show_rules:
                self.draw_rules_screen()
            elif not self.game_started:
                self.draw_start_screen()
            else:
                # 生成和更新金色苹果
                self.spawn_golden_food()
                self.update_golden_food()
                
                # 更新鼓励语
                self.update_encouragement(dt)
                
                # 绘制游戏区域
                self.screen.fill(BLACK, (0, 0, GAME_WIDTH, GAME_HEIGHT))
                self.draw_grid()
                self.snake.draw(self.screen)
                
                # 绘制食物（只有当前存在的食物）
                if self.food.position is not None:
                    self.food.draw(self.screen)
                
                # 绘制金色苹果（如果存在）
                if self.golden_food:
                    self.golden_food.draw(self.screen)
                
                # 绘制鼓励语
                self.draw_encouragement()
                
                # 绘制右侧面板
                self.draw_score_panel()
                
                # 绘制暂停或结束画面
                if self.paused:
                    self.draw_pause()
                elif self.game_over:
                    self.draw_game_over()
                else:
                    # 更新游戏状态
                    self.game_over = self.snake.update()
                    
                    # 检查是否吃到普通食物
                    if self.food.position is not None and self.snake.get_head_position() == self.food.position:
                        self.snake.grow()
                        self.check_encouragement()  # 检查是否需要鼓励
                        self.food.randomize_position()
                        # 确保食物不出现在蛇身上
                        while (self.food.position in self.snake.positions or 
                              (self.golden_food and self.food.position == self.golden_food.position)):
                            self.food.randomize_position()
                    
                    # 检查是否吃到金色食物
                    if self.golden_food and self.snake.get_head_position() == self.golden_food.position:
                        self.snake.grow(30)  # 金色苹果得30分
                        self.check_encouragement()  # 检查是否需要鼓励
                        self.golden_food = None
                        self.golden_active = False
                        
                        # 生成新的普通食物
                        self.food.randomize_position()
                        while self.food.position in self.snake.positions:
                            self.food.randomize_position()
                    
                    # 更新鼓励系统
                    self.check_encouragement()
            
            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()