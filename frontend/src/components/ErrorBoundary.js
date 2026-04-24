import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(err) {
    return { hasError: true, message: err?.message || "Unknown error" };
  }

  componentDidCatch(err) {
    console.error("App error:", err);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="page">
          <div className="page-header">
            <h1 className="page-title">Something broke</h1>
            <p className="page-subtitle">An unexpected error occurred. Please refresh.</p>
          </div>
          <div className="card">
            <pre style={{ whiteSpace: "pre-wrap", fontSize: "0.85rem" }}>{this.state.message}</pre>
            <button className="quick-action-btn primary" onClick={() => window.location.reload()}>
              Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
