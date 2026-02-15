"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MOCK_PATIENTS } from "@/lib/triage-engine";
import PatientCard from "./PatientCard";
import { Patient } from "@/types";
import { AlertOctagon, RefreshCw } from "lucide-react";

export default function TriageDashboard() {
    const [patients, setPatients] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<"All" | "High" | "Medium" | "Low">("All");

    useEffect(() => {
        // Simulate real-time data fetching
        setTimeout(() => {
            setPatients(MOCK_PATIENTS.sort((a, b) => b.riskScore - a.riskScore));
            setLoading(false);
        }, 1500);
    }, []);

    const filteredPatients = filter === "All"
        ? patients
        : patients.filter(p => p.riskLevel === filter);

    return (
        <div className="w-full">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <AlertOctagon className="text-medical-critical animate-pulse" />
                        Priority Queue
                    </h2>
                    <p className="text-sm opacity-60">Real-time AI prioritization based on clinical urgency.</p>
                </div>

                <div className="flex gap-2">
                    {(["All", "High", "Medium", "Low"] as const).map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${filter === f ? "bg-medical-brand text-white shadow-lg shadow-medical-brand/25" : "bg-white/5 hover:bg-white/10"
                                }`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="w-full h-64 flex flex-col items-center justify-center opacity-50">
                    <RefreshCw className="animate-spin mb-4 text-medical-brand" size={32} />
                    <p>Syncing with Clinical Engine...</p>
                </div>
            ) : (
                <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <AnimatePresence>
                        {filteredPatients.map((patient, index) => (
                            <PatientCard key={patient.id} patient={patient} index={index} />
                        ))}
                    </AnimatePresence>

                    {filteredPatients.length === 0 && (
                        <div className="col-span-full py-12 text-center opacity-40">
                            No patients found in this category.
                        </div>
                    )}
                </motion.div>
            )}
        </div>
    );
}
