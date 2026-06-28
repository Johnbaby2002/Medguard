import { spawnProcess, rootDir } from "./common.mjs";

console.log("Starting MedGuard backend and frontend...");
console.log("Backend docs: http://127.0.0.1:8000/docs");
console.log("Frontend: http://127.0.0.1:3000/register.html");
console.log("Press Ctrl+C to stop both.");

const backend = spawnProcess("node", ["scripts/backend.mjs"], { cwd: rootDir });
const frontend = spawnProcess("node", ["scripts/frontend.mjs"], { cwd: rootDir });

function stopAll() {
  backend.kill("SIGINT");
  frontend.kill("SIGINT");
}

process.on("SIGINT", () => {
  stopAll();
  process.exit(0);
});

backend.on("exit", (code) => {
  if (code && code !== 0) {
    frontend.kill("SIGINT");
    process.exit(code);
  }
});

frontend.on("exit", (code) => {
  if (code && code !== 0) {
    backend.kill("SIGINT");
    process.exit(code);
  }
});
