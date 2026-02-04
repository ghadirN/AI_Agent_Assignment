import os
import json
from datetime import datetime
from openai import OpenAI
import gradio as gr

# 1. SETUP FROM SECRETS
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"), 
)
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct"

# 2. LOAD BUSINESS DATA
SUMMARY_PATH = "me/business_summary.txt"
if os.path.exists(SUMMARY_PATH):
    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        summary_text = f.read()
else:
    summary_text = "The Cozy Oven is a small-batch, artisanal bakery that embodies slow, mindful moments."

system_prompt = f"""You are the friendly assistant for The Cozy Oven bakery. 
Mission: {summary_text}
Rules: Be friendly. Only use tools if the user wants to sign up or if you don't know an answer."""

# 3. TOOLS
def record_customer_interest(email: str, name: str, message: str) -> str:
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "name": name, "email": email, "message": message,
    }
    # Note: On HF Spaces, this file is temporary and clears on reboot
    with open("leads_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return "Lead recorded successfully. Thank you for your interest in The Cozy Oven!"

def record_feedback(question: str) -> str:
    entry = {"timestamp": datetime.utcnow().isoformat(), "question": question}
    with open("feedback_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return "Thanks for your feedback! The team will review this."

# Define tool dictionary for the agent
BUSINESS_TOOL_FUNCS = {
    "record_customer_interest": record_customer_interest,
    "record_feedback": record_feedback,
}

business_tools = [
    {
        "type": "function",
        "function": {
            "name": "record_customer_interest",
            "description": "Record a new lead for the bakery.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "name": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["email", "name", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_feedback",
            "description": "Record feedback or unknown questions.",
            "parameters": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"],
            },
        },
    },
]

# 4. AGENT LOGIC
def run_business_agent(user_input: str, chat_history=None):
    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        for u, a in chat_history:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=business_tools,
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        
        if not message.tool_calls:
            return message.content

        messages.append(message) 
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            tool_func = BUSINESS_TOOL_FUNCS.get(tool_name)
            result = tool_func(**args) if tool_func else "Tool error."
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        return final_response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# 5. GRADIO INTERFACE
demo = gr.ChatInterface(
    fn=run_business_agent, 
    title="The Cozy Oven",
    description="Artisanal Bakery Assistant"
)

if __name__ == "__main__":
    # REQUIRED FOR HUGGING FACE
    demo.launch(server_name="0.0.0.0", server_port=7860)
