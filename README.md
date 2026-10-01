# Antenna Sanitizer

Terminal user interface built with [Textual](https://github.com/Textualize/textual).

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python 3.14, the venv and dependencies)
- `make`

## Quick start

```bash
make install   # create .venv and install dependencies
make run       # launch the TUI
make help      # list all commands
```

## Development

| Command             | Description                                  |
| ------------------- | -------------------------------------------- |
| `make dev`          | Run with Textual dev mode (live CSS reload)  |
| `make console`      | Textual devtools console (use with `dev`)    |
| `make lint`         | Ruff lint                                    |
| `make format`       | Ruff format                                  |
| `make check`        | Lint + format check — run before PRs         |

## Layout

```
src/
├── main.py             # module entrypoint — launches the TUI
├── core/               # domain logic — no UI imports
│   └── stations.py     # station data loading and sampling
└── tui/                # Textual presentation layer
    ├── app.py
    ├── screens/
    ├── widgets/
    └── styles/app.tcss
```

`core` is independent of `tui`, so domain logic can be reused without the interface.
