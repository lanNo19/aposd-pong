import dataclasses
import random
from typing import Final, Tuple, Optional, cast, Iterable

from icontract import ensure, require, invariant


class PositiveInt(int):
    @require(lambda value: value > 0)
    def __new__(cls, value: int) -> "PositiveInt":
        return cast(PositiveInt, value)


class NonNegativeInt(int):
    @require(lambda value: value >= 0)
    def __new__(cls, value: int) -> "NonNegativeInt":
        return cast(NonNegativeInt, value)


class ImmutablePosition:
    """
    Represent a position in the game.
    Origin is at the top-left corner.
    """
    _x: int
    _y: int

    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def same_coordinates(self, other: 'ImmutablePosition') -> bool:
        """Check if this position has the same coordinates as another."""
        return self._x == other._x and self._y == other._y


@dataclasses.dataclass
class Position(ImmutablePosition):
    """Represent a mutable position in the game world."""
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

    def update_coordinates(self, other: 'ImmutablePosition') -> None:
        """Update the coordinates to match the other position."""
        self._x = other._x
        self._y = other._y

    def update(self, x: int, y: int) -> None:
        """Update the coordinates to the specified values."""
        self._x = x
        self._y = y


class Speed:
    """
    Represents speed with a magnitude and direction.
    Direction is represented by the sign: positive or negative.
    -1 - left/down
    +1 - right/up
    """
    _value: int  # Magnitude of speed
    _direction: int  # 1 for positive direction, -1 for negative direction in coordinate system

    @require(lambda value: value >= 0)
    def __init__(self, value: int, direction: int = 1) -> None:
        """
        Initialize speed with a magnitude and direction.
        Args:
            value: The magnitude of speed (non-negative)
            direction: 1 for positive direction, -1 for negative direction
        """
        self._value = value
        self._direction = 1 if direction > 0 else -1

    @property
    def value(self) -> int:
        """Get the magnitude of speed."""
        return self._value

    @property
    def direction(self) -> int:
        """Get the direction (1 or -1)."""
        return self._direction

    @property
    def velocity(self) -> int:
        """Get the velocity (speed with direction)."""
        return self._value * self._direction

    def reverse(self) -> None:
        """Reverse the direction of the speed."""
        self._direction *= -1

    def increase(self, amount: int) -> None:
        """Increase the magnitude of speed."""
        self._value += amount

    def decrease(self, amount: int) -> None:
        """Decrease the magnitude of speed, but not below zero."""
        self._value = max(0, self._value - amount)

    def set_value(self, value: int) -> None:
        """Set the magnitude of speed to a new value."""
        self._value = max(0, value)


class Paddle:
    """
    Represents a paddle in the Pong game.
    The paddle can move up and down within the bounds of the playing field.
    """
    position: Position
    height: PositiveInt
    width: PositiveInt
    speed: PositiveInt

    def __init__(self, x: int, y: int, height: int, width: int, speed: int) -> None:
        """Initialize a paddle with position, dimensions and movement speed."""
        self.position = Position(x, y)
        self.height = PositiveInt(height)
        self.width = PositiveInt(width)
        self.speed = PositiveInt(speed)

    def move_up(self, game_height: int) -> None:
        """Move the paddle up, respecting the upper boundary."""
        new_y = max(0, self.position.y - self.speed)
        self.position.update(self.position.x, new_y)

    def move_down(self, game_height: int) -> None:
        """Move the paddle down, respecting the lower boundary."""
        new_y = min(game_height - self.height, self.position.y + self.speed)
        self.position.update(self.position.x, new_y)

    def get_hit_factor(self, ball_y: int) -> float:
        """
        Calculate a factor based on where the ball hit the paddle.
        Returns:
            float: A value between -1.0 (top of paddle) and 1.0 (bottom of paddle)
        """
        # Calculate the relative hit position
        relative_hit = ball_y - self.position.y
        # Normalize to range [-1.0, 1.0]
        # -1.0 means hit at the very top
        # 0.0 means hit at the center
        # 1.0 means hit at the very bottom
        normalized_hit = (relative_hit / self.height) * 2 - 1
        return max(-1.0, min(1.0, normalized_hit))


