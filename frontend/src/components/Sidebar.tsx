
import { NavLink } from "react-router-dom";

const navigation = [
  { label: "Dashboard", icon: "▦", path: "/" },
  { label: "Documents", icon: "▤", path: "/documents" },
  { label: "AI Assistant", icon: "✦", path: "/assistant" },
  { label: "Settings", icon: "⚙", path: "/settings" },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">K</div>
        <div>
          <strong>KIP</strong>
          <span>Knowledge Intelligence</span>
        </div>
      </div>

      <div className="workspace-label">WORKSPACE</div>

      <nav className="sidebar-nav" aria-label="Main navigation">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <span className="nav-icon" aria-hidden="true">
              {item.icon}
            </span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="avatar">K</div>
        <div>
          <strong>Demo Workspace</strong>
          <span>Development environment</span>
        </div>
      </div>
    </aside>
  );
}
