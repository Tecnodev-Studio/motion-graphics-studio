# Using it with different AI assistants

The toolkit is just files + a CLI, so any assistant that can read files and run shell commands can drive it.
- **Claude (skills / Claude Code)**: copy this folder (or only `SKILL.md` + the repo) into the skills directory; the frontmatter in `SKILL.md` makes it auto-trigger.
- **OpenAI Codex CLI, Cursor, Gemini CLI, Aider, Cline, OpenCode, Continue...**: they read `AGENTS.md` (or your rules file) - it points to `SKILL.md`. Tell the agent: "Follow SKILL.md in this repo".
- **Local models** (Ollama, LM Studio, llama.cpp front-ends with tool use): same; smaller models do better with the examples: say "copy `examples/compare/project.py` and change texts, times and colours".
- **Chat-only assistants (no shell)**: ask the assistant to write `project.py` and `phrases.txt`; you run the commands from the README yourself and paste back any error text and what `sheet.png` looks like.
Tips for any model: always render stills and look at them; keep `project.py` small and edit instead of rewriting; use `MGS_DURATION=5` for quick tests; never run unreviewed project files.
