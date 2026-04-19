import requests

try:
    response = requests.post(
        "https://ai-powered-customer-support-chatbot-mjof.onrender.com/api/chat/stream",
        headers={"X-User-Id": "guest-test", "Content-Type": "application/json"},
        json={"message": "What is the status of order ORD-5002?"},
        stream=True
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
            
except Exception as e:
    print(f"Error: {e}")
