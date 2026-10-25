# Notes for whoever maintains this repo (usually Claude)

- Explain changes in plain Chinese, deliver updates as ready-to-use files, and never ask the owner to edit code.
- Target runtime is **Windows + Python 3.11**. Always run `python3.11 -m py_compile core.py bot.py` before shipping (3.12+ syntax such as backslashes inside f-string expressions crashes on 3.11).
- `.bat` / `.ps1` files must use CRLF line endings; `.ps1` files need a UTF-8 BOM (Windows PowerShell 5.1 reads Chinese otherwise as garbage).
- Test without spending quota: set `"mock": true` in a config copy and run `python bot.py --local --config <copy>`; for the real CLI paths, use small fake `claude` / `codex` scripts on PATH.
- New config keys go into `config.example.json`; `load_config` fills missing keys from it automatically, so users never need to hand-edit their `config.json` after an update.
- Never commit `config.json`, `state/`, `项目/`, `信箱/`, `回收站/` (see `.gitignore`).
- Security model to preserve: GPT is read-only (and Computer Use / browser features are disabled) except on a turn whose `[方案]` was approved; AIs cannot delete files themselves (button + recycle folder); only the owner's Discord ID is obeyed; never add features that resell or proxy access to Claude/OpenAI.
- Review every outside pull request yourself before the owner merges it.
