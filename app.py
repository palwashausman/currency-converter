import os
import requests
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Live AI Currency Converter")
st.title("Live AI Currency Converter")
st.caption("Ask naturally (e.g., 'How much is 250 USD in PKR?' or 'Convert 500 EUR to AED').")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
EXCHANGE_KEY = st.secrets["EXCHANGE_RATE_API_KEY"]

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts an amount from one currency to another using live exchange rates."""
    from_curr = from_currency.upper().strip()
    to_curr = to_currency.upper().strip()
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_KEY}/pair/{from_curr}/{to_curr}/{amount}"
    response = requests.get(url, timeout=10).json()
    if response.get("result") == "success":
        return f"{amount:,.2f} {from_curr} = {response['conversion_result']:,.2f} {to_curr} (Rate: 1 {from_curr} = {response['conversion_rate']:.4f} {to_curr})"
    return f"Could not fetch rate for {from_curr} to {to_curr}."

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask for a live currency conversion..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful live FX currency assistant. Always use the convert_currency tool for conversions.",
            tools=[convert_currency],
        ),
    )
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
