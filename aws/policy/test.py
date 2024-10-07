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
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.5)  # Use ChatOpenAI for chat model
    logger.info("LLM successfully initialized.")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    exit(1)

def generate_comprehensive_practice(service_name: str, practice: dict) -> str:
    """Generates a comprehensive best practice including checks for the given recommendation."""
    
    prompt_template = PromptTemplate(
        input_variables=["service_name", "title", "description", "severity"],
        template="""\
Create a security and compliance check for the following AWS service best practice:

Service: {service_name}
Title: {title}
Description: {description}

The security check should include:

- ID: A unique identifier for the best practice.
- Title: A concise title for the check.
- Profile Applicability: The levels or categories that the check applies to (e.g., Level 1, Level 2).
- Description: A detailed explanation of the check, including its importance.
- Rationale: Why this check is recommended, including potential risks if not followed.
- Audit: Steps to verify compliance with this check.
- Remediation: Actions to take if the check is not compliant.
- Default Value: The default state of the service regarding the best practice.

Format the output as a YAML structure:
"""
    )

    title = practice.get('best_practice', 'N/A')
    description = practice.get('description', 'N/A')
    severity = practice.get('severity', 'N/A')

    prompt = prompt_template.format(service_name=service_name, title=title, description=description, severity=severity)
    logger.debug(f"Generated prompt: {prompt}")  # Log the prompt for debugging

    try:
        # Use the invoke method for the chat model
        messages = [{"role": "user", "content": prompt}]
        response = llm.invoke(messages)  # Use invoke as recommended by LangChain
        
        # Access the content from the response
        if response:
            content = response.content  # Using `content` attribute for AIMessage object
            return content.strip() if content else "No content generated."
        else:
            logger.warning("Received an unexpected empty response.")
            return "No content generated."
    except Exception as e:
        logger.error(f"Error while generating comprehensive practice for {service_name}: {e}")
        return "Error generating content."

def load_best_practices_from_file(filepath: str) -> list:
    """Loads best practices from a single YAML file."""
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
            logger.debug(f"Loaded data: {data}")  # Debugging output
            return data.get('architecture_best_practices', []) + data.get('security_best_practices', [])
    except Exception as e:
        logger.error(f"Error loading file {filepath}: {e}")
        return []

def save_comprehensive_practices(service_name: str, practices: list, output_directory: str):
    """Saves each comprehensive best practice to individual YAML files."""
    try:
        for index, practice in enumerate(practices):
            yaml_filename = os.path.join(output_directory, f'{service_name.replace(" ", "_")}_best_practice_{index + 1}.yaml')

            # Convert the generated practice to structured YAML format and save
            try:
                practices_dict = yaml.safe_load(practice)
                save_to_yaml(practices_dict, yaml_filename)
                logger.info(f"Comprehensive best practice saved to {yaml_filename}")
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML for {service_name} best practice {index + 1}: {e}")
                # Save the raw response as text for further analysis
                with open(yaml_filename, 'w') as file:
                    file.write(practice)
                logger.warning(f"Saved raw response to {yaml_filename} due to YAML parsing error.")
    except Exception as e:
        logger.error(f"Error saving comprehensive best practices for {service_name}: {e}")

