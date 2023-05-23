from ruamel.yaml import YAML

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
embed_color = data['embed_color']
embed_error_color = data['embed_error_color']