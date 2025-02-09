from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from eth_account import Account
from eth_account.messages import encode_defunct
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class LayerEdge:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://dashboard.layeredge.io",
            "Referer": "https://dashboard.layeredge.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Layer Edge - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, address):
        if address not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[address] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[address]

    def rotate_proxy_for_account(self, address):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[address] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
        
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def generate_checkin_payload(self, account: str, address: str):
        timestamp = int(time.time() * 1000)
        try:
            message = f"I am claiming my daily node point for {address} at {timestamp}"
            encoded_message = encode_defunct(text=message)

            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = signed_message.signature.hex()

            data = {"sign":f"0x{signature}", "timestamp":timestamp, "walletAddress":address}
            
            return data
        except Exception as e:
            return None
    
    def generate_node_payload(self, account: str, address: str, msg_type: str):
        timestamp = int(time.time() * 1000)
        try:
            message = f"Node {msg_type} request for {address} at {timestamp}"
            encoded_message = encode_defunct(text=message)

            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = signed_message.signature.hex()

            data = {"sign":f"0x{signature}", "timestamp":timestamp}
            
            return data
        except Exception as e:
            return None
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account
    
    def print_message(self, address, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )
    
    async def print_clear_message(self):
        while True:
            await asyncio.sleep(60)
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}All Accounts Have Been Processed Successfully. Wait For Next Cycle...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def user_data(self, address: str, proxy=None, retries=5):
        url = f"https://referralapi.layeredge.io/api/referral/wallet-details/{address}"

        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.headers) as response:
                        if response.status == 404:
                            await self.user_confirm(address, proxy)
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(self.mask_account(address), proxy, Fore.RED, f"GET User Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def user_confirm(self, address: str, proxy=None, retries=5):
        url = "https://referralapi.layeredge.io/api/referral/register-wallet/tHc67a1g"
        data = json.dumps({"walletAddress":address})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }

        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(address, proxy, Fore.RED, f"Try Confirm Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def daily_checkin(self, account: str, address: str, proxy=None, retries=5):
        url = "https://referralapi.layeredge.io/api/light-node/claim-node-points"
        data = json.dumps(self.generate_checkin_payload(account, address))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }

        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status == 405:
                            return self.print_message(address, proxy, Fore.YELLOW, "Already Check-In Today")
                        
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    data = json.dumps(self.generate_checkin_payload(account, address))
                    continue
                
                return self.print_message(address, proxy, Fore.RED, f"Check-In Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def node_status(self, address: str, proxy=None, retries=5):
        url = f"https://referralapi.layeredge.io/api/light-node/node-status/{address}"

        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=self.headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(address, proxy, Fore.RED, f"GET Node Status Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def start_node(self, account: str, address: str, proxy=None, retries=5):
        url = f"https://referralapi.layeredge.io/api/light-node/node-action/{address}/start"
        data = json.dumps(self.generate_node_payload(account, address, "activation"))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }

        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    data = json.dumps(self.generate_node_payload(account, address, "activation"))
                    continue
                
                return self.print_message(address, proxy, Fore.RED, f"Start Node Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def stop_node(self, account: str, address: str, proxy=None, retries=5):
        url = f"https://referralapi.layeredge.io/api/light-node/node-action/{address}/stop"
        data = json.dumps(self.generate_node_payload(account, address, "deactivation"))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }

        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    data = json.dumps(self.generate_node_payload(account, address, "deactivation"))
                    continue
                
                return self.print_message(address, proxy, Fore.RED, f"Stop Node Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def process_user_earning(self, address: str, use_proxy: bool):
        while True:
            await asyncio.sleep(24 * 60 * 60)

            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            balance = "N/A"
            user = await self.user_data(address, proxy)
            if user:
                balance = user.get("nodePoints")

            self.print_message(address, proxy, Fore.WHITE, f"Earning {balance} PTS")
        
    async def process_claim_checkin(self, account: str, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            check_in = await self.daily_checkin(account, address, proxy)
            if check_in and check_in.get("message") == "node points claimed successfully":
                self.print_message(address, proxy, Fore.GREEN, "Check-In Success")

            await asyncio.sleep(12 * 60 * 60)
        
    async def process_perform_node(self, account: str, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            reconnect_time = 10 * 60

            node = await self.node_status(address, proxy)
            if node and node.get("message") == "node status":
                last_connect = node['data']['startTimestamp']

                if last_connect is None:
                    start = await self.start_node(account, address, proxy)
                    if start and start.get("message") == "node action executed successfully":
                        last_connect = start['data']['startTimestamp']
                        now_time = int(time.time())
                        reconnect_time = last_connect + 86400 - now_time

                        self.print_message(address, proxy, Fore.GREEN, 
                            f"Node Is Connected "
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Reconnect After: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{self.format_seconds(reconnect_time)}{Style.RESET_ALL}"
                        )
                        
                else:
                    now_time = int(time.time())
                    connect_time = last_connect + 86400

                    if now_time >= connect_time:
                        stop = await self.stop_node(account, address, proxy)
                        if stop and stop.get("message") == "node action executed successfully":
                            self.print_message(address, proxy, Fore.GREEN, 
                                f"Node Disconnected"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.BLUE + Style.BRIGHT}Reconnecting...{Style.RESET_ALL}"
                            )
                            await asyncio.sleep(3)

                            start = await self.start_node(account, address, proxy)
                            if start and start.get("message") == "node action executed successfully":
                                last_connect = start['data']['startTimestamp']
                                now_time = int(time.time())
                                reconnect_time = last_connect + 86400 - now_time

                                self.print_message(address, proxy, Fore.GREEN, 
                                    f"Node Is Connected "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reconnect After: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{self.format_seconds(reconnect_time)}{Style.RESET_ALL}"
                                )

                    else:
                        reconnect_time = connect_time - now_time
                        self.print_message(address, proxy, Fore.YELLOW, 
                            f"Node Is Already Connected "
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Reconnect After: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{self.format_seconds(reconnect_time)}{Style.RESET_ALL}"
                        )

            await asyncio.sleep(reconnect_time)
            
    async def process_accounts(self, account: str, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        user = None
        while user is None:
            user = await self.user_data(address, proxy)
            if not user:
                proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                continue

            balance = user.get("nodePoints", "N/A")
            self.print_message(address, proxy, Fore.WHITE, f"Earning {balance} PTS")

            tasks = []
            tasks.append(self.process_user_earning(address, use_proxy))
            tasks.append(self.process_claim_checkin(account, address, use_proxy))
            tasks.append(self.process_perform_node(account, address, use_proxy))
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            
            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{self.mask_account(account)}{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} GET Address Failed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT} Check Your Private Key Fisrt {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                            continue

                        tasks.append(self.process_accounts(account, address, use_proxy))

                tasks.append(self.print_clear_message())
                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = LayerEdge()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Layer Edge - BOT{Style.RESET_ALL}                                       "                              
        )