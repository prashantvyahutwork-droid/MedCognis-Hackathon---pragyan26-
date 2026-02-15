"use client";

import { motion } from "framer-motion";
import { Activity, AlertTriangle, CheckCircle, Clock, FileText, Heart, Thermometer } from "lucide-react";
import * as Dialog from "@radix-ui/react-dialog";
import { Patient, RiskLevel } from "@/types";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface PatientCardProps {
    patient: Patient;
    index: number;
}

const riskColors: Record<RiskLevel, string> = {
    Low: "border-medical-success/50 bg-medical-success/10 text-emerald-200",
    Medium: "border-medical-warning/50 bg-medical-warning/10 text-amber-200",
    High: "border-medical-critical/50 bg-medical-critical/10 text-rose-200",
};

const badgeColors: Record<RiskLevel, string> = {
    Low: "bg-medical-success text-white",
    Medium: "bg-medical-warning text-black",
    High: "bg-medical-critical text-white animate-pulse",
};

export default function PatientCard({ patient, index }: PatientCardProps) {
    const [open, setOpen] = useState(false);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.4 }}
            className={cn(
                "glass-panel p-4 relative overflow-hidden transition-all hover:scale-[1.02] hover:shadow-lg cursor-pointer group",
                riskColors[patient.riskLevel]
            )}
            onClick={() => setOpen(true)}
        >
            <div className="flex justify-between items-start mb-3">
                <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        {patient.name}
                        <span className="text-xs font-normal opacity-70">({patient.gender}, {patient.age})</span>
                    </h3>
                    <p className="text-sm opacity-80 mt-1 flex items-center gap-1">
                        <Clock size={14} /> Admitted: {new Date(patient.admittedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                </div>
                <span className={cn("px-2 py-1 rounded-full text-xs font-bold uppercase tracking-wider", badgeColors[patient.riskLevel])}>
                    {patient.riskLevel}
                </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm mb-4">
                <div className="flex items-center gap-2 opacity-90">
                    <Heart size={16} className="text-rose-400" /> HR: {patient.vitals.heartRate}
                </div>
                <div className="flex items-center gap-2 opacity-90">
                    <Thermometer size={16} className="text-amber-400" /> {patient.vitals.temperature}°C
                </div>
            </div>

            <div className="mb-4">
                <p className="text-xs uppercase tracking-widest opacity-50 mb-1">Chief Complaint</p>
                <div className="flex flex-wrap gap-1">
                    {patient.symptoms.map(s => (
                        <span key={s} className="px-2 py-0.5 bg-white/10 rounded text-xs">{s}</span>
                    ))}
                </div>
            </div>

            <div className="flex justify-between items-center mt-2 border-t border-white/10 pt-3">
                <span className="text-xs font-mono opacity-60">ID: {patient.id}</span>
                <button className="text-xs flex items-center gap-1 hover:text-white transition-colors">
                    <FileText size={14} /> Explain AI Logic
                </button>
            </div>

            {/* Radix UI Dialog for AI Explanation */}
            <Dialog.Root open={open} onOpenChange={setOpen}>
                <Dialog.Portal>
                    <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 transition-opacity" />
                    <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-[#0f172a] border border-white/10 p-6 rounded-2xl shadow-2xl z-50 focus:outline-none">
                        <Dialog.Title className="text-xl font-bold mb-2 flex items-center gap-2">
                            <Activity className="text-medical-brand" /> AI Triage Analysis
                        </Dialog.Title>
                        <Dialog.Description className="text-slate-400 mb-4 text-sm">
                            Detailed breakdown of risk assessment for {patient.name}.
                        </Dialog.Description>

                        <div className="space-y-4">
                            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-sm opacity-70">Risk Score</span>
                                    <span className={cn("text-xl font-bold", patient.riskScore > 70 ? "text-medical-critical" : "text-medical-success")}>
                                        {patient.riskScore}/100
                                    </span>
                                </div>
                                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div
                                        className={cn("h-full transition-all duration-1000", badgeColors[patient.riskLevel])}
                                        style={{ width: `${patient.riskScore}%` }}
                                    />
                                </div>
                            </div>

                            <div>
                                <h4 className="text-sm font-semibold mb-2 opacity-80">AI Reasoning:</h4>
                                <ul className="space-y-2">
                                    {patient.justification.map((reason, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                                            <CheckCircle size={16} className="text-medical-brand mt-0.5 shrink-0" />
                                            {reason}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        <div className="mt-6 flex justify-end">
                            <Dialog.Close asChild>
                                <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">
                                    Close Analysis
                                </button>
                            </Dialog.Close>
                        </div>
                    </Dialog.Content>
                </Dialog.Portal>
            </Dialog.Root>
        </motion.div>
    );
}
