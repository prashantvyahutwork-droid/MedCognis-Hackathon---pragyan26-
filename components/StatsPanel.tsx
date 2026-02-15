"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from "recharts";

const data = [
    { name: 'Emerg.', value: 40, color: '#e11d48' }, // Critical
    { name: 'Neuro', value: 25, color: '#f59e0b' }, // Warning
    { name: 'Cardio', value: 20, color: '#10b981' }, // Success
    { name: 'Ortho', value: 15, color: '#2563eb' }, // Brand
];

const waitTimes = [
    { name: 'ER', time: 12 },
    { name: 'Neuro', time: 45 },
    { name: 'Cardio', time: 30 },
    { name: 'Gen', time: 90 },
];

export default function StatsPanel() {
    return (
        <div className="grid grid-cols-1 gap-4">
            <div className="glass-panel p-4">
                <h3 className="text-sm font-semibold mb-4 text-slate-400 uppercase tracking-wider">Dept Load</h3>
                <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={50}
                                outerRadius={70}
                                paddingAngle={5}
                                dataKey="value"
                                stroke="none"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                                itemStyle={{ color: '#f1f5f9' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div className="flex justify-center gap-4 mt-2">
                    {data.map((entry) => (
                        <div key={entry.name} className="flex items-center gap-1 text-xs">
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></span>
                            <span className="opacity-70">{entry.name}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="glass-panel p-4">
                <h3 className="text-sm font-semibold mb-4 text-slate-400 uppercase tracking-wider">Wait Times (mins)</h3>
                <div className="h-40 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={waitTimes}>
                            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                            <YAxis hide />
                            <Tooltip
                                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                                itemStyle={{ color: '#f1f5f9' }}
                            />
                            <Bar dataKey="time" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={20} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
