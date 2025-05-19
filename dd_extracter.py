import re
import json

def extract_json_from_txt(file_path, output_file):
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read().strip()
    # Regular expression to find JSON objects starting with {"badges":[],"image":{"remote":{"uri":
    pattern = r'\{"badges":\[\],"image":\{"remote":\{"uri":.*?\}\}\}\}'
    matches = re.findall(pattern, data)

    extracted_json = []
    for match in matches:
        try:
            parsed_json = json.loads(match)  # Validate JSON
            extracted_json.append(parsed_json)
        except json.JSONDecodeError:
            continue  # Ignore invalid JSON

    # Save valid JSON objects to output file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(extracted_json, json_file, indent=2, ensure_ascii=False)

    print(f"Extracted {len(extracted_json)} valid JSON objects and saved to {output_file}")

# Example usage
file_path = "raw_data.txt"  # Replace with your actual file path
output_file = "extracted_data.json"
extract_json_from_txt(file_path, output_file)
