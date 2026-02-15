import requests
import time
import statistics
import concurrent.futures
import json

BASE_URL = "http://localhost:8000"

# Sample data for testing
SAMPLES = [
    {
        "Age": 25, "Gender": "Male", "Symptoms": "Fever", 
        "Blood_Pressure": 120, "Heart_Rate": 70, "Temperature": 37.0, 
        "O2_Saturation": 98, "Pain_Severity": 1, "Consciousness": "Alert", 
        "Pre_Existing_Conditions": "None"
    },
    {
        "Age": 75, "Gender": "Female", "Symptoms": "Chest Pain", 
        "Blood_Pressure": 190, "Heart_Rate": 110, "Temperature": 38.5, 
        "O2_Saturation": 88, "Pain_Severity": 9, "Consciousness": "Confused", 
        "Pre_Existing_Conditions": "Heart Disease"
    }
]

def test_endpoint(endpoint, payload, iterations=10):
    latencies = []
    url = f"{BASE_URL}/{endpoint}"
    
    print(f"Benchmarking /{endpoint} for {iterations} iterations...")
    for _ in range(iterations):
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            latencies.append(time.time() - start_time)
        except Exception as e:
            print(f"Error during iteration: {e}")
            
    if latencies:
        avg = statistics.mean(latencies) * 1000
        p95 = statistics.quantiles(latencies, n=20)[18] * 1000 # p95
        print(f"  Avg Latency: {avg:.2f}ms")
        print(f"  P95 Latency: {p95:.2f}ms")
        return latencies
    return []

def run_benchmarks():
    print("--- MedCognis Health Backend Performance Analysis ---")
    
    # Test /predict
    predict_latencies = test_endpoint("predict", SAMPLES[0], iterations=20)
    
    # Test /analyze-report
    report_payload = {
        "name": "Jane Smith",
        "age": 45,
        "gender": "Female",
        "report": "Patient presents with persistent cough and shortness of breath for 3 days. Elevated temperature noted (38.2C). Heart rate is around 95 bpm."
    }
    report_latencies = test_endpoint("analyze-report", report_payload, iterations=10)
    
    # Stress Test (Concurrent requests)
    print("\nRunning Stress Test (10 concurrent requests to /predict)...")
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(requests.post, f"{BASE_URL}/predict", json=SAMPLES[1]) for _ in range(10)]
        concurrent.futures.wait(futures)
    total_time = time.time() - start_time
    print(f"Total time for 10 concurrent requests: {total_time:.2f}s (Throughput: {10/total_time:.2f} req/s)")

if __name__ == "__main__":
    try:
        run_benchmarks()
    except Exception as e:
        print(f"Benchmarking failed: {e}")