class Ball:
    """
    Represents the ball in the Pong game, a square
    The ball moves with separate horizontal and vertical speeds.
    """
    position: Position
    size: PositiveInt
    horizontal_speed: Speed
    vertical_speed: Speed
    base_speed: PositiveInt
    max_speed: PositiveInt
    speed_increment: PositiveInt

    def __init__(
            self,
            x: int,
            y: int,
            size: int,
            initial_speed: int,
            max_speed: int,
            speed_increment: int
    ) -> None:
        """
        Initialize a ball with position, size and speed parameters.
        Args:
            x: Initial x-coordinate
            y: Initial y-coordinate
            size: Ball width
            initial_speed: Starting speed value
            max_speed: Maximum speed value
            speed_increment: How much to increase speed after each hit
        """
        self.position = Position(x, y)
        self.size = PositiveInt(size)

        # Randomize initial direction
        h_dir = random.choice([-1, 1])
        v_dir = random.choice([-1, 1])

        self.horizontal_speed = Speed(initial_speed, h_dir)
        # Start with no vertical speed
        self.vertical_speed = Speed(0, v_dir)

        self.base_speed = PositiveInt(initial_speed)
        self.max_speed = PositiveInt(max_speed)
        self.speed_increment = PositiveInt(speed_increment)

    def update_position(self) -> None:
        """Update the ball's position based on its speeds."""
        new_x = self.position.x + self.horizontal_speed.velocity
        new_y = self.position.y + self.vertical_speed.velocity
        next_ball: Position
        next_ball = Position(x = new_x, y = new_y)
        self.position.update_coordinates(next_ball)

    def bounce_horizontal(self) -> None:
        """Bounce off a horizontal surface (top/bottom wall)."""
        self.vertical_speed.reverse()

    def bounce_vertical(self, hit_factor: float) -> None:
        """
        Bounce off a vertical surface (paddle) with angle determined by hit location.
        Args:
            hit_factor: Value from -1.0 to 1.0 indicating where the paddle was hit
                       (-1.0 = top, 0.0 = center, 1.0 = bottom)
        """
        # Reverse horizontal direction
        self.horizontal_speed.reverse()

        # Increase horizontal speed after each hit, up to max_speed
        new_h_speed = min(
            self.horizontal_speed.value + self.speed_increment,
            self.max_speed
        )
        self.horizontal_speed.set_value(new_h_speed)

        # Adjust vertical speed based on hit factor
        # Determine the desired vertical speed magnitude based on how far from center the paddle was hit.
        # abs(hit_factor) ranges from 0 (center) to 1 (edge).
        # Scale this by self.max_speed (or another suitable constant) to get the magnitude.
        desired_v_speed_magnitude = abs(hit_factor) * self.max_speed  # Use max_speed for more pronounced effect

        # Determine the vertical direction based on the hit_factor.
        # Positive hit_factor means downwards (positive y direction).
        # Negative hit_factor means upwards (negative y direction).
        # If hit_factor is 0, perhaps no vertical speed change is desired, or maintain direction.
        if hit_factor > 0:
            vertical_direction = 1
        elif hit_factor < 0:
            vertical_direction = -1
        else:
            # If hit exactly in the center, maybe don't add vertical speed or maintain current direction.
            # Let's maintain current direction but the magnitude will be close to 0 if max_speed is used above.
            vertical_direction = self.vertical_speed.direction

        # Set the new vertical speed magnitude and direction.
        # We take the maximum of the current vertical speed value and the desired speed from the hit,
        # to ensure speed can increase even with small hit factors, but is dominated by edge hits.
        # Clamped by max_speed.
        final_v_speed_value = min(int(max(self.vertical_speed.value, desired_v_speed_magnitude)), self.max_speed)

        self.vertical_speed.set_value(final_v_speed_value)
        # Only change direction if hit_factor is not zero.
        if hit_factor != 0:
            self.vertical_speed._direction = vertical_direction

    def reset(self, x: int, y: int) -> None:
        """Reset ball to position with initial speed in a random direction."""
        self.position.update(x, y)

        # Reset speeds to initial values with random directions
        h_dir = random.choice([-1, 1])
        v_dir = random.choice([-1, 1])

        self.horizontal_speed = Speed(self.base_speed, h_dir)
        self.vertical_speed = Speed(0, v_dir)


