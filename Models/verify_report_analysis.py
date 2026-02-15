import requests
import json

BASE_URL = "http://localhost:8000"

def test_analyze_report():
    print("Testing /analyze-report endpoint...")
    payload = {
        "name": "John Doe",
        "age": 55,
        "gender": "Male",
        "report": "Patient reports sharp chest pain and high fever for 3 days. Experiencing shortness of breath."
    }
    try:
        response = requests.post(f"{BASE_URL}/analyze-report", json=payload)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_save_diagnosis(analysis_data):
    if not analysis_data: return
    print("\nTesting /save-diagnosis endpoint...")
    payload = {
        "name": analysis_data["analysis"]["name"],
        "summary": analysis_data["analysis"]["summary"],
        "timestamp": "2026-02-15T00:45:00Z"
    }
    try:
        response = requests.post(f"{BASE_URL}/save-diagnosis", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analysis = test_analyze_report()
    test_save_diagnosis(analysis)
