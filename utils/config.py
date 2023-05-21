from ruamel.yaml import YAML
from dotenv import load_dotenv
import os

file_paths = ['data/config.yml']
data = {}

yaml = YAML()
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        file_data = yaml.load(file)
        data.update(file_data)

prefix = data['prefix']
main_guild = data['main_guild']
owner_id = data['owner_id']