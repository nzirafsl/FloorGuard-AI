import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Vite's dev server root — src/ files are resolved from here
  root: ".",
  // Point the HTML entry to the project root index.html (created below)
  // The templates/index.html remains as a reference; Vite uses root index.html
  server: {
    port: 5173,
    open: true, // auto-open browser on npm run dev
  },
  build: {
    outDir: "dist",
  },
});
