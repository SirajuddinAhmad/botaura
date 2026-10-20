# GIWA Sepolia x AuraLaunch Auto Farmer Bot 🤖⚡

Bot otomatisasi multi-wallet berbasis Python untuk melakukan transaksi harian dan aktivitas insentif testnet di **GIWA Sepolia** dan platform **Aura Protocol Launchpad** ([beta.auralaunch.org/incentives](https://beta.auralaunch.org/incentives)).

---

## 📌 Fitur Utama

- 🔗 **Multi-Wallet Support**: Menjalankan transaksi untuk banyak wallet sekaligus melalui daftar `private_keys.txt`.
- 🌐 **Proxy Support (Opsional)**: Dukungan HTTP & SOCKS5 proxy via `proxies.txt` untuk setiap wallet agar aman dari deteksi Sybil.
- 💰 **Daily Active Transactions**:
  - **Self-Transfer**: Mengirim micro-ETH ke address sendiri (saldo tidak berkurang kecuali gas fee testnet yang sangat kecil).
  - **Random Transfer**: Mengirim micro-ETH ke address acak untuk simulasi aktivitas transfer riil.
- 🚀 **Smart Contract Deployment & Interaction**:
  - Deploy kontrak EVM ringan di GIWA Sepolia untuk mendapatkan status/history **Contract Deployer**.
  - Interaksi langsung (memanggil fungsi kontrak) untuk mencatatkan jejak interaksi smart contract.
- 🎁 **Aura Protocol Daily Incentives**:
  - Otomatisasi check-in harian dan verifikasi signature Web3 wallet.
- 🛡️ **Anti-Sybil Delay**: Interval jeda waktu acak (*random sleep*) antar transaksi dan antar wallet.
- ⏳ **Auto Loop (24 Jam)**: Fitur otomatis berulang setiap 24 jam untuk menjaga *daily streak* insentif Anda.
- 📊 **Balance Checker**: Cek saldo ETH testnet seluruh wallet dengan satu klik.

---

## ⚙️ Informasi Jaringan (GIWA Sepolia Testnet)

Tambahkan jaringan ini di MetaMask atau wallet Web3 Anda jika belum ada:

| Parameter | Nilai |
|---|---|
| **Network Name** | GIWA Sepolia |
| **RPC URL** | `https://sepolia-rpc.giwa.io` |
| **Chain ID** | `91342` |
| **Currency Symbol** | `ETH` |
| **Block Explorer** | [https://sepolia-explorer.giwa.io](https://sepolia-explorer.giwa.io) |

### 🚰 Cara Mendapatkan Testnet ETH (Faucet):
1. Klaim Sepolia ETH di faucet Ethereum Sepolia (e.g. Alchemy / Infura Sepolia Faucet / PoW Faucet).
2. Bridge ETH dari Sepolia ke GIWA Sepolia melalui official bridge GIWA, atau
3. Gunakan faucet resmi GIWA di [https://giwa.io](https://giwa.io) / [Nodit Faucet](https://faucet.nodit.io).

---

## 🚀 Panduan Instalasi & Menjalankan Bot

### 1. Prasyarat
Pastikan komputer Anda sudah terpasang **Python 3.8+**.

### 2. Buka Terminal / CMD di Folder Bot
Masuk ke direktori bot:
```bash
cd "d:\portofolio\portofolio Designer\giwa_aura_farmer"
```

### 3. Install Dependensi
Jalankan perintah berikut untuk menginstal library yang dibutuhkan (`web3`, `eth-account`, `requests`, `colorama`, `python-dotenv`):
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Wallet
Buat file bernama `private_keys.txt` di dalam folder `giwa_aura_farmer/`. Masukkan private key wallet testnet Anda (satu per baris):
```text
0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```
*(Catatan: Jangan pernah menggunakan private key wallet utama yang berisi aset riil. Gunakan selalu wallet khusus testnet/burner).*

### 5. Konfigurasi Pengaturan (Opsional)
Salin `.env.example` menjadi `.env` jika ingin mengubah konfigurasi default (RPC, batas delay, jumlah tx harian, dll):
```bash
copy .env.example .env
```

### 6. Jalankan Bot
```bash
python bot.py
```

---

## 📋 Menu Pilihan di Bot

Saat bot dijalankan, Anda dapat memilih mode yang diinginkan:

1. **[1] FULL AUTO**:
   - Check-in insentif Aura Protocol
   - Deploy smart contract baru di GIWA Sepolia
   - Interaksi panggil fungsi smart contract
   - Kirim transaksi harian (Self & Random Transfer) sesuai jumlah yang ditentukan
2. **[2] TX ONLY**:
   - Hanya melakukan transaksi transfer micro-ETH untuk mengumpulkan jumlah transaksi dan hari aktif.
3. **[3] DEPLOY ONLY**:
   - Khusus deploy kontrak dan interaksi kontrak saja.
4. **[4] CHECK-IN ONLY**:
   - Khusus klaim reward check-in harian di Aura Protocol.
5. **[5] CHECK BALANCES**:
   - Menampilkan tabel saldo ETH seluruh wallet Anda untuk memastikan saldo gas fee mencukupi.

---

## 🔒 Tips Keamanan & Anti-Deteksi Sybil

1. **Jeda Waktu**: Jangan mengatur delay terlalu cepat (default bot adalah 10-30 detik per tx dan 20-60 detik per wallet).
2. **Proxy**: Jika menggunakan lebih dari 5 wallet, gunakan proxy yang berbeda di `proxies.txt` untuk menghindari pembatasan IP.
3. **Saldo Gas**: Pastikan setiap wallet memiliki minimal 0.001 - 0.005 ETH di GIWA Sepolia agar transaksi tidak gagal karena kehabisan gas.
