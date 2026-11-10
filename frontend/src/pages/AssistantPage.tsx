
import { useState, type FormEvent, type ReactNode } from "react";

import {
  askAssistant,
  type AssistantResponse,
} from "../api/assistant";

type AssistantPageProps = {
  organizationId: string;
};

function getPdfUrl(
  organizationId: string,
  documentId: string,
  pageNumber: number,
): string {
  const baseUrl =
    `/api/v1/organizations/${encodeURIComponent(organizationId)}` +
    `/documents/${encodeURIComponent(documentId)}/file`;

  const page = Math.max(1, Math.floor(pageNumber));

  return `${baseUrl}#page=${page}`;
}

function renderAnswerWithCitations(
  answer: string,
  result: AssistantResponse,
  organizationId: string,
): ReactNode[] {
  const parts = answer.split(/(\[\d+\])/g);

  return parts.map((part, index) => {
    const match = /^\[(\d+)\]$/.exec(part);

    if (!match) {
      return part;
    }

    const sourceIndex = Number(match[1]) - 1;
    const source = result.sources[sourceIndex];

    // Do not create a link for an unknown citation.
    if (!source) {
      return part;
    }

    return (
      <a
        key={`citation-${index}`}
        href={getPdfUrl(
          organizationId,
          source.document_id,
          source.page_number,
        )}
        target="_blank"
        rel="noopener noreferrer"
        className="assistant-citation-link"
        aria-label={`Open citation ${sourceIndex + 1}: ${source.filename}, page ${source.page_number}`}
        title={`${source.filename} — Page ${source.page_number}`}
      >
        {part}
      </a>
    );
  });
}

export function AssistantPage({
  organizationId,
}: AssistantPageProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AssistantResponse | null>(
    null,
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await askAssistant(
        organizationId,
        trimmedQuestion,
        5,
      );

      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to get an answer.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="assistant-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">KNOWLEDGE INTELLIGENCE</p>
          <h1>AI Assistant</h1>
          <p className="page-description">
            Ask questions about your documents and get
            AI-powered answers with source references.
          </p>
        </div>
        <span className="environment-badge">Local AI</span>
      </header>

      <div className="assistant-intro">
        <div className="assistant-intro-icon" aria-hidden="true">
          ✦
        </div>
        <div>
          <h2>Your knowledge, intelligently connected.</h2>
          <p>
            Search across your uploaded PDFs and get answers
            grounded in your document library.
          </p>
        </div>
      </div>

      <form className="assistant-form" onSubmit={handleSubmit}>
        <label htmlFor="assistant-question">
          Ask your documents
        </label>

        <textarea
          id="assistant-question"
          className="assistant-textarea"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="e.g. What is the maximum PDF upload size?"
          rows={4}
          maxLength={500}
          disabled={loading}
          required
        />

        <div className="assistant-form-footer">
          <span>{question.length}/500 characters</span>

          <button
            className="assistant-submit"
            type="submit"
            disabled={loading || !question.trim()}
          >
            {loading ? "Generating answer..." : "✦ Ask AI"}
          </button>
        </div>
      </form>

      {loading && (
        <div className="assistant-status" role="status">
          <span className="assistant-spinner" aria-hidden="true" />
          Searching documents and generating your answer...
        </div>
      )}

      {error && (
        <div className="assistant-error" role="alert">
          {error}
        </div>
      )}

      {result && (
        <div className="assistant-results">
          <section
            className="assistant-answer-card"
            aria-label="AI answer"
          >
            <div className="assistant-section-heading">
              <span className="assistant-section-icon">✦</span>
              <h2>AI Answer</h2>
            </div>

            <p className="assistant-answer-text">
              {renderAnswerWithCitations(
                result.answer,
                result,
                organizationId,
              )}
            </p>

            {result.model && (
              <div className="assistant-answer-meta">
                <span>Model: {result.model}</span>
                <span>
                  {result.usage.duration_seconds.toFixed(2)}s
                </span>
              </div>
            )}
          </section>

          {result.sources.length > 0 && (
            <section className="assistant-sources-card">
              <div className="assistant-section-heading">
                <h2>Retrieved sources</h2>
                <span className="assistant-source-count">
                  {result.sources.length}
                </span>
              </div>

              <ol className="assistant-source-list">
                {result.sources.map((source, index) => (
                  <li
                    key={`${source.document_id}-${source.page_number}-${source.chunk_index}`}
                    className="assistant-source-item"
                  >
                    <span className="assistant-source-number">
                      {index + 1}
                    </span>

                    <div className="assistant-source-details">
                      <a
                        href={getPdfUrl(
                          organizationId,
                          source.document_id,
                          source.page_number,
                        )}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="assistant-source-link"
                        aria-label={`Open ${source.filename}, page ${source.page_number}`}
                      >
                        {source.filename}
                      </a>
                      <span>Page {source.page_number}</span>
                    </div>
                  </li>
                ))}
              </ol>

              <p className="assistant-sources-note">
                These are the excerpts retrieved for the AI.
                Not every retrieved excerpt is necessarily
                cited in the answer.
              </p>
            </section>
          )}
        </div>
      )}
    </section>
  );
}
