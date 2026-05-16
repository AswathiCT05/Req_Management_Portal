import React from "react";

// Provides the shared layout for login and signup pages.
export default function AuthLayout({ title, subtitle, children }) {
  return (
    <main className="auth-page">
      <div className="auth-brand">Requirements<span>Intake</span></div>
      <section className="auth-panel">
        <div>
          <h1>{title}</h1>
          <p className="muted">{subtitle}</p>
        </div>
        {children}
      </section>
    </main>
  );
}
