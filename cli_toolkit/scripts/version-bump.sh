#!/bin/bash

# version-bump.sh — safe version updater with dynamic paths
set -e

GIT_ROOT="$(git rev-parse --show-toplevel)"
VERSION_FILE="$GIT_ROOT/version.txt"

# Prompt for package name to dynamically build paths
read -p "Enter your main package name (e.g., chatbot): " package_name
PACKAGE_PATHS=(
  "$GIT_ROOT/src/$package_name/core/__init__.py"
  "$GIT_ROOT/src/$package_name/api/__init__.py"
  "$GIT_ROOT/src/$package_name/ui/__init__.py"
)

echo "🔍 Checking pre-requisites..."

if [ ! -d "$GIT_ROOT/.git" ]; then
  echo "❌ Not a Git repository."
  exit 1
fi

if [ ! -f "$VERSION_FILE" ]; then
  echo "❌ $VERSION_FILE not found."
  exit 1
fi

for path in "${PACKAGE_PATHS[@]}"; do
  if [ ! -f "$path" ]; then
    echo "❌ $path not found."
    exit 1
  fi
done

cd "$GIT_ROOT"
branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" != "main" ]; then
  echo "❌ Must be on 'main' branch. Current: $branch"
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Working directory is not clean."
  exit 1
fi

current_version=$(cat "$VERSION_FILE")
echo "✅ Current version: $current_version"

read -p "Enter the new version (e.g., 1.2.3): " new_version
if [[ ! $new_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "❌ Invalid version format."
  exit 1
fi

if git rev-parse "v$new_version" >/dev/null 2>&1; then
  echo "⚠️  Tag v$new_version already exists."
  read -p "Do you want to rollback and replace it? [y/N] " confirm_rollback
  if [[ "$confirm_rollback" != "y" && "$confirm_rollback" != "Y" ]]; then
    echo "❌ Aborted to prevent tag conflict."
    exit 1
  fi
  git tag -d "v$new_version" || true
  git push --delete origin "v$new_version" || true
fi

echo "$new_version" > "$VERSION_FILE"

for path in "${PACKAGE_PATHS[@]}"; do
  if grep -q "^__version__" "$path"; then
    sed -i.bak -E "s/^(__version__ *= *[\"'])[0-9]+\.[0-9]+\.[0-9]+([\"'])/\1$new_version\2/" "$path"
  else
    echo -e "\n__version__ = \"$new_version\"" >> "$path"
  fi
  rm -f "${path}.bak"
done

git add "$VERSION_FILE" "${PACKAGE_PATHS[@]}"
git commit -m "🔖 Bump version to $new_version"
git tag -a "v$new_version" -m "Release version $new_version"
git push origin main
git push origin "v$new_version"

echo "🎉 Version $new_version updated, committed, tagged, and pushed!"
