import gym
from gym import spaces
import pygame
import numpy as np

RUNNING = 0
WIN = 1
LOSE = 2

TEXT_HEIGHT = 40
GRID_SIZE = 10
GRID_BORDER = 0

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

ROAD = 0
WALL = 1
FOOD = 2
SNAKE_HEAD = 3
SNAKE_BODY = 4
GRID_TYPE_MAX = 5

OBSERVATION_SPACE_SIZE = 11


class GreedySnakeWorldEnv(gym.Env):

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 4
    }

    def __init__(self, render_mode=None, world_size=30, render_fps=4):
        self.metadata["render_fps"] = render_fps

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.window = None
        self.clock = None

        self.world_size = world_size
        self.world_shape = (world_size, world_size)
        self.world_grid_count = world_size * world_size

        self.window_size = world_size * (GRID_SIZE + GRID_BORDER) + GRID_BORDER

        self.loop_frame_count_limit = world_size * 4

        self.action_space = spaces.Discrete(4)
        self.action_to_direction = {
            UP: np.array([0, -1]),
            DOWN: np.array([0, 1]),
            LEFT: np.array([-1, 0]),
            RIGHT: np.array([1, 0]),
        }

        # self.observation_space = spaces.Dict({
        #     # "world": spaces.Box(0, GRID_TYPE_MAX - 1, shape=(world_size * world_size,), dtype=np.int32),
        #     "food": spaces.Box(0, world_size-1, shape=(2,), dtype=np.int32),
        #     "snake_direction": spaces.Box(0, world_size-1, shape=(2,), dtype=np.int32),
        #     "snake_head": spaces.Box(0, world_size-1, shape=(2,), dtype=np.int32),
        #     # "snake_tail": spaces.Box(0, world_size-1, shape=(2,), dtype=np.int32),
        # })
        self.observation_space = spaces.Box(
            0, 1, shape=(OBSERVATION_SPACE_SIZE,), dtype=np.bool_)

    def _is_collision(self, location=None):
        if location is None:
            location = self.snake_locations[0]
        # 检查是否撞墙
        if self.world[location[0], location[1]] == WALL:
            return True
        # 检查是否撞到身体
        for i in range(1, len(self.snake_locations) - 1):
            if np.linalg.norm(location - self.snake_locations[i]) == 0:
                return True

        return False

    def _get_obs(self):
        # return {
        #     # "world": self.world.flatten(),
        #     "food": self.food_location,
        #     "snake_direction": self.snake_direction,
        #     "snake_head": np.array(self.snake_locations[0]),
        #     # "snake_tail": np.array(self.snake_locations[-1]),
        # }
        snake_direction = self.snake_direction
        snake_head_location = self.snake_locations[0]
        food_location = self.food_location

        snake_head_location_up = (
            snake_head_location + self.action_to_direction[UP])
        snake_head_location_down = (
            snake_head_location + self.action_to_direction[DOWN])
        snake_head_location_left = (
            snake_head_location + self.action_to_direction[LEFT])
        snake_head_location_right = (
            snake_head_location + self.action_to_direction[RIGHT])

        snake_direction_up = all(
            snake_direction == self.action_to_direction[UP])
        snake_direction_down = all(
            snake_direction == self.action_to_direction[DOWN])
        snake_direction_left = all(
            snake_direction == self.action_to_direction[LEFT])
        snake_direction_right = all(
            snake_direction == self.action_to_direction[RIGHT])

        return [
            # Danger straight
            (snake_direction_up and self._is_collision(snake_head_location_up)) or
            (snake_direction_down and self._is_collision(snake_head_location_down)) or
            (snake_direction_left and self._is_collision(snake_head_location_left)) or
            (snake_direction_right and self._is_collision(snake_head_location_right)),

            # Danger right
            (snake_direction_up and self._is_collision(snake_head_location_right)) or
            (snake_direction_down and self._is_collision(snake_head_location_left)) or
            (snake_direction_left and self._is_collision(snake_head_location_up)) or
            (snake_direction_right and self._is_collision(snake_head_location_down)),

            # Danger left
            (snake_direction_up and self._is_collision(snake_head_location_left)) or
            (snake_direction_down and self._is_collision(snake_head_location_right)) or
            (snake_direction_left and self._is_collision(snake_head_location_down)) or
            (snake_direction_right and self._is_collision(snake_head_location_up)),

            # Move Dir
            snake_direction_up,
            snake_direction_down,
            snake_direction_left,
            snake_direction_right,

            # Food location
            food_location[0] < snake_head_location[0],  # food left
            food_location[0] > snake_head_location[0],  # food right
            food_location[1] < snake_head_location[1],  # food up
            food_location[1] > snake_head_location[1],   # food down
        ]

    def _get_info(self):
        return {
            "world": self.world,
            "food": self.food_location,
            "snake": np.array(self.snake_locations),
            "observation_space": self._get_obs(),
        }

    def _init_world(self):
        # 构造一个空的世界
        self.world = np.zeros(self.world_shape, dtype=np.int32)
        # 在四周填充墙壁
        for x in range(0, self.world_size):
            for y in range(0, self.world_size):
                if x == 0 or x == self.world_size - 1 or y == 0 or y == self.world_size - 1:
                    self.world[x, y] = WALL

    def _init_snake(self):
        world_size_half = int(self.world_size / 2)
        location = np.array([world_size_half, world_size_half])
        self.snake_locations = []
        self.snake_locations.append(location)
        self.world[location[0], location[1]] = SNAKE_HEAD

        for i in range(0, 3):
            location = location + self.action_to_direction[DOWN]
            self.snake_locations.append(location)
            self.world[location[0], location[1]] = SNAKE_BODY
        self.snake_direction = self.action_to_direction[UP]

    def _create_food(self):
        count = self.np_random.integers(
            0, self.world_grid_count, size=1, dtype=np.int32)
        while_count = 0
        while True:
            x = int(count / self.world_size)
            y = int(count % self.world_size)
            if self.world[x, y] == ROAD:
                self.food_location = np.array([x, y])
                self.world[x, y] = FOOD
                return True
            count += 1
            count %= self.world_grid_count
            while_count += 1

            if while_count > self.world_grid_count:
                break
        return False

    def _move_snake(self, action):
        if self.world_state != RUNNING:
            return
        # 监测移动方向是否合法
        old_direction = self.snake_direction
        new_direction = self.action_to_direction[action]
        if np.linalg.norm(old_direction + new_direction) == 0:
            return

        self.frame_index += 1
        # 计算新的蛇头
        old_snake_head_location = self.snake_locations[0]
        new_snake_head_location = old_snake_head_location + new_direction
        # 检查是否撞墙
        if self.world[new_snake_head_location[0], new_snake_head_location[1]] == WALL:
            self.world_state = LOSE
            return
        # 检查是否撞到身体
        for i in range(1, len(self.snake_locations) - 1):
            if np.linalg.norm(new_snake_head_location - self.snake_locations[i]) == 0:
                self.world_state = LOSE
                return
        # 检测是否吃到食物
        if self.world[new_snake_head_location[0], new_snake_head_location[1]] == FOOD:
            self.score += 1
            self.loop_frame_count = 0
            self.world[old_snake_head_location[0],
                       old_snake_head_location[1]] = SNAKE_BODY
            self.world[new_snake_head_location[0],
                       new_snake_head_location[1]] = SNAKE_HEAD
            self.snake_locations.insert(0, new_snake_head_location)
            self.snake_direction = new_direction
            # 创建食物失败标识地图已经没有可以防止食物的位置
            if not self._create_food():
                self.world_state = WIN
            return
        # 这里处理只是移动的情况
        old_snake_tail_location = self.snake_locations[-1]
        self.world[old_snake_tail_location[0],
                   old_snake_tail_location[1]] = ROAD
        self.snake_locations.pop()
        self.world[old_snake_head_location[0],
                   old_snake_head_location[1]] = SNAKE_BODY
        self.world[new_snake_head_location[0],
                   new_snake_head_location[1]] = SNAKE_HEAD
        self.snake_locations.insert(0, new_snake_head_location)
        self.snake_direction = new_direction

        self.loop_frame_count += 1
        if self.loop_frame_count >= self.loop_frame_count_limit:
            self.score -= 1
            self.loop_frame_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # 初始化参数
        # 分数
        self.score = 0
        # 帧数
        self.frame_index = 0
        # 食物位置
        self.food_location = np.array([0, 0])
        # 蛇的位置
        self.snake_locations = np.array([0, 0])
        # 蛇当前方向
        self.snake_direction = self.action_to_direction[UP]
        # 循环帧计数
        self.loop_frame_count = 0

        # 初始化世界
        self._init_world()
        # 世界状态
        self.world_state = RUNNING
        # 初始化蛇
        self._init_snake()
        # 创建食物
        self._create_food()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        old_score = self.score

        self._move_snake(action)

        observation = self._get_obs()
        reward = self.score - old_score
        terminated = self.world_state != RUNNING
        truncated = False
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.window_size, self.window_size + TEXT_HEIGHT))
            pygame.display.set_caption("Greedy Snake")
            self.font = pygame.font.SysFont(None, 20)
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface(
            (self.window_size, self.window_size + TEXT_HEIGHT))
        canvas.fill((255, 255, 255))

        for x in range(0, self.world_size):
            for y in range(0, self.world_size):
                grid_type = self.world[x, y]
                color = (255, 255, 255)
                if grid_type == ROAD:
                    color = (127, 127, 127)
                elif grid_type == WALL:
                    color = (0, 0, 0)
                elif grid_type == FOOD:
                    color = (255, 0, 0)
                elif grid_type == SNAKE_HEAD:
                    color = (0, 0, 255)
                elif grid_type == SNAKE_BODY:
                    color = (0, 255, 0)

                pygame.draw.rect(
                    canvas,
                    color,
                    pygame.Rect(
                        (GRID_BORDER + x * (GRID_SIZE + GRID_BORDER),
                         TEXT_HEIGHT + GRID_BORDER + y * (GRID_SIZE + GRID_BORDER)),
                        (GRID_SIZE, GRID_SIZE),
                    ),
                )
        text_score = self.font.render(
            "Score:{}".format(self.score), True, (0, 0, 0))
        text_frame_index = self.font.render(
            "FrameIndex:{}".format(self.frame_index), True, (0, 0, 0))
        canvas.blit(text_score, text_score.get_rect())
        canvas.blit(text_frame_index,
                    text_frame_index.get_rect(topleft=(0, 20)))

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
