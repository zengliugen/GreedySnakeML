from gym.envs.registration import register

register(
    id="GreedySnakeWorld-v0",
    entry_point="gym_greedy_snake.envs:GreedySnakeWorldEnv",
)
