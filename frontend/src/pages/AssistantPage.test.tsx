
import { afterEach, expect, it, vi } from "vitest";
import {
  cleanup,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { AssistantPage } from "./AssistantPage";
import {
  askAssistant,
  type AssistantResponse,
} from "../api/assistant";

vi.mock("../api/assistant", () => ({
  askAssistant: vi.fn(),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

const organizationId = "organization-1";

const pdfUrl =
  "/api/v1/organizations/organization-1" +
  "/documents/document-1/file#page=2";

const citationName =
  "Open citation 1: Operations_Runbook.pdf, page 2";

const successfulResponse: AssistantResponse = {
  organization_id: organizationId,
  question: "What is the maximum PDF upload size?",
  answer: "The maximum PDF upload size is 10 MiB [1].",
  sources: [
    {
      document_id: "document-1",
      filename: "Operations_Runbook.pdf",
      page_number: 2,
      chunk_index: 0,
      similarity: 0.92,
    },
  ],
  model: "qwen2.5:3b",
  usage: {
    input_tokens: 150,
    output_tokens: 30,
    duration_seconds: 2.345,
  },
};

async function expectAnswerWithClickableCitation() {
  const citation = await screen.findByRole("link", {
    name: citationName,
  });

  expect(citation).toHaveAttribute("href", pdfUrl);
  expect(citation).toHaveAttribute("target", "_blank");
  expect(citation).toHaveAttribute(
    "rel",
    "noopener noreferrer",
  );

  const answerSection = screen.getByRole("region", {
    name: "AI answer",
  });

  expect(answerSection).toHaveTextContent(
    "The maximum PDF upload size is 10 MiB [1].",
  );
}

it("displays an AI answer with clickable citations and source information", async () => {
  const user = userEvent.setup();

  vi.mocked(askAssistant).mockResolvedValue(successfulResponse);

  render(<AssistantPage organizationId={organizationId} />);

  await user.type(
    screen.getByRole("textbox", {
      name: "Ask your documents",
    }),
    "What is the maximum PDF upload size?",
  );

  await user.click(
    screen.getByRole("button", { name: /Ask AI/i }),
  );

  await waitFor(() => {
    expect(askAssistant).toHaveBeenCalledWith(
      organizationId,
      "What is the maximum PDF upload size?",
      5,
    );
  });

  await expectAnswerWithClickableCitation();

  const sourceLink = screen.getByRole("link", {
    name: "Open Operations_Runbook.pdf, page 2",
  });

  expect(sourceLink).toHaveAttribute("href", pdfUrl);
  expect(sourceLink).toHaveAttribute("target", "_blank");

  expect(
    screen.getByText("Operations_Runbook.pdf"),
  ).toBeInTheDocument();

  expect(screen.getByText("Page 2")).toBeInTheDocument();

  expect(
    screen.getByText("Model: qwen2.5:3b"),
  ).toBeInTheDocument();

  expect(screen.getByText("2.35s")).toBeInTheDocument();
});

it("shows a loading state while the answer is pending", async () => {
  const user = userEvent.setup();

  let resolveRequest!: (value: AssistantResponse) => void;

  vi.mocked(askAssistant).mockImplementation(
    () =>
      new Promise<AssistantResponse>((resolve) => {
        resolveRequest = resolve;
      }),
  );

  render(<AssistantPage organizationId={organizationId} />);

  await user.type(
    screen.getByRole("textbox", {
      name: "Ask your documents",
    }),
    "What is the upload limit?",
  );

  await user.click(
    screen.getByRole("button", { name: /Ask AI/i }),
  );

  expect(screen.getByRole("status")).toHaveTextContent(
    "Searching documents and generating your answer...",
  );

  expect(
    screen.getByRole("button", {
      name: /Generating answer/i,
    }),
  ).toBeDisabled();

  expect(
    screen.getByRole("textbox", {
      name: "Ask your documents",
    }),
  ).toBeDisabled();

  resolveRequest(successfulResponse);

  await expectAnswerWithClickableCitation();

  await waitFor(() => {
    expect(
      screen.queryByRole("status"),
    ).not.toBeInTheDocument();
  });
});

it("displays an API error and allows retrying", async () => {
  const user = userEvent.setup();

  vi.mocked(askAssistant)
    .mockRejectedValueOnce(
      new Error(
        "The AI service is temporarily unavailable. Check that Ollama is running.",
      ),
    )
    .mockResolvedValueOnce(successfulResponse);

  render(<AssistantPage organizationId={organizationId} />);

  await user.type(
    screen.getByRole("textbox", {
      name: "Ask your documents",
    }),
    "What is the upload limit?",
  );

  await user.click(
    screen.getByRole("button", { name: /Ask AI/i }),
  );

  expect(
    await screen.findByRole("alert"),
  ).toHaveTextContent(
    "The AI service is temporarily unavailable.",
  );

  await user.click(
    screen.getByRole("button", { name: /Ask AI/i }),
  );

  await expectAnswerWithClickableCitation();

  expect(
    screen.queryByRole("alert"),
  ).not.toBeInTheDocument();

  expect(askAssistant).toHaveBeenCalledTimes(2);
});

it("does not submit an empty or whitespace-only question", async () => {
  const user = userEvent.setup();

  render(<AssistantPage organizationId={organizationId} />);

  const submitButton = screen.getByRole("button", {
    name: /Ask AI/i,
  });

  expect(submitButton).toBeDisabled();

  await user.type(
    screen.getByRole("textbox", {
      name: "Ask your documents",
    }),
    "   ",
  );

  expect(submitButton).toBeDisabled();
  expect(askAssistant).not.toHaveBeenCalled();
});

it("displays the refusal response for an unanswerable question", async () => {
  const user = userEvent.setup();

  vi.mocked(askAssistant).mockResolvedValue({
    ...successfulResponse,
    question: "Who is the CEO?",
    answer: "I don't know based on the provided documents.",
    sources: [],
    model: "qwen2.5:3b",
  });

  render(<AssistantPage organizationId={organizationId} />);

  await user.type(
    screen.getByRole("textbox", {
      name: "Ask your documents",
    }),
    "Who is the CEO?",
  );

  await user.click(
    screen.getByRole("button", { name: /Ask AI/i }),
  );

  expect(
    await screen.findByText(
      "I don't know based on the provided documents.",
    ),
  ).toBeInTheDocument();

  expect(
    screen.queryByText("Retrieved sources"),
  ).not.toBeInTheDocument();

  expect(
    screen.queryByRole("link", {
      name: citationName,
    }),
  ).not.toBeInTheDocument();
});
