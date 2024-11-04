import boto3
import logging
import subprocess
from botocore.exceptions import BotoCoreError, ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = 'AuditCheck'
table = dynamodb.Table(table_name)

# Function to execute command and capture output
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        logger.error(f"Command execution error: {str(e)}")
        return "Command execution failed."

# Function to retrieve items with command and process them
def process_commands():
    last_evaluated_key = None

    while True:
        # Scan for items with 'command' field
        scan_kwargs = {
            "FilterExpression": "attribute_exists(command)"
        }
        
        if last_evaluated_key:
            scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

        try:
            response = table.scan(**scan_kwargs)
        except (BotoCoreError, ClientError) as e:
            logger.error(f"DynamoDB scan error: {str(e)}")
            break
        
        items = response.get('Items', [])
        if not items:
            logger.info("No items found with 'command' field.")
            break

        for item in items:
            item_id = item.get('id')
            command_text = item.get('command', '')

            # Execute the command and capture the result
            result_text = execute_command(command_text)

            # Process the result as needed (this example simply logs it)
            processed_result = f"Processed output: {result_text}"  # Customize processing logic here
            logger.info(f"Processed result for item ID '{item_id}': {processed_result}")

            # Update DynamoDB with the processed result
            try:
                table.update_item(
                    Key={'id': item_id},
                    UpdateExpression="SET #res = :result",
                    ExpressionAttributeNames={'#res': 'result'},
                    ExpressionAttributeValues={':result': processed_result}
                )
                logger.info(f"Updated item ID '{item_id}' with processed result.")
            except (BotoCoreError, ClientError) as e:
                logger.error(f"Failed to update item ID '{item_id}' with processed result: {str(e)}")

        # Check for pagination
        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break

# Run the function to process commands
if __name__ == "__main__":
    process_commands()
