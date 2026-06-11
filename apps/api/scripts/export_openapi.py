import json
import sys
from pathlib import Path

from api.main import app


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openapi.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(app.openapi(), indent=2) + "\n")


if __name__ == "__main__":
    main()
