module.exports = {
  apps: [
    {
      name: "rian-fastapi",
      script: "/home/ubuntu/RIAN_project/venv/bin/uvicorn",
      args: "main:app --host 0.0.0.0 --port 8000 --workers 4",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "2G",
      env: {
        DISPLAY: ":99",
        ENVIRONMENT: "production"
      }
    }
  ]
};
