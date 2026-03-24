import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ children }) {
  const { user, loading, token } = useAuth();

  // Still checking the token — show nothing to avoid layout flicker
  if (loading) {
    return null;
  }

  // No token and no user — redirect to login
  if (!user && !token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
