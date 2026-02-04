# AI_Agent_Assignment
The Cozy Oven Bakery Bot
A custom AI assistant built to help customers at The Cozy Oven, an artisanal bakery. This bot handles FAQs and captures customer leads automatically.

🔗 Live Bot
(https://huggingface.co/spaces/GhadirNahle/the-cozy-oven-bot)

🛠 How it Works
The Brain: Uses Gemini 2.0 (via OpenRouter) to chat with customers.

The Interface: Built with Gradio for a simple, clean web view.

The Tools: If a customer wants to sign up or leave a message, the bot saves that info to a local file (leads_log.jsonl) so the bakery owner can see it.

The Persona: Trained to be friendly and helpful, matching the bakery's "slow and mindful" vibe.

📂 Files in this Repo
app.py: The code that runs the bot.

requirements.txt: The libraries needed to make it work.

me/business_summary.txt: The bakery's info used to train the bot.
