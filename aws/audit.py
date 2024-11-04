# import boto3
# import yaml
# import os
# from datetime import datetime

# # Load the policy from the YAML file
# def load_policy(file_path):
#     with open(file_path, 'r') as file:
#         return yaml.safe_load(file)

# # Function to get the next available file suffix
# def get_next_suffix(base_filename, output_dir):
#     # Get the list of files in the output directory that match the base filename pattern
#     existing_files = [f for f in os.listdir(output_dir) if f.startswith(base_filename) and f.endswith('.yaml')]
    
#     # Extract existing suffix numbers
#     suffixes = []
#     for filename in existing_files:
#         # Extract the number from the filename (e.g., from "filename.1.yaml" get "1")
#         parts = filename.split('.')
#         if len(parts) > 1 and parts[1].isdigit():
#             suffixes.append(int(parts[1]))
    
#     # Return the next suffix (1 greater than the max existing suffix)
#     return max(suffixes, default=0) + 1

# # Audit MFA status for IAM users according to the policy
# def audit_policy(policies, output_dir, base_filename):
#     iam_client = boto3.client('iam')
    
#     # Get the current date for ID generation
#     current_date = datetime.now().strftime('%Y%m%d')

#     # Get the AWS account ID
#     sts_client = boto3.client('sts')
#     account_id = sts_client.get_caller_identity()["Account"]
    
#     # Define the AWS Account Name (you may want to change this if necessary)
#     # account_name = "My AWS Account"  # Replace with the actual account name or retrieve dynamically if needed

#     # Iterate over each rule in the policy
#     for policy in policies:
#         rule = policy.get('rule', {})
       
#         # Check that the policy ID and title are correct
#         print(f"Auditing policy: {rule['ID']} - {rule['Title']}")
        
#         # Perform the actual audit using the AWS CLI commands outlined in the policy
#         users = iam_client.list_users()
        
#         for user in users['Users']:
#             user_name = user['UserName']
#             mfa_devices = iam_client.list_mfa_devices(UserName=user_name)
#             recommendation = rule.get('Remediation')
#             # Check if MFA is enabled
#             if not mfa_devices['MFADevices']:
#                 # Create the ID in the specified format
#                 finding_id = f"{account_id}_{current_date}_{rule['ID']}"
#                 if not mfa_devices['MFADevices']:
#                    status = 'DISABLED'  # Status when MFA is not enabled
#                 else:
#                    status = 'ENABLED'  # Status when MFA is enabled
#                 # Prepare the output data
#                 output_data = {
#                     # 'AWS Account Name': account_name,  # Now using AWS Account Name
#                     'ID': finding_id,
#                     'Service Name': rule['Title'],
#                     'Status': status,
#                     'Recommendation': recommendation
#                 }
                
#                 # Get the next available suffix
#                 next_suffix = get_next_suffix(base_filename, output_dir)
                
#                 # Generate the output file name with the incremented suffix
#                 output_file_name = f"{base_filename}.{next_suffix}.yaml"
#                 output_file_path = os.path.join(output_dir, output_file_name)
                
#                 # Save findings to the YAML file
#                 with open(output_file_path, 'w') as output_file:
#                     yaml.dump(output_data, output_file)
                
#                 print(f"Finding for user '{user_name}' saved to '{output_file_path}'.")
#             else:
#                 print(f"User '{user_name}' has MFA enabled.")

# def main():
#     policy_file = r'D:\best_practices\aws\comprehensive_best_practices\aws_account_management\AWS_Account_Management_best_practice_1.yaml'
#     output_dir = r'D:\best_practices\aws\comprehensive_best_practices\aws_account_management\output'  # Specify your output directory

#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)

#     # Extract the base filename (without extension)
#     base_filename = os.path.splitext(os.path.basename(policy_file))[0]
    
#     # Load the policy from the YAML file
#     policies = load_policy(policy_file)
    
#     audit_policy(policies, output_dir, base_filename)

# if __name__ == "__main__":
#     main()




# import boto3
# import yaml
# import os
# from datetime import datetime

# # Load the policy from the YAML file
# def load_policy(file_path):
#     with open(file_path, 'r') as file:
#         return yaml.safe_load(file)

# # Function to get the next available file suffix
# def get_next_suffix(base_filename, output_dir):
#     existing_files = [f for f in os.listdir(output_dir) if f.startswith(base_filename) and f.endswith('.yaml')]
#     suffixes = [int(filename.split('.')[1]) for filename in existing_files if filename.split('.')[1].isdigit()]
#     return max(suffixes, default=0) + 1

# # Audit MFA status for IAM users according to the policy
# def audit_policy(policies, output_dir, base_filename):
#     iam_client = boto3.client('iam')
#     sts_client = boto3.client('sts')
    
#     current_date = datetime.now().strftime('%Y%m%d')
#     account_id = sts_client.get_caller_identity()["Account"]
    
#     for policy in policies:
#         rule = policy.get('rule', {})
#         rule_id = rule.get('ID')
#         rule_title = rule.get('Title')
        
#         if not rule_id or not rule_title:
#             print(f"Skipping invalid policy format: {policy}")
#             continue
        
#         print(f"Auditing policy: {rule_id} - {rule_title}")
        
