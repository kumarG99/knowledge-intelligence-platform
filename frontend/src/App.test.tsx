
import { expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import App from "./App";

test("navigates between workspace pages", async () => {
  const user = userEvent.setup();

  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("heading", { name: "Dashboard" }),
  ).toBeTruthy();

  await user.click(screen.getByRole("link", { name: /Documents/i }));

  expect(
    screen.getByRole("heading", { name: "Documents" }),
  ).toBeTruthy();

  await user.click(screen.getByRole("link", { name: /AI Assistant/i }));

  expect(
    screen.getByRole("heading", { name: "AI Assistant" }),
  ).toBeTruthy();

  await user.click(screen.getByRole("link", { name: /Settings/i }));

  expect(
    screen.getByRole("heading", { name: "Settings" }),
  ).toBeTruthy();
});
