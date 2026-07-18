import {
  getHealth,
  type HealthCheckResponse,
  ResolutionMode,
  schemaFields,
} from "api-client";
import { useEffect, useState } from "react";

type HealthState =
  | { status: "loading" }
  | { status: "ready"; data: HealthCheckResponse }
  | { status: "error"; message: string };
type ResolutionModeValue = (typeof ResolutionMode)[keyof typeof ResolutionMode];
const resolutionModeOptions = [
  {
    label: schemaFields.JuryResolutionConfigCreate.mode.title,
    value: ResolutionMode.jury,
    description: schemaFields.JuryResolutionConfigCreate.mode.description,
  },
  {
    label: schemaFields.JudgeResolutionConfigCreate.mode.title,
    value: ResolutionMode.judge,
    description: schemaFields.JudgeResolutionConfigCreate.mode.description,
  },
  {
    label: schemaFields.NoneResolutionConfigCreate.mode.title,
    value: ResolutionMode.none,
    description: schemaFields.NoneResolutionConfigCreate.mode.description,
  },
];

export default function App() {
  const [health, setHealth] = useState<HealthState>({ status: "loading" });
  const [resolutionMode, setResolutionMode] = useState<ResolutionModeValue>(
    ResolutionMode.none,
  );
  const resolutionModeDescription =
    resolutionModeOptions.find((option) => option.value === resolutionMode)
      ?.description ?? "";

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
      <section style={{ width: "min(480px, calc(100vw - 32px))" }}>
        <h1>API Health</h1>
        <p>
          {health.status === "loading" && "Checking..."}
          {health.status === "ready" && health.data.status}
          {health.status === "error" && `Error: ${health.message}`}
        </p>
        <label
          style={{
            display: "grid",
            gap: 8,
            marginTop: 24,
            color: "#374151",
            fontWeight: 600,
          }}
        >
          Resolution mode
          <select
            value={resolutionMode}
            onChange={(event) => {
              setResolutionMode(event.target.value as ResolutionModeValue);
            }}
            style={{
              minHeight: 40,
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "0 10px",
              font: "inherit",
            }}
          >
            {resolutionModeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <p style={{ minHeight: 24, color: "#64748b" }}>
          {resolutionModeDescription}
        </p>
      </section>
    </main>
  );
}
