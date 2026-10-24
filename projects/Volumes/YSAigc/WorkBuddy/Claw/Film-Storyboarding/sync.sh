#!/bin/bash
# Auto-sync: copies WorkBuddy skill/expert files → Film-Storyboarding repo → push to GitHub
set -e

REPO_DIR="/Users/zc/WorkBuddy/Film-Storyboarding-repo"
SKILLS_SRC="$HOME/.workbuddy/skills"
EXPERT_SRC="$HOME/.workbuddy/plugins/marketplaces/my-experts/plugins/film-storyboarding"

echo "=== Syncing WorkBuddy → Film-Storyboarding ==="

# Sync skills
echo "[1/3] Syncing skills..."
rsync -a --delete "$SKILLS_SRC/movie-story/" "$REPO_DIR/skills/movie-story/" 2>/dev/null || true
rsync -a --delete "$SKILLS_SRC/ai-video-prompt-expert/" "$REPO_DIR/skills/ai-video-prompt-expert/" 2>/dev/null || true
rsync -a --delete "$SKILLS_SRC/storyboard-generator/" "$REPO_DIR/skills/storyboard-generator/" 2>/dev/null || true
rsync -a --delete "$SKILLS_SRC/aigc-director/" "$REPO_DIR/skills/aigc-director/" 2>/dev/null || true
rsync -a --delete "$SKILLS_SRC/film-storyboard-pro/" "$REPO_DIR/skills/film-storyboard-pro/" 2>/dev/null || true

# Sync expert
echo "[2/3] Syncing expert..."
rsync -a --delete "$EXPERT_SRC/" "$REPO_DIR/experts/film-storyboarding/" 2>/dev/null || true

# Commit & push if changes
cd "$REPO_DIR"
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "[3/3] Changes detected — committing & pushing..."
    git add -A
    git commit -m "sync: auto-update $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "✅ Pushed!"
else
    echo "[3/3] No changes. Skipping push."
fi
