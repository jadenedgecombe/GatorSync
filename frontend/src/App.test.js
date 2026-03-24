import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

test("renders GatorSync nav brand", () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
  const brand = screen.getByText(/GatorSync/i);
  expect(brand).toBeInTheDocument();
});
