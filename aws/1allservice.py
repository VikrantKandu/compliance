import boto3
import yaml
import os

def list_aws_services():
    # Create a session using default credentials
    session = boto3.Session()
    client = session.client('service-quotas')

    service_list = []
    next_token = None

    while True:
        # Retrieve the list of services
        if next_token:
            response = client.list_services(NextToken=next_token)
        else:
            response = client.list_services()

        # Extract service names
        services = response.get('Services', [])
        service_list.extend([
            {"ServiceCode": service['ServiceCode'], "ServiceName": service['ServiceName']}
            for service in services
        ])

        # Check for pagination
        next_token = response.get('NextToken')
        if not next_token:
            break

    return service_list

def save_to_yaml(data, filename):
    with open(filename, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def main():
    services = list_aws_services()
    
    # Get the current directory and define the YAML filename
    current_directory = os.path.dirname(os.path.abspath(__file__))
    yaml_filename = os.path.join(current_directory, 'aws_services.yaml')

    save_to_yaml(services, yaml_filename)
    print(f"AWS services have been saved to {yaml_filename}")

if __name__ == "__main__":
    main()
