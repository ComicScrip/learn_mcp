import { useState } from "react";
import type { CallTool, Todo } from "./types";

// Les plus récentes d'abord, et seulement les 15 dernières : avec l'historique,
// la base contient des centaines de tâches.
const RECENT = 15;

export function TodoList({ todos, call }: { todos: Todo[]; call: CallTool }) {
  const [title, setTitle] = useState("");
  const recent = [...todos].reverse().slice(0, RECENT);

  return (
    <main className="card">
      <header className="header">
        <h2>Mes tâches</h2>
        <button className="link" onClick={() => call("show_stats", { period: "week" })}>
          Voir les stats →
        </button>
      </header>

      <form
        className="add"
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

      <ul className="todos">
        {recent.map((t) => (
          <li key={t.id}>
            <label>
              <input
                type="checkbox"
                checked={t.done}
                onChange={() => call("toggle_todo", { todo_id: t.id })}
              />
              <span className={t.done ? "done" : ""}>{t.title}</span>
            </label>
            <time className="muted">
              {new Date(t.created_at).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}
            </time>
          </li>
        ))}
      </ul>
      {todos.length > RECENT && (
        <p className="muted small">
          {RECENT} plus récentes sur {todos.length}
        </p>
      )}
    </main>
  );
}
