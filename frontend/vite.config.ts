import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

// L'hôte MCP affiche UNE ressource HTML dans une iframe sandboxée :
// on inline donc tout le JS/CSS dans dist/mcp-app.html.
export default defineConfig({
  plugins: [react(), viteSingleFile()],
  build: {
    outDir: "dist",
    rollupOptions: { input: "mcp-app.html" },
  },
});
