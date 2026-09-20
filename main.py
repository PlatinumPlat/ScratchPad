from camera import ScratchPadCamera
from openai_parser import parse_paper
from game import Game
from interpreter import Interpreter


def main():

    camera = ScratchPadCamera()

    try:

        image_path = camera.capture()

    finally:

        camera.close()

    if image_path is None:

        print(
            "ScratchPad closed."
        )

        return

    print()
    print(
        "Analyzing ScratchPad..."
    )
    print()

    program = parse_paper(
        image_path
    )

    print()
    print(
        "========== AI PROGRAM =========="
    )

    print(program)

    print(
        "================================"
    )

    print()

    game = Game()

    interpreter = Interpreter(
        game,
        program
    )

    interpreter.execute(
        program["program"]
    )

    game.run()


if __name__ == "__main__":

    main()