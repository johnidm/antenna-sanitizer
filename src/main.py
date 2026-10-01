"""Application entry point"""


def main() -> int:
    from src.tui.app import AntennaSanitizerApp  # noqa: PLC0415

    AntennaSanitizerApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
