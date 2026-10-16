
import { useEffect, useState } from "react";
import { getOrganization, type Organization } from "../api/organizations";

type OrganizationCardProps = {
  organizationId: string;
};

export function OrganizationCard({ organizationId }: OrganizationCardProps) {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadOrganization() {
      try {
        const data = await getOrganization(organizationId);

        if (!cancelled) {
          setOrganization(data);
          setError(null);
        }
      } catch {
        if (!cancelled) {
          setError("Unable to load workspace information.");
          setOrganization(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadOrganization();

    return () => {
      cancelled = true;
    };
  }, [organizationId]);

  if (loading) {
    return <p role="status">Loading workspace...</p>;
  }

  if (error) {
    return <p role="alert">{error}</p>;
  }

  if (!organization) {
    return <p>No workspace found.</p>;
  }

  return (
    <section className="organization-card">
      <p className="eyebrow">CURRENT WORKSPACE</p>
      <h3>{organization.name}</h3>
      <p>Connected to your KIP organization database.</p>
    </section>
  );
}
