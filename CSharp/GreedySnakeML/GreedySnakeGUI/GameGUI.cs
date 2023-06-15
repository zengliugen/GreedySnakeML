namespace GreedySnakeGUI
{
    using GreedySnake;

    public partial class GameGUI : Form
    {
        public Game Game;

        public Bitmap GameImage;
        public Graphics GameImageGraphics;
        public Graphics Graphics;
        public GameGUI()
        {
            this.InitializeComponent();

            this.Game = new Game();

            this.GameImage = new Bitmap(550, 600);
            this.GameImageGraphics = Graphics.FromImage(this.GameImage);
            this.Graphics = this.CreateGraphics();
        }
        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            this.DrawGame();
        }
        public void RestartGame()
        {
            this.Game.Reset();
            this.DrawGame();
        }
        public void DrawGame()
        {
            this.GameImageGraphics.Clear(Color.White);
            for (var i = 0; i < Game.Width; i++)
            {
                for (var j = 0; j < Game.Height; j++)
                {
                    var gridType = this.Game.Map[i, j];
                    Brush brush;
                    switch (gridType)
                    {
                        case EGridType.Road:
                            brush = Brushes.Gray;
                            break;
                        case EGridType.Wall:
                            brush = Brushes.Black;
                            break;
                        case EGridType.SnakeHead:
                            brush = Brushes.Blue;
                            break;
                        case EGridType.SnakeBody:
                            brush = Brushes.Green;
                            break;
                        case EGridType.Food:
                            brush = Brushes.Red;
                            break;
                        default:
                            continue;
                    }
                    var rectangle = new Rectangle((i * 10) + i, (j * 10) + j, 10, 10);
                    this.GameImageGraphics.FillRectangle(brush, rectangle);
                }
            }
            this.GameImageGraphics.DrawString($"FrameIndex:{this.Game.FrameIndex}", this.Font, Brushes.Black, new PointF(10, 560));
            this.GameImageGraphics.DrawString($"Score:{this.Game.Score}", this.Font, Brushes.Black, new PointF(10, 580));

            this.Graphics.DrawImage(this.GameImage, 0, 0);
        }
        private void GameGUI_KeyDown(Object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Up)
            {
                this.Game.SnakeMove(EDirection.Up);
            }
            else if (e.KeyCode == Keys.Down)
            {
                this.Game.SnakeMove(EDirection.Down);
            }
            else if (e.KeyCode == Keys.Left)
            {
                this.Game.SnakeMove(EDirection.Left);
            }
            else if (e.KeyCode == Keys.Right)
            {
                this.Game.SnakeMove(EDirection.Right);
            }
            if (this.Game.GameState == EGameState.Win)
            {
                MessageBox.Show("You Win!");
                this.RestartGame();
            }
            else if (this.Game.GameState == EGameState.Lose)
            {
                MessageBox.Show("You Lose!");
                this.RestartGame();
            }
            else
            {
                this.DrawGame();
            }
        }
    }
}