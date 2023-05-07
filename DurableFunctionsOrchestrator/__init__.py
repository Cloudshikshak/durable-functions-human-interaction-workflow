import logging
from datetime import timedelta

import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    # Get input passed to starter function
    input = context.get_input()

    # Send text message to the given number
    challenge_code = yield context.call_activity("SendChallenge", input['phone_number'])

    # Start timer
    # Stop Durable function after 10 minutes
    expiry_time = context.current_utc_datetime + timedelta(minutes=10)

    status = "Code challenge sent to user. Waiting for response..."
    context.set_custom_status(status)

    # Wait for either the timer or response from user
    timeout_task = context.create_timer(expiry_time)
    challenge_response_task = context.wait_for_external_event("ChallengeResponseEvent")

    result_task = yield context.task_any([challenge_response_task, timeout_task])

    if result_task == challenge_response_task:
        # We got back a response! Compare it to the challenge code
        if (str(challenge_response_task.result) == str(challenge_code)):
            status = "Challenge code valid. Phone number verified."
            verified = True
        else:
            status = "Challenge response failed. Phone number NOT verified."
            verified = False
    else:
        # Timer expired
        status = "Timeout. No response from user. Phone number NOT verified."
        verified = False

    context.set_custom_status(status)

    # close timer
    if not timeout_task.is_completed:
        # All pending timers must be complete or canceled before the function exits.
        timeout_task.cancel()

    return verified

main = df.Orchestrator.create(orchestrator_function)