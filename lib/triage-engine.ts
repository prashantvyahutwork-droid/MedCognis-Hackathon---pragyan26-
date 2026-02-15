import { Patient, RiskLevel } from "@/types";

// Mock AI Logic to simulate triage analysis
export function assessRisk(
    symptoms: string[],
    vitals: Patient["vitals"],
    history: string[]
): {
    riskScore: number;
    riskLevel: RiskLevel;
    department: string;
    justification: string[];
    predicted_disease?: string;
    recommended_specialist?: string;
    curing_process?: string[];
} {
    let score = 0;
    const justification: string[] = [];

    // 1. Symptom Analysis
    const criticalSymptoms = ["Chest Pain", "Difficulty Breathing", "Severe Trauma", "Stroke Symptoms", "Unconscious"];
    const moderateSymptoms = ["High Fever", "Persistent Vomiting", "Abdominal Pain", "Dehydration"];

    symptoms.forEach((s) => {
        if (criticalSymptoms.includes(s)) {
            score += 40;
            justification.push(`Critical symptom detected: ${s}`);
        } else if (moderateSymptoms.includes(s)) {
            score += 20;
            justification.push(`Moderate symptom detected: ${s}`);
        } else {
            score += 5;
        }
    });

    // 2. Vitals Analysis
    if (vitals.heartRate > 120 || vitals.heartRate < 40) {
        score += 15;
        justification.push(`Abnormal Heart Rate: ${vitals.heartRate} bpm`);
    }
    if (vitals.spo2 < 90) {
        score += 20;
        justification.push(`Low SpO2: ${vitals.spo2}%`);
    }
    if (vitals.temperature > 39) {
        score += 10;
        justification.push(`High Fever: ${vitals.temperature}°C`);
    }

    // 3. History Analysis
    if (history.includes("Heart Disease") && symptoms.includes("Chest Pain")) {
        score += 30;
        justification.push("History of Heart Disease with Chest Pain increases risk significantly.");
    }

    // Determine Risk Level
    let riskLevel: RiskLevel = "Low";
    let department = "General Practice";

    if (score >= 70) {
        riskLevel = "High";
        department = "Emergency / Trauma";
    } else if (score >= 40) {
        riskLevel = "Medium";
        department = "Internal Medicine";
    }

    // Cap score at 100
    const finalScore = Math.min(score, 100);

    // Basic disease mapping for mock logic
    let predicted_disease = "General Condition";
    let recommended_specialist = "General Physician";
    let curing_process = ["Clinical observation", "Monitor vitals"];

    if (symptoms.includes("Chest Pain")) {
        predicted_disease = riskLevel === "High" ? "Acute Coronary Syndrome" : "Stable Angina";
        recommended_specialist = riskLevel === "High" ? "Senior Cardiologist" : "Cardiology Specialist";
        curing_process = ["Immediate ECG", "Troponin test", "Cardiology consult"];
    } else if (symptoms.includes("Fever")) {
        predicted_disease = riskLevel === "High" ? "Sepsis / Severe Infection" : "Viral Syndrome";
        recommended_specialist = riskLevel === "High" ? "Emergency Physician" : "Internal Medicine Specialist";
        curing_process = ["IV rehydration", "Blood cultures", "Antipyretics"];
    } else if (symptoms.includes("Shortness of Breath") || symptoms.includes("Difficulty Breathing")) {
        predicted_disease = "Respiratory Distress";
        recommended_specialist = "Pulmonology Chief";
        curing_process = ["Oxygen therapy", "Nebulization", "Chest X-ray"];
    }

    return {
        riskScore: finalScore,
        riskLevel,
        department,
        justification,
        predicted_disease,
        recommended_specialist,
        curing_process
    };
}

export const MOCK_PATIENTS: Patient[] = [
    {
        id: "P-1001",
        name: "John Doe",
        age: 45,
        gender: "Male",
        symptoms: ["Chest Pain", "Shortness of Breath"],
        vitals: { heartRate: 110, bloodPressure: "150/95", spo2: 92, temperature: 37.2 },
        history: ["Hypertension"],
        riskScore: 85,
        riskLevel: "High",
        department: "Emergency",
        admittedAt: "2026-02-15T00:00:00.000Z",
        justification: ["Critical symptom detected: Chest Pain", "Abnormal Heart Rate"],
        predicted_disease: "Acute Coronary Syndrome",
        recommended_specialist: "Senior Cardiologist",
        curing_process: ["Immediate 12-lead ECG", "Administer Aspirin", "Troponin Test"],
    },
    {
        id: "P-1002",
        name: "Jane Smith",
        age: 29,
        gender: "Female",
        symptoms: ["Severe Migraine", "Nausea"],
        vitals: { heartRate: 78, bloodPressure: "120/80", spo2: 98, temperature: 36.8 },
        history: [],
        riskScore: 30,
        riskLevel: "Low",
        department: "Neurology",
        admittedAt: "2026-02-15T00:00:00.000Z",
        justification: ["Moderate symptom detected: Severe Migraine"],
        predicted_disease: "Migraine with Aura",
        recommended_specialist: "Neurology Specialist",
        curing_process: ["Rest in dark room", "Hydration", "Oral Analgesics"],
    },
    {
        id: "P-1003",
        name: "Robert Brown",
        age: 62,
        gender: "Male",
        symptoms: ["Abdominal Pain", "Fever"],
        vitals: { heartRate: 95, bloodPressure: "135/85", spo2: 96, temperature: 39.2 },
        history: ["Diabetes"],
        riskScore: 55,
        riskLevel: "Medium",
        department: "Internal Medicine",
        admittedAt: "2026-02-15T00:00:00.000Z",
        justification: ["Moderate symptom detected: Abdominal Pain", "High Fever: 39.2°C"],
        predicted_disease: "Acute Gastroenteritis",
        recommended_specialist: "Gastroenterology Specialist",
        curing_process: ["Stool cultures", "IV Fluid rehydration", "Antispasmodics"],
    },
    {
        id: "P-1004",
        name: "Emily White",
        age: 8,
        gender: "Female",
        symptoms: ["Cough", "Sore Throat"],
        vitals: { heartRate: 90, bloodPressure: "100/60", spo2: 99, temperature: 37.5 },
        history: ["Asthma"],
        riskScore: 15,
        riskLevel: "Low",
        department: "Pediatrics",
        admittedAt: "2026-02-15T00:00:00.000Z",
        justification: ["Mild symptoms"],
        predicted_disease: "Viral Upper Respiratory Infection",
        recommended_specialist: "General Physician",
        curing_process: ["Steam inhalation", "Honey-based cough syrup", "Rest"],
    },
    {
        id: "P-1005",
        name: "Michael Green",
        age: 55,
        gender: "Male",
        symptoms: ["Sudden weakness in left arm", "Slurred speech"],
        vitals: { heartRate: 88, bloodPressure: "160/100", spo2: 95, temperature: 37.0 },
        history: ["Smoker"],
        riskScore: 92,
        riskLevel: "High",
        department: "Stroke Unit",
        admittedAt: "2026-02-15T00:00:00.000Z",
        justification: ["Critical symptom detected: Stroke Symptoms"],
        predicted_disease: "Acute Ischemic Stroke",
        recommended_specialist: "Stroke Neurology Chief",
        curing_process: ["Immediate CT Head", "NIH Stroke Scale assessment", "Assess for tPA eligibility"],
    }
];
