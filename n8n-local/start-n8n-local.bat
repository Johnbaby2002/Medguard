@echo off
setlocal

set "N8N_TEMPLATES_ENABLED=true"
set "N8N_TEMPLATES_HOST=https://api.n8n.io/api/"
set "N8N_DYNAMIC_TEMPLATES_HOST=https://dynamic-templates.n8n.io/templates"
set "N8N_URL=http://localhost:5678"

echo Starting local n8n with templates enabled...
start "" "%N8N_URL%"
n8n

endlocal
