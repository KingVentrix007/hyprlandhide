#!/bin/bash

logfile="/tmp/hypr-hide-debug.log"
echo "--- $(date) RESTORE ---" >> "$logfile"

HIDE_DIR="$HOME/.local/share/hypr-hide"
mkdir -p "$HIDE_DIR"

# Loop through all hidden windows
for file in "$HIDE_DIR"/*.json; do
    [[ -e "$file" ]] || continue

    echo "Restoring $file" >> "$logfile"
    client=$(cat "$file")
    address=$(echo "$client" | jq -r '.address')
    title=$(echo "$client" | jq -r '.title')
    x=$(echo "$client" | jq -r '.at[0]')
    y=$(echo "$client" | jq -r '.at[1]')
    floating=$(echo "$client" | jq -r '.floating')

    # Switch to the workspace (safety)
    workspace=$(echo "$client" | jq -r '.workspace.name')
    echo "Switching to workspace $workspace for $title ($address)" >> "$logfile"
    hyprctl dispatch workspace "$workspace"
    sleep 0.2

    # Focus the window to make it "active" again
    echo "Focusing window $address" >> "$logfile"
    hyprctl dispatch focuswindow address:$address
    sleep 0.2

    # Ensure it's floating before moving
    if [[ "$floating" != "true" ]]; then
        echo "Setting window $address to floating" >> "$logfile"
        hyprctl dispatch togglefloating address:$address
        sleep 0.2
    fi

    # Move the window back to saved coordinates
    echo "Moving window $address to $x,$y" >> "$logfile"
    hyprctl dispatch movewindowpixel address:$address "$x" "$y"
    sleep 0.2

    # Cleanup
    rm -f "$file"
done
