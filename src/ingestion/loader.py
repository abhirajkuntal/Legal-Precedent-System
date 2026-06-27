from pathlib import Path

from src.ingestion.parser import parse_case_file


def load_all_cases(data_dir: str):

    data_path = Path(data_dir)

    all_cases = []

    for json_file in data_path.rglob("*.json"):

        # Skip metadata files
        if "metadata" in json_file.parts:
            continue

        try:
            case = parse_case_file(json_file)

            all_cases.append(case)

        except Exception as e:
            print(f"Failed: {json_file}")
            print(e)

    return all_cases


# yield_all_cases - yield one parsed case at a time - to save memory - to work with larger dataset 
'''
def yield_all_cases(data_dir: str):
    data_path = Path(data_dir)

    # Use rglob to recursively find all JSON files
    for json_file in data_path.rglob("*.json"):

        # Skip metadata files
        if "metadata" in json_file.parts:
            continue

        try:
            # Yield hands the parsed case back to the caller one at a time
            # instead of storing them all in a massive list.
            yield parse_case_file(json_file)

        except Exception as e:
            print(f"Failed to process {json_file}: {e}")
'''

