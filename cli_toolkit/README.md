# CLI Toolkit for Modular Python Projects

This CLI toolkit helps you scaffold and manage modular Python projects using a simple command-line interface.

## 📦 Installation

Unzip the toolkit into the root of your project:

```bash
unzip cli_toolkit.zip
cd cli_toolkit
chmod +x manage.sh scripts/*.sh
```

## 🚀 Usage

Run the CLI via the `manage.sh` script:

```bash
./manage.sh [command]
```

### Available Commands

| Command        | Description                                                   |
|----------------|---------------------------------------------------------------|
| `create`       | Scaffold a new modular Python project structure               |
| `add-tool`     | Add a new tool module to your project                         |
| `version-bump` | Bump project version, update `__version__`, commit, and tag   |
| `update-fork`  | Sync your local fork with the upstream repo and rebase branches |

## 📁 Project Structure Example

```
cli_toolkit/
├── manage.sh
└── scripts/
    ├── add-tool.sh
    ├── create-project.sh
    ├── update-fork.sh
    └── version-bump.sh
```

## 🧠 Tips

- Make sure you're in a clean git state before using `version-bump` or `update-fork`.
- You can extend this toolkit by adding more scripts to `scripts/` and wiring them in `manage.sh`.

Enjoy building!


Version 4

Both scripts have been refactored for robust path management:

✅ Refactored Scripts (Now Using GIT_ROOT Instead of cd)
version_bump_refactored

update_fork_refactored

Each script:

Dynamically detects the Git root using git rev-parse --show-toplevel.

Avoids changing directories globally.

Uses absolute paths for file access and Git operations.

This ensures they play nicely with your manage.sh structure and won’t break if run from different working directories.