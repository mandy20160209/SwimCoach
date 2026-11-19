After each save point, push it to GitHub.

# SwimCoach notes

## How to run

1. Put the MindDo `KEYGEN_URL` and `KEYGEN_TOKEN` in the local `.env` file. Never share them in chat or commit them.
2. Run: `python3 server.py`
3. Open: http://localhost:8000

Model: `gpt-5.6-luna` (set `OPENAI_MODEL` in the environment if your account uses a different available model).

## What’s done

- Version 1 web app with a written posture description, guided posture feedback, and safe lessons.
- Posture lesson links, a swimmer-level check, and a real server-side AI question flow.
- The AI key comes from `getKey()` through the server-only key helper; it is never sent to the browser.
- AI requests include the project instructions from `BRIEF.md` every time.
- Buttons show “Thinking…” and are disabled during an AI request.
- Browser progress is saved in `storage.js` using localStorage.
- Saves on this computer only for now.
- After each save point, push it to GitHub.

## Safety

- Think first before asking the AI.
- Swim with a coach, lifeguard, or responsible adult nearby. Never swim alone.
- Stop for pain, dizziness, or trouble breathing. The app is not a medical or competition judge.

## MVP check

- Written posture check: works from the swimmer’s own description and gives simple, guided feedback.
- Fix-posture videos: works through clearly labeled YouTube search links.
- Swimming knowledge: works through the level selector and local save.
- Safe AI answers: works when MindDo returns a current key, the internet works, and the configured model works; otherwise it shows `error.message` and logs `error.fix` once.

## Vercel

- The page is static at the project root.
- The online AI endpoint is `api/coach.py`, a Vercel Python Function served at `/api/coach`.
- Vercel finds the function automatically from the `api` folder; no special build command or `vercel.json` setting is needed.
- Add two Vercel environment variables named `KEYGEN_URL` and `KEYGEN_TOKEN` for the Production, Preview, and Development environments as needed. Do not add the OpenAI key to Vercel.
- `OPENAI_MODEL` is optional. If it is not set, the function uses `gpt-5.6-luna`.
- The local command remains `python3 server.py`; it reads the MindDo settings from the ignored local `.env` file.
- Browser saving remains localStorage on each device; Vercel does not add a database.

## Maybe Later

- Show an AI response in detail about what the user does wrong.
- Improve the written posture description with more tested examples.

## Next

- Test the written posture guidance with swimmers and coaches.
- Verify the model name and key with the OpenAI account.
- Add a short demo script and challenge entry materials.
