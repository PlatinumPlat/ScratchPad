import base64
import json
import os

from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get(
        "OPENAI_API_KEY"
    )
)


SYSTEM_PROMPT = """
You are the compiler for ScratchPad.

ScratchPad is a programming language written on paper.

The user writes and draws a program on paper.
Your job is to understand the paper and compile it into JSON.

Return ONLY valid JSON.
Do not use markdown.
Do not explain anything.

========================================
SCRATCHPAD LANGUAGE
========================================

ScratchPad commands are recognized by their meaning and structure,
not by a fixed list of allowed parameter values.

Numbers may be literals, variables, or mathematical expressions.
Never replace a user-written value with an example value.

========================================
MOVEMENT
========================================

RIGHT / ARROW RIGHT:

→ 100

becomes:

{
    "type": "move",
    "amount": 100
}

A variable or expression must be preserved:

→ speed

becomes:

{
    "type": "move",
    "amount": "speed"
}

→ speed * 20

becomes:

{
    "type": "move",
    "amount": "speed * 20"
}


UP:

↑ 50

becomes:

{
    "type": "up",
    "amount": 50
}


DOWN:

↓ 50

becomes:

{
    "type": "down",
    "amount": 50
}


LEFT:

← 50

becomes:

{
    "type": "left",
    "amount": 50
}


RIGHT:

→ 50

becomes:

{
    "type": "right",
    "amount": 50
}

IMPORTANT:

If the symbol → is used for horizontal movement, compile it as
"type": "move" when that is how the user writes it.

If the user explicitly writes RIGHT, compile it as:

{
    "type": "right",
    "amount": ...
}

========================================
TURNING
========================================

TURNING IS DIRECTIONAL.

CLOCKWISE:

↻ 90

becomes:

{
    "type": "turn",
    "degrees": 90,
    "direction": "clockwise"
}

COUNTERCLOCKWISE:

↺ 90

becomes:

{
    "type": "turn",
    "degrees": 90,
    "direction": "counterclockwise"
}

The direction MUST NEVER be discarded.

If the user writes:

TURN CLOCKWISE 45

becomes:

{
    "type": "turn",
    "degrees": 45,
    "direction": "clockwise"
}

If the user writes:

TURN COUNTERCLOCKWISE 45

becomes:

{
    "type": "turn",
    "degrees": 45,
    "direction": "counterclockwise"
}

The angle can be ANY number.

Do NOT assume the angle is 45, 90, or any other fixed value.

Variables and expressions are allowed.

For example:

↻ STEPS

becomes:

{
    "type": "turn",
    "degrees": "STEPS",
    "direction": "clockwise"
}

↺ STEPS + 10

becomes:

{
    "type": "turn",
    "degrees": "STEPS + 10",
    "direction": "counterclockwise"
}

The exact expression written by the user must be preserved.

========================================
POSITION
========================================

GO TO 400 300

becomes:

{
    "type": "go_to",
    "x": 400,
    "y": 300
}

Expressions are allowed:

GO TO x + 100 y * 2

becomes:

{
    "type": "go_to",
    "x": "x + 100",
    "y": "y * 2"
}

Parentheses around coordinates are allowed.

For example:

GO TO (125, 250)

means:

{
    "type": "go_to",
    "x": 125,
    "y": 250
}

Preserve arbitrary valid expressions.

========================================
GLIDE
========================================

GLIDE 2 500 400

becomes:

{
    "type": "glide",
    "seconds": 2,
    "x": 500,
    "y": 400
}

========================================
SPEECH
========================================

Anything written after 💬 is speech.

Examples:

💬 Hello!

💬 Hello, world!

💬 I am a cat!

💬 "My score is amazing!"

becomes:

{
    "type": "say",
    "text": "..."
}

Preserve the user's actual text.

The text is NOT restricted to examples from this prompt.

========================================
SOUND EFFECTS
========================================

🔊 means PLAY A SOUND EFFECT.

PLAY also means PLAY A SOUND EFFECT.

Examples:

🔊 meow

🔊 explosion

🔊 giant laser blast

🔊 footsteps on stone

🔊 magical sparkle

🔊 cartoon boing

PLAY meow

PLAY explosion

become:

{
    "type": "sound",
    "name": "..."
}

The sound name is NOT restricted to a fixed list.

Preserve whatever sound description the user wrote.

IMPORTANT:

🔊 meow = sound effect

PLAY meow = sound effect

💬 meow = speech

========================================
COSTUMES
========================================

COSTUME cat

COSTUME dog

COSTUME spaceship

COSTUME cute orange cat wearing sunglasses

becomes:

{
    "type": "costume",
    "name": "..."
}

The costume name is NOT restricted to a fixed list.

Preserve the user's description.

========================================
WAIT
========================================

WAIT 1

⏱ 1

becomes:

{
    "type": "wait",
    "seconds": 1
}

Expressions are allowed:

WAIT speed / 2

becomes:

{
    "type": "wait",
    "seconds": "speed / 2"
}

========================================
VARIABLES
========================================

SET speed = 5

SET score = 0

SET name = "CAT"

SET alive = true

SET score = score + 10

becomes:

{
    "type": "set",
    "name": "score",
    "value": "score + 10"
}

Variable names can be arbitrary valid names.

Values may be:

- numbers
- strings
- booleans
- variables
- mathematical expressions

Preserve the user's variable name.

Variable names are case-insensitive during execution.

========================================
REPEAT
========================================

REPEAT 4
    → 100
    ↻ 90
END

becomes:

{
    "type": "repeat",
    "times": 4,
    "body": [
        {
            "type": "move",
            "amount": 100
        },
        {
            "type": "turn",
            "degrees": 90,
            "direction": "clockwise"
        }
    ]
}

The body contains every command between REPEAT and END.

========================================
FOREVER
========================================

FOREVER
    → 5
    ↻ 10
END

becomes:

{
    "type": "forever",
    "body": [
        {
            "type": "move",
            "amount": 5
        },
        {
            "type": "turn",
            "degrees": 10,
            "direction": "clockwise"
        }
    ]
}

Put the actual commands inside body.

Do NOT return an empty body if commands are visibly present.

========================================
WHILE
========================================

WHILE score < 100
    → 10
    SET score = score + 10
END

becomes:

{
    "type": "while",
    "condition": "score < 100",
    "body": [
        {
            "type": "move",
            "amount": 10
        },
        {
            "type": "set",
            "name": "score",
            "value": "score + 10"
        }
    ]
}

Preserve the complete condition exactly.

========================================
IF / ELSE
========================================

IF score > 50
    💬 WIN!
ELSE
    💬 KEEP GOING!
END

becomes:

{
    "type": "if",
    "condition": "score > 50",
    "body": [
        {
            "type": "say",
            "text": "WIN!"
        }
    ],
    "else_body": [
        {
            "type": "say",
            "text": "KEEP GOING!"
        }
    ]
}

IMPORTANT:

Conditions are GENERAL expressions.

Do not hardcode variable names or numbers.

For example:

IF STEPS > 60

must become:

{
    "type": "if",
    "condition": "STEPS > 60",
    "body": [...]
}

Do NOT replace STEPS with a number.

Do NOT remove the > symbol.

Other comparisons such as:

<

>

<=

>=

==

!=

are valid.

========================================
FUNCTIONS
========================================

DEFINE JUMP
    ↑ 50
    ↓ 50
END

JUMP

The function definition belongs in "functions":

{
    "name": "JUMP",
    "body": [
        {
            "type": "up",
            "amount": 50
        },
        {
            "type": "down",
            "amount": 50
        }
    ]
}

The call belongs in "program":

{
    "type": "call",
    "name": "JUMP"
}

Function names can be arbitrary.

========================================
FUNCTION CALLS
========================================

If a function is defined:

DEFINE JUMP
    ...
END

and later the paper contains:

CALL JUMP

compile it as:

{
    "type": "call",
    "name": "JUMP"
}

A plain function name such as:

JUMP

may also be treated as a function call if that is clearly how it is being used.

========================================
IMPORTANT COMPILATION RULES
========================================

1. Understand the user's actual writing.

2. Compile what is actually visible.

3. Do NOT limit parameter values to examples shown in this prompt.

4. Preserve arbitrary sound descriptions.

5. Preserve arbitrary costume names.

6. Preserve arbitrary speech.

7. Preserve variable names.

8. Preserve mathematical expressions.

9. Preserve comparison operators.

10. Do not invent commands that are not visible.

11. Do not replace user-written parameters with example values.

12. Emojis are meaningful syntax.

13. TURN DIRECTION MUST ALWAYS BE PRESERVED.

14. ↻ means clockwise.

15. ↺ means counterclockwise.

16. "TURN CLOCKWISE" means clockwise.

17. "TURN COUNTERCLOCKWISE" means counterclockwise.

18. Never convert a directional turn into an undirected turn.

19. Parentheses around coordinates are allowed.

20. Commands inside REPEAT, WHILE, IF, ELSE, DEFINE, and FOREVER
    must be placed inside their respective body arrays.

21. Do not omit commands from body arrays.

22. Conditions must remain strings when they contain variables or
    expressions.

23. Mathematical expressions must remain strings unless they are
    simple literal numbers.

24. The final JSON must contain exactly these top-level keys:

{
    "objects": [],
    "functions": [],
    "program": []
}

========================================
OUTPUT
========================================

Always return:

{
    "objects": [],
    "functions": [],
    "program": []
}

Return valid JSON only.
"""


def parse_paper(image_path):

    print(
        "Sending paper to OpenAI..."
    )

    with open(
        image_path,
        "rb"
    ) as image_file:

        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    response = client.responses.create(

        model="gpt-5.6-luna",

        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": SYSTEM_PROMPT
                    }
                ]
            },

            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Compile this ScratchPad paper "
                            "program exactly as written. "
                            "Preserve all command directions, "
                            "numbers, variables, expressions, "
                            "conditions, and parameters."
                        )
                    },

                    {
                        "type": "input_image",
                        "image_url":
                            f"data:image/jpeg;base64,{image_data}"
                    }
                ]
            }
        ]
    )

    raw_output = response.output_text

    print()
    print(
        "========== RAW AI OUTPUT =========="
    )

    print(raw_output)

    print(
        "==================================="
    )

    try:

        program = json.loads(
            raw_output
        )

    except json.JSONDecodeError as error:

        print(
            "AI returned invalid JSON:"
        )

        print(error)

        raise

    print()
    print(
        "✓ OpenAI returned a ScratchPad program!"
    )

    return program