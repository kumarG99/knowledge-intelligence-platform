
export type Document = {
  id: string;
  organization_id: string;
  filename: string;
  content_type: string;
  created_at: string;
};

export async function getDocuments(
  organizationId: string,
): Promise<Document[]> {
  const response = await fetch(
    `/api/v1/organizations/${encodeURIComponent(organizationId)}/documents`,
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch documents: ${response.status}`);
  }

  return (await response.json()) as Document[];
}


export async function uploadDocument(
  organizationId: string,
  file: File,
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `/api/v1/organizations/${encodeURIComponent(organizationId)}/documents`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    if (response.status === 413) {
      throw new Error("PDF exceeds the 10 MB limit.");
    }

    if (response.status === 400) {
      throw new Error("Please select a valid PDF file.");
    }

    throw new Error("Unable to upload document. Please try again.");
  }

  return (await response.json()) as Document;
}
