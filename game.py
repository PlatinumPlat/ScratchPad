import math
import os
import time

import pygame

from elevenlabs_generator import (
    generate_speech,
    generate_sound_effect
)


WIDTH = 1000
HEIGHT = 700


class Game:

    def __init__(self):

        pygame.init()

        pygame.mixer.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "ScratchPad"
        )

        self.clock = pygame.time.Clock()

        # Generated OpenAI sprite
        self.sprite = None

        self.x = 300
        self.y = 300

        self.angle = 0

        self.costume = "default"

        self.message = ""

        self.message_timer = 0

        self.running = True

    # =================================
    # MOVEMENT
    # =================================

    def move(self, amount):

        radians = math.radians(
            self.angle
        )

        start_x = self.x
        start_y = self.y

        target_x = (
            self.x
            + math.cos(radians)
            * amount
        )

        target_y = (
            self.y
            + math.sin(radians)
            * amount
        )

        frames = max(
            1,
            int(abs(amount))
        )

        for frame in range(frames):

            t = (
                frame + 1
            ) / frames

            self.x = (
                start_x
                + (
                    target_x
                    - start_x
                ) * t
            )

            self.y = (
                start_y
                + (
                    target_y
                    - start_y
                ) * t
            )

            self.handle_events()

            self.draw()

            self.clock.tick(60)

            if not self.running:
                return

    def turn(self, degrees):

        start_angle = self.angle

        frames = max(
            1,
            int(abs(degrees))
        )

        for frame in range(frames):

            t = (
                frame + 1
            ) / frames

            self.angle = (
                start_angle
                + degrees * t
            )

            self.handle_events()

            self.draw()

            self.clock.tick(60)

            if not self.running:
                return

    def go_to(self, x, y):

        self.x = float(x)
        self.y = float(y)

        self.draw()

    def glide(
        self,
        seconds,
        target_x,
        target_y
    ):

        start_x = self.x
        start_y = self.y

        frames = max(
            1,
            int(seconds * 60)
        )

        for frame in range(frames):

            t = (
                frame + 1
            ) / frames

            self.x = (
                start_x
                + (
                    target_x
                    - start_x
                ) * t
            )

            self.y = (
                start_y
                + (
                    target_y
                    - start_y
                ) * t
            )

            self.handle_events()

            self.draw()

            self.clock.tick(60)

            if not self.running:
                return

    def move_direction(
        self,
        direction,
        amount
    ):

        if direction == "up":

            self.y -= amount

        elif direction == "down":

            self.y += amount

        elif direction == "left":

            self.x -= amount

        elif direction == "right":

            self.x += amount

        self.draw()

    # =================================
    # COSTUMES
    # =================================

    def change_costume(self, name):

        from sprite_generator import generate_sprite

        name = str(name).strip()

        print()
        print(
            f"Changing costume to: {name}"
        )

        sprite_path = generate_sprite(
            name
        )

        try:

            self.sprite = pygame.image.load(
                sprite_path
            ).convert_alpha()

            # Scale generated sprite
            max_size = 180

            width, height = (
                self.sprite.get_size()
            )

            scale = min(
                max_size / width,
                max_size / height
            )

            new_size = (
                max(
                    1,
                    int(width * scale)
                ),
                max(
                    1,
                    int(height * scale)
                )
            )

            self.sprite = (
                pygame.transform.smoothscale(
                    self.sprite,
                    new_size
                )
            )

            self.costume = name

            print(
                f"✓ Costume loaded: {name}"
            )

            self.draw()

        except Exception as error:

            print(
                "Sprite loading error:"
            )

            print(error)

            self.sprite = None

    # =================================
    # SPEECH
    # =================================

    def say(self, text):

        self.message = text

        self.message_timer = 180

        self.draw()

        try:

            path = generate_speech(
                text
            )

            pygame.mixer.music.load(
                path
            )

            pygame.mixer.music.play()

        except Exception as error:

            print(
                "TTS error:"
            )

            print(error)

    # =================================
    # SOUND
    # =================================

    def play_sound(self, name):

        try:

            possible_paths = [

                os.path.join(
                    "assets",
                    "sounds",
                    f"{name}.wav"
                ),

                os.path.join(
                    "assets",
                    "sounds",
                    f"{name}.mp3"
                )

            ]

            local_path = None

            for path in possible_paths:

                if os.path.exists(path):

                    local_path = path

                    break

            if local_path:

                sound = pygame.mixer.Sound(
                    local_path
                )

                sound.play()

                return

            path = generate_sound_effect(
                name
            )

            sound = pygame.mixer.Sound(
                path
            )

            sound.play()

        except Exception as error:

            print(
                "Sound error:"
            )

            print(error)

    # =================================
    # WAIT
    # =================================

    def wait(self, seconds):

        start = time.time()

        while (
            time.time() - start
            < seconds
        ):

            self.handle_events()

            self.draw()

            self.clock.tick(60)

            if not self.running:
                return

    # =================================
    # EVENTS
    # =================================

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q:

                    self.running = False

    # =================================
    # CHARACTER DRAWING
    # =================================

    def draw_character(self):

        x = int(self.x)
        y = int(self.y)

        # Generated OpenAI sprite
        if self.sprite is not None:
            # Rotate sprite according to ScratchPad angle
            rotated_sprite = pygame.transform.rotate(
                self.sprite,
                -self.angle
            )

            sprite_rect = (
                rotated_sprite.get_rect(
                    center=(x, y)
                )
            )

            self.screen.blit(
                rotated_sprite,
                sprite_rect
            )

            return

        # Default character if no sprite
        pygame.draw.circle(
            self.screen,
            (80, 140, 240),
            (x, y),
            30
        )

    # =================================
    # DRAW
    # =================================

    def draw(self):

        self.screen.fill(
            (245, 245, 245)
        )

        # Character
        self.draw_character()

        # Speech

        if self.message_timer > 0:

            font = pygame.font.Font(
                None,
                28
            )

            text = font.render(
                self.message,
                True,
                (0, 0, 0)
            )

            self.screen.blit(
                text,
                (
                    int(self.x + 45),
                    int(self.y - 45)
                )
            )

            self.message_timer -= 1

        pygame.display.flip()

    # =================================
    # MAIN LOOP
    # =================================

    def run(self):

        while self.running:

            self.handle_events()

            self.draw()

            self.clock.tick(60)

        pygame.quit()