# This code is a modified version of the original repository:
# https://github.com/vkamppp/R2-Testnet
# Modifications made by [Your GitHub Username]
# Date of modification: June 8, 2025
# This version supports multiple chain selection but executes transactions ONLY on BSC Testnet.

import time
import json
from decimal import Decimal
from web3 import Web3
from eth_abi import encode
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
console.print(Panel.fit(
    "[bold cyan]🚀 R2 Testnet Auto\n[green]By ADFMIND TEAM[/green]\n[link=https://t.me/AirdropFamilyIDN]Join Telegram[/link]",
    title="🔥 Welcome",
    subtitle="Testnet Tools"))

# --- Load all network configurations from the file ---
with open("network_config.json") as f:
    network_configs_all = json.load(f)['networks'] # Load the 'networks' object

console.print("\n[bold blue]Pilih jaringan yang akan digunakan:[/bold blue]")
network_keys = list(network_configs_all.keys())
for i, net_key in enumerate(network_keys):
    console.print(f"[{i}] {network_configs_all[net_key]['name']}")

selected_index = int(console.input("\n[bold green]Masukkan nomor jaringan: [/bold green]"))

# Get the key for the selected network
selected_network_key = network_keys[selected_index]
# Get the full configuration for the selected network
netconf = network_configs_all[selected_network_key]

web3 = Web3(Web3.HTTPProvider(netconf["rpcUrl"]))
chainId = netconf["chainId"]

if web3.is_connected():
    console.print(f"✅ [green]Connected to {netconf['name']}[/green]\n")
else:
    console.print(f"❌ [red]Gagal konek ke jaringan {netconf['name']}[/red]")
    exit()

# --- Load Token ABI ---
with open("tokenabi.json") as f:
    tokenabi = json.load(f)

# --- Helper Functions (No change here) ---
def getNonce(sender): return int(web3.eth.get_transaction_count(sender))
def getgasPrice(): return int(web3.eth.gas_price * Decimal(1.1))

def show_status(title, sender, target, status, tx=None):
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("From", justify="center")
    table.add_column("To", justify="center")
    table.add_column("Status", justify="center")
    if tx:
        table.add_column("TX-ID", justify="center")
    row = [sender[-6:], target[-6:], status]
    if tx:
        row.append(tx)
    table.add_row(*row)
    console.print(table)

def apprvCheck(tokenaddr, sender, targetaddr):
    contract = web3.eth.contract(address=tokenaddr, abi=tokenabi)
    return contract.functions.allowance(sender, targetaddr).call()

def approveTokens(tokenaddr, targetaddr, sender, senderkey):
    try:
        token_contract = web3.eth.contract(address=tokenaddr, abi=tokenabi)
        try:
            gas_limit = token_contract.functions.approve(targetaddr, 2**256 - 1).estimate_gas({'from': sender})
        except Exception as e:
            console.print(f"[yellow]Warning: Could not estimate gas for approval, using default (e.g., 100000). Error: {e}[/yellow]")
            gas_limit = 100000 # Fallback gas limit

        approve_tx = token_contract.functions.approve(targetaddr, 2**256 - 1).build_transaction({
            'chainId': chainId,
            'from': sender,
            'gasPrice': getgasPrice(),
            'gas': gas_limit,
            'nonce': getNonce(sender)
        })
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(approve_tx, senderkey).rawTransaction)
        console.print(f"🔄 [yellow]Approving from {sender[-6:]} to {targetaddr[-6:]}...[/yellow]")
        web3.eth.wait_for_transaction_receipt(tx_hash)
        show_status("✅ Approve Success", sender, targetaddr, "[green]Success[/green]", web3.to_hex(tx_hash))
    except Exception as e:
        show_status("❌ Approve Error", sender, targetaddr, f"[red]{str(e)}[/red]")

def tx_process(title, sender, target, tx_hash, totalamount):
    console.print(f"⏳ [cyan]{title} {totalamount} RUSD...[/cyan]")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    show_status(f"✅ {title} Success", sender, target, "[green]Success[/green]", web3.to_hex(tx_hash))

