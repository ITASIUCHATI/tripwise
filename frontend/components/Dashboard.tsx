'use client';

import {
    useEffect,
    useState,
} from 'react';

import {
    Bar,
    BarChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';

import { api } from '../lib/api';

type DashboardStats = {
    total: number;
    averageBudget: number;
};

export default function Dashboard() {
    const [data, setData] =
        useState<DashboardStats | null>(null);

    const [error, setError] = useState('');

    useEffect(() => {
        api('/trips/stats')
            .then(setData)
            .catch(() =>
                setError(
                    'Unable to load dashboard data.',
                ),
            );
    }, []);

    const chartData = [
        {
            name: 'Trips',
            value: data?.total || 0,
        },
        {
            name: 'Avg Budget',
            value: data?.averageBudget || 0,
        },
    ];

    return (
        <main className="page">
            <div className="section-head">
                <p className="eyebrow">
                    OVERVIEW
                </p>

                <h1>Travel dashboard</h1>

                <p>
                    Track your saved trips and
                    average travel budget.
                </p>
            </div>

            {error && (
                <div className="card error">
                    {error}
                </div>
            )}

            <div className="stats">
                <div className="card">
                    <span>Saved trips</span>

                    <strong>
                        {data?.total || 0}
                    </strong>
                </div>

                <div className="card">
                    <span>Average budget</span>

                    <strong>
                        ₹
                        {Math.round(
                            data?.averageBudget || 0,
                        ).toLocaleString('en-IN')}
                    </strong>
                </div>
            </div>

            <div className="card chart">
                <ResponsiveContainer
                    width="100%"
                    height={260}
                >
                    <BarChart
                        data={chartData}
                    >
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </main>
    );
}