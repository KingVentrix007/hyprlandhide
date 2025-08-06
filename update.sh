#!/bin/bash

# Copy source files
cp /mnt/MyCodeProjects/hyprlandhide/{PKGBUILD,LICENSE,min.sh,HyprHideGui.py,config.cfg,min.py} ~/aur-hyprhide/

# Check if the install flag is passed
if [[ "$1" == "--install-release" ]]; then
    COMMIT_MSG="$2"

    # If no commit message is provided
    if [[ -z "$COMMIT_MSG" ]]; then
        echo "❌ Error: Please provide a commit message like:"
        echo "./publish.sh --install-release \"Update for v1.1\""
        exit 1
    fi

    cd ~/aur-hyprhide/ || exit 1

    # Generate .SRCINFO and push
    makepkg --printsrcinfo > .SRCINFO
    git add .
    git commit -m "$COMMIT_MSG"
    git push origin master
fi
