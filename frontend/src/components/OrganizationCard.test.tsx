
import { afterEach, expect, test, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";

import { OrganizationCard } from "./OrganizationCard";
import { getOrganization } from "../api/organizations";

vi.mock("../api/organizations", () => ({
  getOrganization: vi.fn(),
}));

const mockedGetOrganization = vi.mocked(getOrganization);

afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});

test("shows loading and then organization information", async () => {
  let resolveRequest!: (value: { id: string; name: string }) => void;

  mockedGetOrganization.mockReturnValue(
    new Promise((resolve) => {
      resolveRequest = resolve;
    }),
  );

  render(<OrganizationCard organizationId="org-123" />);

  expect(screen.getByRole("status").textContent).toContain(
    "Loading workspace",
  );

  resolveRequest({
    id: "org-123",
    name: "KIP Demo Organization",
  });

  expect(
    await screen.findByText("KIP Demo Organization"),
  ).toBeTruthy();
});

test("shows an error when the API request fails", async () => {
  mockedGetOrganization.mockRejectedValue(new Error("Network error"));

  render(<OrganizationCard organizationId="org-123" />);

  expect(
    (await screen.findByRole("alert")).textContent,
  ).toContain("Unable to load workspace information");
});
