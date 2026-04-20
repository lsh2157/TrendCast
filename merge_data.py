import json

def merge_and_clean_json(file_list, output_file):
    combined_data = []
    for file_name in file_list:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        combined_data.append(json.loads(line))
            print(f"successfully read: {file_name}")
        except Exception as e:
            print(f"read {file_name} error: {e}")

    seen_identifiers = set()
    cleaned_data = []

    for item in combined_data:
        source = item.get('source', '')
        
        if source == "Google Trends":
            identifier = f"{item.get('keyword')}_{item.get('timestamp')}"
        else:
            identifier = f"{item.get('title')}_{item.get('publishedAt')}"

        if identifier not in seen_identifiers:
            cleaned_data.append(item)
            seen_identifiers.add(identifier)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
    
    print(f"--- processed ---")
    print(f"original data: {len(combined_data)} | adjusted data: {len(cleaned_data)}")

merge_and_clean_json(['kafka_backup.json', 'kafka_backup_0415.json', 'kafka_backup_0417.json'], 'final_cleaned_data.json')