#         users = iam_client.list_users()
        
#         for user in users['Users']:
#             user_name = user['UserName']
#             mfa_devices = iam_client.list_mfa_devices(UserName=user_name)
#             recommendation = rule.get('Remediation')
            
#             if not mfa_devices['MFADevices']:  # Only create finding if MFA is disabled
#                 finding_id = f"{account_id}_{current_date}_{rule_id}_{user_name}"
#                 output_data = {
#                     'ID': finding_id,
#                     'Service Name': rule_title,
#                     'Recommendation': recommendation
#                 }
                
#                 next_suffix = get_next_suffix(base_filename, output_dir)
#                 output_file_name = f"{base_filename}.{next_suffix}.yaml"
#                 output_file_path = os.path.join(output_dir, output_file_name)
                
#                 with open(output_file_path, 'w') as output_file:
#                     yaml.dump(output_data, output_file, default_flow_style=False)
                
#                 print(f"Finding for user '{user_name}' saved to '{output_file_path}'.")
#             else:
#                 print(f"User '{user_name}' has MFA enabled.")

# # Main function to process all YAML files in the folder
# def main():
#     input_dir = r'D:\best_practices\git_aws\compliance\aws\comprehensive_best_practices\amazon_appflow'  # Folder containing policy files
#     output_dir = r'D:\best_practices\git_aws\compliance\aws\audit_output\amazon_appflow'  # Specify the output directory

#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)

#     # Iterate through all YAML files in the input directory
#     for file_name in os.listdir(input_dir):
#         if file_name.endswith('.yaml'):
#             file_path = os.path.join(input_dir, file_name)
#             base_filename = os.path.splitext(file_name)[0]
            
#             print(f"\nProcessing policy file: {file_name}")
#             policies = load_policy(file_path)
            
#             if policies:  # Ensure policies are loaded successfully
#                 audit_policy(policies, output_dir, base_filename)
#             else:
#                 print(f"Warning: Policy file '{file_name}' is empty or malformed.")

# if __name__ == "__main__":
#     main()




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
    existing_files = [f for f in os.listdir(output_dir) if f.startswith(base_filename) and f.endswith('.yaml')]
    suffixes = [int(filename.split('.')[1]) for filename in existing_files if filename.split('.')[1].isdigit()]
    return max(suffixes, default=0) + 1

# Audit MFA status for IAM users according to the policy
def audit_policy(policies, output_dir, base_filename):
    iam_client = boto3.client('iam')
    sts_client = boto3.client('sts')
    
    current_date = datetime.now().strftime('%Y%m%d')
    account_id = sts_client.get_caller_identity()["Account"]
    
    for policy in policies:
        # Check if the policy is a dictionary and contains the key 'rule'
        if isinstance(policy, dict) and 'rule' in policy:
            rules = policy['rule']  # This should be a list of rules
            
            for rule in rules:
                if isinstance(rule, dict):
                    rule_id = rule.get('ID')
                    rule_title = rule.get('Title')
                    recommendation = rule.get('Remediation')

                    if not rule_id or not rule_title:
                        print(f"Skipping invalid policy format: {rule}")
                        continue
                    
                    print(f"Auditing policy: {rule_id} - {rule_title}")
                    
                    users = iam_client.list_users()
                    
                    for user in users['Users']:
                        user_name = user['UserName']
                        mfa_devices = iam_client.list_mfa_devices(UserName=user_name)
                        
                        if not mfa_devices['MFADevices']:  # Only create finding if MFA is disabled
                            finding_id = f"{account_id}_{current_date}_{rule_id}_{user_name}"
                            output_data = {
                                'ID': finding_id,
                                'Service Name': rule_title,
                                'Recommendation': recommendation
                            }
                            
                            next_suffix = get_next_suffix(base_filename, output_dir)
                            output_file_name = f"{base_filename}.{next_suffix}.yaml"
                            output_file_path = os.path.join(output_dir, output_file_name)
                            
                            with open(output_file_path, 'w') as output_file:
                                yaml.dump(output_data, output_file, default_flow_style=False)
                            
                            print(f"Finding for user '{user_name}' saved to '{output_file_path}'.")
                        else:
                            print(f"User '{user_name}' has MFA enabled.")
        else:
            print(f"Skipping invalid policy format: {policy}")

# Main function to process all YAML files in the folder
def main():
    input_dir = r'D:\best_practices\git_aws\compliance\aws\comprehensive_best_practices\amazon_athena'  # Folder containing policy files
    output_dir = r'D:\best_practices\git_aws\compliance\aws\audit_output\amazon_athena'  # Specify the output directory

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through all YAML files in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.yaml'):
            file_path = os.path.join(input_dir, file_name)
            base_filename = os.path.splitext(file_name)[0]
            
            print(f"\nProcessing policy file: {file_name}")
            policies = load_policy(file_path)
            
            if policies:  # Ensure policies are loaded successfully
                audit_policy(policies, output_dir, base_filename)
                print(f"Completed processing of {file_name}. Moving to the next file.\n")
            else:
                print(f"Warning: Policy file '{file_name}' is empty or malformed. Skipping to the next file.")

if __name__ == "__main__":
    main()
