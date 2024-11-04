# import os
# import yaml

# def load_yaml(file_path):
#     """Load YAML file content."""
#     try:
#         with open(file_path, 'r') as file:
#             return yaml.safe_load(file)
#     except FileNotFoundError:
#         print(f"Error: The file '{file_path}' was not found.")
#         return None
#     except yaml.YAMLError as e:
#         print(f"Error: YAML parsing error in '{file_path}': {e}")
#         return None

# def update_yaml(file_path, data):
#     """Write updated content back to YAML file."""
#     try:
#         with open(file_path, 'w') as file:
#             yaml.safe_dump(data, file, sort_keys=False, default_flow_style=False)
#         print(f"Updated '{file_path}' successfully.")
#     except IOError as e:
#         print(f"Error writing to '{file_path}': {e}")

# # Define the path to the directory containing YAML files
# target_yaml_folder = r'D:\best_practices\git_aws\compliance\aws\comprehensive_best_practices\aws_cloud_map'  # Replace with your actual folder path

# # Iterate over each YAML file in the target directory
# for filename in os.listdir(target_yaml_folder):
#     if filename.endswith(".yaml"):  # Only process YAML files
#         file_path = os.path.join(target_yaml_folder, filename)

#         # Load the target YAML file
#         target_data = load_yaml(file_path)

#         if target_data is not None:
#             # Check if target_data is a list
#             if isinstance(target_data, list):
#                 # Iterate through each item to update the ID
#                 for item in target_data:
#                     if isinstance(item, dict) and 'rule' in item:
#                         # Access the nested 'rule' dictionary
#                         rule = item['rule']
#                         if isinstance(rule, dict):  # Ensure 'rule' is a dictionary
#                             rule['ID'] = 'AWSCloudMap'  # New ID value
#                             print(f"Updated ID for rule '{rule.get('Title', 'Unnamed')}' to '{rule['ID']}' in '{filename}'.")
#                         else:
#                             print(f"Warning: 'rule' in '{filename}' is not a dictionary: {rule}")

#             # Save the updated target YAML file
#             update_yaml(file_path, target_data)

# print(f"Updated all YAML files in '{target_yaml_folder}' with respective IDs.")


import os
import yaml

def load_yaml(file_path):
    """Load YAML file content."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: YAML parsing error in '{file_path}': {e}")
        return None

def update_yaml(file_path, data):
    """Write updated content back to YAML file."""
    try:
        with open(file_path, 'w') as file:
            yaml.safe_dump(data, file, sort_keys=False, default_flow_style=False)
        print(f"Updated '{file_path}' successfully.")
    except IOError as e:
        print(f"Error writing to '{file_path}': {e}")

def update_rule_id(rules, new_id):
    """Update ID for each rule in the list of rules."""
    for rule in rules:
        if isinstance(rule, dict) and 'ID' in rule:
            rule['ID'] = new_id  # Update to the new ID value
            print(f"Updated ID for rule '{rule.get('Title', 'Unnamed')}' to '{rule['ID']}'.")

def traverse_and_update(data, key_to_update, new_value):
    """Recursively traverse the data structure to update specified keys."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_to_update:
                data[key] = new_value
                print(f"Updated '{key}' to '{new_value}'.")
            else:
                traverse_and_update(value, key_to_update, new_value)
    elif isinstance(data, list):
        for item in data:
            traverse_and_update(item, key_to_update, new_value)

# Define the path to the directory containing YAML files
target_yaml_folder = r'D:\best_practices\git_aws\compliance\aws\comprehensive_best_practices\amazon_pinpoint'

# Specify the key and the new value for updating
key_to_update = 'ID'  # Change as needed (e.g., 'Title', 'Description')
new_value = 'pinpoint'  # New value to set for the specified key

# Iterate over each YAML file in the target directory
for filename in os.listdir(target_yaml_folder):
    if filename.endswith(".yaml"):  # Only process YAML files
        file_path = os.path.join(target_yaml_folder, filename)

        # Load the target YAML file
        target_data = load_yaml(file_path)

        if target_data is not None:
            # Update IDs specifically in rules
            if isinstance(target_data, dict) and 'rule' in target_data:
                rules = target_data['rule']
                if isinstance(rules, list):
                    update_rule_id(rules, new_value)

            # Traverse and update any other specified keys
            traverse_and_update(target_data, key_to_update, new_value)

            # Save the updated target YAML file
            update_yaml(file_path, target_data)

print(f"Updated all YAML files in '{target_yaml_folder}' with specified updates.")
