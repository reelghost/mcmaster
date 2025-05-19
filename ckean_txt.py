import json

def clean_json_lines(input_file, output_file):
    cleaned_lines = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()  # Remove leading/trailing spaces
            try:
                # Fix multiple backslashes and convert JSON string properly
                corrected_line = line.encode().decode('unicode_escape')
                corrected_line = corrected_line.replace('\\u0026', '&')  # Fix encoded ampersands
                
                # Parse the corrected JSON
                parsed_json = json.loads(corrected_line)
                
                # Append cleaned JSON
                cleaned_lines.append(parsed_json)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line: {line[:100]}...\nError: {e}")
    
    # Write the cleaned JSON as an array
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_lines, f, indent=4, ensure_ascii=False)

    print(f"Cleaned JSON saved to {output_file}")

# Example usage
clean_json_lines("raw_data.txt", "output.json")
