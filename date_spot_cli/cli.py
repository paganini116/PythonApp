import argparse
import itertools
import sys
import threading
import time

from date_spot_cli.openai_client import suggest_date_spots


RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"


def non_empty_string(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise argparse.ArgumentTypeError("value must be a non-empty string")
    return cleaned


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("budget must be an integer") from exc

    if parsed <= 0:
        raise argparse.ArgumentTypeError("budget must be a positive integer")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Suggest date spots based on food preferences, city, and budget."
    )
    parser.add_argument(
        "--person1-food",
        required=True,
        type=non_empty_string,
        help="Food preference for the first person.",
    )
    parser.add_argument(
        "--person2-food",
        required=True,
        type=non_empty_string,
        help="Food preference for the second person.",
    )
    parser.add_argument(
        "--city",
        required=True,
        type=non_empty_string,
        help="City to search in.",
    )
    parser.add_argument(
        "--budget",
        required=True,
        type=positive_int,
        help="Total budget for the date.",
    )
    return parser


def format_output(
    person1_food: str,
    person2_food: str,
    city: str,
    budget: int,
    suggestions: str,
) -> str:
    header = build_boxed_header("DATE SPOT SUGGESTIONS")
    details = (
        f"{CYAN}City:{RESET} {city}\n"
        f"{CYAN}Preferences:{RESET} {person1_food}, {person2_food}\n"
        f"{CYAN}Budget:{RESET} ${budget}"
    )
    return f"{header}\n{details}\n\n{suggestions}"


def build_boxed_header(title: str) -> str:
    width = len(title) + 4
    top_bottom = f"{CYAN}+{'-' * width}+{RESET}"
    middle = f"{CYAN}|{RESET}  {BOLD}{title}{RESET}  {CYAN}|{RESET}"
    return f"{top_bottom}\n{middle}\n{top_bottom}"


class Spinner:
    def __init__(self, message: str) -> None:
        self.message = message
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._start_time = 0.0

    def start(self) -> None:
        self._start_time = time.time()
        print(f"[...] {self.message}...")
        self._thread.start()

    def stop(self) -> None:
        elapsed = time.time() - self._start_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._stop_event.set()
        self._thread.join()
        clear_line = " " * (len(self.message) + 4)
        sys.stdout.write(f"\r{clear_line}\r")
        sys.stdout.flush()

    def _spin(self) -> None:
        for frame in itertools.cycle("|/-\\"):
            if self._stop_event.is_set():
                break
            sys.stdout.write(f"\r{CYAN}{self.message}{RESET} {frame}")
            sys.stdout.flush()
            time.sleep(0.1)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    spinner = Spinner("Looking for date spots")

    try:
        spinner.start()
        suggestions = suggest_date_spots(
            person1_food=args.person1_food,
            person2_food=args.person2_food,
            city=args.city,
            budget=args.budget,
        )
    except ValueError as exc:
        spinner.stop()
        parser.exit(status=1, message=f"Error: {exc}\n")
    except Exception as exc:
        spinner.stop()
        parser.exit(status=1, message=f"OpenAI request failed: {exc}\n")
    spinner.stop()
    print(f"[OK] Found a few date spot ideas.\n")

    print(
        format_output(
            person1_food=args.person1_food,
            person2_food=args.person2_food,
            city=args.city,
            budget=args.budget,
            suggestions=suggestions,
        )
    )
    return 0
