#!/bin/bash

# Copy source files
cp /mnt/MyCodeProjects/hyprlandhide/{PKGBUILD,LICENSE,min.sh,HyprHideGui.py,hyprland_interface,HyprHideDev.py,config.cfg,min.py,version.txt} ~/aur-hyprhide/

# Replace pkgver in PKGBUILD with version.txt
VERSION=$(< /mnt/MyCodeProjects/hyprlandhide/version.txt)
sed -i "s/^pkgver=.*/pkgver=$VERSION/" ~/aur-hyprhide/PKGBUILD

# Check if the install flag is passed
if [[ "$1" == "--install-release" ]]; then
    COMMIT_MSG="$2"

    if [[ -z "$COMMIT_MSG" ]]; then
        echo "❌ Error: Please provide a commit message like:"
        echo "./publish.sh --install-release \"Update for v$VERSION\""
        exit 1
    fi

    cd ~/aur-hyprhide/ || exit 1

    # Generate .SRCINFO and push
    makepkg --printsrcinfo > .SRCINFO
    git add .
    git commit -m "$COMMIT_MSG"
    git push origin master
fi