@invariant(
    lambda self: 0 <= self._left_paddle.position.y <= self.height - self._left_paddle.height,
    "Left paddle within the world's vertical bounds"
)
@invariant(
    lambda self: 0 <= self._right_paddle.position.y <= self.height - self._right_paddle.height,
    "Right paddle within the world's vertical bounds"
)
@invariant(
    lambda self: 0 <= self._ball.position.x <= self.width,
    "Ball's x-coordinate within world bounds"
)
@invariant(
    lambda self: 0 <= self._ball.position.y <= self.height,
    "Ball's y-coordinate within world bounds"
)
class World:
    """
    The world of the Pong game.
    Contains the paddles, ball, and handles their interactions.
    """
    width: Final[PositiveInt]
    height: Final[PositiveInt]

    _left_paddle: Final[Paddle]
    _right_paddle: Final[Paddle]
    _ball: Final[Ball]

    def __init__(self, width: int = 800, height: int = 600) -> None:
        """
        Initialize the Pong game world.
        Args:
            width: Width of the game world
            height: Height of the game world
        """
        self.width = PositiveInt(width)
        self.height = PositiveInt(height)

        paddle_height = 100
        paddle_width = 15
        paddle_speed = 10

        # Position paddles on the sides with some padding
        self._left_paddle = Paddle(
            x=20,
            y=(height - paddle_height) // 2,
            height=paddle_height,
            width=paddle_width,
            speed=paddle_speed
        )

        self._right_paddle = Paddle(
            x=width - 20 - paddle_width,
            y=(height - paddle_height) // 2,
            height=paddle_height,
            width=paddle_width,
            speed=paddle_speed
        )

        # Initialize ball in the center
        self._ball = Ball(
            x=width // 2,
            y=height // 2,
            size=15,
            initial_speed=4,
            max_speed=12,
            speed_increment=1
        )

    @property
    def left_paddle(self) -> ImmutablePosition:
        return self._left_paddle.position

    @property
    def right_paddle(self) -> ImmutablePosition:
        return self._right_paddle.position

    @property
    def ball(self) -> ImmutablePosition:
        return self._ball.position

    def reset_ball(self) -> None:
        """Reset the ball to the center of the screen."""
        self._ball.reset(self.width // 2, self.height // 2)

    def collision_left(self, paddle: Paddle, ball: Ball) -> bool:
            return (
                    ball.position.x <= paddle.position.x + paddle.width and
                    ball.position.x + ball.horizontal_speed.velocity <= paddle.position.x + paddle.width and
                    ball.position.y + ball.size >= paddle.position.y and
                    ball.position.y <= paddle.position.y + paddle.height
            )

    def collision_right(self, paddle: Paddle, ball: Ball) -> bool:
            return (
                    ball.position.x + ball.size >= paddle.position.x and
                    ball.position.x + ball.size + ball.horizontal_speed.velocity >= paddle.position.x and
                    ball.position.y + ball.size >= paddle.position.y and
                    ball.position.y <= paddle.position.y + paddle.height
            )
    def update_world(self) -> int:
        """
        Update the state of the world for one frame.

        :return:
        0 - continue current game
        1 - player 1 won
        2 - player 2 won
        """
        # Update ball position
        self._ball.update_position()

        # Check for collisions with top and bottom walls
        if self._ball.position.y <= 0 or self._ball.position.y >= self.height - self._ball.size:
            self._ball.bounce_horizontal()
            # Ensure ball stays within bounds after bouncing
            if self._ball.position.y < 0:
                self._ball.position.update(self._ball.position.x, 0)
            elif self._ball.position.y > self.height - self._ball.size:
                self._ball.position.update(self._ball.position.x, self.height - self._ball.size)

        # Check for collisions with paddles
        # Check right paddle first as the ball is moving towards it if scoring for player 1 is imminent
        if self._ball.horizontal_speed.direction > 0 and self.collision_right(self._right_paddle, self._ball):
             # Calculate where on the paddle the ball hit
            hit_factor = self._right_paddle.get_hit_factor(self._ball.position.y + self._ball.size // 2)
            self._ball.bounce_vertical(hit_factor)
            # Ensure ball doesn't get stuck in paddle by placing it just outside
            self._ball.position.update(self._right_paddle.position.x - self._ball.size, self._ball.position.y)


        # Check left paddle second as the ball is moving towards it if scoring for player 2 is imminent
        elif self._ball.horizontal_speed.direction < 0 and self.collision_left(self._left_paddle, self._ball):
            # Calculate where on the paddle the ball hit
            hit_factor = self._left_paddle.get_hit_factor(self._ball.position.y + self._ball.size // 2)
            self._ball.bounce_vertical(hit_factor)
            # Ensure ball doesn't get stuck in paddle by placing it just outside
            self._ball.position.update(self._left_paddle.position.x + self._left_paddle.width, self._ball.position.y)

        # Check if ball went past paddles (scoring) - Perform this check *after* updating position and collisions
        if self._ball.position.x < 0:
            self.restart_game() # Reset ball position immediately on scoring
            return 2 # Player 2 won the round
        elif self._ball.position.x > self.width:
            self.restart_game() # Reset ball position immediately on scoring
            return 1 # Player 1 won the round
        else:
            return 0 # Continue game

    def move_left_paddle_up(self) -> None:
        """Move the left paddle up."""
        self._left_paddle.move_up(self.height)

    def move_left_paddle_down(self) -> None:
        """Move the left paddle down."""
        self._left_paddle.move_down(self.height)

    def move_right_paddle_up(self) -> None:
        """Move the right paddle up."""
        self._right_paddle.move_up(self.height)

    def move_right_paddle_down(self) -> None:
        """Move the right paddle down."""
        self._right_paddle.move_down(self.height)

    def restart_game(self) -> None:
        """Restart the game, resetting scores and positions."""

        # Reset paddle positions
        self._left_paddle.position.update(
            self._left_paddle.position.x,
            (self.height - self._left_paddle.height) // 2
        )
        self._right_paddle.position.update(
            self._right_paddle.position.x,
            (self.height - self._right_paddle.height) // 2
        )

        # Reset ball
        self.reset_ball()
