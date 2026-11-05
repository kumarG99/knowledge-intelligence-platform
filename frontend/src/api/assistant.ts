
export type AssistantSource = {
  document_id: string;
  filename: string;
  page_number: number;
  chunk_index: number;
  similarity: number;
};

export type AssistantUsage = {
  input_tokens: number;
  output_tokens: number;
  duration_seconds: number;
};

export type AssistantResponse = {
  organization_id: string;
  question: string;
  answer: string;
  sources: AssistantSource[];
  model: string | null;
  usage: AssistantUsage;
};

export async function askAssistant(
  organizationId: string,
  question: string,
  limit: number = 5,
): Promise<AssistantResponse> {
  const response = await fetch(
    `/api/v1/organizations/${encodeURIComponent(organizationId)}/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        limit,
      }),
    },
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Workspace not found.");
    }

    if (response.status === 422) {
      throw new Error("Please enter a valid question.");
    }

    if (response.status === 503) {
      throw new Error(
        "The AI service is temporarily unavailable. Check that Ollama is running.",
      );
    }

    throw new Error(
      "Unable to get an answer. Please try again.",
    );
  }

  return (await response.json()) as AssistantResponse;
}
