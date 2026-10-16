
import { afterEach, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";

import { DocumentsPage } from "./DocumentsPage";
import { getDocuments, uploadDocument } from "../api/documents";

vi.mock("../api/documents", () => ({
  getDocuments: vi.fn(),
  uploadDocument: vi.fn(),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

it("loads, searches, and uploads documents", async () => {
  const user = userEvent.setup();

  const existingDocuments = [
    {
      id: "document-1",
      organization_id: "organization-1",
      filename: "KIP_Knowledge_Base.pdf",
      content_type: "application/pdf",
      created_at: "2026-10-15T10:00:00Z",
    },
    {
      id: "document-2",
      organization_id: "organization-1",
      filename: "Operations_Runbook.pdf",
      content_type: "application/pdf",
      created_at: "2026-10-15T11:00:00Z",
    },
  ];

  vi.mocked(getDocuments).mockResolvedValue(existingDocuments);

  render(<DocumentsPage organizationId="organization-1" />);

  // 1. Documents load from the API.
  expect(
    await screen.findByText("KIP_Knowledge_Base.pdf"),
  ).toBeInTheDocument();

  expect(
    screen.getByText("Operations_Runbook.pdf"),
  ).toBeInTheDocument();

  expect(screen.getByText("2 documents")).toBeInTheDocument();

  // 2. Searching filters the document table.
  await user.type(
    screen.getByRole("searchbox", { name: "Search documents" }),
    "Operations",
  );

  expect(
    screen.getByText("Operations_Runbook.pdf"),
  ).toBeInTheDocument();

  expect(
    screen.queryByText("KIP_Knowledge_Base.pdf"),
  ).not.toBeInTheDocument();

  // Clear the search before uploading.
  await user.clear(
    screen.getByRole("searchbox", { name: "Search documents" }),
  );

  // 3. Uploading adds a document without refreshing.
  const uploadedDocument = {
    id: "document-3",
    organization_id: "organization-1",
    filename: "New_Test_Document.pdf",
    content_type: "application/pdf",
    created_at: "2026-10-15T12:00:00Z",
  };

  vi.mocked(uploadDocument).mockResolvedValue(uploadedDocument);

  const file = new File(
    ["%PDF-1.4\nTest content"],
    "New_Test_Document.pdf",
    { type: "application/pdf" },
  );

  const fileInput = screen.getByLabelText("Select PDF to upload");

  await user.upload(fileInput, file);

  await waitFor(() => {
    expect(uploadDocument).toHaveBeenCalledWith(
      "organization-1",
      file,
    );
  });

  expect(
    await screen.findByText("New_Test_Document.pdf"),
  ).toBeInTheDocument();

  expect(screen.getByText("3 documents")).toBeInTheDocument();

  expect(
    screen.getByText("New_Test_Document.pdf uploaded successfully."),
  ).toBeInTheDocument();
});