def buyRUSD(addrtarget, sender, senderkey, amount):
    try:
        totalamount = int(amount) / 10**6
        funcbuy = bytes.fromhex('095e7a95') # This selector must be correct for R2USD on BSC Testnet
        enc = encode(['address', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256'],
                     [sender, amount, 0, 0, 0, 0, 0])
        data = web3.to_hex(funcbuy + enc)
        tx = {
            'chainId': chainId,
            'from': sender,
            'to': addrtarget,
            'data': data,
            'gasPrice': getgasPrice(),
            'gas': web3.eth.estimate_gas({'from': sender, 'to': addrtarget, 'data': data}),
            'nonce': getNonce(sender)
        }
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(tx, senderkey).rawTransaction)
        tx_process("Buy", sender, addrtarget, tx_hash, totalamount)
    except Exception as e:
        show_status("❌ Buy Error", sender, addrtarget, f"[red]{str(e)}[/red]")

def stakesRUSD(addrtarget, sender, senderkey, amount):
    try:
        totalamount = int(amount) / 10**6
        data = web3.to_hex(bytes.fromhex('1a5f0f00') + encode(['uint256'] * 10, [amount] + [0]*9)) # This selector must be correct for SR2USD on BSC Testnet
        tx = {
            'chainId': chainId,
            'from': sender,
            'to': addrtarget,
            'data': data,
            'gasPrice': getgasPrice(),
            'gas': web3.eth.estimate_gas({'from': sender, 'to': addrtarget, 'data': data}),
            'nonce': getNonce(sender)
        }
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(tx, senderkey).rawTransaction)
        tx_process("Stake", sender, addrtarget, tx_hash, totalamount)
    except Exception as e:
        show_status("❌ Stake Error", sender, addrtarget, f"[red]{str(e)}[/red]")

def addLiquidity(addrtarget, sender, senderkey, amount):
    try:
        totalamount = int(amount) / 10**6
        # These contract addresses are for Sepolia, ensuring they come from netconf for the selected chain
        rUSD_contract_address = web3.to_checksum_address(netconf['contracts']['R2USD'])
        sRUSD_contract_address = web3.to_checksum_address(netconf['contracts']['SR2USD'])

        data = web3.to_hex(
            bytes.fromhex('2e1a7d4d') + encode(
                ['address', 'address', 'uint256', 'uint256', 'uint256', 'address', 'uint256'],
                [rUSD_contract_address,
                 sRUSD_contract_address,
                 amount, 0, 0, sender, int(time.time()) + 1000]
            )
        )
        tx = {
            'chainId': chainId,
            'from': sender,
            'to': addrtarget,
            'data': data,
            'gasPrice': getgasPrice(),
            'gas': web3.eth.estimate_gas({'from': sender, 'to': addrtarget, 'data': data}),
            'nonce': getNonce(sender)
        }
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(tx, senderkey).rawTransaction)
        tx_process("Add Liquidity", sender, addrtarget, tx_hash, totalamount)
    except Exception as e:
        show_status("❌ Liquidity Error", sender, addrtarget, f"[red]{str(e)}[/red]")

