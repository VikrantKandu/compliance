# import os
# import yaml
# import boto3
# from datetime import datetime

# # Initialize DynamoDB resource
# dynamodb = boto3.resource('dynamodb')
# table_name = 'AuditCheck'

# # Create or load DynamoDB table
# def initialize_table():
#     try:
#         table = dynamodb.Table(table_name)
#         table.load()
#         print(f"Table '{table_name}' already exists.")
#     except dynamodb.meta.client.exceptions.ResourceNotFoundException:
#         print(f"Table '{table_name}' does not exist. Creating table...")
#         table = dynamodb.create_table(
#             TableName=table_name,
#             KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
#             AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
#             ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
#         )
#         table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
#         print(f"Table '{table_name}' created successfully.")
#     return table

# # Function to determine the next available item ID for a given rule_id
# def generate_item_id(table, rule_id):
#     # Query existing items with the rule_id prefix
#     response = table.scan(
#         FilterExpression="begins_with(id, :rule_id)",
#         ExpressionAttributeValues={":rule_id": rule_id}
#     )
    
#     # Extract existing suffixes and determine the next increment
#     existing_ids = [item['id'] for item in response.get('Items', [])]
#     suffix_numbers = [
#         int(id.split('_')[-1]) for id in existing_ids if id.startswith(rule_id)
#     ]
    
#     # Determine the next suffix
#     next_suffix = max(suffix_numbers) + 1 if suffix_numbers else 1
#     return f"{rule_id}_{next_suffix:03d}"

# # Function to store BestPractices, Audit, and Recommendation in DynamoDB
# def store_audit_summary(table, item_id, best_practices, audit_steps, recommendation_steps):
#     try:
#         table.put_item(
#             Item={
#                 'id': item_id,
#                 'BestPractices': best_practices,
#                 'Audit': audit_steps,
#                 'Recommendation': recommendation_steps
#             }
#         )
#         print(f"Audit summary for item ID '{item_id}' added to the table.")
#     except Exception as e:
#         print(f"Failed to store audit summary for item ID '{item_id}': {str(e)}")

# # Main function to process YAML files and store audit summaries
# def main():
#     table = initialize_table()
#     yaml_directory = r'D:\best_practices\git_aws\compliance\aws\comprehensive_best_practices\access_analyzer'

#     # Process each YAML file in the directory
#     for filename in os.listdir(yaml_directory):
#         if filename.endswith('.yml') or filename.endswith('.yaml'):
#             file_path = os.path.join(yaml_directory, filename)

#             with open(file_path, 'r') as file:
#                 content = yaml.safe_load(file)
#                 print(f"Loaded content from {filename}:", content)

#                 if isinstance(content, list):
#                     for rule in content:
#                         rule_data = rule.get('rule') if isinstance(rule, dict) else None

#                         if isinstance(rule_data, dict):
#                             rule_id = rule_data.get('ID', 'UnknownID')
#                             item_id = generate_item_id(table, rule_id)

#                             best_practices = {
#                                 'Title': rule_data.get('Title'),
#                                 'Profile Applicability': rule_data.get('Profile Applicability'),
#                                 'Description': rule_data.get('Description'),
#                                 'Rationale': rule_data.get('Rationale')
#                             }
#                             audit_steps = rule_data.get('Audit', [])
#                             recommendation_steps = rule_data.get('Remediation', [])

#                             store_audit_summary(
#                                 table=table,
#                                 item_id=item_id,
#                                 best_practices=best_practices,
#                                 audit_steps=audit_steps,
#                                 recommendation_steps=recommendation_steps
#                             )

#                         else:
#                             print(f"Warning: Expected a dictionary for rule_data, got {type(rule_data)}. Skipping this entry.")
#                 else:
#                     print(f"Unexpected structure in file {filename}: Expected a list.")

# # Run the main function
# if __name__ == "__main__":
#     main()



import os
import yaml
import boto3
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = 'AuditCheck'

# Create or load DynamoDB table
def initialize_table():
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table '{table_name}' already exists.")
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        print(f"Table '{table_name}' does not exist. Creating table...")
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table '{table_name}' created successfully.")
    return table

# Function to generate item ID, starting at 001
def generate_item_id(rule_id, index):
    return f"{rule_id}_{index:03d}"

# Function to store BestPractices, Audit, and Recommendation in DynamoDB
def store_audit_summary(table, item_id, best_practices, audit_steps, recommendation_steps):
    try:
        table.put_item(
            Item={
                'id': item_id,
                'BestPractices': best_practices,
                'Audit': audit_steps,
                'Recommendation': recommendation_steps
            }
        )
        print(f"Audit summary for item ID '{item_id}' added to the table.")
    except Exception as e:
        print(f"Failed to store audit summary for item ID '{item_id}': {str(e)}")

# Main function to process YAML files and store audit summaries
def main():
    table = initialize_table()
    yaml_directory = r'D:\best_practices\git_aws\compliance\aws\comprehensive_best_practices\aws_cloud_map'
    # Process each YAML file in the directory
    item_index = 1  # Start item index at 1 for each run
    for filename in os.listdir(yaml_directory):
        if filename.endswith('.yml') or filename.endswith('.yaml'):
            file_path = os.path.join(yaml_directory, filename)

            with open(file_path, 'r') as file:
                content = yaml.safe_load(file)
                print(f"Loaded content from {filename}:", content)

                if isinstance(content, list):
                    for rule in content:
                        rule_data = rule.get('rule') if isinstance(rule, dict) else None

                        if isinstance(rule_data, dict):
                            rule_id = rule_data.get('ID', 'UnknownID')
                            item_id = generate_item_id(rule_id, item_index)
                            item_index += 1  # Increment index for each item

                            best_practices = {
                                'Title': rule_data.get('Title'),
                                'Profile Applicability': rule_data.get('Profile Applicability'),
                                'Description': rule_data.get('Description'),
                                'Rationale': rule_data.get('Rationale')
                            }
                            audit_steps = rule_data.get('Audit', [])
                            recommendation_steps = rule_data.get('Remediation', [])

                            store_audit_summary(
                                table=table,
                                item_id=item_id,
                                best_practices=best_practices,
                                audit_steps=audit_steps,
                                recommendation_steps=recommendation_steps
                            )

                        else:
                            print(f"Warning: Expected a dictionary for rule_data, got {type(rule_data)}. Skipping this entry.")
                else:
                    print(f"Unexpected structure in file {filename}: Expected a list.")

# Run the main function
if __name__ == "__main__":
    main()
