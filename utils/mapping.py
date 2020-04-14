import json

data = {'test': 'hello'}

with open('config\\mapping.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)