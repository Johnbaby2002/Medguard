import { NavLink, Outlet, useNavigate } from "react-router-dom";

export default function Layout() {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("medguard_token");
    localStorage.removeItem("medguard_user");
    navigate("/");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2 className="sidebar-title">MedGuard</h2>

        <nav className="sidebar-nav">
          <NavLink className="sidebar-link" to="/dashboard">
            Dashboard
          </NavLink>
          <NavLink className="sidebar-link" to="/medications">
            Medications
          </NavLink>
          <NavLink className="sidebar-link" to="/safety">
            Safety
          </NavLink>
          <NavLink className="sidebar-link" to="/profile">
            Profile
          </NavLink>
          <NavLink className="sidebar-link" to="/reminders">
            Reminders
          </NavLink>
          <NavLink className="sidebar-link" to="/reports">
            Reports
          </NavLink>
        </nav>

        <button className="logout-button" onClick={logout}>
          Logout
        </button>
      </aside>

      <main className="page">
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}