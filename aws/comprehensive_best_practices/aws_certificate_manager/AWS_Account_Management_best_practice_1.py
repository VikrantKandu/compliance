import boto3
import yaml
import os
from datetime import datetime
from collections import OrderedDict

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

# Custom Dumper class to preserve order
class OrderedDumper(yaml.SafeDumper):
    pass

def _dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

OrderedDumper.add_representer(OrderedDict, _dict_representer)

# Audit MFA status for IAM users according to the policy
def audit_policy(policies, output_dir, base_filename):
    iam_client = boto3.client('iam')
    
    # Get the current date for ID generation
    current_date = datetime.now().strftime('%Y%m%d')

    # Get the AWS account ID
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]

    # Prepare a list to hold findings
    findings = []

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
                
                # Prepare the output data in an ordered dictionary
                output_data = OrderedDict({
                    'ID': finding_id,
                    'Service Name': rule['Title'],
                    'Status': status,
                    'AWS Account ID': account_id,
                    'Recommendation': recommendation[:]  # Use slicing to create a new list
                })
                
                findings.append(output_data)  # Collect findings
                print(f"Finding for user '{user_name}' added to findings list.")
            else:
                print(f"User '{user_name}' has MFA enabled.")

    # After auditing all users, write findings to a YAML file
    if findings:
        next_suffix = get_next_suffix(base_filename, output_dir)
        output_file_name = f"{base_filename}.{next_suffix}.yaml"
        output_file_path = os.path.join(output_dir, output_file_name)

        # Save all findings to the YAML file, preserving order
        with open(output_file_path, 'w') as output_file:
            yaml.dump(findings, output_file, Dumper=OrderedDumper, default_flow_style=False)

        print(f"Findings saved to '{output_file_path}'.")
    else:
        print("No findings to save.")

def main():
    policy_file = r'D:\best_practices\aws\comprehensive_best_practices\aws_certificate_manager\AWS_Certificate_Manager_(ACM)_architecture_best_practice_1.yaml'
    output_dir = r'D:\best_practices\aws\comprehensive_best_practices\aws_certificate_manager\output'  # Specify your output directory

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract the base filename (without extension)
    base_filename = os.path.splitext(os.path.basename(policy_file))[0]
    
    # Load the policy from the YAML file
    policies = load_policy(policy_file)
    
    audit_policy(policies, output_dir, base_filename)

if __name__ == "__main__":
    main()
