import { findPython, frontendDir, run } from "./common.mjs";

const python = findPython();
const port = process.env.FRONTEND_PORT || "3000";

console.log(`Starting MedGuard frontend pages on http://127.0.0.1:${port}`);
run(python.command, [...python.args, "-m", "http.server", port, "--bind", "127.0.0.1"], { cwd: frontendDir });
