import { useAuth } from "../context/AuthContext";

/**
 * Only renders children if the user has one of the allowed roles.
 * Usage: <RoleGuard roles={["admin", "ta"]}>...</RoleGuard>
 */
function RoleGuard({ roles, children, fallback = null }) {
  const { user } = useAuth();

  if (!user || !roles.includes(user.role)) {
    return fallback;
  }

  return children;
}

export default RoleGuard;
