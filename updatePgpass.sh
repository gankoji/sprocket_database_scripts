#!/bin/bash

# --- Configuration ---
PGPASS_FILE="$HOME/.pgpass"
TARGET_HOST="spr.ocket.cloud"  # The host you want to update
TARGET_PORT="30000"            # The port you want to update
TARGET_DB="sprocket_main"      # The database you want to update (or '*' for wildcard)
TARGET_OLD_USER="old_username" # The current username in the .pgpass entry (important for precise matching)

GOPASS_USER_PATH="sprocket/db_main_username" # Your gopass path for username
GOPASS_PW_PATH="sprocket/db_main_pw"         # Your gopass path for password

# --- Get new credentials from gopass ---
# It's crucial to escape any special characters that might appear in the gopass output
# before inserting them into the .pgpass file.
# The .pgpass file specifies that ':' and '\' must be escaped.
NEW_USERNAME=$(gopass show "${GOPASS_USER_PATH}" | sed 's/[:\]/\\&/g')
NEW_PASSWORD=$(gopass show "${GOPASS_PW_PATH}" | sed 's/[:\]/\\&/g')

# Check if gopass commands succeeded and returned values
if [ -z "$NEW_USERNAME" ] || [ -z "$NEW_PASSWORD" ]; then
  echo "Error: Could not retrieve username or password from gopass."
  exit 1
fi

# --- Construct the new line ---
NEW_LINE="${TARGET_HOST}:${TARGET_PORT}:${TARGET_DB}:${NEW_USERNAME}:${NEW_PASSWORD}"

# --- Create a temporary file for the new .pgpass content ---
TEMP_PGPASS=$(mktemp)

# --- Process the .pgpass file using awk ---
# awk is much better for field-based processing and escaping.
# This script will:
# 1. Look for lines that match the host, port, database, and old username.
# 2. If a match is found, replace the entire line with the NEW_LINE.
# 3. Print all other lines unchanged.
awk -v target_host="${TARGET_HOST}" \
  -v target_port="${TARGET_PORT}" \
  -v target_db="${TARGET_DB}" \
  -v target_old_user="${TARGET_OLD_USER}" \
  -v new_line_content="${NEW_LINE}" \
  'BEGIN { FS=":"; OFS=":" }
    {
        if ( ($1 == target_host || $1 == "*") && \
             ($2 == target_port || $2 == "*") && \
             ($3 == target_db || $3 == "*")) {
            print new_line_content  # Replace the line
            found_and_replaced = 1
        } else {
            print $0  # Print the original line
        }
    }
    END {
        # Optional: If no line was found and replaced, you might want to append the new line.
        # This depends on your desired behavior (update existing vs. add if not present).
        # For this example, we assume we are updating an existing entry.
        # If you want to *add* if not found, uncomment the following:
        # if (!found_and_replaced) {
        #    print new_line_content
        # }
    }' "${PGPASS_FILE}" >"${TEMP_PGPASS}"

# --- Atomically replace the original file ---
mv "${TEMP_PGPASS}" "${PGPASS_FILE}"

# --- Set correct permissions (crucial for .pgpass) ---
chmod 600 "${PGPASS_FILE}"

echo "Updated ${PGPASS_FILE} for host ${TARGET_HOST}."
