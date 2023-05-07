import json, os, random

def main(phoneNumber: str, message) -> str:
    challenge = random.randint(1000, 10000)
    payload = {
        "body": f"Your verification code is {challenge}",
        "to": phoneNumber,
        "from": os.environ["TwilioFromNumber"]
    }

    message.set(json.dumps(payload))
    
    return challenge
