
export type Organization = {
  id: string;
  name: string;
};

export async function getOrganization(
  organizationId: string,
): Promise<Organization> {
  const response = await fetch(
    `/api/v1/organizations/${encodeURIComponent(organizationId)}`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch organization: ${response.status}`,
    );
  }

  return (await response.json()) as Organization;
}
