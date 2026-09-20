import hashlib
import os

from elevenlabs.client import ElevenLabs


API_KEY = os.environ.get(
    "ELEVENLABS_API_KEY"
)

if not API_KEY:

    raise RuntimeError(
        "ELEVENLABS_API_KEY is not set."
    )


client = ElevenLabs(
    api_key=API_KEY
)


GENERATED_DIR = os.path.join(
    "assets",
    "generated"
)

os.makedirs(
    GENERATED_DIR,
    exist_ok=True
)


# ElevenLabs' current documentation uses
# this voice in its Flash v2.5 example.
VOICE_ID = "pNInz6obpgDQGcFmaJgB"


def _filename(
    prefix,
    text
):

    digest = hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()[:12]

    return os.path.join(
        GENERATED_DIR,
        f"{prefix}_{digest}.mp3"
    )


def generate_speech(text):

    path = _filename(
        "speech",
        text
    )

    # Reuse previously generated audio.
    if os.path.exists(path):

        print(
            f"Using cached speech: {text}"
        )

        return path

    print(
        f'Generating speech: "{text}"'
    )

    audio = client.text_to_speech.convert(

        voice_id=VOICE_ID,

        model_id="eleven_flash_v2_5",

        text=text,

        output_format="mp3_22050_32"
    )

    # Write to a temporary file first.
    # This prevents incomplete API responses
    # from becoming "cached" audio files.

    temporary_path = (
        path + ".tmp"
    )

    try:

        with open(
            temporary_path,
            "wb"
        ) as file:

            for chunk in audio:

                if chunk:

                    file.write(chunk)

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
        f"✓ Speech saved: {path}"
    )

    return path


def generate_sound_effect(
    description,
    duration=None
):

    cache_key = (
        description
        + str(duration)
    )

    path = _filename(
        "sfx",
        cache_key
    )

    if os.path.exists(path):

        print(
            f"Using cached sound: {description}"
        )

        return path

    print(
        f'Generating sound effect: "{description}"'
    )

    kwargs = {

        "text": description,

        "model_id":
            "eleven_text_to_sound_v2",

        "output_format":
            "mp3_22050_32"
    }

    if duration is not None:

        kwargs[
            "duration_seconds"
        ] = duration

    audio = (
        client
        .text_to_sound_effects
        .convert(**kwargs)
    )

    temporary_path = (
        path + ".tmp"
    )

    try:

        with open(
            temporary_path,
            "wb"
        ) as file:

            for chunk in audio:

                if chunk:

                    file.write(chunk)

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
        f"✓ Sound effect saved: {path}"
    )

    return path