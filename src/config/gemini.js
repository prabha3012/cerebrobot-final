// gemini.js
import { GoogleGenAI } from "@google/genai";

// Paste your API key from Google AI Studio
const API_KEY = "AIzaSyCOkrj7YkETNum4rIsHhWsLs5AEoglyhXQ"; // 🔐 Don't share publicly!
const MODEL = "models/gemma-3-27b-it"; // ✅ Free-tier model

async function runChat(prompt) {
  const ai = new GoogleGenAI({ apiKey: API_KEY });

  const contents = [
    {
      role: "user",
      parts: [{ text: prompt }],
    },
  ];

  const config = {
    responseMimeType: "text/plain",
  };

  try {
    const response = await ai.models.generateContentStream({
      model: MODEL,
      contents,
      config,
    });

    let fullText = "";
    for await (const chunk of response) {
      fullText += chunk.text;
    }

    console.log(fullText);
    return fullText;
  } catch (err) {
    console.error("Gemini Error:", err.message);
    throw err;
  }
   
}

export default runChat;
