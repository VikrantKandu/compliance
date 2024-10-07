import yaml
import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize your LLM (OpenAI in this case)
try:
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)
    logger.info("LLM successfully initialized.")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    exit(1)

def generate_comprehensive_practice(service_name: str, practice: dict) -> dict:
    """Generates a comprehensive best practice including checks for the given recommendation."""
    
    prompt_template = PromptTemplate(
        input_variables=["service_name", "title", "description", "severity"],
        template="""\
            Create a security and compliance check for the following AWS service best practice:
            Please ensure that the output does not include any code formatting, special characters, or backticks.
            The output should be strictly in plain text and formatted as YAML.

            The security check should include:
            rule:
            - ID: A unique identifier for the best practice.
            - Title: A concise title for the check.
            - Profile Applicability: The levels or categories that the check applies to (e.g., Level 1, Level 2).
            - Description: A detailed explanation of the check, including its importance.
            - Rationale: Why this check is recommended, including potential risks if not followed.
            - Audit: Programmatically generate specific steps to verify compliance with this check, based on the best practice.
            - Default Value: The default state of the service regarding the best practice.
            - Remediation: Actions to take if the check is not compliant.

            Please format the output as a YAML structure without any additional formatting or code blocks.
        """
    )

    title = practice.get('best_practice', 'N/A')
    description = practice.get('description', 'N/A')
    severity = practice.get('severity', 'N/A')

    prompt = prompt_template.format(service_name=service_name, title=title, description=description, severity=severity)
    
    try:
        messages = [{"role": "user", "content": prompt}]
        response = llm.invoke(messages)
        
        if response and hasattr(response, 'content'):
            content = response.content
            if content:
                # Sanitize output
                content = content.replace("`", "")  # Remove backticks
                logger.debug(f"Raw model output: {content}")  # Debug line
                return yaml.safe_load(content.strip())
            else:
                logger.warning("Received an unexpected empty response.")
                return {}
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error for service {service_name}: {e}")
        logger.error(f"Content that caused the error: {content}")
    except Exception as e:
        logger.error(f"Error while generating comprehensive practice for {service_name}: {e}")
    return {}

def load_best_practices_from_file(filepath: str) -> (list, list):
    """Loads architecture and security best practices from a single YAML file."""
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
            logger.debug(f"Loaded data: {data}")
            return (
                data.get('architecture_best_practices', []),
                data.get('security_best_practices', [])
            )
    except Exception as e:
        logger.error(f"Error loading file {filepath}: {e}")
        return [], []

def save_comprehensive_practices(service_name: str, practices: list, output_directory: str, practice_type: str):
    """Saves each comprehensive best practice to individual YAML files in sequential format."""
    try:
        for index, practice in enumerate(practices):
            yaml_filename = os.path.join(output_directory, f'{service_name.replace(" ", "_")}_{practice_type}_best_practice_{index + 1}.yaml')

            # Ensure practice is wrapped in a list for sequential format
            practices_list = [practice]

            # Save the structured YAML format
            save_to_yaml(practices_list, yaml_filename)
            logger.info(f"Comprehensive {practice_type} best practice saved to {yaml_filename}")
    except Exception as e:
        logger.error(f"Error saving comprehensive best practices for {service_name}: {e}")

def save_to_yaml(data: any, filepath: str):
    """Saves data to a YAML file."""
    try:
        with open(filepath, 'w') as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)
    except Exception as e:
        logger.error(f"Error saving to file {filepath}: {e}")

def main():
    # Manually define one service
    service_name = "AWS X-Ray"

    # Define the directory where best practice files are stored
    input_directory = os.getenv('INPUT_DIRECTORY', r'D:\best_practices\aws\policy\AWS_X-Ray_best_practices.yaml')
    
    # Load best practices from the file
    architecture_practices, security_practices = load_best_practices_from_file(input_directory)

    output_directory = os.getenv('OUTPUT_DIRECTORY', r'D:\best_practices\aws\comprehensive_best_practices\aws_x_ray')
    os.makedirs(output_directory, exist_ok=True)

    # Generate comprehensive practices for architecture practices
    comprehensive_architecture_practices = []
    for practice in architecture_practices:
        comprehensive_practice = generate_comprehensive_practice(service_name, practice)
        logger.debug(f"Comprehensive architecture practice generated: {comprehensive_practice}")
        if comprehensive_practice:
            comprehensive_architecture_practices.append(comprehensive_practice)

    if comprehensive_architecture_practices:
        save_comprehensive_practices(service_name, comprehensive_architecture_practices, output_directory, "architecture")

    # Generate comprehensive practices for security practices
    comprehensive_security_practices = []
    for practice in security_practices:
        comprehensive_practice = generate_comprehensive_practice(service_name, practice)
        logger.debug(f"Comprehensive security practice generated: {comprehensive_practice}")
        if comprehensive_practice:
            comprehensive_security_practices.append(comprehensive_practice)

    if comprehensive_security_practices:
        save_comprehensive_practices(service_name, comprehensive_security_practices, output_directory, "security")

if __name__ == "__main__":
    main()
