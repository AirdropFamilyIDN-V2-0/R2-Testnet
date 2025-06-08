# This code is a modified version of the original repository:
# https://github.com/vkamppp/R2-Testnet
# Modifications made by vkamppp
# Date of modification: June 8, 2025

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

with open("network_config.json") as f:
    network_config = json.load(f)

console.print("\n[bold blue]Pilih jaringan yang akan digunakan:[/bold blue]")
for i, net in enumerate(network_config.keys()):
    console.print(f"[{i}] {network_config[net]['name']}")

selected_index = int(console.input("\n[bold green]Masukkan nomor jaringan: [/bold green]"))
selected_network = list(network_config.keys())[selected_index]
netconf = network_config[selected_network]

web3 = Web3(Web3.HTTPProvider(netconf["rpcUrl"]))
chainId = netconf["chainId"]

if web3.is_connected():
    console.print(f"✅ [green]Connected to {netconf['name']}[/green]\n")
else:
    console.print(f"❌ [red]Gagal konek ke jaringan {netconf['name']}[/red]")
    exit()


with open("tokenabi.json") as f:
    tokenabi = json.load(f)

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
        approve_tx = token_contract.functions.approve(targetaddr, 2**256 - 1).build_transaction({
            'chainId': chainId,
            'from': sender,
            'gasPrice': getgasPrice(),
            'gas': token_contract.functions.approve(targetaddr, 2**256 - 1).estimate_gas({'from': sender}),
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
        funcbuy = bytes.fromhex('095e7a95')
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
        data = web3.to_hex(bytes.fromhex('1a5f0f00') + encode(['uint256'] * 10, [amount] + [0]*9))
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
        data = web3.to_hex(
            bytes.fromhex('2e1a7d4d') + encode(
                ['address', 'address', 'uint256', 'uint256', 'uint256', 'address', 'uint256'],
                [web3.to_checksum_address('0x20c54C5F742F123Abb49a982BFe0af47edb38756'),
                 web3.to_checksum_address('0xBD6b25c4132F09369C354beE0f7be777D7d434fa'),
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
    amount = int(5 * 10**6)

    try:
        with open("pk.txt", "r") as f:
            keys = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        console.print("[red]❌ File pk.txt tidak ditemukan![/red]")
        return

    for index, privkey in enumerate(keys, 1):
        try:
            sender = web3.eth.account.from_key(privkey)
            sender_address = sender.address
            sender_key = privkey

            console.print(f"\n[bold green]🚀 Wallet #{index}: {sender_address}[/bold green]")

            USDC = web3.to_checksum_address('0xef84994eF411c4981328fFcE5Fda41cD3803faE4')
            rUSD = web3.to_checksum_address('0x20c54C5F742F123Abb49a982BFe0af47edb38756')
            sRUSD = web3.to_checksum_address('0xBD6b25c4132F09369C354beE0f7be777D7d434fa')
            liquidity = web3.to_checksum_address('0xF64a77f6e57d9fEeFd2E8fEDbd0032798dAC21Fa')

            if apprvCheck(USDC, sender_address, rUSD) < amount:
                approveTokens(USDC, rUSD, sender_address, sender_key)
            buyRUSD(rUSD, sender_address, sender_key, amount)
            time.sleep(10)

            if apprvCheck(rUSD, sender_address, sRUSD) < amount:
                approveTokens(rUSD, sRUSD, sender_address, sender_key)
            stakesRUSD(sRUSD, sender_address, sender_key, amount)
            time.sleep(10)

            if apprvCheck(rUSD, sender_address, liquidity) < amount:
                approveTokens(rUSD, liquidity, sender_address, sender_key)
            if apprvCheck(sRUSD, sender_address, liquidity) < amount:
                approveTokens(sRUSD, liquidity, sender_address, sender_key)
            addLiquidity(liquidity, sender_address, sender_key, amount)

            console.print(f"[cyan]✅ Semua langkah selesai untuk wallet #{index} ({sender_address[-6:]})[/cyan]")
            time.sleep(15) 

        except Exception as e:
            console.print(f"[red]❌ Gagal memproses wallet #{index}: {e}[/red]")

def main_loop():
    while True:
        run_actions()
        console.print("[yellow]🕒 Menunggu 24 jam sebelum lanjut...[/yellow]")
        time.sleep(86400) 

if __name__ == "__main__":
    main_loop()
