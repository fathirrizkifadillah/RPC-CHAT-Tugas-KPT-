"""Modul Pengujian Kinerja (Benchmark) Sistem Distributed Chat Room gRPC.

Mengukur:
- Latensi rata-rata, median, p95, min, dan max (ms)
- Throughput (requests / messages per second)
- Tingkat keberhasilan dan kegagalan
Untuk skenario 1, 5, dan 20 client bersamaan sesuai ketentuan PDF Halaman 12.

Hasil diekspor ke format JSON, CSV, dan grafik PNG (Matplotlib).
"""

import argparse
from concurrent import futures
import csv
import json
import os
from pathlib import Path
import statistics
import sys
import time
from typing import Any, Dict, List, Tuple
import uuid

import grpc
from tabulate import tabulate

# Reconfigure stdout for utf-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
src_dir = str(Path(__file__).resolve().parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from chat_room import chat_room_pb2 as pb
from chat_room import chat_room_pb2_grpc as pb_grpc
from chat_room.server import create_server


def benchmark_scenario(
    server_address: str, num_clients: int, messages_per_client: int, timeout: float = 5.0
) -> Dict[str, Any]:
    """Menjalankan pengujian beban untuk sejumlah client bersamaan."""
    print(f"\n[BENCHMARK] Menjalankan skenario: {num_clients} client bersamaan (@ {messages_per_client} pesan)...")

    latencies_ms: List[float] = []
    success_count = 0
    failure_count = 0
    connected_clients = 0

    # Barrier / start time synchronization
    start_benchmark_time = time.perf_counter()

    def client_worker(client_idx: int) -> Tuple[int, int, List[float]]:
        nonlocal connected_clients
        c_success = 0
        c_fail = 0
        c_latencies: List[float] = []

        channel = grpc.insecure_channel(server_address)
        stub = pb_grpc.LayananChatStub(channel)
        username = f"BenchUser_{client_idx:02d}"

        try:
            # 1. Registrasi Join
            join_req = pb.JoinRequest(
                username=username,
                client_id=f"bench-c-{client_idx}",
                request_id=f"bench-join-{client_idx}-{uuid.uuid4().hex[:6]}",
            )
            join_resp = stub.Join(join_req, timeout=timeout)
            if not join_resp.success:
                return 0, messages_per_client, []
            connected_clients += 1

            # 2. Pengiriman Pesan Berulang
            for msg_idx in range(messages_per_client):
                rid = f"bench-msg-{client_idx}-{msg_idx}-{uuid.uuid4().hex[:6]}"
                msg_req = pb.SendMessageRequest(
                    request_id=rid,
                    sender_username=username,
                    content=f"Benchmark payload #{msg_idx} from client {client_idx}",
                    timestamp=int(time.time() * 1000),
                )

                t_start = time.perf_counter()
                try:
                    resp = stub.SendMessage(msg_req, timeout=timeout)
                    t_end = time.perf_counter()
                    if resp.success:
                        c_success += 1
                        c_latencies.append((t_end - t_start) * 1000.0)  # ms
                    else:
                        c_fail += 1
                except grpc.RpcError:
                    c_fail += 1

            return c_success, c_fail, c_latencies

        except Exception:
            return 0, messages_per_client, []
        finally:
            channel.close()

    # Eksekusi paralel menggunakan thread pool
    with futures.ThreadPoolExecutor(max_workers=num_clients) as executor:
        worker_futures = [executor.submit(client_worker, i) for i in range(num_clients)]
        for f in futures.as_completed(worker_futures):
            s, fl, lats = f.result()
            success_count += s
            failure_count += fl
            latencies_ms.extend(lats)

    total_duration_sec = time.perf_counter() - start_benchmark_time
    total_requests = num_clients * messages_per_client

    avg_latency = statistics.mean(latencies_ms) if latencies_ms else 0.0
    median_latency = statistics.median(latencies_ms) if latencies_ms else 0.0
    min_latency = min(latencies_ms) if latencies_ms else 0.0
    max_latency = max(latencies_ms) if latencies_ms else 0.0
    p95_latency = (
        statistics.quantiles(latencies_ms, n=20)[18] if len(latencies_ms) >= 20 else max_latency
    )

    throughput_rps = success_count / total_duration_sec if total_duration_sec > 0 else 0.0

    return {
        "num_clients": num_clients,
        "messages_per_client": messages_per_client,
        "total_requests": total_requests,
        "connected_clients": connected_clients,
        "success_count": success_count,
        "failure_count": failure_count,
        "total_duration_sec": round(total_duration_sec, 4),
        "throughput_rps": round(throughput_rps, 2),
        "avg_latency_ms": round(avg_latency, 3),
        "median_latency_ms": round(median_latency, 3),
        "p95_latency_ms": round(p95_latency, 3),
        "min_latency_ms": round(min_latency, 3),
        "max_latency_ms": round(max_latency, 3),
    }


def generate_plots(results: List[Dict[str, Any]], output_path: str) -> None:
    """Menghasilkan grafik visualisasi performa perbandingan client."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt

        clients = [str(r["num_clients"]) for r in results]
        latencies = [r["avg_latency_ms"] for r in results]
        throughputs = [r["throughput_rps"] for r in results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 1. Grafik Latensi Rata-rata
        bars1 = ax1.bar(clients, latencies, color="#2b5c8f", width=0.5, edgecolor="black")
        ax1.set_title("Latensi Rata-rata vs Jumlah Client", fontsize=12, fontweight="bold")
        ax1.set_xlabel("Jumlah Client Konkuren", fontsize=11)
        ax1.set_ylabel("Latensi Rata-rata (ms)", fontsize=11)
        ax1.grid(axis="y", linestyle="--", alpha=0.7)
        for bar in bars1:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + (max(latencies) * 0.02), f"{yval:.2f} ms", ha="center", va="bottom", fontsize=10)

        # 2. Grafik Throughput
        bars2 = ax2.bar(clients, throughputs, color="#2e7d32", width=0.5, edgecolor="black")
        ax2.set_title("Throughput vs Jumlah Client", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Jumlah Client Konkuren", fontsize=11)
        ax2.set_ylabel("Throughput (Requests / detik)", fontsize=11)
        ax2.grid(axis="y", linestyle="--", alpha=0.7)
        for bar in bars2:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + (max(throughputs) * 0.02), f"{yval:.1f} req/s", ha="center", va="bottom", fontsize=10)

        plt.suptitle("Analisis Kinerja Distributed Chat Room gRPC", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        print(f"[PLOT] Grafik visualisasi benchmark berhasil disimpan di: {output_path}")

    except Exception as e:
        print(f"⚠️ Gagal membuat grafik matplotlib: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Distributed Chat Room gRPC Benchmark")
    parser.add_argument("--server", default="", help="Address of existing gRPC server (if empty, starts an in-process server)")
    parser.add_argument("--clients", default="1,5,20", help="Comma-separated client counts to test (default: 1,5,20)")
    parser.add_argument("--messages", type=int, default=50, help="Number of messages per client (default: 50)")
    parser.add_argument("--output-dir", default="benchmarks/results", help="Directory to save raw results")
    args = parser.parse_args()

    client_counts = [int(c.strip()) for c in args.clients.split(",") if c.strip()]
    messages_per_client = args.messages

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    server_address = args.server
    temp_server = None

    if not server_address:
        print("[SETUP] Menjalankan in-process benchmark gRPC server di port 50051...")
        temp_server, _, _ = create_server(host="127.0.0.1", port=50051, max_workers=50)
        temp_server.start()
        server_address = "127.0.0.1:50051"
        time.sleep(0.5)

    all_results: List[Dict[str, Any]] = []

    try:
        for c in client_counts:
            res = benchmark_scenario(
                server_address=server_address,
                num_clients=c,
                messages_per_client=messages_per_client,
            )
            all_results.append(res)
            time.sleep(0.5)  # Cooldown singkat antar skenario

        # Cetak Tabel Rekapitulasi
        table_rows = [
            [
                r["num_clients"],
                r["total_requests"],
                r["success_count"],
                r["failure_count"],
                f"{r['avg_latency_ms']:.2f}",
                f"{r['p95_latency_ms']:.2f}",
                f"{r['throughput_rps']:.1f}",
                f"{r['total_duration_sec']:.2f}",
            ]
            for r in all_results
        ]

        print("\n" + "=" * 80)
        print("HASIL PENGUJIAN KINERJA gRPC CHAT ROOM (1, 5, 20 CLIENT)")
        print("=" * 80)
        print(
            tabulate(
                table_rows,
                headers=[
                    "Client",
                    "Total Req",
                    "Sukses",
                    "Gagal",
                    "Avg Lat (ms)",
                    "p95 Lat (ms)",
                    "Throughput (req/s)",
                    "Durasi (s)",
                ],
                tablefmt="github",
            )
        )
        print("=" * 80 + "\n")

        # Simpan ke JSON
        json_path = output_dir / "benchmark_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "server_address": server_address,
                    "results": all_results,
                },
                f,
                indent=2,
            )
        print(f"[JSON] Data mentah JSON disimpan di: {json_path}")

        # Simpan ke CSV
        csv_path = output_dir / "benchmark_results.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
            writer.writeheader()
            writer.writerows(all_results)
        print(f"[CSV] Data mentah CSV disimpan di: {csv_path}")

        # Hasilkan Grafik PNG
        plot_path = output_dir / "latency_throughput_chart.png"
        generate_plots(all_results, str(plot_path))

    finally:
        if temp_server:
            print("[TEARDOWN] Menghentikan in-process benchmark server...")
            temp_server.stop(grace=1).wait()


if __name__ == "__main__":
    main()
