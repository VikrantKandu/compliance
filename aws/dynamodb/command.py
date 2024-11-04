
import os
import boto3
import openai
import logging
from botocore.exceptions import BotoCoreError, ClientError
from time import sleep

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DynamoDB and OpenAI
dynamodb = boto3.resource('dynamodb')
table_name = 'AuditCheck'
table = dynamodb.Table(table_name)

# Load OpenAI API Key from environment variable
openai.api_key = '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'

# Function to call OpenAI API to generate command
def generate_command(best_practices, audit_steps):
    prompt = f"""
    Based on the following Best Practice and Audit steps, create a command to verify compliance:

    Best Practice: {best_practices}
    Audit Steps: {audit_steps}

    Command:
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate a concise command for compliance verification based on audit steps."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        command_text = response.choices[0].message['content'].strip()
        return command_text
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return "Command generation failed."

# Function to retrieve and update items with commands
def add_command_to_items():
    last_evaluated_key = None

    while True:
        scan_kwargs = {
            "FilterExpression": "attribute_exists(BestPractices) AND attribute_exists(Audit)"
        }
        
        if last_evaluated_key:
            scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

        try:
            response = table.scan(**scan_kwargs)
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error scanning table: {str(e)}")
            break
        
        items = response.get('Items', [])
        if not items:
            logger.info("No items found with 'BestPractices' and 'Audit' fields.")
            break

        for item in items:
            item_id = item.get('id')
            best_practices = item.get('BestPractices', {})
            audit_steps = item.get('Audit', [])

            # Generate command text
            command_text = generate_command(best_practices, audit_steps)
            command_text = command_text.strip("`,\"")  # Clean up command text
            # Attempt to update the item in DynamoDB
            try:
                table.update_item(
                    Key={'id': item_id},
                    UpdateExpression="SET #cmd = :command",
                    ExpressionAttributeNames={'#cmd': 'command'},
                    ExpressionAttributeValues={':command': command_text}
                )
                logger.info(f"Added command to item ID '{item_id}': {command_text}")
            except (BotoCoreError, ClientError) as e:
                logger.error(f"Failed to update item ID '{item_id}' with command: {str(e)}")
                sleep(1)  # Small delay before retrying to reduce load in case of issues

        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break

# Run the function to add commands
if __name__ == "__main__":
    add_command_to_items()
