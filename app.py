import platform
import queue
import subprocess
import threading
import time
from datetime import datetime

from setting import NUM_PING, NUM_WORKER, BASE_URL, BRANCH, KEY, MINUTE
from utils.output_translation import output_success
from utils.requester import Postman


def main_loop():

    seq = 0
    while True:
        plat = platform.system()

        ping_args = set_ping_args(plat)

        # antrian alamat untuk di ping
        pending = queue.Queue()

        # antrian untuk hasil
        done = queue.Queue()

        # memuat worker sebanyak NUM-WORKER
        workers = []
        for _ in range(NUM_WORKER):
            workers.append(threading.Thread(
                target=worker_func, args=(ping_args, pending, done)))

        # Membuat objek postman
        postman = Postman()
        postman.set_base_url(BASE_URL)
        postman.set_param_get({
            "key": KEY,
            "branch": BRANCH,
            "category": "CCTV"
        })
        postman.set_param_post({
            "key": KEY
        })

        # Masukkan alamat ke antrian pending
        cctv_list = postman.get_ip_list()
        if len(cctv_list) == 0:
            print("Request IP Cctv Gagal ...")
        seq = seq + 1
        print(f"seq : {seq} - {datetime.now().strftime('%H:%M:%S WIB - %d %b')}")
        print(f"Mendapatkan {len(cctv_list)} IP CCTV ...")
        print(f"Memproses icmp ping ...")
        for ip_addr in cctv_list:
            pending.put(ip_addr)  # memasukkan ip address ke pending

        # memulai semua worker
        for w in workers:
            w.daemon = True
            w.start()

        # Cetak hasilnya begitu tiba
        num_terminated = 0
        ip_cctv_up = []
        ip_cctv_down = []
        ip_cctv_half = []
        while num_terminated < NUM_WORKER:
            result = done.get()
            if result is None:
                # Worker di akhiri
                num_terminated += 1
            else:
                if result[0] == 0:
                    ip_cctv_down.append(result[2])
                elif result[0] == 1:
                    ip_cctv_half.append(result[2])
                elif result[0] == 2:
                    ip_cctv_up.append(result[2])

        # Menunggu semua worker diakhiri
        for w in workers:
            w.join()

        # Post to server
        post_to_server(postman, ip_cctv_up, ip_cctv_half, ip_cctv_down)

        print(f"Mengulang dalam {MINUTE} menit")
        print("----------------------------")
        time.sleep(60 * MINUTE)


def worker_func(ping_args, pending, done):
    try:
        while True:
            # Mendapatkan alamat selanjutnya untuk di ping
            address = pending.get_nowait()

            start_time = time.time()

            ping = subprocess.Popen(ping_args + [address],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
                                    )
            out, error = ping.communicate()

            ping_time = (time.time() - start_time) / float(NUM_PING)
            ping_time = "%.3f" % ping_time

            out = output_success(str(out), str(error))

            # hasilnya dimasukkan ke done
            done.put([out, ping_time, address])

    except queue.Empty:
        # Tidak ada lagi alamat
        pass
    finally:
        # Beritahu main thread pekerjaannya diakhiri
        done.put(None)


def set_ping_args(os: str) -> list:
    if os == "Windows":
        return ["ping", "-n", f"{NUM_PING}", "-w", "500"]
    elif os == "Linux":
        return ["ping", "-c", f"{NUM_PING}", "-l", "1", "-W", "5"]
    else:
        raise ValueError("Platform tidak didukung")


def post_to_server(postman: Postman, ip_cctv_up: list, ip_cctv_half: list, ip_cctv_down: list):
    if len(ip_cctv_up) != 0:
        response = postman.post_ip_status(ip_cctv_up, 2)
        print(f"{len(ip_cctv_up)} CCTV UP : send = {response}".rstrip())
        time.sleep(.300)

    if len(ip_cctv_half) != 0:
        response = postman.post_ip_status(ip_cctv_half, 1)
        print(f"{len(ip_cctv_half)} CCTV HALF : send = {response}".rstrip())
        time.sleep(.300)

    if len(ip_cctv_down) != 0:
        response = postman.post_ip_status(ip_cctv_down, 0)
        print(f"{len(ip_cctv_down)} CCTV DOWN : send = {response}".rstrip())


if __name__ == '__main__':
    main_loop()
