#!/bin/bash

# update-fork.sh — safely sync your fork with upstream and rebase branches
set -e

GIT_ROOT="$(git rev-parse --show-toplevel)"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

if [[ -n $(git -C "$GIT_ROOT" diff --name-only --diff-filter=U) ]]; then
    echo -e "${RED}❗ You have unresolved merge conflicts. Please resolve them first.${NC}"
    git -C "$GIT_ROOT" status
    read -r -p "Auto-resolve by keeping local changes? (y/n): " auto_resolve
    if [[ "$auto_resolve" == "y" ]]; then
        conflicted_files=$(git -C "$GIT_ROOT" diff --name-only --diff-filter=U)
        for file in $conflicted_files; do
            if [[ -e "$GIT_ROOT/$file" ]]; then
                git -C "$GIT_ROOT" checkout --ours -- "$file" || git -C "$GIT_ROOT" restore --source=HEAD -- "$file"
                git -C "$GIT_ROOT" add "$file"
            else
                echo -e "${YELLOW}⚠️  Skipping '$file' – not found locally.${NC}"
            fi
        done
        git -C "$GIT_ROOT" commit -m "Auto-resolved merge conflicts by keeping local changes"
    else
        echo -e "${YELLOW}Resolve conflicts manually and rerun.${NC}"
        exit 1
    fi
fi

if git -C "$GIT_ROOT" remote get-url upstream &>/dev/null; then
    echo -e "${GREEN}🔄 Fetching updates from upstream...${NC}"
    git -C "$GIT_ROOT" fetch upstream
else
    echo -e "${YELLOW}⚠️  No 'upstream' remote configured.${NC}"
    read -p "Skip upstream merge and continue? (y/n): " skip_upstream
    if [[ "$skip_upstream" != "y" ]]; then
        echo "Configure it with: git remote add upstream <url>"
        exit 1
    fi
    skip_upstream_merge=true
fi

read -p "Check for deleted files tracked in 'main'? (y/n): " check_moved
if [[ "$check_moved" == "y" ]]; then
    deleted_files=$(git -C "$GIT_ROOT" ls-files --deleted)
    if [[ -n "$deleted_files" ]]; then
        echo -e "${YELLOW}Deleted files:${NC}\n$deleted_files"
        read -p "Remove from Git tracking? (y/n): " confirm_rm
        if [[ "$confirm_rm" == "y" ]]; then
            echo "$deleted_files" | xargs -I{} git -C "$GIT_ROOT" rm "{}"
            git -C "$GIT_ROOT" commit -m "Remove deleted files from main"
        fi
    fi
fi

git -C "$GIT_ROOT" checkout main

if [[ "$skip_upstream_merge" != "true" ]]; then
    echo -e "${GREEN}🔗 Merging upstream/main into local main...${NC}"
    git -C "$GIT_ROOT" merge upstream/main
fi

if [[ -n $(git -C "$GIT_ROOT" diff --name-only --diff-filter=U) ]]; then
    echo -e "${RED}❗ Conflicts during merge. Resolve them manually.${NC}"
    exit 1
fi

git -C "$GIT_ROOT" push origin main || {
    echo -e "${YELLOW}Push to origin failed. Choose an option:${NC}"
    echo "1) Pull and merge remote changes"
    echo "2) Force-push local main"
    echo "3) Abort"
    read -p "Enter option [1-3]: " push_choice
    case $push_choice in
        1) git -C "$GIT_ROOT" pull --no-rebase; git -C "$GIT_ROOT" push origin main ;;
        2) git -C "$GIT_ROOT" push --force-with-lease origin main ;;
        *) echo "Aborted."; exit 1 ;;
    esac
}

echo -e "${YELLOW}📂 Listing branches...${NC}"
git -C "$GIT_ROOT" branch
read -p "Update a feature branch? (y/n): " update_branch
if [[ "$update_branch" == "y" ]]; then
    read -p "Enter feature branch name: " branch
    git -C "$GIT_ROOT" checkout "$branch"
    divergence=$(git -C "$GIT_ROOT" rev-list --left-right --count origin/$branch...$branch)
    local_ahead=$(echo $divergence | awk '{print $2}')
    remote_ahead=$(echo $divergence | awk '{print $1}')
    if [[ "$local_ahead" -gt 0 && "$remote_ahead" -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  Diverged from origin/$branch. Choose an action:${NC}"
        echo "1) Force-push local"
        echo "2) Merge remote"
        echo "3) Show graph"
        echo "4) Abort"
        read -p "Enter option [1-4]: " choice
        case $choice in
            1) git -C "$GIT_ROOT" push --force-with-lease ;;
            2) git -C "$GIT_ROOT" pull --no-rebase ;;
            3) git -C "$GIT_ROOT" log --oneline --graph --all --decorate --color; exit 1 ;;
            *) echo "Aborted."; exit 1 ;;
        esac
    fi
    echo -e "${YELLOW}📌 Rebasing onto main...${NC}"
    git -C "$GIT_ROOT" rebase -X theirs main || {
        echo -e "${RED}⚠️  Conflicts during rebase.${NC}"
        read -p "Auto-resolve in favor of local? (y/n): " resolve_choice
        if [[ "$resolve_choice" == "y" ]]; then
            conflicted_files=$(git -C "$GIT_ROOT" diff --name-only --diff-filter=U)
            for file in $conflicted_files; do
                if [[ -e "$GIT_ROOT/$file" ]]; then
                    git -C "$GIT_ROOT" checkout --ours -- "$file" || git -C "$GIT_ROOT" restore --source=HEAD -- "$file"
                    git -C "$GIT_ROOT" add "$file"
                elif git -C "$GIT_ROOT" ls-files --stage | grep -q "$file"; then
                    git -C "$GIT_ROOT" rm "$file" || true
                fi
            done
            git -C "$GIT_ROOT" rebase --continue
        else
            echo -e "${YELLOW}Resolve conflicts manually then run: git rebase --continue${NC}"
            exit 1
        fi
    }
    echo -e "${GREEN}✅ Feature branch rebased!${NC}"
else
    echo -e "${GREEN}👍 Main branch updated!${NC}"
fi
