import turtle
from typing import List, Tuple

from pong.world import World, ImmutablePosition

# Define constants for colors, fonts, etc. if desired
PADDLE_COLOR = "white"
BALL_COLOR = "white"
TEXT_COLOR = "white"
# ... other constants

class Drawer:
    def __init__(self, screen: turtle.Screen, world_width: int, world_height: int):
        self.screen = screen
        self.world_width = world_width
        self.world_height = world_height

        # Screen setup
        self.screen.setup(width=world_width, height=world_height)
        self.screen.bgcolor("black")
        self.screen.tracer(0) # Turn off auto screen updates

        # Create drawing turtles
        self._paddle_left_turtle = self._create_base_turtle()
        self._paddle_right_turtle = self._create_base_turtle()
        self._ball_turtle = self._create_base_turtle()
        self._pen_turtle = self._create_base_turtle()
        self._pen_turtle.hideturtle()

        # Initial configuration (example)
        self._paddle_left_turtle.shape("square")
        self._paddle_right_turtle.shape("square")
        self._ball_turtle.shape("square")
        # Set initial colors, sizes here based on World constants if available

    def _create_base_turtle(self) -> turtle.Turtle:
        """Helper to create a standard turtle for drawing."""
        t = turtle.Turtle()
        t.speed(0) # Fastest drawing speed
        t.color(PADDLE_COLOR) # Default color
        t.penup()
        return t

    def _to_turtle_coords(self, world_pos: ImmutablePosition, obj_width: int = 0, obj_height: int = 0) -> Tuple[float, float]:
        """Converts world (top-left origin) to turtle (center origin) coordinates."""
        # Basic conversion
        tx = world_pos.x - self.world_width / 2
        ty = self.world_height / 2 - world_pos.y

        # Adjust so (tx, ty) represents the center of the object for turtle.goto()
        tx += obj_width / 2
        ty -= obj_height / 2
        return tx, ty

    def update_screen(self):
        self.screen.update()

    def clear_screen(self):
        # More efficient than screen.clear() if turtles are persistent
        self._pen_turtle.clear()
        # Potentially hide game elements if needed
        # self._paddle_left_turtle.hideturtle()
        # self._paddle_right_turtle.hideturtle()
        # self._ball_turtle.hideturtle()

    def draw_world(self, world: World, score: List[int]):
        # --- Clear previous text ---
        self._pen_turtle.clear()

        # --- Ensure turtles are visible ---
        self._paddle_left_turtle.showturtle()
        self._paddle_right_turtle.showturtle()
        self._ball_turtle.showturtle()

        # --- Draw Paddles ---
        lp = world._left_paddle # Need access to internal object state
        lp_pos = lp.position
        lp_h = lp.height
        lp_w = lp.width
        self._paddle_left_turtle.shapesize(stretch_wid=lp_h/20, stretch_len=lp_w/20, outline=None)
        tx, ty = self._to_turtle_coords(lp_pos, lp_w, lp_h)
        self._paddle_left_turtle.goto(tx, ty)

        rp = world._right_paddle
        rp_pos = rp.position
        rp_h = rp.height
        rp_w = rp.width
        self._paddle_right_turtle.shapesize(stretch_wid=rp_h/20, stretch_len=rp_w/20, outline=None)
        tx, ty = self._to_turtle_coords(rp_pos, rp_w, rp_h)
        self._paddle_right_turtle.goto(tx, ty)

        # --- Draw Ball ---
        ball = world._ball
        b_pos = ball.position
        b_size = ball.size
        self._ball_turtle.shapesize(stretch_wid=b_size/20, stretch_len=b_size/20, outline=None)
        tx, ty = self._to_turtle_coords(b_pos, b_size, b_size)
        self._ball_turtle.goto(tx, ty)

        # --- Draw Score ---
        self._pen_turtle.color(TEXT_COLOR)
        score_y = self.world_height / 2 - 50 # Position score near top
        self._pen_turtle.goto(-self.world_width / 4, score_y)
        self._pen_turtle.write(f"{score[0]}", align="center", font=("Courier", 24, "normal"))
        self._pen_turtle.goto(self.world_width / 4, score_y)
        self._pen_turtle.write(f"{score[1]}", align="center", font=("Courier", 24, "normal"))

        # --- Update Screen ---
        self.update_screen()

    def draw_menu(self, title: str, options: List[str], selected_index: int):
        # Hide game elements
        self._paddle_left_turtle.hideturtle()
        self._paddle_right_turtle.hideturtle()
        self._ball_turtle.hideturtle()
        # Clear previous text
        self._pen_turtle.clear()

        self._pen_turtle.color(TEXT_COLOR)
        self._pen_turtle.penup()
        self._pen_turtle.hideturtle()

        # Draw Title
        title_y = self.world_height * 0.3
        self._pen_turtle.goto(0, title_y)
        self._pen_turtle.write(title, align="center", font=("Courier", 30, "bold"))

        # Draw Options
        start_y = title_y - 100
        line_height = 50
        for i, option in enumerate(options):
            y = start_y - i * line_height
            self._pen_turtle.goto(0, y)
            prefix = "> " if i == selected_index else "  "
            self._pen_turtle.write(f"{prefix}{option}", align="center", font=("Courier", 24, "normal"))

        self.update_screen()

# --- End of Drawer Class ---