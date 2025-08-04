address="0x55610a873ba0"
output="/home/tristank/.local/share/hypr-hide/${address}.png"

# Get window info JSON
clients_json=$(hyprctl clients -j)

# Extract geometry (x, y, width, height) for window by address
x=$(echo "$clients_json" | jq -r ".[] | select(.address==\"$address\") | .at[0]")
y=$(echo "$clients_json" | jq -r ".[] | select(.address==\"$address\") | .at[1]")
w=$(echo "$clients_json" | jq -r ".[] | select(.address==\"$address\") | .size[0]")
h=$(echo "$clients_json" | jq -r ".[] | select(.address==\"$address\") | .size[1]")

if [[ -z "$x" || -z "$y" || -z "$w" || -z "$h" ]]; then
  echo "Window $address not found or missing geometry"
  exit 1
fi

echo "Focusing window $address..."
hyprctl dispatch focuswindow address:$address

# Wait a bit for focus
sleep 0.1

echo "Taking screenshot at geometry: $x,$y ${w}x${h}"
grim -g "${x},${y} ${w}x${h}" "$output"

echo "Screenshot saved to $output"

# Optional: move window offscreen after to avoid interfering
# hyprctl dispatch movewindow address:$address 9999 9999
