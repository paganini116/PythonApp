# Date Spot CLI

A minimal Python CLI that takes two food preferences, a city, and a budget, then uses the OpenAI Chat Completions API to suggest date spots.

## Setup

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure your OpenAI API key is available in the shell:

```bash
export OPENAI_API_KEY="your_key_here"
```

## Run

```bash
python main.py \
  --person1-food sushi \
  --person2-food tacos \
  --city Seattle \
  --budget 120
```

## What Happens At Runtime

The app follows this call flow:

1. `main.py` calls `date_spot_cli.cli.main()`.
2. `build_parser()` defines and parses the CLI arguments.
3. `non_empty_string()` validates `--person1-food`, `--person2-food`, and `--city`.
4. `positive_int()` validates `--budget`.
5. `cli.main()` calls `suggest_date_spots()`.
6. `get_api_key()` checks that `OPENAI_API_KEY` exists.
7. `build_prompt()` creates the prompt using the food preferences, city, and budget.
8. `suggest_date_spots()` calls `client.chat.completions.create(...)`.
9. The model returns 3 recommendations as text.
10. `format_output()` builds the terminal-friendly output.
11. `cli.main()` prints the final result.

## Function Responsibilities

- `main.py`: program entrypoint
- `build_parser()`: defines the CLI interface
- `non_empty_string()`: validates required text inputs
- `positive_int()`: validates the budget
- `cli.main()`: orchestrates parse, validate, request, and print
- `format_output()`: formats the final terminal output
- `get_api_key()`: validates environment configuration
- `build_prompt()`: builds the user prompt sent to OpenAI
- `suggest_date_spots()`: performs the Chat Completions API request

## Test

```bash
pytest tests/
```
