import type { CallToolResult } from "@modelcontextprotocol/client";
import { useApp, useHostStyles } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { StatsView } from "./StatsView";
import "./styles.css";
import { TodoList } from "./TodoList";
import { dataFrom, type Stats, type Todo } from "./types";

function TodoApp() {
  const [todos, setTodos] = useState<Todo[] | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [view, setView] = useState<"todos" | "stats">("todos");

  // Tous les résultats de tools passent par ici, qu'ils viennent de l'hôte
  // (ontoolresult) ou d'un appel fait par l'UI (callServerTool).
  // Le contenu décide de la vue : {"todos": ...} ou {"stats": ...}.
  const handleResult = (result: CallToolResult) => {
    const data = dataFrom(result);
    if (data.todos) {
      setTodos(data.todos);
      setView("todos");
    }
    if (data.stats) {
      setStats(data.stats);
      setView("stats");
    }
  };

  // 1. Connexion à l'hôte (Claude, VS Code...) via postMessage avec window.parent.
  const { app, isConnected, error } = useApp({
    appInfo: { name: "Todos", version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      // 2. L'hôte nous pousse le résultat du tool qui a ouvert l'UI
      //    (show_todos ou show_stats).
      app.ontoolresult = handleResult;
    },
  });

  // Reprend les couleurs, polices et le thème clair/sombre de l'hôte.
  useHostStyles(app, app?.getHostContext());

  if (error) return <p className="muted">Erreur : {error.message}</p>;
  if (!isConnected || !app) return <p className="muted">Connexion à l'hôte…</p>;

  // 3. L'UI appelle elle-même des tools du serveur (l'hôte relaie la requête).
  const call = async (name: string, args: Record<string, unknown> = {}) => {
    handleResult(await app.callServerTool({ name, arguments: args }));
  };

  if (view === "stats" && stats) return <StatsView stats={stats} call={call} />;
  if (todos) return <TodoList todos={todos} call={call} />;
  return <p className="muted">Chargement…</p>;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <TodoApp />
  </StrictMode>,
);
