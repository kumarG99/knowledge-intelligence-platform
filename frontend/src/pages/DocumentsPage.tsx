
import { useEffect, useRef, useState } from "react";

import {
  getDocuments,
  uploadDocument,
  type Document,
} from "../api/documents";

type DocumentsPageProps = {
  organizationId: string;
};

export function DocumentsPage({ organizationId }: DocumentsPageProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const filteredDocuments = documents.filter((document) =>
    document.filename
      .toLowerCase()
      .includes(searchQuery.trim().toLowerCase()),
  );

  useEffect(() => {
    let cancelled = false;

    async function loadDocuments() {
      setLoading(true);
      setError(null);

      try {
        const data = await getDocuments(organizationId);

        if (!cancelled) {
          setDocuments(data);
        }
      } catch {
        if (!cancelled) {
          setError("Unable to load documents.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDocuments();

    return () => {
      cancelled = true;
    };
  }, [organizationId]);

  async function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file) return;

    setUploadError(null);
    setUploadSuccess(null);

    if (
      file.type !== "application/pdf" ||
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setUploadError("Please choose a valid PDF file.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError("PDF exceeds the 10 MB limit.");
      event.target.value = "";
      return;
    }

    setUploading(true);

    try {
      const uploadedDocument = await uploadDocument(
        organizationId,
        file,
      );

      setDocuments((previous) => [
        uploadedDocument,
        ...previous,
      ]);

      setUploadSuccess(
        `${uploadedDocument.filename} uploaded successfully.`,
      );
    } catch (err) {
      setUploadError(
        err instanceof Error
          ? err.message
          : "Unable to upload document.",
      );
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <section className="documents-page">
      <div className="documents-header">
        <div>
          <p className="eyebrow">KNOWLEDGE LIBRARY</p>
          <h2>Documents</h2>
          <p>Manage the documents in your workspace.</p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          style={{ display: "none" }}
          aria-label="Select PDF to upload"
        />

        <button
          type="button"
          className="documents-upload-button"
          disabled={uploading || loading}
          onClick={() => fileInputRef.current?.click()}
        >
          {uploading ? "Uploading..." : "+ Upload PDF"}
        </button>
      </div>

      {uploadError && (
        <p className="documents-upload-error" role="alert">
          {uploadError}
        </p>
      )}

      {uploadSuccess && (
        <p className="documents-upload-success" role="status">
          {uploadSuccess}
        </p>
      )}

      {!loading && !error && (
        <div className="documents-toolbar">
          <input
            type="search"
            className="documents-search"
            placeholder="Search documents..."
            aria-label="Search documents"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
          />

          <span className="documents-count">
            {documents.length}{" "}
            {documents.length === 1 ? "document" : "documents"}
          </span>
        </div>
      )}

      {loading && (
        <p role="status">Loading documents...</p>
      )}

      {!loading && error && (
        <p role="alert">{error}</p>
      )}

      {!loading && !error && documents.length === 0 && (
        <div className="documents-empty">
          <h3>No documents yet</h3>
          <p>
            Upload your first PDF to start building your
            knowledge library.
          </p>
        </div>
      )}

      {!loading &&
        !error &&
        documents.length > 0 &&
        filteredDocuments.length === 0 && (
          <div className="documents-empty">
            <h3>No matching documents</h3>
            <p>Try a different filename or search term.</p>
          </div>
        )}

      {!loading && !error && filteredDocuments.length > 0 && (
        <div className="documents-table-wrapper">
          <table className="documents-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>File type</th>
                <th>Uploaded</th>
              </tr>
            </thead>

            <tbody>
              {filteredDocuments.map((document) => (
                <tr key={document.id}>
                  <td className="document-name">
                    {document.filename}
                  </td>

                  <td>PDF</td>

                  <td>
                    {new Date(
                      document.created_at,
                    ).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
