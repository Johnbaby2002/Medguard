import { backendDir, pythonForBackend, run } from "./common.mjs";

const python = pythonForBackend();
run(python.command, [...python.args, "-m", "pytest"], { cwd: backendDir });
