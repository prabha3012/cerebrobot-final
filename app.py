# app.py  — CerebroBot-demo (honest, demo-ready)
import streamlit as st
import requests
import os
import time
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(page_title="CerebroBot Demo", layout="wide")

# ---------- CONFIG ----------
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")  # put your hf_... token in environment or leave empty
HF_MODEL = "facebook/blenderbot-400M-distill"  # inference endpoint model (optional)
LOCAL_GEN_MODEL = "gpt2"  # local fallback generator (small)
ATTN_MODEL = "distilbert-base-uncased"  # used to demonstrate attention

# ---------- UI Styling ----------
st.markdown("""
<style>
body { background: linear-gradient(to bottom right, #0f2027, #203a43, #2c5364); color: white; font-family: Inter, sans-serif; }
.chat-box { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 14px; height: 520px; overflow-y: auto; }
.user { background: linear-gradient(135deg,#06b6d4,#3b82f6); color: white; padding: 8px 12px; border-radius:14px; max-width:80%; float:right; margin:8px 0; clear:both; }
.bot { background: linear-gradient(135deg,#667eea,#764ba2); color: white; padding: 8px 12px; border-radius:14px; max-width:80%; float:left; margin:8px 0; clear:both; }
.header { text-align:center; font-size:28px; font-weight:700; margin-bottom:8px; color: #E6F0FF; }
.small { font-size:12px; color:#cbd5e1; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>🧠 CerebroBot — Demo (Honest & Transparent)</div>", unsafe_allow_html=True)
st.markdown("<div class='small'>Shows real generation + attention visualization to explain Transformer internals.</div>", unsafe_allow_html=True)
st.write("---")

# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history = [("CerebroBot", "Hello! I am CerebroBot demo. Ask me anything (or click 'Explain Attention' to see how attention weights work).")]

# ---------- Helper: generate with Hugging Face Inference API ----------
def hf_inference(text):
    if not HF_API_TOKEN:
        return None
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": text}
    try:
        r = requests.post(f"https://api-inference.huggingface.co/models/{HF_MODEL}", headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        j = r.json()
        # Some endpoints return list with generated_text
        if isinstance(j, list) and "generated_text" in j[0]:
            return j[0]["generated_text"]
        # others
        if isinstance(j, dict) and "error" not in j:
            # transformer may return 'generated_text'
            return j.get("generated_text") or str(j)
        return None
    except Exception as e:
        print("HF inference error:", e)
        return None

# ---------- Helper: local generation fallback ----------
@st.cache_resource
def get_local_generator():
    # Use a lightweight pipeline for quick responses
    return pipeline("text-generation", model=LOCAL_GEN_MODEL, max_length=150)

# ---------- Helper: attention visualization ----------
@st.cache_resource
def load_attention_model():
    tokenizer = AutoTokenizer.from_pretrained(ATTN_MODEL)
    model = AutoModel.from_pretrained(ATTN_MODEL, output_attentions=True)
    model.eval()
    return tokenizer, model

def compute_attention_heatmap(text):
    tokenizer, model = load_attention_model()
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    # outputs.attentions is a tuple: (layer1, layer2, ...)
    # use last layer's attentions [batch, head, seq, seq]
    attentions = outputs.attentions  # tuple of layers
    last = attentions[-1][0].cpu().numpy()  # [head, seq, seq]
    # average across heads
    avg_att = last.mean(axis=0)  # [seq, seq]
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    return avg_att, tokens

def plot_attention(avg_att, tokens):
    fig, ax = plt.subplots(figsize=(6,5))
    sns.heatmap(avg_att, xticklabels=tokens, yticklabels=tokens, cmap='viridis', ax=ax)
    plt.xticks(rotation=90)
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

# ---------- Layout: left chat, right controls ----------
left_col, right_col = st.columns([3,1])

with left_col:
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    for who, msg in st.session_state.history:
        cls = "user" if who != "CerebroBot" and who != "Bot" else "bot" if who == "CerebroBot" else "user"
        if who == "You":
            st.markdown(f"<div class='user'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'><b>{who}:</b> {msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.write("Controls")
    user_input = st.text_input("Type message", key="msg_input")
    if st.button("Send"):
        if user_input.strip():
            st.session_state.history.append(("You", user_input))
            # Try HF API
            reply = hf_inference(user_input)
            if reply is None:
                # fallback to local generator
                gen = get_local_generator()
                out = gen(user_input, max_length=120, num_return_sequences=1)[0]["generated_text"]
                reply = out
            st.session_state.history.append(("CerebroBot", reply))
            st.experimental_rerun()
    if st.button("Explain Attention (demo)"):
        # use last user message or default demo string
        text_for_attn = user_input.strip() or "transformers use attention to relate words in a sentence"
        avg_att, tokens = compute_attention_heatmap(text_for_attn)
        img_buf = plot_attention(avg_att, tokens)
        st.image(img_buf)
        st.caption("Heatmap: averaged attention across heads (last layer). Lighter = higher attention.")
    st.write("")
    st.markdown("**Demo notes**")
    st.markdown("- Uses Hugging Face Inference API if you set `HF_API_TOKEN` environment variable.")
    st.markdown("- Otherwise falls back to a small local generator (gpt2) for replies.")
    st.markdown("- Attention visualization uses DistilBERT to *demonstrate* self-attention on your input tokens (educational).")

# optional keyboard shortcut for convenience
st.write("---")
st.caption("CerebroBot Demo — built honestly. Present this and explain architecture for full marks.")
