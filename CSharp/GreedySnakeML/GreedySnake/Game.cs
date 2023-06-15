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
        public Int32 Width;
        public Int32 Height;
        public Int32 GridCount;
        public EGridType[,] Map;
        public List<Position> Snake;
        public Random Random;
        public Int32 Score;
        public EGameState GameState;
        public EDirection LastMoveDirection = EDirection.Up;
        public Int32 FrameIndex = 0;
        public Game(Int32 width, Int32 height)
        {
            this.Width = width;
            this.Height = height;
            this.GridCount = this.Width * this.Height;
            this.Map = new EGridType[this.Width, this.Height];
            this.Snake = new List<Position>();
            this.Random = new Random();
            this.Score = 0;
            this.GameState = EGameState.Runinig;
            this.FrameIndex = 0;

            this.Initialize();
        }
        private void Initialize()
        {
            this.InitializeMap();
            this.InitializeSnake();
            this.CreateFood();
        }
        private void InitializeMap()
        {
            for (var i = 0; i < this.Width; i++)
            {
                for (var j = 0; j < this.Height; j++)
                {
                    if (i == 0 || i == this.Width - 1 || j == 0 || j == this.Height - 1)
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
            var snakePosition = new Position(this.Width / 2, (this.Height / 2) - 2);
            this.Snake.Add(snakePosition);
            this.Snake.Add(snakePosition + new Position(0, 1));
            this.Snake.Add(snakePosition + new Position(0, 2));
            this.Snake.Add(snakePosition + new Position(0, 3));
            for (var i = 0; i < this.Snake.Count; i++)
            {
                this.SetMapGrid(this.Snake[i], i == 0 ? EGridType.SnakeHead : EGridType.SnakeBody);
            }
            this.LastMoveDirection = EDirection.Up;
        }
        private void CreateFood()
        {
            var foodPosition = this.RandomFoodPosition();
            this.SetMapGrid(foodPosition, EGridType.Food);
        }
        private void SetMapGrid(Position position, EGridType gridType)
        {
            this.Map[position.X, position.Y] = gridType;
        }
        private Position RandomFoodPosition()
        {
            var count = this.Random.Next(this.GridCount);
            while (true)
            {
                var x = count / this.Width;
                var y = count % this.Width;
                if (this.Map[x, y] == EGridType.Road)
                {
                    return new Position(x, y);
                }
                count++;
                count %= this.GridCount;
            }
        }
        private Boolean CheckIsWin()
        {
            for (var i = 0; i < this.Width; i++)
            {
                for (var j = 0; j < this.Width; j++)
                {
                    if (this.Map[i, j] == EGridType.Road)
                    {
                        return false;
                    }
                }
            }
            return true;
        }
        public void SnakeMove(EDirection direction)
        {
            Position movePosition;
            switch (direction)
            {
                case EDirection.Up:
                    if (this.LastMoveDirection == EDirection.Down)
                    {
                        return;
                    }
                    movePosition = new Position(0, -1);
                    break;
                case EDirection.Down:
                    if (this.LastMoveDirection == EDirection.Up)
                    {
                        return;
                    }
                    movePosition = new Position(0, 1);
                    break;
                case EDirection.Left:
                    if (this.LastMoveDirection == EDirection.Right)
                    {
                        return;
                    }
                    movePosition = new Position(-1, 0);
                    break;
                case EDirection.Right:
                    if (this.LastMoveDirection == EDirection.Left)
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
                this.CreateFood();
                this.Score++;
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
                    if (this.CheckIsWin())
                    {
                        this.GameState = EGameState.Win;
                    }
                }
                else
                {
                    this.GameState = EGameState.Lose;
                }
            }
            this.LastMoveDirection = direction;
            this.FrameIndex++;
        }
    }
}