import boto3
import yaml
import os

def list_enabled_services():
    # Create a session using default credentials
    session = boto3.Session()
    client = session.client('service-quotas')

    enabled_services = []
    next_token = None

    while True:
        # Retrieve the list of services
        if next_token:
            response = client.list_services(NextToken=next_token)
        else:
            response = client.list_services()

        for service in response.get('Services', []):
            service_code = service['ServiceCode']
            service_name = service['ServiceName']

            # Get service quotas to check if the service is enabled
            try:
                quotas = client.list_service_quotas(ServiceCode=service_code)
                if quotas['Quotas']:  # If there are quotas, the service is enabled
                    enabled_services.append({
                        "ServiceCode": service_code,
                        "ServiceName": service_name
                    })
            except Exception as e:
                print(f"Could not retrieve quotas for {service_name}: {e}")

        # Check for pagination
        next_token = response.get('NextToken')
        if not next_token:
            break

    return enabled_services

def save_to_yaml(data, filename):
    with open(filename, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def main():
    enabled_services = list_enabled_services()

    # Save results to YAML file in the same directory as the script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    yaml_filename = os.path.join(current_directory, 'enabled_aws_services.yaml')

    save_to_yaml(enabled_services, yaml_filename)
    print(f"Enabled AWS services have been saved to {yaml_filename}")

if __name__ == "__main__":
    main()
