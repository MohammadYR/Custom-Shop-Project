import { useSyncExternalStore } from "react";

export const tokens = {
  access: localStorage.getItem("access") ?? "",
  refresh: localStorage.getItem("refresh") ?? "",
};
let listeners: Array<() => void> = [];

const tokensStore = {
  subscribe(listener: () => void) {
    listeners = [...listeners, listener];
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
  getSnapshot() {
    return tokens;
  },
};

export function storeTokens(access: string, refresh: string) {
  tokens.access = access;
  tokens.refresh = refresh;
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
  emitChange();
}

export function removeTokens() {
  tokens.access = "";
  tokens.refresh = "";
  localStorage.setItem("access", "");
  localStorage.setItem("refresh", "");
  emitChange();
}

function emitChange() {
  for (const listener of listeners) {
    listener();
  }
}

export function useAuth() {
  const tokens = useSyncExternalStore(
    tokensStore.subscribe,
    tokensStore.getSnapshot,
  );
  return { tokens, isLogin: !!tokens.access };
}
