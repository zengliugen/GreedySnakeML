namespace GreedySnake
{
    using System.Diagnostics.CodeAnalysis;

    public enum EGridType
    {
        Road,
        Wall,
        SnakeHead,
        SnakeBody,
        Food,
    }
    public enum EDirection
    {
        Up,
        Down,
        Left,
        Right,
    }
    public enum EGameState
    {
        Runinig,
        Win,
        Lose,
    }
    public struct Position
    {
        public Int32 X;
        public Int32 Y;
        public Position(Int32 x, Int32 y)
        {
            this.X = x;
            this.Y = y;
        }

        public static Position operator +(Position left, Position right)
        {
            return new Position(left.X + right.X, left.Y + right.Y);
        }
        public static Boolean operator ==(Position left, Position right)
        {
            return left.X == right.X && left.Y == right.Y;
        }
        public static Boolean operator !=(Position left, Position right)
        {
            return left.X != right.X || left.Y != right.Y;
        }
        public override Boolean Equals([NotNullWhen(true)] Object? obj)
        {
            if (obj is Position position)
            {
                return this == position;
            }
            return false;
        }
        public override Int32 GetHashCode()
        {
            return this.X.GetHashCode() ^ this.Y.GetHashCode();
        }
    }
    public class Game
    {
        public const Int32 Width = 50;
        public const Int32 Height = 50;
        public const Int32 GridCount = Width * Height;
        public const Int32 GridTypeMax = 4;

        public Random Random;
        public EGridType[,] Map;
        public List<Position> Snake;
        public EDirection SnakeDirection;
        public Position FoodPosition;

        public EGameState GameState;
        public Int32 Score;
        public Int32 FrameIndex;
        public Game(Int32 seed = 0)
        {
            this.Random = seed == 0 ? new Random() : new Random(seed);
            this.Map = new EGridType[Width, Height];
            this.Snake = new List<Position>();
            this.SnakeDirection = EDirection.Up;
            this.FoodPosition = new Position(-1, -1);
            this.GameState = EGameState.Runinig;
            this.Score = 0;
            this.FrameIndex = 0;

            this.Initialize();
        }
        public void Reset()
        {
            this.SnakeDirection = EDirection.Up;
            this.FoodPosition = new Position(-1, -1);
            this.GameState = EGameState.Runinig;
            this.Score = 0;
            this.FrameIndex = 0;

            this.Initialize();
        }
        public void SnakeMove(EDirection direction)
        {
            Position movePosition;
            switch (direction)
            {
                case EDirection.Up:
                    if (this.SnakeDirection == EDirection.Down)
                    {
                        return;
                    }
                    movePosition = new Position(0, -1);
                    break;
                case EDirection.Down:
                    if (this.SnakeDirection == EDirection.Up)
                    {
                        return;
                    }
                    movePosition = new Position(0, 1);
                    break;
                case EDirection.Left:
                    if (this.SnakeDirection == EDirection.Right)
                    {
                        return;
                    }
                    movePosition = new Position(-1, 0);
                    break;
                case EDirection.Right:
                    if (this.SnakeDirection == EDirection.Left)
                    {
                        return;
                    }
                    movePosition = new Position(1, 0);
                    break;
                default:
                    return;
            }
            var snakeHeadPosition = this.Snake[0];
            var nextSnakeHeadPosition = snakeHeadPosition + movePosition;
            var nextGridType = this.Map[nextSnakeHeadPosition.X, nextSnakeHeadPosition.Y];
            if (nextGridType == EGridType.Food)
            {
                this.SetMapGrid(snakeHeadPosition, EGridType.SnakeBody);
                this.Snake.Insert(0, nextSnakeHeadPosition);
                this.SetMapGrid(nextSnakeHeadPosition, EGridType.SnakeHead);
                this.Score++;
                if (this.CheckIsWin())
                {
                    this.GameState = EGameState.Win;
                    this.FoodPosition = new Position(-1, -1);
                }
                else
                {
                    this.CreateFood();
                }
            }
            else
            {
                var snakeTailPosition = this.Snake[this.Snake.Count - 1];
                this.SetMapGrid(snakeTailPosition, EGridType.Road);
                this.Snake.RemoveAt(this.Snake.Count - 1);
                this.SetMapGrid(snakeHeadPosition, EGridType.SnakeBody);
                this.Snake.Insert(0, nextSnakeHeadPosition);
                nextGridType = this.Map[nextSnakeHeadPosition.X, nextSnakeHeadPosition.Y];
                if (nextGridType == EGridType.Road)
                {
                    this.SetMapGrid(nextSnakeHeadPosition, EGridType.SnakeHead);
                }
                else
                {
                    this.Score = 0;
                    this.GameState = EGameState.Lose;
                }
            }
            this.SnakeDirection = direction;
            this.FrameIndex++;
        }
        private void Initialize()
        {
            this.InitializeMap();
            this.InitializeSnake();
            this.CreateFood();
        }
        private void InitializeMap()
        {
            for (var i = 0; i < Width; i++)
            {
                for (var j = 0; j < Height; j++)
                {
                    if (i == 0 || i == Width - 1 || j == 0 || j == Height - 1)
                    {
                        this.Map[i, j] = EGridType.Wall;
                    }
                    else
                    {
                        this.Map[i, j] = EGridType.Road;
                    }
                }
            }
        }
        private void InitializeSnake()
        {
            this.Snake.Clear();
            var snakePosition = new Position(Width / 2, (Height / 2) - 2);
            this.Snake.Add(snakePosition);
            this.Snake.Add(snakePosition + new Position(0, 1));
            this.Snake.Add(snakePosition + new Position(0, 2));
            this.Snake.Add(snakePosition + new Position(0, 3));
            for (var i = 0; i < this.Snake.Count; i++)
            {
                this.SetMapGrid(this.Snake[i], i == 0 ? EGridType.SnakeHead : EGridType.SnakeBody);
            }
            this.SnakeDirection = EDirection.Up;
        }
        private void CreateFood()
        {
            this.FoodPosition = this.RandomFoodPosition();
            this.SetMapGrid(this.FoodPosition, EGridType.Food);
        }
        private void SetMapGrid(Position position, EGridType gridType)
        {
            this.Map[position.X, position.Y] = gridType;
        }
        private Position RandomFoodPosition()
        {
            var count = this.Random.Next(GridCount);
            while (true)
            {
                var x = count / Width;
                var y = count % Width;
                if (this.Map[x, y] == EGridType.Road)
                {
                    return new Position(x, y);
                }
                count++;
                count %= GridCount;
            }
        }
        private Boolean CheckIsWin()
        {
            for (var i = 0; i < Width; i++)
            {
                for (var j = 0; j < Width; j++)
                {
                    if (this.Map[i, j] == EGridType.Road)
                    {
                        return false;
                    }
                }
            }
            return true;
        }
    }
}