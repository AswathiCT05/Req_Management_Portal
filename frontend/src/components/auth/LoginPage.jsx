import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { login } from "../../api.js";
import Field from "../common/Field.jsx";
import AuthLayout from "./AuthLayout.jsx";

// Handles user login and redirects to the protected requirements page.
export default function LoginPage({ onLogin }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const message = location.state?.message;

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const user = await login(form);
      onLogin(user);
      navigate("/requirements", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Login" subtitle="Access the requirements workspace.">
      {message && <div className="notice success">{message}</div>}
      {error && <div className="notice error">{error}</div>}
      <form className="stack" onSubmit={handleSubmit}>
        <Field
          label="Email"
          type="email"
          required
          value={form.email}
          onChange={(event) => setForm({ ...form, email: event.target.value })}
        />
        <Field
          label="Password"
          type="password"
          required
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
        />
        <button className="primary" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <p className="switch">
        New here? <Link to="/signup">Create an account</Link>
      </p>
    </AuthLayout>
  );
}
