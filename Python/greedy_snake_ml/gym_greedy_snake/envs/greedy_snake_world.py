import gym
from gym import spaces
import pygame
import numpy as np

RUNNING = 0
WIN = 1
LOSE = 2

GRID_SIZE = 10
GRID_BORDER = 1

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


class GreedySnakeWorldEnv(gym.Env):

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 4
    }

    def __init__(self, render_mode=None, world_size=50, render_fps=4):
        self.metadata["render_fps"] = render_fps

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.window = None
        self.clock = None

        self.world_size = world_size
        self.world_shape = (world_size, world_size)
        self.world_grid_count = world_size * world_size

        self.window_size = world_size * (GRID_SIZE + GRID_BORDER) + GRID_BORDER

        self.action_space = spaces.Discrete(4)
        self._action_to_direction = {
            UP: np.array([0, -1]),
            DOWN: np.array([0, 1]),
            LEFT: np.array([-1, 0]),
            RIGHT: np.array([1, 0]),
        }

        self.observation_space = spaces.Dict({
            "world": spaces.Box(0, GRID_TYPE_MAX - 1, shape=(world_size * world_size,), dtype=int),
            "food": spaces.Box(0, world_size-1, shape=(2,), dtype=int),
            "snake_head": spaces.Box(0, world_size-1, shape=(2,), dtype=int),
            "snake_tail": spaces.Box(0, world_size-1, shape=(2,), dtype=int),
        })

    def _get_obs(self):
        return {
            "world": self._world.flatten(),
            "food": self._food_location,
            "snake_head": np.array(self._snake_locations[0]),
            "snake_tail": np.array(self._snake_locations[-1]),
        }

    def _get_info(self):
        return {
            "world": self._world,
            "food": self._food_location,
            "snake": np.array(self._snake_locations),
        }

    def _init_world(self):
        # 构造一个空的世界
        self._world = np.zeros(self.world_shape, dtype=int)
        # 在四周填充墙壁
        for x in range(0, self.world_size):
            for y in range(0, self.world_size):
                if x == 0 or x == self.world_size - 1 or y == 0 or y == self.world_size - 1:
                    self._world[x, y] = WALL

    def _init_snake(self):
        world_size_half = int(self.world_size / 2)
        location = np.array([world_size_half, world_size_half])
        self._snake_locations = []
        self._snake_locations.append(location)
        self._world[location[0], location[1]] = SNAKE_HEAD

        for i in range(0, 3):
            location = location + self._action_to_direction[DOWN]
            self._snake_locations.append(location)
            self._world[location[0], location[1]] = SNAKE_BODY

    def _create_food(self):
        count = self.np_random.integers(
            0, self.world_grid_count, size=1, dtype=int)
        while_count = 0
        while True:
            x = int(count / self.world_size)
            y = int(count % self.world_size)
            if self._world[x, y] == ROAD:
                self._food_location = np.array([x, y])
                self._world[x, y] = FOOD
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
        new_direction = self._action_to_direction[action]
        if np.linalg.norm(old_direction + new_direction) == 0:
            return

        self.frame_index += 1
        # 计算新的蛇头
        old_snake_head_location = self._snake_locations[0]
        new_snake_head_location = old_snake_head_location + new_direction
        # 检查是否撞墙
        if self._world[new_snake_head_location[0], new_snake_head_location[1]] == WALL:
            self.world_state = LOSE
            return
        # 检查是否撞到身体
        for i in range(1, len(self._snake_locations) - 1):
            if np.linalg.norm(new_snake_head_location - self._snake_locations[i]) == 0:
                self.world_state = LOSE
                return
        # 检测是否吃到食物
        if self._world[new_snake_head_location[0], new_snake_head_location[1]] == FOOD:
            self.score += 1
            self._world[old_snake_head_location[0],
                        old_snake_head_location[1]] = SNAKE_BODY
            self._world[new_snake_head_location[0],
                        new_snake_head_location[1]] = SNAKE_HEAD
            self._snake_locations.insert(0, new_snake_head_location)
            self.snake_direction = new_direction
            # 创建食物失败标识地图已经没有可以防止食物的位置
            if not self._create_food():
                self.world_state = WIN
            return
        # 这里处理只是移动的情况
        old_snake_tail_location = self._snake_locations[-1]
        self._world[old_snake_tail_location[0],
                    old_snake_tail_location[1]] = ROAD
        self._snake_locations.pop()
        self._world[old_snake_head_location[0],
                    old_snake_head_location[1]] = SNAKE_BODY
        self._world[new_snake_head_location[0],
                    new_snake_head_location[1]] = SNAKE_HEAD
        self._snake_locations.insert(0, new_snake_head_location)
        self.snake_direction = new_direction

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # 初始化世界
        self._init_world()
        # 初始化蛇
        self._init_snake()
        # 创建食物
        self._create_food()
        # 初始化参数
        # 分数
        self.score = 0
        # 帧数
        self.frame_index = 0
        # 蛇当前方向
        self.snake_direction = self._action_to_direction[UP]
        # 世界状态
        self.world_state = RUNNING

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
                (self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))

        for x in range(0, self.world_size):
            for y in range(0, self.world_size):
                grid_type = self._world[x, y]
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
                        (x * (GRID_SIZE + GRID_BORDER),
                         y * (GRID_SIZE + GRID_BORDER)),
                        (GRID_SIZE, GRID_SIZE),
                    ),
                )

        pygame.display.set_caption(
            "Greedy Snake(Score:{} FrameIndex:{})".format(self.score, self.frame_index))

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
