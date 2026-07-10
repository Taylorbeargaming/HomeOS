"use client";

import { useEffect, useState } from "react";
import { getHealth } from "../lib/api";

export default function BackendStatus() {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    getHealth()
      .then((data) => setStatus(`🟢 ${data.status}`))
      .catch(() => setStatus("🔴 Offline"));
  }, []);

  return <p>Backend Status: {status}</p>;
}