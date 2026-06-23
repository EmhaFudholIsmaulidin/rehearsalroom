import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import { Spinner } from "./components/ui";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Songs from "./pages/Songs";
import Schedule from "./pages/Schedule";
import SessionDetail from "./pages/SessionDetail";
import Members from "./pages/Members";

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

function PublicOnly({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <Spinner />;
  if (user) return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={
              <PublicOnly>
                <Auth />
              </PublicOnly>
            }
          />
          <Route
            path="/dashboard"
            element={
              <Protected>
                <Dashboard />
              </Protected>
            }
          />
          <Route
            path="/songs"
            element={
              <Protected>
                <Songs />
              </Protected>
            }
          />
          <Route
            path="/schedule"
            element={
              <Protected>
                <Schedule />
              </Protected>
            }
          />
          <Route
            path="/sessions/:sessionId"
            element={
              <Protected>
                <SessionDetail />
              </Protected>
            }
          />
          <Route
            path="/members"
            element={
              <Protected>
                <Members />
              </Protected>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
