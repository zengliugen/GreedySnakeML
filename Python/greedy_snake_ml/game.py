import pygame
import gym
import gym_greedy_snake

env = gym.make('GreedySnakeWorld-v0', render_mode="human", render_fps=30)

observation = None
reward = None
terminated = None
truncated = None
info = None

observation, info = env.reset()

for _ in range(0, 1000):
    observation, reward, terminated, truncated, info = env.step(
        env.action_space.sample())
    if terminated:
        env.reset()

env.close()

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
