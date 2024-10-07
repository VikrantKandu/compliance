import boto3
import yaml
import os
from datetime import datetime

# Load the policy from the YAML file
def load_policy(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to get the next available file suffix
def get_next_suffix(base_filename, output_dir):
    # Get the list of files in the output directory that match the base filename pattern
    existing_files = [f for f in os.listdir(output_dir) if f.startswith(base_filename) and f.endswith('.yaml')]
    
    # Extract existing suffix numbers
    suffixes = []
    for filename in existing_files:
        # Extract the number from the filename (e.g., from "filename.1.yaml" get "1")
        parts = filename.split('.')
        if len(parts) > 1 and parts[1].isdigit():
            suffixes.append(int(parts[1]))
    
    # Return the next suffix (1 greater than the max existing suffix)
    return max(suffixes, default=0) + 1

# Audit MFA status for IAM users according to the policy
def audit_policy(policies, output_dir, base_filename):
    iam_client = boto3.client('iam')
    
    # Get the current date for ID generation
    current_date = datetime.now().strftime('%Y%m%d')

    # Get the AWS account ID
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    
    # Define the AWS Account Name (you may want to change this if necessary)
    # account_name = "My AWS Account"  # Replace with the actual account name or retrieve dynamically if needed

    # Iterate over each rule in the policy
    for policy in policies:
        rule = policy.get('rule', {})
       
        # Check that the policy ID and title are correct
        print(f"Auditing policy: {rule['ID']} - {rule['Title']}")
        
        # Perform the actual audit using the AWS CLI commands outlined in the policy
        users = iam_client.list_users()
        
        for user in users['Users']:
            user_name = user['UserName']
            mfa_devices = iam_client.list_mfa_devices(UserName=user_name)
            recommendation = rule.get('Remediation')
            # Check if MFA is enabled
            if not mfa_devices['MFADevices']:
                # Create the ID in the specified format
                finding_id = f"{account_id}_{current_date}_{rule['ID']}"
                if not mfa_devices['MFADevices']:
                   status = 'DISABLED'  # Status when MFA is not enabled
                else:
                   status = 'ENABLED'  # Status when MFA is enabled
                # Prepare the output data
                output_data = {
                    # 'AWS Account Name': account_name,  # Now using AWS Account Name
                    'ID': finding_id,
                    'Service Name': rule['Title'],
                    'Status': status,
                    'Recommendation': recommendation
                }
                
                # Get the next available suffix
                next_suffix = get_next_suffix(base_filename, output_dir)
                
                # Generate the output file name with the incremented suffix
                output_file_name = f"{base_filename}.{next_suffix}.yaml"
                output_file_path = os.path.join(output_dir, output_file_name)
                
                # Save findings to the YAML file
                with open(output_file_path, 'w') as output_file:
                    yaml.dump(output_data, output_file)
                
                print(f"Finding for user '{user_name}' saved to '{output_file_path}'.")
            else:
                print(f"User '{user_name}' has MFA enabled.")

def main():
    policy_file = r'D:\best_practices\aws\comprehensive_best_practices\aws_account_management\AWS_Account_Management_best_practice_1.yaml'
    output_dir = r'D:\best_practices\aws\comprehensive_best_practices\aws_account_management\output'  # Specify your output directory

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract the base filename (without extension)
    base_filename = os.path.splitext(os.path.basename(policy_file))[0]
    
    # Load the policy from the YAML file
    policies = load_policy(policy_file)
    
    audit_policy(policies, output_dir, base_filename)

if __name__ == "__main__":
    main()
