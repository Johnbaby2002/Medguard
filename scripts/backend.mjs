import { existsSync, copyFileSync } from "node:fs";
import { join } from "node:path";
import { backendDir, pythonForBackend, run } from "./common.mjs";

const envPath = join(backendDir, ".env");
const sqliteExamplePath = join(backendDir, ".env.sqlite.example");

if (!existsSync(envPath) && existsSync(sqliteExamplePath)) {
  copyFileSync(sqliteExamplePath, envPath);
}

const python = pythonForBackend();
run(python.command, [...python.args, "dev.py"], { cwd: backendDir });
