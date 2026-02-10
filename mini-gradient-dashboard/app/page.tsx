"use client"
import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    tasks_completed: 0,
    consensus_history: [],
    reputation: {},
  });

  const fetchMetrics = async () => {
    try {
      const res = await fetch("http://localhost:8000/metrics");
      const data = await res.json();
      setMetrics((prev) => ({ ...prev, ...data }));
    } catch (err) {
      console.error("Failed to fetch metrics", err);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, []);

  const reputationData = Object.entries(metrics.reputation || {}).map(([peer, score]) => ({
    peer,
    score,
  }));

  return (
    <div className="min-h-screen bg-white p-8 grid gap-6">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-3xl font-bold"
      >
        Mini Gradient Dashboard
      </motion.h1>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="rounded-2xl shadow-md">
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-2">Tasks Completed</h2>
            <p className="text-4xl font-bold">{metrics.tasks_completed}</p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-md">
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-2">Last Consensus</h2>
            <p className="text-4xl font-bold">
              {metrics.consensus_history?.slice(-1)[0] ?? "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-2xl shadow-md">
        <CardContent className="p-6">
          <h2 className="text-xl font-semibold mb-4">Consensus History</h2>
          <div className="flex flex-wrap gap-2">
            {metrics.consensus_history?.map((digit, i) => (
              <Badge key={i} variant="outline" className="text-base px-3 py-1">
                {digit}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-2xl shadow-md">
        <CardContent className="p-6">
          <h2 className="text-xl font-semibold mb-4">Peer Reputation</h2>
          {reputationData.length === 0 ? (
            <p>No reputation data yet.</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={reputationData}>
                  <XAxis dataKey="peer" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="score" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
