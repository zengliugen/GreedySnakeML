import pygame
import gym
import gym_greedy_snake

from stable_baselines3 import DQN
from stable_baselines3.common.vec_env.dummy_vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy

import os.path


observation = None
reward = None
terminated = None
truncated = None
info = None

model_path = "./model/GreddySnake-v0.model"
model_buffer_path = "./model/GreddySnake-v0.model_buffer"
tensorboard_log_path = "./tensorboard/GreddySnake-v0/"

# env = gym.make('GreedySnakeWorld-v0', render_mode="human", render_fps=30)

# observation, info = env.reset()

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             env.close()
#         elif event.type == pygame.KEYDOWN:
#             isSetp = False
#             if event.key == pygame.K_UP:
#                 observation, reward, terminated, truncated, info = env.step(0)
#                 isSetp = True
#             elif event.key == pygame.K_DOWN:
#                 observation, reward, terminated, truncated, info = env.step(1)
#                 isSetp = True
#             elif event.key == pygame.K_LEFT:
#                 observation, reward, terminated, truncated, info = env.step(2)
#                 isSetp = True
#             elif event.key == pygame.K_RIGHT:
#                 observation, reward, terminated, truncated, info = env.step(3)
#                 isSetp = True

#             if isSetp and terminated:
#                 env.reset()

# for _ in range(0, 1000):
#     observation, reward, terminated, truncated, info = env.step(
#         env.action_space.sample())
#     if terminated:
#         env.reset()

# env = gym.make('GreedySnakeWorld-v0', render_mode="human", render_fps=300)
# env = gym.make('GreedySnakeWorld-v0')

# env = DummyVecEnv([lambda: env])

# # while True:
# model = None

# if os.path.exists(model_path):
#     model = DQN.load(model_path)
#     model.load_replay_buffer(model_buffer_path)
# else:
#     model = DQN(
#         "MlpPolicy",
#         env=env,
#         learning_rate=2.3e-3,
#         batch_size=64,
#         buffer_size=100000,
#         learning_starts=1000,
#         gamma=0.99,
#         target_update_interval=10,
#         train_freq=256,
#         gradient_steps=128,
#         exploration_fraction=0.16,
#         exploration_final_eps=0.04,
#         policy_kwargs={"net_arch": [256, 256]},
#         verbose=1,
#         tensorboard_log=tensorboard_log_path,
#         device="cuda",
#     )

# model.set_env(env, force_reset=True)

# model.learn(total_timesteps=1e6)

# model.save(model_path)

# model.save_replay_buffer(model_buffer_path)

env = gym.make('GreedySnakeWorld-v0', render_mode="human",
               world_size=50, render_fps=120)
# env = gym.make('GreedySnakeWorld-v0')

env = DummyVecEnv([lambda: env])

model = DQN.load(model_path)

observation = env.reset()

best_score = 0

for i in range(0, 100):
    score = 0
    terminated = False

    while not terminated:
        action, _ = model.predict(observation=observation)
        observation, reward, terminated, info = env.step(action)
        score += reward
        env.render()
    if score > best_score:
        best_score = score
    print("index:{} score:{} best_score:{}".format(i, score, best_score))

env.close()

print("over")
