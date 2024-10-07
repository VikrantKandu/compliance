# # # //  for every services we need to find and security policies based on 
# # # // best security and architectural pratices list - make sure cover all

import yaml
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import openai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OpenAI API key not found in environment variables.")
    exit(1)
else:
    openai.api_key = api_key
    logger.info("OpenAI API key successfully loaded.")

# Initialize your LLM (OpenAI in this case)
try:
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.4)
    logger.info("LLM successfully initialized.")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    exit(1)

def get_best_practices(service_name):
    prompt_template = PromptTemplate(
        input_variables=["service_name"],
        template="""\
        Please create a comprehensive list of architecture and security best practices for {service_name}, including a description and a severity level for each practice. The severity levels should indicate the potential impact if the best practice is not followed, categorized as Critical, High, Medium, or Low. Organize into sections for architecture best practices and security best practices.

        Substitute {service_name} with the specific AWS service for which you want to generate.
        Understand the Severity Levels:

        Critical: Non-compliance could lead to system failure, data loss, or significant security breaches.
        High: Non-compliance could cause major issues, including performance degradation or security vulnerabilities.
        Medium: Non-compliance could result in noticeable issues, such as reduced efficiency or minor security risks.
        Low: Non-compliance might result in minor issues with limited impact.

        **Important: Do not use asterisks or bullet points. Only use plain text formatting.**

        Format the response as follows in plain text format:

        architecture_best_practices:
          - best_practice: Title of the architecture best practice.
            description: A brief explanation of what the architecture best practice entails.
            severity: The assigned severity level (Critical, High, Medium, or Low).

        security_best_practices:
          - best_practice: Title of the security best practice.
            description: A brief explanation of what the security best practice entails.
            severity: The assigned severity level (Critical, High, Medium, or Low).
        """
    )
    prompt = prompt_template.format(service_name=service_name)

    # Log the generated prompt for debugging purposes
    logger.info(f"Generated prompt for {service_name}:\n{prompt}\n")

    # Invoke the LLM and handle potential errors
    try:
        response = llm.invoke(prompt)  # Use the correct method to invoke the LLM
        # Extract the content from the AIMessage object
        if hasattr(response, 'content'):
            return response.content
        else:
            logger.warning(f"No valid content received for {service_name}.")
            return "No best practices found."
    except Exception as e:
        logger.error(f"Error while getting best practices for {service_name}: {e}")
        return "An error occurred while retrieving best practices."

def load_services_from_yaml(filepath):
    try:
        with open(filepath, 'r') as file:
            logger.info(f"Loading services from YAML file: {filepath}")
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"YAML file not found: {filepath}")
        exit(1)
    except Exception as e:
        logger.error(f"Error loading YAML file: {e}")
        exit(1)

def save_to_yaml(data, filepath):
    # Ensure the directory for the file exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
            logger.info(f"Saved best practices to {filepath}")
    except Exception as e:
        logger.error(f"Error saving to YAML file: {e}")

def main():
    # Specify the path to your input YAML file
    input_yaml_path = r'D:\best_practices\aws\aws_services.yaml'  # Use raw string for Windows paths
    services_info = load_services_from_yaml(input_yaml_path)

    # Define the output directory for storing best practices files
    output_directory = r'D:\best_practices\AWS\policy'  # Change this path as needed

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    for service in services_info:
        service_name = service.get('ServiceName')
        if not service_name:
            logger.warning("ServiceName missing in input YAML file. Skipping.")
            continue
        
        # Get best practices for the service using LangChain
        practices = get_best_practices(service_name)

        # Create a sanitized service name
        sanitized_service_name = service_name.replace(" ", "_")  # Replace spaces with underscores
        
        # Create a filename for each service's best practices
        yaml_filename = os.path.join(output_directory, f'{sanitized_service_name}_best_practices.yaml')

        # Save the practices to a YAML file in the specified output directory
        try:
            # Convert the best practices (which is text) to structured YAML format
            practices_dict = yaml.safe_load(practices)
            save_to_yaml(practices_dict, yaml_filename)
            logger.info(f"Best practices for {service_name} have been saved to {yaml_filename}")
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML from response for {service_name}: {e}")
            # Save the response as raw text for further analysis
            with open(yaml_filename, 'w') as file:
                file.write(practices)
                logger.warning(f"Saved raw response to {yaml_filename} due to YAML parsing error.")

if __name__ == "__main__":
    main()
