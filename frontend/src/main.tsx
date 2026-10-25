import type { CallToolResult } from "@modelcontextprotocol/client";
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";

type Todo = { id: number; title: string; done: boolean };

// Tous nos tools Python renvoient {"todos": [...]} -> c'est le `structuredContent`.
const todosFrom = (result: CallToolResult) =>
  (result.structuredContent as { todos: Todo[] } | undefined)?.todos ?? [];

function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [title, setTitle] = useState("");

  // 1. Connexion à l'hôte (Claude, VS Code...) via postMessage avec window.parent.
  const { app, isConnected, error } = useApp({
    appInfo: { name: "Todos", version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      // 2. L'hôte nous pousse le résultat du tool qui a ouvert l'UI (show_todos).
      app.ontoolresult = (result) => setTodos(todosFrom(result));
    },
  });

  if (error) return <p>Erreur : {error.message}</p>;
  if (!isConnected || !app) return <p>Connexion à l'hôte…</p>;

  // 3. L'UI appelle elle-même des tools du serveur (l'hôte relaie la requête).
  const call = async (name: string, args: Record<string, unknown>) => {
    const result = await app.callServerTool({ name, arguments: args });
    setTodos(todosFrom(result));
  };

  return (
    <main style={{ fontFamily: "system-ui", padding: 16 }}>
      <h2>Mes tâches</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {todos.map((t) => (
          <li key={t.id}>
            <label>
              <input
                type="checkbox"
                checked={t.done}
                onChange={() => call("toggle_todo", { todo_id: t.id })}
              />{" "}
              <span style={{ textDecoration: t.done ? "line-through" : "none" }}>
                {t.title}
              </span>
            </label>
          </li>
        ))}
      </ul>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!title.trim()) return;
          call("add_todo", { title });
          setTitle("");
        }}
      >
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Nouvelle tâche" />
        <button type="submit">Ajouter</button>
      </form>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <TodoApp />
  </StrictMode>,
);
