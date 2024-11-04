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
        table.load()  # Raises exception if table does not exist
        print(f"Table '{table_name}' already exists.")
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        print(f"Table '{table_name}' does not exist. Creating table...")
        # Create the table if it doesn't exist
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'  # String
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        # Wait for the table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table '{table_name}' created successfully.")
    return table

# Function to store audit summary in DynamoDB
def store_audit_summary(table, aws, servicecode, item_id, best_practices, result, recommendation, command, timestamp):
    try:
        table.put_item(
            Item={
                'id': item_id,
                'aws': aws,
                'servicecode': servicecode,
                'best_practices': best_practices,
                'result': result,
                'recommendation': recommendation,
                'command': command,
                'timestamp': timestamp
            }
        )
        print(f"Audit summary for file '{item_id}' added to the table.")
    except Exception as e:
        print(f"Failed to store audit summary for file '{item_id}': {str(e)}")

# Function to generate a static ID
def generate_static_id(index, service_code):
    return f"{service_code}_{index}"

# Main function to process YAML files and store audit summaries
def main():
    # Initialize the DynamoDB table
    table = initialize_table()

    # Directory containing YAML files
    yaml_directory = r'D:\best_practices\git_aws\compliance\aws\comprehensive_best_practices\amazon_api_gateway'  # Update this path

    # Process each YAML file in the directory
    file_index = 1
    for filename in os.listdir(yaml_directory):
        if filename.endswith('.yml') or filename.endswith('.yaml'):
            file_path = os.path.join(yaml_directory, filename)

            with open(file_path, 'r') as file:
                best_practices = yaml.safe_load(file)
                print(f"Loaded content from {filename}:", best_practices)

                # Ensure the content is a list
                if isinstance(best_practices, list):
                    for rule in best_practices:
                        rule_data = rule.get('rule', {})
                        print(f"Processing rule: {rule_data}")  # Updated to use rule_data

                        # Access audit checks and recommendations directly from rule_data
                        audit_checks = rule_data.get('Audit', [])
                        recommendation_steps = rule_data.get('Remediation', [])

                        # Print audit checks and recommendation steps
                        print("Audit Checks:", audit_checks)
                        print("Recommendation Steps:", recommendation_steps)

                        # Ensure they are lists
                        if not isinstance(audit_checks, list):
                            print(f"Warning: Invalid 'Audit' format in {filename}. Using empty list.")
                            audit_checks = []
                        
                        if not isinstance(recommendation_steps, list):
                            print(f"Warning: Invalid 'Remediation' format in {filename}. Using empty list.")
                            recommendation_steps = []

                        # Define command structure
                        command = {
                            "action": "Audit Root Account MFA",
                            "details": "Ensure MFA is enabled for the AWS root account."
                        }

                        # Determine pass/fail result
                        file_result = "Pass"
                        for step in audit_checks:
                            if "MFA" in step:  # Example check for MFA failure
                                file_result = "Fail"
                                print("Audit failed due to missing MFA.")
                                break

                        # Always store the recommendation steps
                        recommendation = {
                            "steps": recommendation_steps
                        }

                        # Store in DynamoDB
                        pss = "Amazon_Api Gateway"  # Replace or dynamically determine as needed
                        store_audit_summary(
                            table=table,
                            aws="AWS",
                            servicecode=f"Servicecode",
                            item_id=generate_static_id(file_index, pss),
                            best_practices=rule_data,
                            result=file_result,
                            recommendation=recommendation,
                            command=command,
                            timestamp=datetime.now().isoformat()
                        )

                        file_index += 1
                else:
                    print(f"Unexpected structure in file {filename}: Expected a list.")

# Run the main function
if __name__ == "__main__":
    main()



