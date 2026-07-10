import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, Activity, Pill } from "lucide-react";
import { login } from "../api/auth";
import { Link } from "react-router-dom";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("patient@example.com");
  const [password, setPassword] = useState("StrongPassword123");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const data = await login({ email, password });

      localStorage.setItem("medguard_token", data.access_token);
      localStorage.setItem("medguard_user", JSON.stringify(data.user));

      navigate("/dashboard");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        gridTemplateColumns: "1fr 460px",
        background: "#0f172a",
      }}
    >
      <div
        style={{
          padding: "80px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          color: "white",
        }}
      >
        <div
          style={{
            width: 72,
            height: 72,
            borderRadius: 20,
            background: "rgba(124,58,237,0.15)",
            display: "grid",
            placeItems: "center",
            marginBottom: 28,
          }}
        >
          <ShieldCheck size={34} />
        </div>

        <p
          style={{
            color: "#8b5cf6",
            fontWeight: 700,
            letterSpacing: 1,
            textTransform: "uppercase",
          }}
        >
          Medication Safety Platform
        </p>

        <h1
          style={{
            fontSize: 58,
            lineHeight: 1.05,
            marginTop: 12,
            maxWidth: 700,
          }}
        >
          Smarter medication safety for everyday care.
        </h1>

        <p
          style={{
            marginTop: 24,
            color: "#94a3b8",
            fontSize: 18,
            maxWidth: 650,
            lineHeight: 1.7,
          }}
        >
          Analyze medication interactions, track reminders, review risk reports,
          and maintain a complete health profile in one place.
        </p>

        <div
          style={{
            display: "flex",
            gap: 20,
            marginTop: 42,
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              background: "#111827",
              borderRadius: 18,
              padding: 18,
              minWidth: 180,
            }}
          >
            <Activity size={22} />
            <p style={{ marginTop: 12, fontWeight: 700 }}>
              Safety Monitoring
            </p>
            <p style={{ color: "#94a3b8", marginTop: 8 }}>
              Detect medication risks instantly.
            </p>
          </div>

          <div
            style={{
              background: "#111827",
              borderRadius: 18,
              padding: 18,
              minWidth: 180,
            }}
          >
            <Pill size={22} />
            <p style={{ marginTop: 12, fontWeight: 700 }}>
              Medication Tracking
            </p>
            <p style={{ color: "#94a3b8", marginTop: 8 }}>
              Organize treatments and reminders.
            </p>
          </div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          placeItems: "center",
          padding: 40,
        }}
      >
        <form
          onSubmit={handleSubmit}
          style={{
            width: "100%",
            maxWidth: 420,
            padding: 36,
            borderRadius: 28,
            background: "#111827",
            boxShadow: "0 30px 80px rgba(0,0,0,0.45)",
            color: "white",
          }}
        >
          <h2
            style={{
              fontSize: 34,
              fontWeight: 800,
            }}
          >
            MedGuard
          </h2>

          <p
            style={{
              marginTop: 10,
              color: "#94a3b8",
            }}
          >
            Sign in to continue.
          </p>

          <label
            style={{
              display: "grid",
              gap: 8,
              marginTop: 28,
            }}
          >
            <span>Email</span>

            <input
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label
            style={{
              display: "grid",
              gap: 8,
              marginTop: 18,
            }}
          >
            <span>Password</span>

            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && (
            <p
              style={{
                color: "#fca5a5",
                marginTop: 16,
              }}
            >
              {error}
            </p>
          )}

          <button
            className="primary-button"
            type="submit"
            disabled={isLoading}
            style={{
              width: "100%",
              marginTop: 24,
            }}
          >
            {isLoading ? "Signing in..." : "Sign in"}
          </button>

          <p
            style={{
              marginTop: 16,
              textAlign: "center",
            }}
          >
            <Link to="/register">Create account</Link>
          </p>

          <div
            style={{
              marginTop: 22,
              padding: 14,
              borderRadius: 12,
              background: "rgba(255,255,255,0.04)",
              color: "#94a3b8",
              fontSize: 13,
            }}
          >
            Demo Account
            <br />
            patient@example.com
            <br />
            StrongPassword123
          </div>
        </form>
      </div>
    </div>
  );
}