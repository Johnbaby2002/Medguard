import { copyFileSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { randomBytes } from "node:crypto";
import { backendDir, findPython, run, venvDir, venvPythonPath } from "./common.mjs";

const envPath = join(backendDir, ".env");
const sqliteExamplePath = join(backendDir, ".env.sqlite.example");

console.log("Setting up MedGuard...");

const python = findPython();
if (!existsSync(venvDir)) {
  console.log("Creating backend virtual environment...");
  run(python.command, [...python.args, "-m", "venv", venvDir]);
}

if (!existsSync(envPath)) {
  console.log("Creating backend/.env for local SQLite development...");
  copyFileSync(sqliteExamplePath, envPath);
  const secret = randomBytes(32).toString("hex");
  const envText = readFileSync(envPath, "utf8").replace(
    "JWT_SECRET_KEY=change-this-in-production",
    `JWT_SECRET_KEY=${secret}`
  );
  writeFileSync(envPath, envText);
}

const venvPython = venvPythonPath();
console.log("Installing backend dependencies...");
run(venvPython, ["-m", "pip", "install", "-r", "requirements.txt"], { cwd: backendDir });
run(venvPython, ["-m", "pip", "install", "-r", "requirements-dev.txt"], { cwd: backendDir });

console.log("");
console.log("Setup complete.");
console.log("Run the full app with:");
console.log("  npm run dev");
console.log("");
console.log("Frontend: http://127.0.0.1:3000/register.html");
console.log("Backend docs: http://127.0.0.1:8000/docs");
