import hashlib
import json
import time
import uuid

class Block:
    """A single block in the blockchain."""
    def __init__(self, index, transactions, timestamp, previous_hash, proof):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.proof = proof
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculates the unique hash for the block."""
        transactions_data = []
        for t in self.transactions:
            if isinstance(t, SmartContractTransaction):
                transactions_data.append({
                    "type": "smart_contract",
                    "sender_address": t.sender_address,
                    "function_name": t.function_name,
                    "arguments": t.arguments
                })
            else:
                transactions_data.append(t.__dict__)

        block_data = {
            "index": self.index,
            "transactions": transactions_data,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "proof": self.proof
        }
        
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Transaction:
    """A single transaction record."""
    def __init__(self, sender_address, recipient_address, amount):
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.amount = amount

class SmartContractTransaction(Transaction):
    """A transaction that triggers a smart contract function."""
    def __init__(self, sender_address, function_name, arguments):
        super().__init__(sender_address, "smart_contract_address", 0)
        self.function_name = function_name
        self.arguments = arguments

class Wallet:
    """A simple wallet to generate a unique address."""
    def __init__(self):
        self.address = str(uuid.uuid4()).replace('-', '')

class Blockchain:
    """The main blockchain class."""
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.world_state = {}  # The "database" for smart contracts
        self.create_genesis_block(proof=100)

    def create_genesis_block(self, proof):
        """Creates the very first block in the blockchain."""
        genesis_block = Block(0, [], time.time(), "0", proof)
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """Returns the last block in the chain."""
        return self.chain[-1]

    def add_transaction(self, transaction):
        """Adds a new transaction to the current list of transactions."""
        self.current_transactions.append(transaction)
        
        # If the transaction is a smart contract call, execute it immediately
        if isinstance(transaction, SmartContractTransaction):
            self.execute_smart_contract(transaction)

    def proof_of_work(self, last_block_hash):
        """Simple Proof of Work Algorithm."""
        proof = 0
        while not self.valid_proof(last_block_hash, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_block_hash, proof):
        """Validates the proof: Does the hash start with 4 leading zeros?"""
        guess = f'{last_block_hash}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def mine_block(self):
        """Mines a new block by finding the Proof of Work."""
        new_block_transactions = self.current_transactions
        
        last_block = self.last_block
        last_block_hash = last_block.hash

        proof = self.proof_of_work(last_block_hash)

        new_block = Block(len(self.chain), new_block_transactions, time.time(), last_block_hash, proof)
        self.chain.append(new_block)

        self.current_transactions = []
        return new_block

    def execute_smart_contract(self, transaction):
        """Executes a smart contract transaction and updates the world state."""
        if transaction.function_name == "createShipment":
            shipment_id = transaction.arguments.get('shipmentID')
            product_details = transaction.arguments.get('productDetails')
            
            if shipment_id not in self.world_state:
                self.world_state[shipment_id] = {
                    "status": "Created",
                    "product_details": product_details,
                    "custodian": transaction.sender_address,
                    "temp_logs": [],
                    "max_temp_limit": 8,
                    "min_temp_limit": 2
                }
                print(f"Smart Contract Executed: Shipment '{shipment_id}' created by {transaction.sender_address}.")
            else:
                print(f"Error: Shipment '{shipment_id}' already exists.")

        elif transaction.function_name == "updateTemperature":
            shipment_id = transaction.arguments.get('shipmentID')
            temp = transaction.arguments.get('currentTemp')
            
            if shipment_id in self.world_state:
                self.world_state[shipment_id]["temp_logs"].append(temp)
                
                if temp > self.world_state[shipment_id]["max_temp_limit"] or temp < self.world_state[shipment_id]["min_temp_limit"]:
                    if self.world_state[shipment_id]["status"] != "Compromised":
                        self.world_state[shipment_id]["status"] = "Compromised"
                        print(f"Smart Contract Executed: Shipment '{shipment_id}' COMPROMISED due to temperature breach!")
                print(f"Smart Contract Executed: Temperature for '{shipment_id}' updated to {temp}.")
            else:
                print(f"Error: Shipment '{shipment_id}' not found.")
        
        elif transaction.function_name == "transferCustody":
            shipment_id = transaction.arguments.get('shipmentID')
            new_custodian = transaction.arguments.get('newCustodian')

            if shipment_id in self.world_state:
                shipment = self.world_state[shipment_id]
                if shipment["status"] == "Compromised":
                    print(f"Error: Cannot transfer '{shipment_id}'. It's compromised.")
                else:
                    shipment["custodian"] = new_custodian
                    shipment["status"] = "In-Transit"
                    print(f"Smart Contract Executed: Custody for '{shipment_id}' transferred to {new_custodian}.")
            else:
                print(f"Error: Shipment '{shipment_id}' not found.")


# --- Demonstration of the Blockchain ---

# Create a new blockchain instance
my_blockchain = Blockchain()

# Create wallets for users
wallet_manufacturer = Wallet()
wallet_logistics = Wallet()
wallet_pharmacy = Wallet()
wallet_iot_oracle = Wallet()

print("Manufacturer Address:", wallet_manufacturer.address)
print("Logistics Address:", wallet_logistics.address)
print("Pharmacy Address:", wallet_pharmacy.address)
print("IoT Oracle Address:", wallet_iot_oracle.address)
print("\n")

# --- Demo: Create a new shipment (Success Case) ---
print("--- Creating a New Shipment ---")
tx_create = SmartContractTransaction(
    sender_address=wallet_manufacturer.address,
    function_name="createShipment",
    arguments={"shipmentID": "COVID_VACCINE_1", "productDetails": "Pfizer Vax"}
)
my_blockchain.add_transaction(tx_create)
mined_block_1 = my_blockchain.mine_block()
print("\n")

# --- Demo: Simulate temperature logs (Success and Failure) ---
print("--- Simulating IoT Temperature Data ---")
tx_temp_normal = SmartContractTransaction(
    sender_address=wallet_iot_oracle.address,
    function_name="updateTemperature",
    arguments={"shipmentID": "COVID_VACCINE_1", "currentTemp": 5} # 5C is within range (2-8)
)
my_blockchain.add_transaction(tx_temp_normal)
mined_block_2 = my_blockchain.mine_block()
print("\n")

tx_temp_breach = SmartContractTransaction(
    sender_address=wallet_iot_oracle.address,
    function_name="updateTemperature",
    arguments={"shipmentID": "COVID_VACCINE_1", "currentTemp": 9.5} # 9.5C is a breach
)
my_blockchain.add_transaction(tx_temp_breach)
mined_block_3 = my_blockchain.mine_block()
print("\n")

# --- Demo: Attempt to transfer a compromised shipment (Failure Case) ---
print("--- Attempting to Transfer a Compromised Shipment ---")
tx_transfer = SmartContractTransaction(
    sender_address=wallet_logistics.address,
    function_name="transferCustody",
    arguments={"shipmentID": "COVID_VACCINE_1", "newCustodian": wallet_pharmacy.address}
)
my_blockchain.add_transaction(tx_transfer)
mined_block_4 = my_blockchain.mine_block()
print("\n")

# --- Print the World State and Final Blockchain ---
print("--- Final World State ---")
print(json.dumps(my_blockchain.world_state, indent=4, sort_keys=True))
print("\n")

print("--- Final Blockchain ---")
for block in my_blockchain.chain:
    block_to_print = block.__dict__.copy()
    block_to_print['transactions'] = [t.__dict__ for t in block_to_print['transactions']]
    print(json.dumps(block_to_print, indent=4, sort_keys=True))
    