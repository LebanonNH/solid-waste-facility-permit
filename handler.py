import re
import json
from landfillpermit.models import session, City
from landfillpermit.pdf import permit

def issue_permit(event, context):
    errors = []
    try:
        body = json.loads(event['body'])
    except:
        errors.append("Request JSON is malformed")
    print(body)
    first_name = body['first_name']
    surname = body['surname']
    email = body['email']
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    match = re.match(pattern, email)
    if not match:
        errors.append("Email address is malformed")
    city = body['city']
    query = session.query(City).filter(City.city_name == city).first()
    if not query:
        errors.append("Invalid City") 
    if errors:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'errors': errors
        }
    resp = permit(first_name, surname, email, city)
    return resp
       