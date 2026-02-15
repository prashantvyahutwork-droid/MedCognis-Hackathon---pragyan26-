import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_predict():
    print("Testing /predict endpoint...")
    data = {
        "Age": 45,
        "Gender": "Male",
        "Symptoms": "Chest Pain",
        "Blood_Pressure": 150,
        "Heart_Rate": 110,
        "Temperature": 37.5,
        "O2_Saturation": 92,
        "Pain_Severity": 8,
        "Consciousness": "Alert",
        "Pre_Existing_Conditions": "Hypertension"
    }
    try:
        response = requests.post(f"{BASE_URL}/predict", json=data)
        if response.status_code == 200:
            print("✅ Predict Success:", response.json()["risk_level"])
        else:
            print("❌ Predict Failed:", response.status_code, response.text)
    except Exception as e:
        print("❌ Predict Error:", e)

def test_train():
    print("\nTesting /train endpoint...")
    # Use existing data file for test if available, or create a small dummy one
    dummy_csv = "data/dummy_test.csv"
    os.makedirs("data", exist_ok=True)
    with open(dummy_csv, "w") as f:
        f.write("Age,Gender,Symptoms,Blood_Pressure,Heart_Rate,Temperature,O2_Saturation,Pain_Severity,Consciousness,Pre_Existing_Conditions,Risk_Level\n")
        f.write("30,Male,Fever,120,80,37.0,98,2,Alert,None,Low\n")
        f.write("60,Female,Chest Pain,160,110,38.5,92,9,Confused,Diabetes,High\n")
    
    try:
        with open(dummy_csv, "rb") as f:
            files = {"file": ("dummy_test.csv", f, "text/csv")}
            response = requests.post(f"{BASE_URL}/train", files=files)
            if response.status_code == 200:
                print("✅ Train Success:", response.json()["status"])
            else:
                print("❌ Train Failed:", response.status_code, response.text)
    except Exception as e:
        print("❌ Train Error:", e)

if __name__ == "__main__":
    test_predict()
    test_train()
