#!/bin/bash

logfile="/tmp/hypr-hide-debug.log"
echo "--- $(date) ---" >> "$logfile"

mkdir -p ~/.local/share/hypr-hide

if ! command -v jq &> /dev/null; then
    echo "ERROR: 'jq' is required but not installed." | tee -a "$logfile"
    exit 1
fi

if ! command -v hyprctl &> /dev/null; then
    echo "ERROR: 'hyprctl' command not found." | tee -a "$logfile"
    exit 1
fi

client=$(hyprctl activewindow -j 2>/dev/null)
echo "Raw client: $client" >> "$logfile"

if [[ -z "$client" || "$client" == "null" ]]; then
    echo "No active window to hide." >> "$logfile"
    exit 1
fi

address=$(echo "$client" | jq -r '.address')
title=$(echo "$client" | jq -r '.title')
x=$(echo "$client" | jq -r '.at[0]')
y=$(echo "$client" | jq -r '.at[1]')
width=$(echo "$client" | jq -r '.size[0]')
height=$(echo "$client" | jq -r '.size[1]')
fullscreen=$(echo "$client" | jq -r '.fullscreen')
floating=$(echo "$client" | jq -r '.floating')

echo "Window info - Address: $address, Title: $title, x=$x y=$y w=$width h=$height fullscreen=$fullscreen floating=$floating" >> "$logfile"

if [[ -z "$address" || "$address" == "null" ]]; then
    echo "No valid window to hide." >> "$logfile"
    exit 1
fi

if [[ "$fullscreen" == "1" ]]; then
    echo "Window is fullscreen, toggling fullscreen off..." >> "$logfile"
    hyprctl dispatch fullscreen "$address" 0
    sleep 0.2
fi

if [[ "$floating" != "true" ]]; then
    echo "Window is not floating, toggling floating ON..." >> "$logfile"
    hyprctl dispatch togglefloating
    # sleep 0.5

    # Check if floating actually toggled
    floating_after=$(hyprctl activewindow -j | jq -r '.floating')
    echo "Floating state after toggle: $floating_after" >> "$logfile"

    if [[ "$floating_after" != "true" ]]; then
        echo "Floating not toggled ON, trying toggle again..." >> "$logfile"
        hyprctl dispatch togglefloating "$address"
        sleep 0.5
        floating_after=$(hyprctl activewindow -j | jq -r '.floating')
        echo "Floating state after second toggle: $floating_after" >> "$logfile"
    fi
fi

# Save window info for restore
echo "$client" > ~/.local/share/hypr-hide/"$address".json

# Move window offscreen
hyprctl dispatch moveactive 5000 5000
echo "Moved window offscreen." >> "$logfile"


# Confirm new position and floating state
after_move=$(hyprctl clients -j | jq -r --arg addr "$address" '.[] | select(.address==$addr) | {at, fullscreen, floating}')
echo "After move: $after_move" >> "$logfile"
