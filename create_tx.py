# create_tx.py (Corrected Version)
import sys
import json
import requests

# Add the 'node' directory to the path, so we can find the 'src' package
sys.path.insert(0, './node')
from src.crypto.wallet import Wallet        # FIXED IMPORT
from src.core.transaction import Transaction  # FIXED IMPORT

# --- PASTE YOUR WALLET DETAILS FROM THE PREVIOUS STEP HERE ---
private_key_hex = "9f7a94a26030ea14e8e731ceaa0d2a719df892708db09d0a0bbb183d33ae5553"
sender_public_key = "0401c3525043dfc24e54f2d641754a8b179fb7d5a537979968fc15993bbc235c593ce56ec7e8c94dd5ec27749a8c21ed5e85e684331e6a84034efcdd63e9a874a7"
# ---

# Create the wallet object to sign with
wallet = Wallet(private_key_bytes=bytes.fromhex(private_key_hex))

# 1. Create the transaction object
tx = Transaction(
    sender=sender_public_key,
    to="0xRECIPIENT_ADDRESS_HERE",
    amount=100,
    nonce=1
)

# 2. Sign the transaction
tx.sign(wallet)

# 3. Get the transaction data as a dictionary
tx_data = tx.to_dict()

print("--- Signed Transaction ---")
print(json.dumps(tx_data, indent=2))

# 4. Send it to a node
node_url = "http://localhost:8001/tx"
print(f"\nSubmitting transaction to {node_url}...")

try:
    response = requests.post(node_url, json=tx_data)
    response.raise_for_status()
    
    print("--- Node Response ---")
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error submitting transaction: {e}")
    print("Response body:", e.response.text if e.response else "No response")