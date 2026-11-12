# Instructions for AI coding agents (any model)

You are helping a person make a motion-graphics video with **Motion Graphics Studio**. Read `SKILL.md` first: it is the complete, tool-agnostic workflow. Essentials:

1. Run `python -m mgs doctor`. Fix what it reports before anything else.
2. Never claim a render worked without looking at it: render **stills**, view the image, then render; afterwards run `python -m mgs check` and view `check_sheet.png`.
3. Everything is free and offline. Do not add paid services, API keys or network calls.
4. Only use facts you verified; mark illustrative visuals as illustrative; tell the user what is estimated (timing) or untested.
5. Keep replies short and in the user's language/dialect. If `profiles/*.md` matches the user's channel, follow it.
6. Long renders: `python -m mgs render project.py --detach`, then poll `render.log`.
