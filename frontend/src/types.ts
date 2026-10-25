import type { CallToolResult } from "@modelcontextprotocol/client";

export type Todo = {
  id: number;
  title: string;
  done: boolean;
  created_at: string;
  done_at: string | null;
};

export type Stats = {
  period: "week" | "month";
  offset: number;
  title: string;
  buckets: { label: string; done: number; pending: number }[];
  totals: { done: number; pending: number };
};

// Appelle un tool du serveur (via l'hôte) ; l'app met elle-même l'affichage à jour.
export type CallTool = (name: string, args?: Record<string, unknown>) => Promise<void>;

// Ce que renvoient nos tools Python, dans `structuredContent` :
//   show_todos / add_todo / toggle_todo -> {"todos": [...]}
//   show_stats                         -> {"stats": {...}}
export type ToolData = { todos?: Todo[]; stats?: Stats };

export const dataFrom = (result: CallToolResult): ToolData =>
  result.isError ? {} : ((result.structuredContent as ToolData | undefined) ?? {});