def run_actions():
    amount = int(5 * 10**6) # This amount needs to be appropriate for the target network tokens

    try:
        with open("pk.txt", "r") as f:
            keys = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        console.print("[red]❌ File pk.txt not found! Please create it and add private keys.[/red]")
        return

    for index, privkey in enumerate(keys, 1):
        try:
            sender = web3.eth.account.from_key(privkey)
            sender_address = sender.address
            sender_key = privkey

            console.print(f"\n[bold green]🚀 Wallet #{index}: {sender_address}[/bold green]")

            # --- Conditional execution of transactions ---
            if selected_network_key == "bsc_testnet":
                console.print(f"[bold magenta]Executing transactions on {netconf['name']}...[/bold magenta]")
                # Get the contract addresses for the selected BSC Testnet dynamically
                USDC_CONTRACT = web3.to_checksum_address(netconf['contracts']['USDC'])
                R2USD_CONTRACT = web3.to_checksum_address(netconf['contracts']['R2USD'])
                SR2USD_CONTRACT = web3.to_checksum_address(netconf['contracts']['SR2USD'])
                # LIQUIDITY_CONTRACT = web3.to_checksum_address(netconf['contracts']['LIQUIDITY']) # Not used for BSC

                # Step 1: Approve USDC for R2USD contract (to buy R2USD)
                console.print(f"[blue]Checking approval for USDC on R2USD...[/blue]")
                if apprvCheck(USDC_CONTRACT, sender_address, R2USD_CONTRACT) < amount:
                    approveTokens(USDC_CONTRACT, R2USD_CONTRACT, sender_address, sender_key)
                buyRUSD(R2USD_CONTRACT, sender_address, sender_key, amount) # Buy R2USD
                time.sleep(10)

                # Step 2: Approve R2USD for SR2USD contract (to stake SR2USD)
                console.print(f"[blue]Checking approval for R2USD on SR2USD...[/blue]")
                if apprvCheck(R2USD_CONTRACT, sender_address, SR2USD_CONTRACT) < amount:
                    approveTokens(R2USD_CONTRACT, SR2USD_CONTRACT, sender_address, sender_key)
                stakesRUSD(SR2USD_CONTRACT, sender_address, sender_key, amount) # Stake R2USD
                time.sleep(10)

                # Step 3: Explicitly skipping Add Liquidity for BSC Testnet
                console.print("[yellow]⏩ Skipping Add Liquidity for BSC Testnet (not supported or not needed)[/yellow]")

            elif selected_network_key == "sepolia": # Example for Sepolia where liquidity might be supported
                console.print(f"[bold magenta]Executing transactions on {netconf['name']} (including Liquidity)...[/bold magenta]")
                USDC_CONTRACT = web3.to_checksum_address(netconf['contracts']['USDC'])
                R2USD_CONTRACT = web3.to_checksum_address(netconf['contracts']['R2USD'])
                SR2USD_CONTRACT = web3.to_checksum_address(netconf['contracts']['SR2USD'])
                LIQUIDITY_CONTRACT = web3.to_checksum_address(netconf['contracts']['LIQUIDITY'])

                # Step 1: Approve USDC for R2USD contract (to buy R2USD)
                console.print(f"[blue]Checking approval for USDC on R2USD...[/blue]")
                if apprvCheck(USDC_CONTRACT, sender_address, R2USD_CONTRACT) < amount:
                    approveTokens(USDC_CONTRACT, R2USD_CONTRACT, sender_address, sender_key)
                buyRUSD(R2USD_CONTRACT, sender_address, sender_key, amount) # Buy R2USD
                time.sleep(10)

                # Step 2: Approve R2USD for SR2USD contract (to stake SR2USD)
                console.print(f"[blue]Checking approval for R2USD on SR2USD...[/blue]")
                if apprvCheck(R2USD_CONTRACT, sender_address, SR2USD_CONTRACT) < amount:
                    approveTokens(R2USD_CONTRACT, SR2USD_CONTRACT, sender_address, sender_key)
                stakesRUSD(SR2USD_CONTRACT, sender_address, sender_key, amount) # Stake R2USD
                time.sleep(10)

                # Step 3: Add Liquidity (only for Sepolia)
                console.print(f"[blue]Checking approvals for Add Liquidity on {netconf['name']}...[/blue]")
                if apprvCheck(R2USD_CONTRACT, sender_address, LIQUIDITY_CONTRACT) < amount:
                    approveTokens(R2USD_CONTRACT, LIQUIDITY_CONTRACT, sender_address, sender_key)
                if apprvCheck(SR2USD_CONTRACT, sender_address, LIQUIDITY_CONTRACT) < amount:
                    approveTokens(SR2USD_CONTRACT, LIQUIDITY_CONTRACT, sender_address, sender_key)
                addLiquidity(LIQUIDITY_CONTRACT, sender_address, sender_key, amount)
                console.print(f"[cyan]✅ Add Liquidity steps completed for wallet #{index} ({sender_address[-6:]})[/cyan]")


            else:
                console.print(f"[yellow]⏩ Skipping Buy/Stake/Liquidity actions for {netconf['name']}. These actions are only supported on BSC Testnet or Sepolia (for LP).[/yellow]")

            console.print(f"[cyan]✅ Wallet #{index} processing complete for {netconf['name']}.[/cyan]")
            time.sleep(15)

        except Exception as e:
            console.print(f"[red]❌ Failed to process wallet #{index} ({sender_address[-6:]}) on {netconf['name']}: {e}[/red]")

def main_loop():
    while True:
        run_actions()
        console.print("[yellow]🕒 Waiting 24 hours before continuing...[/yellow]")
        time.sleep(86400)

if __name__ == "__main__":
    main_loop()
