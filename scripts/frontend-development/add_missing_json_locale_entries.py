"""Tool for adding missing entries to json locales."""
import argparse
import json
from pathlib import Path


def merge_dicts(src_data: dict, dest_data: dict, sort_keys=False) -> dict:
    """Add missing entries to dictionary including nested entries
    Optionally applies sorting following original key order.
    """
    for msg_id, msg in src_data.items():
        if isinstance(msg, dict):
            dest_data[msg_id] = merge_dicts(msg, dest_data.get(msg_id, {}), sort_keys)
        else:
            if msg_id not in dest_data:
                dest_data[msg_id] = msg

    src_key_order = list(src_data.keys())
    return dict(sorted(dest_data.items(), key=lambda x: src_key_order.index(x[0])))


def update_locale(src_path: Path, dest_path: Path, sort_keys=False):
    """Adds missing messages from all files in src_path to dest_path.
    Updates existing files or creates new as required.
    """
    for src_filename in src_path.glob("*.json"):
        print(f"Reading file: {src_filename}")
        with open(src_filename, "r", encoding="utf-8") as src_file:
            src_data: dict = json.loads(src_file.read())
        dest_filename = dest_path / src_filename.name
        print(dest_filename)

        if dest_filename.exists():
            print("Reading existing translations")
            with open(dest_filename, "r", encoding="utf-8") as dest_file:
                dest_data: dict = json.loads(dest_file.read())
                print(dest_data)
        else:
            dest_data = dict()

        dest_data = merge_dicts(src_data, dest_data, sort_keys)

        with open(dest_filename, "w", encoding="utf-8", newline="\n") as dest_file:
            dest_file.write(json.dumps(dest_data, indent=2, ensure_ascii=False))
            dest_file.write("\n")


parser = argparse.ArgumentParser(description="Tool for adding missing entries in json locale files.")
parser.add_argument(
    "--src",
    help="Source directory from where the locale will be read, for example --src ./website/public/locales/en/",
    action="store",
    type=str,
    dest="src_dir",
    required=True,
)
parser.add_argument(
    "--dest",
    help="Target directory, where the locale will be updated",
    action="store",
    type=str,
    dest="dest_dir",
    required=True,
)
parser.add_argument(
    "--sort", help="Use to sort entries following source entries order", action="store_true", dest="sort_keys", default=False
)


if __name__ == "__main__":
    args = parser.parse_args()
    src_path = Path(args.src_dir)
    dest_path = Path(args.dest_dir)
    if not src_path.exists():
        raise RuntimeError(f"Provided source path doesn't exist: {args.src_dir}")
    if not dest_path.exists():
        raise RuntimeError(f"Provided source path doesn't exist: {args.dest_dir}")
    update_locale(src_path, dest_path, args.sort_keys)
