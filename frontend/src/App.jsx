import React from "react";
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { createRequirement, getRequirements, login, signup } from "./api.js";

const statusLabels = {
  open: "Open",
  processed: "Processed",
  obsolete: "Obsolete"
};

// Reads the saved login session from localStorage.
function getStoredUser() {
  const raw = localStorage.getItem("intern_task_user");
  return raw ? JSON.parse(raw) : null;
}

// Stores the auth token and user details after login.
function saveSession(user) {
  localStorage.setItem("intern_task_token", user.token);
  localStorage.setItem("intern_task_user", JSON.stringify(user));
}

// Removes the saved login session on logout.
function clearSession() {
  localStorage.removeItem("intern_task_token");
  localStorage.removeItem("intern_task_user");
}

// Provides the shared layout for login and signup pages.
function AuthLayout({ title, subtitle, children }) {
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

// Renders a labeled input field.
function Field({ label, ...props }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input {...props} />
    </label>
  );
}

// Handles user login and redirects to the protected requirements page.
function LoginPage({ onLogin }) {
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
      saveSession(user);
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

// Handles new account creation and redirects back to login.
function SignupPage() {
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

// Blocks the requirements page unless a user session exists.
function ProtectedRoute({ user, children }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Displays requirement totals, add form, paginated table, and logout action.
function RequirementsPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [requirements, setRequirements] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 1,
    statusCounts: { open: 0, processed: 0, obsolete: 0 }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    title: "",
    description: "",
    status: "open"
  });

  // Keeps status summary values derived from the latest paginated response.
  const totals = useMemo(() => {
    return pagination.statusCounts;
  }, [pagination.statusCounts]);

  const displayName = user?.username || user?.email?.split("@")[0] || "User";
  const isShowingAll = pagination.limit === "all";

  // Loads one backend page, or all rows only when the user selects "All".
  async function loadRequirements(nextPage = pagination.page, nextLimit = pagination.limit) {
    setError("");
    setLoading(true);

    try {
      const requestLimit = nextLimit === "all"
        ? Math.max(pagination.total, requirements.length, 1)
        : nextLimit;
      const data = await getRequirements(nextPage, requestLimit);
      const pageRequirements = data.requirements || [];
      const total = data.total ?? pageRequirements.length;
      const resolvedLimit = nextLimit === "all" ? "all" : data.limit ?? nextLimit;
      const statusCounts = data.status_counts ?? pageRequirements.reduce(
        (acc, item) => ({ ...acc, [item.status]: (acc[item.status] || 0) + 1 }),
        { open: 0, processed: 0, obsolete: 0 }
      );

      setRequirements(pageRequirements);
      setPagination({
        page: data.page ?? nextPage,
        limit: resolvedLimit,
        total,
        totalPages: nextLimit === "all"
          ? 1
          : data.total_pages ?? Math.max(1, Math.ceil(total / requestLimit)),
        statusCounts
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Loads the first page when the requirements screen opens.
  useEffect(() => {
    loadRequirements(1, pagination.limit);
  }, []);

  // Creates a requirement and refreshes the first table page.
  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);

    try {
      await createRequirement({
        title: form.title.trim(),
        description: form.description.trim() || null,
        status: form.status
      });
      await loadRequirements(1, pagination.limit);
      setForm({ title: "", description: "", status: "open" });
      setIsModalOpen(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  // Clears the stored session and returns to login.
  function logout() {
    clearSession();
    onLogout();
    navigate("/login", { replace: true });
  }

  return (
    <main className="app-page">
      <header className="topbar">
        <div>
          <h1>Requirements Management Portal</h1>
        </div>
        <div className="user-actions">
          <span>Welcome {displayName}</span>
          <button className="secondary logout-button" onClick={logout}>Logout</button>
        </div>
      </header>
      {error && <div className="notice error">{error}</div>}

      <section className="content-grid">
        <aside className="side-panel">
          <button className="compose-button" type="button" onClick={() => setIsModalOpen(true)}>
            <span aria-hidden="true">+</span>
            Add Requirement
          </button>
          <section className={`summary ${loading ? "is-loading" : ""}`} aria-label="Requirement status counts">
            <div><span>Total</span><strong>{pagination.total}</strong></div>
            <div><span>Open</span><strong>{totals.open}</strong></div>
            <div><span>Processed</span><strong>{totals.processed}</strong></div>
            <div><span>Obsolete</span><strong>{totals.obsolete}</strong></div>
          </section>
        </aside>

        <section className="table-panel">
          <div className="panel-heading">
            <h2>Existing Requirements</h2>
            <button
              className={`icon-button ${loading ? "is-spinning" : ""}`}
              onClick={() => loadRequirements(pagination.page, pagination.limit)}
              disabled={loading}
              type="button"
              aria-label="Refresh requirements"
              title="Refresh requirements"
            >
              <svg className="refresh-icon" aria-hidden="true" viewBox="0 0 24 24">
                <path d="M20 6v5h-5" />
                <path d="M4 18v-5h5" />
                <path d="M18.8 9A7 7 0 0 0 6.7 6.7L4 9" />
                <path d="M5.2 15A7 7 0 0 0 17.3 17.3L20 15" />
              </svg>
            </button>
          </div>

          {loading ? (
            <div className="loading-state" aria-live="polite">
              <div className="loader-ring" aria-hidden="true" />
              <strong>Loading requirements</strong>
              <span>Preparing your workspace...</span>
            </div>
          ) : requirements.length === 0 ? (
            <div className="empty-state">No requirements yet.</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {requirements.map((item) => (
                    <tr key={item.id}>
                      <td>{item.title}</td>
                      <td>{item.description || "-"}</td>
                      <td>
                        <span className={`badge ${item.status}`}>
                          {statusLabels[item.status] || item.status}
                        </span>
                      </td>
                      <td>{item.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {!loading && pagination.total > 0 && (
            <div className="pagination-bar" aria-label="Requirements pagination">
              <button
                className="pager-button"
                type="button"
                onClick={() => loadRequirements(pagination.page - 1, pagination.limit)}
                disabled={isShowingAll || pagination.page <= 1}
              >
                Previous
              </button>
              <span>
                {isShowingAll ? `Showing all ${pagination.total}` : `Page ${pagination.page} of ${pagination.totalPages}`}
              </span>
              <button
                className="pager-button"
                type="button"
                onClick={() => loadRequirements(pagination.page + 1, pagination.limit)}
                disabled={isShowingAll || pagination.page >= pagination.totalPages}
              >
                Next
              </button>
              <label className="page-size">
                <span>Rows</span>
                <select
                  value={pagination.limit}
                  onChange={(event) => {
                    const value = event.target.value;
                    loadRequirements(1, value === "all" ? "all" : Number(value));
                  }}
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="all">All</option>
                </select>
              </label>
            </div>
          )}
        </section>
      </section>
      {isModalOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={() => setIsModalOpen(false)}>
          <section
            className="modal-panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-requirement-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-heading">
              <h2 id="add-requirement-title">Add Requirement</h2>
              <button
                className="close-button"
                type="button"
                aria-label="Close add requirement form"
                onClick={() => setIsModalOpen(false)}
              >
                x
              </button>
            </div>
            <form className="modal-form" onSubmit={handleSubmit}>
              <Field
                label="Title"
                type="text"
                maxLength="255"
                required
                value={form.title}
                onChange={(event) => setForm({ ...form, title: event.target.value })}
              />
              <label className="field">
                <span>Description</span>
                <textarea
                  rows="5"
                  value={form.description}
                  onChange={(event) => setForm({ ...form, description: event.target.value })}
                />
              </label>
              <label className="field">
                <span>Status</span>
                <select
                  value={form.status}
                  onChange={(event) => setForm({ ...form, status: event.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="processed">Processed</option>
                  <option value="obsolete">Obsolete</option>
                </select>
              </label>
              <button className="primary" disabled={saving}>
                {saving ? "Adding..." : "Add Requirement"}
              </button>
            </form>
          </section>
        </div>
      )}
    </main>
  );
}

// Defines the application routes.
export default function App() {
  const [user, setUser] = useState(getStoredUser);

  return (
    <Routes>
      <Route path="/" element={<Navigate to={user ? "/requirements" : "/login"} replace />} />
      <Route path="/login" element={user ? <Navigate to="/requirements" replace /> : <LoginPage onLogin={setUser} />} />
      <Route path="/signup" element={user ? <Navigate to="/requirements" replace /> : <SignupPage />} />
      <Route
        path="/requirements"
        element={
          <ProtectedRoute user={user}>
            <RequirementsPage user={user} onLogout={() => setUser(null)} />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
