import ast
import operator
import time


class Interpreter:

    def __init__(self, game, program):

        self.game = game

        # Pause between ScratchPad actions
        self.action_delay = 0.25

        self.variables = {
            "x": game.x,
            "y": game.y
        }

        self.functions = {
            str(function["name"]).lower(): function["body"]
            for function in program.get("functions", [])
        }

    # ========================================
    # EXPRESSIONS
    # ========================================

    def evaluate(self, value):

        if value is None:
            return None

        if isinstance(value, (bool, int, float)):
            return value

        if not isinstance(value, str):
            return value

        value = value.strip()

        # Quoted string
        if (
            len(value) >= 2
            and value[0] == '"'
            and value[-1] == '"'
        ):
            return value[1:-1]

        # Booleans
        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

        # Direct variable lookup
        variable_name = value.lower()

        if variable_name in self.variables:
            return self.variables[variable_name]

        try:

            tree = ast.parse(
                value,
                mode="eval"
            )

            return self.evaluate_ast(
                tree.body
            )

        except Exception:

            # Not an expression -> treat as text
            return value

    def evaluate_ast(self, node):

        # Numbers / strings / booleans
        if isinstance(node, ast.Constant):
            return node.value

        # Variables
        if isinstance(node, ast.Name):

            variable_name = node.id.lower()

            if variable_name in self.variables:
                return self.variables[variable_name]

            raise ValueError(
                f"Unknown variable: {node.id}"
            )

        operators = {

            # Math
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,

            # Comparisons
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
        }

        # Math expressions
        if isinstance(node, ast.BinOp):

            operation = operators.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Unsupported math operator"
                )

            return operation(
                self.evaluate_ast(node.left),
                self.evaluate_ast(node.right)
            )

        # Comparisons
        if isinstance(node, ast.Compare):

            left = self.evaluate_ast(
                node.left
            )

            for operation_node, right_node in zip(
                node.ops,
                node.comparators
            ):

                operation = operators.get(
                    type(operation_node)
                )

                if operation is None:
                    raise ValueError(
                        "Unsupported comparison"
                    )

                right = self.evaluate_ast(
                    right_node
                )

                if not operation(
                    left,
                    right
                ):
                    return False

                left = right

            return True

        # Positive / negative numbers
        if isinstance(node, ast.UnaryOp):

            value = self.evaluate_ast(
                node.operand
            )

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        raise ValueError(
            "Unsupported expression"
        )

    # ========================================
    # PAUSE
    # ========================================

    def pause(self):

        """
        Pause between ScratchPad actions.

        This makes quick commands such as
        UP, DOWN, LEFT, and RIGHT visible.
        """

        if self.action_delay <= 0:
            return

        start = time.time()

        while (
            time.time() - start
            < self.action_delay
        ):

            self.game.handle_events()

            if not self.game.running:
                return

            self.game.draw()

            self.game.clock.tick(60)

    # ========================================
    # POSITION VARIABLES
    # ========================================

    def update_position(self):

        self.variables["x"] = self.game.x
        self.variables["y"] = self.game.y

    # ========================================
    # EXECUTE
    # ========================================

    def execute(self, blocks):

        for block in blocks:

            if not self.game.running:
                return

            if not isinstance(block, dict):
                continue

            command = str(
                block.get("type", "")
            ).lower()

            # ========================================
            # SYMBOL COMMANDS
            # ========================================

            if command == "↑":
                command = "up"

            elif command == "↓":
                command = "down"

            elif command == "←":
                command = "left"

            elif command == "→":
                command = "right"

            elif command == "↻":
                command = "turn_clockwise"

            elif command == "↺":
                command = "turn_counterclockwise"

            # ========================================
            # VARIABLES
            # ========================================

            if command == "set":

                name = str(
                    block["name"]
                )

                value = self.evaluate(
                    block["value"]
                )

                # Variables are case-insensitive
                variable_name = name.lower()

                self.variables[variable_name] = value

                # Allow SET X / SET Y
                if variable_name == "x":

                    self.game.x = float(value)

                    self.variables["x"] = (
                        self.game.x
                    )

                    self.game.draw()

                elif variable_name == "y":

                    self.game.y = float(value)

                    self.variables["y"] = (
                        self.game.y
                    )

                    self.game.draw()

            # ========================================
            # MOVEMENT
            # ========================================

            elif command == "move":

                amount = self.evaluate(
                    block["amount"]
                )

                self.game.move(
                    amount
                )

                self.update_position()

            # ========================================
            # TURN
            # ========================================

            elif command == "turn":

                degrees = self.evaluate(
                    block["degrees"]
                )

                direction = str(
                    block.get(
                        "direction",
                        "clockwise"
                    )
                ).lower()

                degrees = float(degrees)

                if direction in (
                    "counterclockwise",
                    "counter-clockwise",
                    "counter_clockwise",
                    "ccw",
                    "left"
                ):

                    degrees = -abs(degrees)

                else:

                    degrees = abs(degrees)

                self.game.turn(
                    degrees
                )

            # ========================================
            # CLOCKWISE TURN SYMBOL
            # ========================================

            elif command == "turn_clockwise":

                degrees = self.evaluate(
                    block.get(
                        "degrees",
                        block.get(
                            "angle",
                            block.get(
                                "amount",
                                0
                            )
                        )
                    )
                )

                self.game.turn(
                    abs(float(degrees))
                )

            # ========================================
            # COUNTERCLOCKWISE TURN SYMBOL
            # ========================================

            elif command == "turn_counterclockwise":

                degrees = self.evaluate(
                    block.get(
                        "degrees",
                        block.get(
                            "angle",
                            block.get(
                                "amount",
                                0
                            )
                        )
                    )
                )

                self.game.turn(
                    -abs(float(degrees))
                )

            # ========================================
            # GO TO
            # ========================================

            elif command == "go_to":

                x = self.evaluate(
                    block["x"]
                )

                y = self.evaluate(
                    block["y"]
                )

                self.game.go_to(
                    x,
                    y
                )

                self.update_position()

            # ========================================
            # GLIDE
            # ========================================

            elif command == "glide":

                seconds = self.evaluate(
                    block["seconds"]
                )

                x = self.evaluate(
                    block["x"]
                )

                y = self.evaluate(
                    block["y"]
                )

                self.game.glide(
                    seconds,
                    x,
                    y
                )

                self.update_position()

            # ========================================
            # UP
            # ========================================

            elif command == "up":

                amount = self.evaluate(
                    block["amount"]
                )

                self.game.move_direction(
                    "up",
                    amount
                )

                self.update_position()

            # ========================================
            # DOWN
            # ========================================

            elif command == "down":

                amount = self.evaluate(
                    block["amount"]
                )

                self.game.move_direction(
                    "down",
                    amount
                )

                self.update_position()

            # ========================================
            # LEFT
            # ========================================

            elif command == "left":

                amount = self.evaluate(
                    block["amount"]
                )

                self.game.move_direction(
                    "left",
                    amount
                )

                self.update_position()

            # ========================================
            # RIGHT
            # ========================================

            elif command == "right":

                amount = self.evaluate(
                    block["amount"]
                )

                self.game.move_direction(
                    "right",
                    amount
                )

                self.update_position()

            # ========================================
            # COSTUME
            # ========================================

            elif command == "costume":

                name = self.evaluate(
                    block["name"]
                )

                self.game.change_costume(
                    str(name)
                )

            # ========================================
            # SPEECH
            # ========================================

            elif command == "say":

                text = self.evaluate(
                    block["text"]
                )

                self.game.say(
                    str(text)
                )

            # ========================================
            # SOUND
            # ========================================

            elif command == "sound":

                name = self.evaluate(
                    block["name"]
                )

                self.game.play_sound(
                    str(name)
                )

            # ========================================
            # WAIT
            # ========================================

            elif command == "wait":

                seconds = self.evaluate(
                    block["seconds"]
                )

                self.game.wait(
                    seconds
                )

            # ========================================
            # REPEAT
            # ========================================

            elif command == "repeat":

                times = int(
                    self.evaluate(
                        block["times"]
                    )
                )

                for _ in range(times):

                    if not self.game.running:
                        return

                    self.execute(
                        block.get(
                            "body",
                            []
                        )
                    )

            # ========================================
            # WHILE
            # ========================================

            elif command == "while":

                while self.evaluate(
                    block["condition"]
                ):

                    if not self.game.running:
                        return

                    self.execute(
                        block.get(
                            "body",
                            []
                        )
                    )

            # ========================================
            # FOREVER
            # ========================================

            elif command == "forever":

                while self.game.running:

                    self.execute(
                        block.get(
                            "body",
                            []
                        )
                    )

            # ========================================
            # IF / ELSE
            # ========================================

            elif command == "if":

                result = self.evaluate(
                    block["condition"]
                )

                if result:

                    self.execute(
                        block.get(
                            "body",
                            []
                        )
                    )

                elif block.get("else_body"):

                    self.execute(
                        block["else_body"]
                    )

            # ========================================
            # FUNCTIONS
            # ========================================

            elif command == "call":

                name = str(
                    block["name"]
                ).lower()

                if name not in self.functions:

                    raise ValueError(
                        f"Unknown function: {block['name']}"
                    )

                self.execute(
                    self.functions[name]
                )

            # ========================================
            # UNKNOWN COMMAND
            # ========================================

            else:

                raise ValueError(
                    f"Unknown ScratchPad command: {command}"
                )

            # ========================================
            # ACTION DELAY
            # ========================================

            if not self.game.running:
                return

            self.pause()