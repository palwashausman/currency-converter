import os
import requests
import gradio as gr
from google import genai
from google.genai import types

client = genai.Client()
EXCHANGE_KEY = os.environ.get("EXCHANGE_RATE_API_KEY")

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts an amount from one currency to another using live exchange rates."""
    from_curr = from_currency.upper().strip()
    to_curr = to_currency.upper().strip()
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_KEY}/pair/{from_curr}/{to_curr}/{amount}"
    response = requests.get(url, timeout=10).json()
    if response.get("result") == "success":
        return f"{amount:,.2f} {from_curr} = {response['conversion_result']:,.2f} {to_curr} (Rate: 1 {from_curr} = {response['conversion_rate']:.4f} {to_curr})"
    return f"Could not fetch rate for {from_curr} to {to_curr}."

def chat_fn(message, history):
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful live FX currency assistant. Always use the convert_currency tool for conversions.",
            tools=[convert_currency],
        ),
    )
    return response.text

demo = gr.ChatInterface(
    fn=chat_fn,
    title="Live AI Currency Converter",
    description="Ask naturally (e.g., 'How much is 250 USD in PKR?' or 'Convert 500 EUR to AED').",
    examples=["How much is 100 USD in PKR?", "Convert 50 GBP to SAR"],
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
