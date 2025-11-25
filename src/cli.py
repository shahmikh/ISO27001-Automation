# src/cli.py

import subprocess
import argparse
from pathlib import Path


# -------------------------
# Utility function
# -------------------------

def run_script(script_name):
    script_path = Path(__file__).resolve().parent / script_name
    print(f"\n▶️ Running {script_name} ...")
    result = subprocess.run(["python", str(script_path)], capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        print(f"✔ {script_name} completed successfully.\n")
    else:
        print(result.stdout)
        print(result.stderr)
        print(f"❌ Error running {script_name}.")
        exit(1)


# -------------------------
# Main CLI
# -------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ISO 27001 Compliance Automation Engine CLI"
    )

    parser.add_argument(
        "command",
        choices=["ingest", "map", "check", "export", "run-all"],
        help="Command to run"
    )

    args = parser.parse_args()

    if args.command == "ingest":
        run_script("ingest.py")

    elif args.command == "map":
        run_script("mapper.py")

    elif args.command == "check":
        run_script("checker.py")

    elif args.command == "export":
        run_script("exporter.py")

    elif args.command == "run-all":
        print("🚀 Running full automation pipeline...\n")

        run_script("ingest.py")
        run_script("mapper.py")
        run_script("checker.py")
        run_script("exporter.py")

        print("\n🎉 Pipeline completed successfully!")
        print("📁 Results available in the data/ folder.")
        print("📊 Excel: data/report.xlsx")
        print("📝 PDF:   data/summary.pdf")


if __name__ == "__main__":
    main()

