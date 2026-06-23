import { createContext, useContext, useState, useEffect } from "react";
import { authApi, bandApi, memberApi, tokens } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [bands, setBands] = useState([]);
  const [currentBand, setCurrentBand] = useState(null);
  const [loading, setLoading] = useState(true);

  // The current user's role within the selected band (band_leader | member)
  const myRole = currentBand?._myRole || null;
  const isLeader = myRole === "band_leader";

  async function loadSession() {
    if (!tokens.access) {
      setLoading(false);
      return;
    }
    try {
      const me = await authApi.me();
      setUser(me);
      await loadBands(me);
    } catch {
      tokens.clear();
    } finally {
      setLoading(false);
    }
  }

  async function loadBands(me = user) {
    const res = await bandApi.myBands();
    const list = res.items || [];
    // Determine the user's role per band via the members list
    setBands(list);
    if (list.length > 0) {
      const saved = localStorage.getItem("current_band_id");
      const pick = list.find((b) => b.id === saved) || list[0];
      await selectBand(pick, me);
    } else {
      setCurrentBand(null);
    }
  }

  async function selectBand(band, me = user) {
    localStorage.setItem("current_band_id", band.id);
    // Figure out this user's role inside the band
    try {
      const members = await memberApi.list(band.id);
      const mine = (members.items || []).find((m) => m.user_id === me?.id);
      setCurrentBand({ ...band, _myRole: mine?.role || "member" });
    } catch {
      setCurrentBand({ ...band, _myRole: "member" });
    }
  }

  useEffect(() => {
    loadSession();
    // eslint-disable-next-line
  }, []);

  async function login(email, password) {
    const data = await authApi.login({ email, password });
    tokens.set(data);
    const me = await authApi.me();
    setUser(me);
    await loadBands(me);
    return me;
  }

  async function register(body) {
    await authApi.register(body);
    return login(body.email, body.password);
  }

  async function logout() {
    try {
      if (tokens.refresh) await authApi.logout(tokens.refresh);
    } catch {
      /* ignore */
    }
    tokens.clear();
    localStorage.removeItem("current_band_id");
    setUser(null);
    setBands([]);
    setCurrentBand(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        bands,
        currentBand,
        myRole,
        isLeader,
        loading,
        login,
        register,
        logout,
        selectBand,
        reloadBands: () => loadBands(),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
