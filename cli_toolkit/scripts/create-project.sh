#!/bin/bash

echo "🚀 Modular Python Project Setup"

read -p "Enter the name of your main Python package (e.g., chatbot): " package_name

# Validate package name
if [[ ! "$package_name" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
  echo "❌ Invalid package name. Use only letters, numbers, and underscores, starting with a letter."
  exit 1
fi

# Check for existing project structure
if [ -d "src" ] || [ -d "tests" ] || [ -f "setup.py" ]; then
  echo "⚠️ Warning: Some project files already exist. This might cause conflicts."
  read -p "Continue anyway? (y/n): " continue_setup
  if [[ ! "$continue_setup" =~ ^[Yy]$ ]]; then
    echo "Setup canceled."
    exit 0
  fi
fi

# Create src directory and module structure
mkdir -p "src/$package_name/core"
mkdir -p "src/$package_name/api"
mkdir -p "src/$package_name/ui"
mkdir -p tests

# Create empty __init__.py files for Python packages
touch "src/__init__.py"
touch "src/$package_name/__init__.py"
touch "src/$package_name/core/__init__.py"
touch "src/$package_name/api/__init__.py"
touch "src/$package_name/ui/__init__.py"

# Create empty module files with package name
touch "src/$package_name/core/${package_name}_core.py"
touch "src/$package_name/api/${package_name}_api.py"
touch "src/$package_name/ui/${package_name}_ui.py"

# Create basic run.py file
touch "run.py"

# Add version file
echo "0.1.0" > version.txt

# Create .gitignore
cat <<EOF > .gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/
.idea/
.vscode/
EOF

# Create empty setup.py
touch setup.py

# Create requirements.txt with basic dependencies
cat <<EOF > requirements.txt
fastapi>=0.95.0
uvicorn>=0.21.0
streamlit>=1.22.0
requests>=2.28.0
pydantic>=1.10.0
EOF

# Create empty README.md
cat <<EOF > README.md
# $package_name

A modular Python application.

## Project Structure

\`\`\`
src/
└── $package_name/
    ├── core/
    │   └── ${package_name}_core.py
    ├── api/
    │   └── ${package_name}_api.py
    └── ui/
        └── ${package_name}_ui.py
\`\`\`

## Setup

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Running the Application

\`\`\`bash
python run.py
\`\`\`
EOF

echo "📁 Project structure created!"

# Validate the setup
echo "🔍 Validating project structure..."
validation_errors=0

# Check required files
required_files=("setup.py" "requirements.txt" "README.md" "run.py")
for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "❌ Missing required file: $file"
    validation_errors=$((validation_errors + 1))
  fi
done

# Check required directories
required_dirs=("src" "tests" "src/$package_name" "src/$package_name/core" "src/$package_name/api" "src/$package_name/ui")
for dir in "${required_dirs[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "❌ Missing required directory: $dir"
    validation_errors=$((validation_errors + 1))
  fi
done

# Check required module files
required_modules=("src/$package_name/core/${package_name}_core.py" "src/$package_name/api/${package_name}_api.py" "src/$package_name/ui/${package_name}_ui.py")
for module in "${required_modules[@]}"; do
  if [ ! -f "$module" ]; then
    echo "❌ Missing required module: $module"
    validation_errors=$((validation_errors + 1))
  fi
done

# Show structure if tree is installed, else fallback to ls
if command -v tree &> /dev/null; then
  tree -I '__pycache__|*.pyc|*.egg-info|venv|env|.git'
else
  echo "(tree not found, using ls -R instead)"
  ls -R
fi

if [ $validation_errors -gt 0 ]; then
  echo "⚠️ Found $validation_errors issues with the project structure."
else
  echo "✅ Project structure validation passed!"
fi

echo ""
echo "✨ Your modular package '$package_name' is ready! ✨"
echo ""
echo "Next steps:"
echo "1. Update setup.py with your project details"
echo "2. Implement your code in src/$package_name/"
echo "3. Run your application with 'python run.py'"
echo ""
echo "For imports between components use:"
echo "from src.$package_name.core.${package_name}_core import YourClass"