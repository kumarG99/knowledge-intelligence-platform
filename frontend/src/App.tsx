
import { Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { OrganizationCard } from "./components/OrganizationCard";
import { DocumentsPage } from "./pages/DocumentsPage";
import "./App.css";

const DEMO_ORGANIZATION_ID = "eafd30dc-f3db-42ba-bd4a-8072da824ebe"

function Dashboard() {
  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">OVERVIEW</p>
          <h1>Dashboard</h1>
          <p className="page-description">
            Your knowledge workspace, all in one place.
          </p>
        </div>
        <span className="environment-badge">Development</span>
      </header>

      <section className="welcome-card">
        <div>
          <p className="eyebrow">WELCOME TO KIP</p>
          <h2>Turn your documents into answers.</h2>
          <p>
            Organize knowledge, search across documents, and get
            AI-powered answers backed by citations.
          </p>
        </div>
        <div className="welcome-symbol" aria-hidden="true">✦</div>
      </section>

      <section className="dashboard-section">
        <h2>Your workspace</h2>
        <OrganizationCard organizationId={DEMO_ORGANIZATION_ID} />
      </section>
    </>
  );
}

function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">WORKSPACE</p>
        <h1>{title}</h1>
        <p className="page-description">{description}</p>
      </div>
    </header>
  );
}

function App() {
  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route
            path="/documents"
            element={
              <DocumentsPage organizationId={DEMO_ORGANIZATION_ID} />
            }
          />
          <Route
            path="/assistant"
            element={
              <PlaceholderPage
                title="AI Assistant"
                description="Ask questions and discover answers from your documents."
              />
            }
          />
          <Route
            path="/settings"
            element={
              <PlaceholderPage
                title="Settings"
                description="Manage your workspace preferences."
              />
            }
          />
          <Route
            path="*"
            element={
              <PlaceholderPage
                title="Page not found"
                description="This page does not exist."
              />
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
