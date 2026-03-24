import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import App from "./App";

test("renders GatorSync brand on login page", () => {
  window.history.pushState({}, "", "/login");
  render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  );
  const brand = screen.getByText(/GatorSync/i);
  expect(brand).toBeInTheDocument();
});
