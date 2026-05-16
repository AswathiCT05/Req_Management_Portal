import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signup } from "../../api.js";
import Field from "../common/Field.jsx";
import AuthLayout from "./AuthLayout.jsx";

// Handles new account creation and redirects back to login.
export default function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await signup(form);
      navigate("/login", {
        replace: true,
        state: { message: "Account created. Please log in." }
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Sign Up" subtitle="Create an account before adding requirements.">
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
          label="Username"
          type="text"
          minLength="3"
          required
          value={form.username}
          onChange={(event) => setForm({ ...form, username: event.target.value })}
        />
        <Field
          label="Password"
          type="password"
          minLength="6"
          required
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
        />
        <button className="primary" disabled={loading}>
          {loading ? "Creating..." : "Create Account"}
        </button>
      </form>
      <p className="switch">
        Already registered? <Link to="/login">Login</Link>
      </p>
    </AuthLayout>
  );
}
