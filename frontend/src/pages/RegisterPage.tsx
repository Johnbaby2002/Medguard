import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../api/auth";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      await register({
        full_name: fullName,
        email,
        password,
        repeat_password: repeatPassword,
        terms_consent: true,
        medical_disclaimer_consent: true,
      });

      navigate("/");
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Registration failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        background: "#0f172a",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          width: 420,
          background: "#111827",
          padding: 32,
          borderRadius: 20,
          color: "white",
        }}
      >
        <h1>Create Account</h1>

        <input
          className="input"
          placeholder="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          style={{ width: "100%", marginTop: 20 }}
        />

        <input
          className="input"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ width: "100%", marginTop: 12 }}
        />

        <input
          className="input"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: "100%", marginTop: 12 }}
        />

        <input
          className="input"
          type="password"
          placeholder="Repeat password"
          value={repeatPassword}
          onChange={(e) => setRepeatPassword(e.target.value)}
          style={{ width: "100%", marginTop: 12 }}
        />

        {error && (
          <p style={{ color: "#fca5a5", marginTop: 12 }}>
            {error}
          </p>
        )}

        <button
          type="submit"
          className="primary-button"
          style={{
            width: "100%",
            marginTop: 20,
          }}
        >
          {loading ? "Creating..." : "Create account"}
        </button>

        <p
          style={{
            marginTop: 16,
            textAlign: "center",
          }}
        >
          <Link to="/">
            Already have an account?
          </Link>
        </p>
      </form>
    </div>
  );
}