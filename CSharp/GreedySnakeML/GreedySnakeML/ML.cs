namespace GreedySnakeML
{
    using System.Collections;
    using System.Reflection.Metadata.Ecma335;

    using GreedySnake;

    using Tensorflow;
    using Tensorflow.Keras.Engine;
    using Tensorflow.NumPy;

    using static Tensorflow.Binding;
    using static Tensorflow.KerasApi;

    public class MLGame
    {
        public const Int32 Depth = 4;

        public Game Game;

        public Single[,,] State;
        public Single Reward;
        public Boolean Done;
        public Object? Info;
        public MLGame(Int32 seed)
        {
            this.Game = new Game(seed);

            this.State = new Single[Game.Width, Game.Height, Depth];
            this.Reward = 0.0f;
            this.Done = false;
            this.Info = null;

            this.ResetState();
        }
        private void ResetState()
        {
            for (var i = 0; i < Game.Width; i++)
            {
                for (var j = 0; j < Game.Height; j++)
                {
                    this.State[i, j, 0] = (Single)this.Game.Map[i, j] / Game.GridTypeMax;
                    this.State[i, j, 1] = (Single)this.Game.Map[i, j] / Game.GridTypeMax;
                    this.State[i, j, 2] = (Single)this.Game.Map[i, j] / Game.GridTypeMax;
                    this.State[i, j, 3] = (Single)this.Game.Map[i, j] / Game.GridTypeMax;
                }
            }
        }
        private void StepState()
        {
            for (var i = 0; i < Game.Width; i++)
            {
                for (var j = 0; j < Game.Height; j++)
                {
                    this.State[i, j, 3] = this.State[i, j, 2];
                    this.State[i, j, 2] = this.State[i, j, 1];
                    this.State[i, j, 1] = this.State[i, j, 0];
                    this.State[i, j, 0] = (Single)this.Game.Map[i, j] / Game.GridTypeMax;
                }
            }
        }
        public Single[,,] Reset()
        {
            this.Game.Reset();
            this.ResetState();
            return this.State;
        }
        public (Single[,,], Single, Boolean, Object?) Step(Int32 action)
        {
            this.Game.SnakeMove((EDirection)action);
            this.Reward = this.Game.Score;
            this.Done = this.Game.GameState != EGameState.Runinig;
            this.StepState();
            return (this.State, this.Reward, this.Done, this.Info);
        }
    }
    public class ML
    {
        public static void run()
        {
            var seed = 42;
            var gamma = 0.99f;
            var epsilon = 1.0f;
            var epsilon_min = 0.1f;
            var epsilon_max = 1.0f;
            var epsilon_interval = epsilon_max - epsilon_min;
            var batch_size = 32;
            var max_steps_per_episode = 10000;

            var env = new MLGame(seed);

            var num_actions = 4;

            IModel create_q_model()
            {
                var inputs = keras.layers.Input((Game.Width, Game.Height, MLGame.Depth));

                var layer1 = keras.layers.Conv2D(32, 8, strides: 4, activation: "relu").Apply(inputs);
                var layer2 = keras.layers.Conv2D(64, 4, strides: 2, activation: "relu").Apply(layer1);
                var layer3 = keras.layers.Conv2D(64, 3, strides: 1, activation: "relu").Apply(layer2);

                var layer4 = keras.layers.Flatten().Apply(layer3);

                var layer5 = keras.layers.Dense(512, activation: "relu").Apply(layer4);
                var action = keras.layers.Dense(num_actions, activation: "linear").Apply(layer5);

                return keras.Model(inputs, action);
            }

            var model = create_q_model();

            var model_target = create_q_model();

            var optimizer = keras.optimizers.Adam(learning_rate: 0.00025f);

            var action_history = new List<Int32>();
            var state_history = new List<Single[,,]>();
            var state_next_history = new List<Single[,,]>();
            var rewards_history = new List<Single>();
            var done_history = new List<Boolean>();
            var episode_reward_history = new List<Single>();
            var running_reward = 0.0f;
            var episode_count = 0;
            var frame_count = 0;

            var epsilon_random_frames = 50000;

            var epsilon_greedy_frames = 1000000.0f;

            var max_memory_length = 100000;

            var update_after_actions = 4;

            var update_target_network = 10000;

            var loss_function = keras.losses.CosineSimilarity();

            while (true)
            {
                var state = env.Reset();

                var episode_reward = 0.0f;

                for (var i = 0; i < max_steps_per_episode; i++)
                {
                    frame_count++;
                    Int32 action;
                    if (frame_count < epsilon_random_frames || epsilon > np.random.random(1)[0])
                    {
                        action = np.random.randint(0, num_actions);
                    }
                    else
                    {
                        var state_tensor = tf.convert_to_tensor(state);
                        state_tensor = tf.expand_dims(state_tensor, 0);
                        var action_probs = model.Apply(state_tensor, training: false);
                        action = tf.arg_max(action_probs[0], 1).numpy();
                    }

                    epsilon -= epsilon_interval / epsilon_greedy_frames;
                    epsilon = Math.Max(epsilon, epsilon_min);

                    var (state_next, reward, done, _) = env.Step(action);
                    //state_next = np.array(state_next);

                    episode_reward += reward;

                    action_history.Add(action);
                    state_history.Add(state);
                    state_next_history.Add(state_next);
                    done_history.Add(done);
                    rewards_history.Add(reward);
                    state = state_next;

                    if (frame_count % update_after_actions == 0 && done_history.Count > batch_size)
                    {
                        var indices = np.random.randint(0, done_history.Count, batch_size);
                        var temp_state_history = new Single[state_history.Count, 50, 50, 4];
                        for (var j = 0; j < state_history.Count; j++)
                        {
                            for (var k = 0; k < Game.Width; k++)
                            {
                                for (var l = 0; l < Game.Height; l++)
                                {
                                    temp_state_history[j, k, l, 0] = state_history[i][k, l, 0];
                                    temp_state_history[j, k, l, 1] = state_history[i][k, l, 1];
                                    temp_state_history[j, k, l, 2] = state_history[i][k, l, 2];
                                    temp_state_history[j, k, l, 3] = state_history[i][k, l, 3];
                                }
                            }
                        }
                        var state_sample = np.array(temp_state_history)[indices];
                        var temp_next_state_history = new Single[state_next_history.Count, 50, 50, 4];
                        for (var j = 0; j < state_history.Count; j++)
                        {
                            for (var k = 0; k < Game.Width; k++)
                            {
                                for (var l = 0; l < Game.Height; l++)
                                {
                                    temp_next_state_history[j, k, l, 0] = state_next_history[i][k, l, 0];
                                    temp_next_state_history[j, k, l, 1] = state_next_history[i][k, l, 1];
                                    temp_next_state_history[j, k, l, 2] = state_next_history[i][k, l, 2];
                                    temp_next_state_history[j, k, l, 3] = state_next_history[i][k, l, 3];
                                }
                            }
                        }
                        var state_next_sample = np.array(temp_next_state_history)[indices];

                        var rewards_sample = np.array(rewards_history.ToArray())[indices];
                        var action_sample = np.array(action_history.ToArray())[indices];
                        var done_sample = np.array(done_history.ToArray())[indices];

                        var future_rewards = model_target.predict(state_next_sample);
                        var updated_q_values = rewards_sample + (gamma * tf.reduce_max(future_rewards, axis: 1));

                        updated_q_values = (updated_q_values * (1 - done_sample)) - done_sample;

                        var masks = tf.one_hot(action_sample, num_actions);

                        using var tape = tf.GradientTape();

                        var q_values = model.Apply(state_sample);
                        var q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis: 2);
                        var loss = loss_function.Call(updated_q_values, q_action);

                        var grads = tape.gradient(loss, model.TrainableVariables);
                        optimizer.apply_gradients(zip(grads, model.TrainableVariables));
                    }

                    if (frame_count % update_target_network == 0)
                    {
                        model_target.set_weights(model.get_weights());
                        print(String.Format("running reward: {0:2f} at episode {1}, frame count {2}", running_reward, episode_count, frame_count));
                    }
                    if (action_history.Count > max_memory_length)
                    {
                        action_history.RemoveAt(0);
                        state_history.RemoveAt(0);
                        state_next_history.RemoveAt(0);
                        rewards_history.RemoveAt(0);
                        done_history.RemoveAt(0);
                    }
                    if (done)
                    {
                        break;
                    }
                }
                episode_reward_history.Add(episode_reward);
                if (episode_reward_history.Count > 100)
                {
                    episode_reward_history.RemoveAt(0);
                }
                running_reward = episode_reward_history.Average();
                episode_count++;
                if (running_reward > 40)
                {
                    print(String.Format("Solved at episode {0}!", episode_count));
                    break;
                }
            }
        }
    }
}