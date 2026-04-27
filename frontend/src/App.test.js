import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import App from "./App";

// ---- App smoke tests ----

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

test("login page has email and password fields", () => {
  window.history.pushState({}, "", "/login");
  render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  );
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
});

test("signup link is visible on login page", () => {
  window.history.pushState({}, "", "/login");
  render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  );
  expect(screen.getByText(/sign up/i)).toBeInTheDocument();
});

test("signup page renders name field", () => {
  window.history.pushState({}, "", "/signup");
  render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  );
  expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
});
