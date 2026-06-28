import { existsSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import process from "node:process";

export const rootDir = dirname(dirname(fileURLToPath(import.meta.url)));
export const backendDir = join(rootDir, "backend");
export const frontendDir = join(rootDir, "frontend-pages");
export const venvDir = join(backendDir, ".venv");

const pythonCandidates = process.platform === "win32"
  ? [["py", ["-3"]], ["python", []], ["python3", []]]
  : [["python3", []], ["python", []]];

export function findPython() {
  if (process.env.PYTHON) {
    return { command: process.env.PYTHON, args: [] };
  }
  for (const [command, args] of pythonCandidates) {
    const result = spawnSync(command, [...args, "--version"], { encoding: "utf8", shell: false });
    if (result.status === 0) {
      return { command, args };
    }
  }
  throw new Error("Python was not found. Install Python 3.11+ and try again.");
}

export function venvPythonPath() {
  return process.platform === "win32"
    ? join(venvDir, "Scripts", "python.exe")
    : join(venvDir, "bin", "python");
}

export function pythonForBackend() {
  const venvPython = venvPythonPath();
  if (existsSync(venvPython)) {
    return { command: venvPython, args: [] };
  }
  return findPython();
}

export function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd || rootDir,
    stdio: "inherit",
    shell: false,
    env: { ...process.env, ...(options.env || {}) }
  });
  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

export function spawnProcess(command, args, options = {}) {
  return spawn(command, args, {
    cwd: options.cwd || rootDir,
    stdio: "inherit",
    shell: false,
    env: { ...process.env, ...(options.env || {}) }
  });
}
