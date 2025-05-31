from aiohttp import (
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, base64, time, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class LayerEdge:
    def __init__(self) -> None:
        self.ws_headers = {
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cahce",
            "Connection": "Upgrade",
            "Host": "websocket.layeredge.io",
            "Origin": "chrome-extension://fnjlbckpopjmpgkjgoiegmnnhahegbcb",
            "Pragma": "no-cahce",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Websocket-Key": "rzO6T9uMr4gMqpvvXN2+AQ==",
            "Sec-Websocket-Version": "13",
            "Upgrade": "websocket",
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
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}edgenOS Light Node - BOT
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
        
    def decode_ws_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            user_id = parsed_payload["sub"]
            exp_time = parsed_payload["exp"]
            
            return user_id, exp_time
        except Exception as e:
            return None
        
    def print_message(self, user_id, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ User Id:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {user_id} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def connect_websocket(self, token: str, user_id: str, use_proxy: bool, rotate_proxy: bool):
        wss_url = f"wss://websocket.layeredge.io/ws/node?token={token}"
        connected = False

        while True:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=60))
            try:
                async with session.ws_connect(wss_url, headers=self.ws_headers) as wss:
                    
                    async def send_heartbeat_message():
                        while True:
                            await asyncio.sleep(25)
                            await wss.send_json({"type":"Heartbeat"})
                            self.print_message(user_id, proxy, Fore.BLUE, "Heartbeat Sent")

                    if not connected:
                        await wss.send_json({"type":"NodeStart"})
                        self.print_message(user_id, proxy, Fore.GREEN, "Node Started Successfully")
                        connected = True
                        send_ping = asyncio.create_task(send_heartbeat_message())

                    while connected:
                        try:
                            response = await wss.receive_json()
                            if response.get("type") == "PointsUpdate":
                                start_time = response.get("data", {}).get("start_time", 0)
                                total_points = response.get("data", {}).get("total_points", 0)
                                total_boost_points = response.get("data", {}).get("total_boost_points", 0)
                                self.print_message(
                                    user_id, proxy, Fore.GREEN, "Points Updated "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Start Time: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{start_time}{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT}Total Points:{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {total_points} PTS {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Total Boost Points: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}{total_boost_points} PTS{Style.RESET_ALL}"
                                )

                            elif response.get("type") == "heartbeat_ack":
                                self.print_message(user_id, proxy, Fore.GREEN, "Heartbeat Ack")

                        except Exception as e:
                            self.print_message(user_id, proxy, Fore.YELLOW, f"Websocket Connection Closed: {Fore.RED + Style.BRIGHT}{str(e)}")
                            if send_ping:
                                send_ping.cancel()
                                try:
                                    await send_ping
                                except asyncio.CancelledError:
                                    self.print_message(user_id, proxy, Fore.YELLOW, f"Send Heartbeat Cancelled")

                            await asyncio.sleep(5)
                            connected = False
                            break

            except Exception as e:
                self.print_message(user_id, proxy, Fore.RED, f"Websocket Not Connected: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(user_id)
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                self.print_message(user_id, proxy, Fore.YELLOW, "Websocket Closed")
                break
            finally:
                await session.close()

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*75)

            tasks = []
            for token in tokens:
                if token:
                    user_id, exp_time = self.decode_ws_token(token)

                    if not user_id or not exp_time:
                        continue

                    if int(time.time()) > exp_time:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ User Id:{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {user_id} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}EdgeOS Key Already Expired{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                        continue

                    tasks.append(asyncio.create_task(self.connect_websocket(token, user_id, use_proxy, rotate_proxy)))

            await asyncio.gather(*tasks)

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
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] edgenOS Light Node - BOT{Style.RESET_ALL}                                       "                              
        )