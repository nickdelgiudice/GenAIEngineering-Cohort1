# Running FastAPI and Streamlit Services

This guide provides commands to start a FastAPI service and run a Streamlit application.

## Starting a FastAPI Service

FastAPI is a modern, high-performance web framework for building APIs. It's typically run with Uvicorn:

```bash
# Make sure you are in your activated virtual environment

# Basic run command
uvicorn main:app --reload

# With custom host and port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# If your FastAPI app is in a different file or uses a different variable
uvicorn your_file:your_app_variable --reload

# Running in production mode (without reload)
uvicorn main:app --workers 4
```

## Running a Streamlit Application

Streamlit is an open-source Python library that makes it easy to create web apps:

```bash
# Make sure you are in your activated virtual environment

# Basic command to run a Streamlit app
streamlit run app.py

# With custom server port
streamlit run app.py --server.port 8501

# With custom server address
streamlit run app.py --server.address 0.0.0.0

# Running with custom theme
streamlit run app.py --theme.primaryColor "#F63366"

# Running without opening browser automatically
streamlit run app.py --server.headless true
```

## Running Both Services Together

You may need to run both the FastAPI and Streamlit app concurrently. Here are some options:

### Using Multiple Terminal Windows

The simplest approach is to use separate terminal windows:

1. Terminal 1: Start your FastAPI service
2. Terminal 2: Start your Streamlit app

### Running Services in Background

#### Linux/macOS

You can run processes in the background using the `&` operator:

```bash
# Start FastAPI in the background
uvicorn main:app --reload &
# Note the process ID (PID) that is displayed

# Start Streamlit in the background
streamlit run app.py &
# Note the process ID (PID) that is displayed
```

To bring a background process to the foreground:

```bash
# Replace 1234 with the actual PID
fg %1234
```

#### Windows

You can use the `start` command to run processes in a new window:

```bash
# Start FastAPI in a new window
start cmd /k "uvicorn main:app --reload"

# Start Streamlit in a new window
start cmd /k "streamlit run app.py"
```

### Using nohup (Linux/macOS)

For keeping processes running even after closing the terminal:

```bash
# Run FastAPI with nohup
nohup uvicorn main:app --reload > fastapi.log 2>&1 &

# Run Streamlit with nohup
nohup streamlit run app.py > streamlit.log 2>&1 &
```

## Checking if Services are Running

### Checking Process Status

#### Linux/macOS

```bash
# List all Python processes
ps aux | grep python

# Find specific processes
ps aux | grep uvicorn
ps aux | grep streamlit

# Get the status of a specific process by PID
ps -p 1234 # Replace 1234 with the actual PID
```

#### Windows

```bash
# List all running processes
tasklist | findstr python

# Find specific processes
tasklist | findstr uvicorn
tasklist | findstr streamlit
```

### Checking Network Services

Check if services are listening on their expected ports:

```bash
# Linux/macOS
netstat -tuln | grep 8000  # For FastAPI default port
netstat -tuln | grep 8501  # For Streamlit default port

# Windows
netstat -an | findstr 8000  # For FastAPI default port
netstat -an | findstr 8501  # For Streamlit default port
```

### Testing Service Availability

```bash
# Test FastAPI (Linux/macOS/Windows)
curl http://localhost:8000

# Open in browser
# FastAPI: http://localhost:8000
# FastAPI Docs: http://localhost:8000/docs
# Streamlit: http://localhost:8501
```

## Accessing Your Services

Once running, you can access your services at:

- API service: http://localhost:5000 (Flask) or http://localhost:8000 (FastAPI)
- Streamlit app: http://localhost:8501

## Stopping the Services

### Stopping Foreground Processes

- For terminal processes running in the foreground: Press `Ctrl+C` in the respective terminal

### Stopping Background Processes

#### Linux/macOS

```bash
# Kill process by PID
kill 1234  # Replace 1234 with the actual PID

# Kill process more forcefully if needed
kill -9 1234  # Replace 1234 with the actual PID

# Kill all uvicorn processes
pkill -f uvicorn

# Kill all streamlit processes
pkill -f streamlit
```

#### Windows

```bash
# Kill process by PID
taskkill /PID 1234  # Replace 1234 with the actual PID

# Kill process forcefully
taskkill /F /PID 1234  # Replace 1234 with the actual PID

# Kill by process name
taskkill /IM uvicorn.exe
taskkill /IM streamlit.exe
```

### Verifying Services Are Stopped

After stopping a service, you can verify it's no longer running using the same commands from the "Checking if Services are Running" section:

```bash
# Linux/macOS
ps aux | grep uvicorn
ps aux | grep streamlit

# Windows
tasklist | findstr uvicorn
tasklist | findstr streamlit
```
