import time
import requests
from typing import Optional, Dict, Any
from modules.wallet import WalletManager
from modules.logger import log_info, log_success, log_warning, log_error
from config import AURA_BASE_URL

class AuraProtocolClient:
    """
    Client for interacting with Aura Protocol incentives & quests API (beta.auralaunch.org).
    Supports SIWE (Sign-In with Ethereum) challenge-response or bearer token authentication.
    """
    def __init__(self, wallet_manager: WalletManager, auth_token: Optional[str] = None):
        self.wm = wallet_manager
        self.auth_token = auth_token
        self.session = requests.Session()
        
        # Configure proxy if provided
        if self.wm.proxy:
            self.session.proxies = {
                "http": self.wm.proxy,
                "https": self.wm.proxy
            }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://beta.auralaunch.org",
            "Referer": "https://beta.auralaunch.org/incentives",
        }
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"

    def authenticate_wallet(self) -> bool:
        """
        Attempts to authenticate with Aura Protocol using Web3 wallet signature.
        """
        log_info(f"Authenticating wallet {self.wm.address} with Aura Protocol API...")
        try:
            timestamp = int(time.time())
            nonce_msg = f"Sign in to Aura Protocol Incentives\nWallet: {self.wm.address}\nTimestamp: {timestamp}"
            signature = self.wm.sign_message(nonce_msg)

            payload = {
                "address": self.wm.address,
                "message": nonce_msg,
                "signature": signature
            }

            # Attempt authentication request
            url = f"{AURA_BASE_URL}/auth/verify"
            response = self.session.post(url, json=payload, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token") or data.get("accessToken")
                if token:
                    self.headers["Authorization"] = f"Bearer {token}"
                    log_success("Successfully authenticated with Aura Protocol!")
                    return True
            log_warning(f"Aura auth response status: {response.status_code}. API might use custom challenge or session cookies.")
            return False
        except Exception as e:
            log_warning(f"Could not connect to Aura backend API: {e}. (On-chain farming continues unaffected)")
            return False

    def claim_daily_checkin(self) -> bool:
        """
        Claims daily login reward on beta.auralaunch.org/incentives.
        """
        log_info("Submitting Daily Check-In to Aura Protocol...")
        try:
            url = f"{AURA_BASE_URL}/incentives/daily-checkin"
            payload = {"address": self.wm.address}
            
            response = self.session.post(url, json=payload, headers=self.headers, timeout=15)
            if response.status_code in (200, 201):
                data = response.json()
                points = data.get("pointsAwarded", "N/A")
                streak = data.get("streak", "N/A")
                log_success(f"Daily Check-In successful! Points awarded: {points}, Current streak: {streak}")
                return True
            elif response.status_code == 400 and "already" in response.text.lower():
                log_warning("Daily Check-In already completed for today.")
                return True
            else:
                log_warning(f"Check-In API returned HTTP {response.status_code}. Details: {response.text[:120]}")
                return False
        except Exception as e:
            log_warning(f"Daily check-in API skipped or unreachable: {e}")
            return False

    def get_user_points(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves user incentive points and streak status.
        """
        try:
            url = f"{AURA_BASE_URL}/incentives/user/{self.wm.address}"
            response = self.session.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None
