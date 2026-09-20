# ScratchPad
Scratch, but on paper!

# About
Remember Scratch, the block-based coding platform you probably used when you were in elementary school?
If you take Scratch and then put it on paper, you get ScratchPad! This programming language allows you to write pseudocode using words and symbols, and then run your program on your computer with AI-powered sprite generation, speech, and sound effects. You can use variables, loops, and user-defined functions to move a robot, make it speak, generate its costume, and create an interactive experience!

# How ScratchPad Works
When the user presses R (for Run), a photo of their handwritten code is captured and sent to OpenAI's GPT-5.6 Luna, which identifies the handwritten commands and converts them into a structured JSON format. ScratchPad then parses this JSON and executes each command using its own interpreter. 

# How to Use

1. **Clone this GitHub repository**

   ```bash
   git clone https://github.com/PlatinumPlat/ScratchPad.git
   cd ScratchPad
   ```

2. **Install the required dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API keys**

   Create a `.env` file in the root directory of the project and add your API keys:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

4. **Run the program!**

   ```bash
   python main.py
   ```
   
# Technologies
ScratchPad was built primarily with Python and Pygame, with OpenAI and ElevenLabs APIs handling the AI-powered parts of the project. I also used OpenAI's GPT-Image-2.5 Flare to generate costumes for sprites, integrated ElevenLabs' Eleven Flash v2.5 for text-to-speech, and incorporated Eleven Text to Sound v2 for generating sound effects.
