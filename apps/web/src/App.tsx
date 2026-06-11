import { getHealth, type HealthCheckResponse } from "api-client";
import { useEffect, useState } from "react";

type HealthState =
  | { status: "loading" }
  | { status: "ready"; data: HealthCheckResponse }
  | { status: "error"; message: string };

export default function App() {
  const [health, setHealth] = useState<HealthState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function loadHealth() {
      try {
        const response = await getHealth();

        if (!cancelled) {
          setHealth({ status: "ready", data: response.data });
        }
      } catch (error) {
        if (!cancelled) {
          setHealth({
            status: "error",
            message: error instanceof Error ? error.message : "Unknown error",
          });
        }
      }
    }

    loadHealth();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        fontFamily: "Inter, system-ui, sans-serif",
        color: "#111827",
        background: "#f8fafc",
      }}
    >
      <section>
        <h1>API Health</h1>
        <p>
          {health.status === "loading" && "Checking..."}
          {health.status === "ready" && health.data.status}
          {health.status === "error" && `Error: ${health.message}`}
        </p>
      </section>
    </main>
  );
}
