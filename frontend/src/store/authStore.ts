import { create } from "zustand";
import type { UserProfile } from "../services/auth";
import { storage } from "../utils/storage";

export type AuthStatus = "idle" | "loading" | "authenticated" | "error" | "not-in-telegram";

interface AuthState {
  status: AuthStatus;
  token: string | null;
  user: UserProfile | null;
  error: string | null;
  setLoading: () => void;
  setAuthenticated: (token: string, user: UserProfile) => void;
  setError: (error: string) => void;
  setNotInTelegram: () => void;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: "idle",
  token: null,
  user: null,
  error: null,

  setLoading: () => {
    set({ status: "loading", error: null });
  },

  setAuthenticated: (token: string, user: UserProfile) => {
    storage.setToken(token);
    storage.setUser(user);
    set({
      status: "authenticated",
      token,
      user,
      error: null,
    });
  },

  setError: (error: string) => {
    set({
      status: "error",
      error,
      token: null,
      user: null,
    });
  },

  setNotInTelegram: () => {
    set({
      status: "not-in-telegram",
      error: "This app must be opened inside Telegram",
      token: null,
      user: null,
    });
  },

  logout: () => {
    storage.clear();
    set({
      status: "idle",
      token: null,
      user: null,
      error: null,
    });
  },

  initialize: () => {
    const token = storage.getToken();
    const user = storage.getUser() as UserProfile | null;

    if (token && user) {
      set({
        status: "authenticated",
        token,
        user,
        error: null,
      });
    }
  },
}));
