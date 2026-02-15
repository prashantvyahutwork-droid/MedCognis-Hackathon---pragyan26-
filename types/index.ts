export type RiskLevel = "Low" | "Medium" | "High";

export interface Patient {
    id: string;
    name: string;
    age: number;
    gender: "Male" | "Female" | "Other";
    symptoms: string[];
    vitals: {
        heartRate: number;
        bloodPressure: string;
        spo2: number;
        temperature: number;
    };
    history: string[];
    riskScore: number;
    riskLevel: RiskLevel;
    department: string;
    admittedAt: string;
    justification: string[];
    predicted_disease?: string;
    recommended_specialist?: string;
    curing_process?: string[];
}