def save_to_yaml(data: any, filepath: str):
    """Saves data to a YAML file."""
    try:
        with open(filepath, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
    except Exception as e:
        logger.error(f"Error saving to file {filepath}: {e}")

def main():
    # Manually define one service
    service_name = "Access Analyzer"

    # Define the directory where best practice files are stored
    input_directory = os.getenv('INPUT_DIRECTORY', r'D:\best_practices\aws\policy\Access_Analyzer_best_practices.yaml')
    
    # Load best practices from the file
    all_best_practices = load_best_practices_from_file(input_directory)

    if not all_best_practices:
        logger.warning(f"No best practices found for service: {service_name}")
        return

    output_directory = os.getenv('OUTPUT_DIRECTORY', r'D:\best_practices\aws\comprehensive_best_practices')
    os.makedirs(output_directory, exist_ok=True)

    # Generate comprehensive practices for each practice in the service
    comprehensive_practices = []
    for practice in all_best_practices:
        comprehensive_practice = generate_comprehensive_practice(service_name, practice)
        logger.debug(f"Comprehensive practice generated: {comprehensive_practice}")  # Log each generated practice
        if comprehensive_practice:
            comprehensive_practices.append(comprehensive_practice)

    if comprehensive_practices:
        # Save each comprehensive practice as a YAML file
        save_comprehensive_practices(service_name, comprehensive_practices, output_directory)

if __name__ == "__main__":
    main()



# import yaml
# import os
# import logging
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate

# # Load environment variables from .env file
# load_dotenv()

# # Initialize logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initialize your LLM (OpenAI in this case)
# try:
#     llm = ChatOpenAI(model_name="gpt-4", temperature=0.5)  # Use ChatOpenAI for chat model
#     logger.info("LLM successfully initialized.")
# except Exception as e:
#     logger.error(f"Failed to initialize LLM: {e}")
#     exit(1)

# def generate_comprehensive_practice(service_name: str, practice: dict) -> str:
#     """Generates a comprehensive best practice including checks for the given recommendation."""
    
#     prompt_template = PromptTemplate(
#         input_variables=["service_name", "title", "description", "severity"],
#         template="""\
# Create a security and compliance check for the following AWS service best practice:

# Service: {service_name}
# Title: {title}
# Description: {description}

# The security check should include:

# - ID: A unique identifier for the best practice.
# - Title: A concise title for the check.
# - Profile Applicability: The levels or categories that the check applies to (e.g., Level 1, Level 2).
# - Description: A detailed explanation of the check, including its importance.
# - Rationale: Why this check is recommended, including potential risks if not followed.
# - Audit: Steps to verify compliance with this check.
# - Remediation: Actions to take if the check is not compliant.
# - Default Value: The default state of the service regarding the best practice.

# Format the output as a YAML structure:
# """
#     )

#     title = practice.get('best_practice', 'N/A')
#     description = practice.get('description', 'N/A')
#     severity = practice.get('severity', 'N/A')

#     prompt = prompt_template.format(service_name=service_name, title=title, description=description, severity=severity)
#     logger.debug(f"Generated prompt: {prompt}")  # Log the prompt for debugging

#     try:
#         # Use the invoke method for the chat model
#         messages = [{"role": "user", "content": prompt}]
#         response = llm.invoke(messages)  # Use invoke as recommended by LangChain
        
#         # Access the content from the response
#         if response:
#             content = response.content  # Using `content` attribute for AIMessage object
#             return content.strip() if content else "No content generated."
#         else:
#             logger.warning("Received an unexpected empty response.")
#             return "No content generated."
#     except Exception as e:
#         logger.error(f"Error while generating comprehensive practice for {service_name}: {e}")
#         return "Error generating content."

# def load_best_practices_from_file(filepath: str) -> list:
#     """Loads best practices from a single YAML file."""
#     try:
#         with open(filepath, 'r') as file:
#             data = yaml.safe_load(file)
#             logger.debug(f"Loaded data: {data}")  # Debugging output
#             return data.get('architecture_best_practices', []) + data.get('security_best_practices', [])
#     except Exception as e:
#         logger.error(f"Error loading file {filepath}: {e}")
#         return []

# def save_comprehensive_practices(service_name: str, practices: str, output_directory: str):
#     """Saves the comprehensive best practices to a YAML file."""
#     yaml_filename = os.path.join(output_directory, f'{service_name.replace(" ", "_")}_comprehensive_best_practices.yaml')
#     try:
#         # Convert the comprehensive practices text to structured YAML format
#         practices_dict = yaml.safe_load(practices)
#         save_to_yaml(practices_dict, yaml_filename)
#         logger.info(f"Comprehensive best practices for {service_name} have been saved to {yaml_filename}")
#     except yaml.YAMLError as e:
#         logger.error(f"Failed to parse YAML from response for {service_name}: {e}")
#         # Save the response as raw text for further analysis
#         with open(yaml_filename, 'w') as file:
#             file.write(practices)
#             logger.warning(f"Saved raw response to {yaml_filename} due to YAML parsing error.")

# def save_to_yaml(data: any, filepath: str):
#     """Saves data to a YAML file."""
#     try:
#         with open(filepath, 'w') as file:
#             yaml.dump(data, file, default_flow_style=False)
#     except Exception as e:
#         logger.error(f"Error saving to file {filepath}: {e}")

# def main():
#     # Manually define one service
#     service_name = "Access Analyzer"

#     # Define the directory where best practice files are stored
#     input_directory = os.getenv('INPUT_DIRECTORY', r'D:\best_practices\aws\policy\Access_Analyzer_best_practices.yaml')
    
#     # Load best practices from the file
#     all_best_practices = load_best_practices_from_file(input_directory)

#     if not all_best_practices:
#         logger.warning(f"No best practices found for service: {service_name}")
#         return

#     output_directory = os.getenv('OUTPUT_DIRECTORY', r'D:\best_practices\aws\comprehensive_best_practices')
#     os.makedirs(output_directory, exist_ok=True)

#     # Generate comprehensive practices for each practice in the service
#     comprehensive_practices = []
#     for practice in all_best_practices:
#         comprehensive_practice = generate_comprehensive_practice(service_name, practice)
#         logger.debug(f"Comprehensive practice generated: {comprehensive_practice}")  # Log each generated practice
#         if comprehensive_practice:
#             comprehensive_practices.append(comprehensive_practice)

#     if comprehensive_practices:
#         # Extract content from each comprehensive practice
#         all_comprehensive_practices_yaml = "\n".join([cp for cp in comprehensive_practices if isinstance(cp, str)])
#         save_comprehensive_practices(service_name, all_comprehensive_practices_yaml, output_directory)

# if __name__ == "__main__":
#     main()
