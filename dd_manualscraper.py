import json
import csv
import re
import os
import urllib.parse


def extract_json_from_txt():
    # Clear the existing data in extracted_data.json
    with open("extracted_data.json", "w", encoding="utf-8") as json_file:
        json_file.write("")

    with open("raw_data.txt", "r", encoding="utf-8") as u_:
        r_data = u_.read().strip()
    # Regular expression to find JSON objects starting with {"badges":[],"image":{"remote":{"uri":
    pattern = r'\{"badges":\[\],"image":\{"remote":\{"uri":.*?\}\}\}\}'

    category_match = re.search(r'"categoryUrlSlug","([a-zA-Z0-9_%\-]+)-\d+"', r_data)
    subcategory_match = re.search(r'"rawSubCategoryUrlSlug","sub-category/([a-zA-Z0-9_%\-]+)-\d+"', r_data)
    category = urllib.parse.unquote(category_match.group(1)) if category_match else None
    subcategory = urllib.parse.unquote(subcategory_match.group(1)) if subcategory_match else None
    

    matches = re.findall(pattern, r_data)

    extracted_json = []
    for match in matches:
        try:
            parsed_json = json.loads(match)  # Validate JSON
            extracted_json.append(parsed_json)
        except json.JSONDecodeError:
            continue  # Ignore invalid JSON

    # Save valid JSON objects to output file
    with open("extracted_data.json", "w", encoding="utf-8") as json_file:
        json.dump(extracted_json, json_file, indent=2, ensure_ascii=False)

    print(
        f"[RWDATA] Extracted {len(extracted_json)} valid JSON objects and saved to extracted_data.json")
    return category.title(), subcategory.title()


def extract_json(rdata):
    # Clear the existing data in extracted_data.json
    with open("extracted_data.json", "w", encoding="utf-8") as json_file:
        json_file.write("")

    category = rdata.get("data").get("retailStoreCategoryFeed").get("name")
    sub_category = rdata.get("data").get(
        "retailStoreCategoryFeed").get("selectedL2Category").get("name")
    items = rdata.get("data").get(
        "retailStoreCategoryFeed").get("legoRetailItems", None)
    # items = rdata.get("data").get("retailStorePageFeed").get("legoSectionBodyList")
    print(f"[API] Extracted a total {len(items)} items")
    for item in items:
        try:
            custom_data = item.get("custom", "")
            with open("raw_data.txt", "a", encoding="utf-8") as rd:
                rd.write(custom_data + ",")
        except TypeError:
            pass

    with open("raw_data.txt", "r", encoding="utf-8") as rd:
        radata = rd.read()
    # Regular expression to find JSON objects starting with {"badges":[],"image":{"remote":{"uri":
    pattern = r'\{"badges":\[\],"image":\{"remote":\{"uri":.*?\}\}\}\}'
    matches = re.findall(pattern, radata)

    extracted_json = []
    for match in matches:
        try:
            parsed_json = json.loads(match)  # Validate JSON
            extracted_json.append(parsed_json)
        except json.JSONDecodeError:
            continue  # Ignore invalid JSON

    # Save valid JSON objects to output file
    with open("extracted_data.json", "w", encoding="utf-8") as json_file:
        json.dump(extracted_json, json_file, indent=2, ensure_ascii=False)

    return category, sub_category


def process_json_to_csv(category, sub_category):
    with open("extracted_data.json", "r", encoding="utf-8") as efile:
        edata = json.load(efile)
    # Open CSV file for writing
    if not os.path.exists(f"doordash/{category}"):
        os.makedirs(f"doordash/{category}")

    # csv_file = f"doordash/{category}/{sub_category}.csv"
    csv_file = f"doordash/{category}/{category}.csv"
    with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["prod_id", "category", "subCategory", "imageUrl",
                        "name", "weight", "stock", "description", "price", "msid"])

        for item in edata:
            try:
                prod_id = item.get("item_data", {}).get("item_id", "")
                image_url = item.get("image", {}).get("remote", {}).get(
                    "uri", "").split("format=auto/")[1]
                name = item.get("item_data", {}).get(
                    "item_name", "").replace('"', '""').replace(",", "")
                weight = item.get("price_name_info", {}).get(
                    "default", {}).get("base", {}).get("subtext", "")
                if not weight:
                    weight = name.split(
                        "(")[-1].replace("(", "").replace(")", "")
                description = item.get("logging", {}).get("description", "")
                price = item.get("price_name_info", {}).get("default", {}).get("base", {}).get(
                    "price", {}).get("discount_price_v2", {}).get("nondiscounted_price", "")
                if not price:
                    price = item.get("item_data", {}).get(
                        "price", {}).get("display_string", "")
                upc = str(item.get("item_data", {}).get("item_msid", ""))
                stock = item.get("logging", {}).get(
                    "badges", "").split(",")[-1]
                if not stock or "stock" not in stock:
                    stock = item.get("item_data", {}).get("stock_level", "")

                # Write row to CSV
                writer.writerow([prod_id, category, sub_category, image_url,
                                name, weight, stock, description, price, upc])
            except Exception as e:
                print(f"Error processing item: {e}")

    print(f"{sub_category} saved in CSV file as {csv_file}")
    # write nothing on rdata and raw_data
    with open("rdata.json", "w", encoding="utf-8") as r:
        r.write("")
    with open("raw_data.txt", "w", encoding="utf-8") as rd:
        rd.write("")
    
    # Example usage
try:
    with open("rdata.json", "r", encoding="utf-8") as r:
        rdatas = json.load(r)
    # for rdata in rdatas: an edit as rdata is not a list now
    category, sub_category = extract_json(rdatas)
    process_json_to_csv(category, sub_category)
except json.JSONDecodeError:
    print("Using raw_data part")
    category, sub_category = extract_json_from_txt()
    # category = "Beauty"
    # sub_category = "Makeup"
    process_json_to_csv(category, sub_category)

