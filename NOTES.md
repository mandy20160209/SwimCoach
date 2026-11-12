After each save point, push it to GitHub.

# SwimCoach notes

## How to run

1. Put a valid OpenAI API key in the local `.env` file. Never share it in chat or commit it.
2. Run: `python3 server.py`
3. Open: http://localhost:8000

Model: `gpt-6-luna` (set `OPENAI_MODEL` in the environment if your account uses a different available model).

## What’s done

- Version 1 web app with a camera preview and posture reflection checklist.
- Posture lesson links, a swimmer-level check, and a real server-side AI question flow.
- The API key is read only by `server.py`; it is never sent to the browser.
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

- Camera posture check: works as a local camera preview and self-reflection checklist; automatic pose detection is next.
- Fix-posture videos: works through clearly labeled YouTube search links.
- Swimming knowledge: works through the level selector and local save.
- Safe AI answers: works when the local key, internet, and configured model work; otherwise it shows a friendly key/internet message.

## Vercel

- The page is static at the project root.
- The online AI endpoint is `api/coach.py`, a Vercel Python Function served at `/api/coach`.
- Vercel finds the function automatically from the `api` folder; no special build command or `vercel.json` setting is needed.
- Add one Vercel environment variable named `OPENAI_API_KEY` for the Production, Preview, and Development environments as needed.
- `OPENAI_MODEL` is optional. If it is not set, the function uses `gpt-6-luna`.
- The local command remains `python3 server.py`; it reads the key from the ignored local `.env` file.
- Browser saving remains localStorage on each device; Vercel does not add a database.

## Maybe Later

- Show an AI response in detail about what the user does wrong.
- Ask the user if the app can access the user’s camera.

## Next

- Replace the camera checklist with tested pose detection.
- Verify the model name and key with the OpenAI account.
- Add a short demo script and challenge entry materials.
