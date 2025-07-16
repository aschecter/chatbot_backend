// server.js
import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import OpenAI from 'openai';


const app = express().use(cors()).use(express.json());
app.options('*', cors());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,   // put this in a .env file, never hard-code
});

// ✨ experiment-specific rules go here
function buildSystemPrompt(variant) {
  if (variant === 'A') {
    return `You are Chatbot-A. Respond to user questions`;
  }
  if (variant === 'B') {
    return `You are Chatbot-B. [[ DEFINE RULES FOR VARIANT B HERE ]]`;
  }
  return 'You are a helpful assistant.';
}

app.post('/chat', async (req, res) => {
  const {messages, variant, meta} = req.body;           // messages = [{role,content}, …]
  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4.1-mini',                              // or whichever model you test
      messages: [
        {role: 'system', content: buildSystemPrompt(variant)},
        ...messages,
      ],
      temperature: 0.7,                                  // [[ TUNE ]]
    });   // :contentReference[oaicite:0]{index=0}

    // TODO: persist {messages, variant, meta, reply: completion.choices[0]} to your DB/file
    res.json({reply: completion.choices[0].message.content});
  } catch (err) {
    console.error(err);
    res.status(500).json({error: 'API failure'});
  }
});

app.listen(process.env.PORT || 3000, () =>
  console.log('Chat backend listening on :3000'),
);
