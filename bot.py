# This code is a modified version of the original repository:
# https://github.com/vkamppp/R2-Testnet
# Modifications made by [Your GitHub Username]
# Date of modification: June 8, 2025
# This version is specifically modified to work ONLY with Binance Smart Chain Testnet.

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

# --- HARDCODED BSC TESTNET CONFIGURATION ---
# BSC Testnet Details
BSC_TESTNET_RPC_URL = "https://bsc-testnet-rpc.publicnode.com/"
BSC_TESTNET_CHAIN_ID = 97
BSC_TESTNET_NAME = "Binance Smart Chain Testnet"

# BSC Testnet Contract Addresses (provided by user)
USDC_CONTRACT = "0x069D3763d1Ca4F724272E5F77A2f67ACDd2f9B35"
R2USD_CONTRACT = "0x20c54C5F742F123Abb49a982BFe0af47edb38756"
SR2USD_CONTRACT = "0x069D3763d1Ca4F724272E5F77A2f67ACDd2f9B35"
LIQUIDITY_CONTRACT = "0xCcE6bfcA2558c15bB5faEa7479A706735Aef9634" # Will be skipped below

web3 = Web3(Web3.HTTPProvider(BSC_TESTNET_RPC_URL))
chainId = BSC_TESTNET_CHAIN_ID

if web3.is_connected():
    console.print(f"✅ [green]Connected to {BSC_TESTNET_NAME}[/green]\n")
else:
    console.print(f"❌ [red]Failed to connect to {BSC_TESTNET_NAME} network.[/red]")
    exit()

# --- Load Token ABI ---
with open("tokenabi.json") as f:
    tokenabi = json.load(f)

# --- Helper Functions ---
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
        funcbuy = bytes.fromhex('095e7a95') # Ensure this is the correct selector for R2USD on BSC Testnet
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
        data = web3.to_hex(bytes.fromhex('1a5f0f00') + encode(['uint256'] * 10, [amount] + [0]*9)) # Ensure this is the correct selector for SR2USD on BSC Testnet
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

# --- Removed addLiquidity function ---

def run_actions():
    amount = int(5 * 10**6) # This amount needs to be appropriate for BSC Testnet tokens

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

            # Step 3: Explicitly skipping Add Liquidity
            console.print("[yellow]⏩ Skipping Add Liquidity for BSC Testnet (not supported or not needed)[/yellow]")

            console.print(f"[cyan]✅ All relevant steps completed for wallet #{index} ({sender_address[-6:]})[/cyan]")
            time.sleep(15)

        except Exception as e:
            console.print(f"[red]❌ Failed to process wallet #{index} ({sender_address[-6:]}): {e}[/red]")

def main_loop():
    while True:
        run_actions()
        console.print("[yellow]🕒 Waiting 24 hours before continuing...[/yellow]")
        time.sleep(86400)

if __name__ == "__main__":
    main_loop()
