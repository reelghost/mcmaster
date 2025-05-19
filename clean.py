import csv

def clean_weight(weight):
    if not weight:
        return weight
    
    # Print the actual characters to debug
    print(f"Original weight: {weight}")
    print(f"Character codes: {[ord(c) for c in weight]}")
    
    # Try different bullet point characters
    bullet_chars = ['•', '·', '∙', '⋅', 'x', 'X']
    for bullet in bullet_chars:
        if bullet in weight:
            weight = weight.split(bullet)[0].strip()
            print(f"Found bullet {bullet}, cleaned to: {weight}")
            return weight
            
    return weight.strip()

# Define input/output path
csv_path = 'doordash\\vitamins.csv'

# Read input CSV
with open(csv_path, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile, delimiter='|')
    header = next(reader)
    rows = list(reader)

# Print first few rows before cleaning
print("\nBefore cleaning:")
for row in rows[:3]:
    print(row[4])

# Clean weight column
for row in rows:
    row[4] = clean_weight(row[4])

# Print first few rows after cleaning
print("\nAfter cleaning:")
for row in rows[:3]:
    print(row[4])

# Write output CSV 
with open(csv_path, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile, delimiter='|')
    writer.writerow(header)
    writer.writerows(rows)
