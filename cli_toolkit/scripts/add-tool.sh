#!/bin/bash

echo "🔧 Tool Module Setup for Modular Python Project"

read -p "Enter the name of your main Python package (e.g., chatbot): " package_name
read -p "Enter the name of the new tool (e.g., data, logger, helper): " tool_name

# Validate inputs
if [[ ! "$package_name" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
  echo "❌ Invalid package name."
  exit 1
fi

if [[ ! "$tool_name" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
  echo "❌ Invalid tool name."
  exit 1
fi

base_dir="src/$package_name"
tool_dir="$base_dir/tools/$tool_name"
# Check if the base directory is a valid Python package
if [ ! -d "$base_dir" ] || [ ! -f "$base_dir/__init__.py" ]; then
  echo "❌ The base package directory '$base_dir' is not a valid Python package. Run the setup script first."
  exit 1
fi

# Define the filename for the tool module
tool_file="$tool_dir/${tool_name}_tool.py"

# Create 'tools' folder if missing
if [ ! -d "$tool_dir" ]; then
  echo "➕ Creating missing folder: $tool_dir"
  mkdir -p "$tool_dir"
  touch "$tool_dir/__init__.py"
else
  echo "✅ Folder already exists: $tool_dir"
fi

# Create tool module file
if [ ! -f "$tool_file" ]; then
  echo "➕ Creating tool module: $tool_file"
  touch "$tool_file"
else
  echo "⚠️ Tool module already exists: $tool_file"
fi

# Show updated structure
if command -v tree &> /dev/null; then
  tree "$tool_dir"
else
  echo "(tree not found, using ls -R instead)"
  ls -R "$tool_dir"
fi

echo "✅ Tool module setup complete!"
