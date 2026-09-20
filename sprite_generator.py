import base64
import hashlib
import os

from openai import OpenAI


client = OpenAI()

GENERATED_DIR = os.path.join(
    "assets",
    "generated"
)

os.makedirs(
    GENERATED_DIR,
    exist_ok=True
)


def _filename(prompt):

    digest = hashlib.md5(
        prompt.encode("utf-8")
    ).hexdigest()[:12]

    return os.path.join(
        GENERATED_DIR,
        f"sprite_{digest}.png"
    )


def generate_sprite(prompt):

    path = _filename(prompt)

    # Reuse previously generated sprites
    if os.path.exists(path):

        print(
            f"Using cached sprite: {prompt}"
        )

        return path

    print()
    print(
        f'Generating sprite: "{prompt}"'
    )
    print()

    result = client.images.generate(
        model="gpt-image-2.5-flare",
        prompt=(
            f"Create a game sprite of {prompt}. "
            "Single character or object only. "
            "Centered in the image. "
            "Full object visible. "
            "Clean, readable silhouette. "
            "No text. "
            "No scenery. "
            "No ground. "
            "Transparent background. "
            "Suitable for a 2D video game. "
            "Simple polished game-art style."
        ),
        background="transparent",
        output_format="png",
        size="1024x1024",
        quality="low"
    )

    image_base64 = result.data[0].b64_json

    image_data = base64.b64decode(
        image_base64
    )

    temporary_path = path + ".tmp"

    try:

        with open(
            temporary_path,
            "wb"
        ) as file:

            file.write(image_data)

        os.replace(
            temporary_path,
            path
        )

    except Exception:

        if os.path.exists(
            temporary_path
        ):
            os.remove(
                temporary_path
            )

        raise

    print(
        f"✓ Sprite saved: {path}"
    )

    return path