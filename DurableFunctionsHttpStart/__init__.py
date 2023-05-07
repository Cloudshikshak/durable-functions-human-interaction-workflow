import logging, phonenumbers
import azure.functions as func
import azure.durable_functions as df

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    if not req.get_body():
        return func.HttpResponse("Missing message body.", status_code=400)
    
    input = req.get_json()

    # Check if phone number present in input
    if 'phone_number' not in input:
        return func.HttpResponse("Missing phone_number in message body.", status_code=400)

    # Check if the phone number is valid
    phone_number = phonenumbers.parse(input['phone_number'], None)
    if not phonenumbers.is_valid_number(phone_number):
        return func.HttpResponse("Invalid phone number.", status_code=400)

    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(req.route_params["functionName"], None, input)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)