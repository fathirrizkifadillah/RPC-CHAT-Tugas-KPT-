"""Script to compile proto/chat_room.proto into Python gRPC stubs.
Ensures seamless relative and absolute imports.
"""

import subprocess
import sys
from pathlib import Path


def generate_stubs():
    repo_root = Path(__file__).resolve().parent.parent
    proto_file = repo_root / "proto" / "chat_room.proto"
    output_dir = repo_root / "src" / "chat_room"

    if not proto_file.exists():
        print(f"Error: Proto file not found at {proto_file}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{repo_root / 'proto'}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file),
    ]

    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, check=True)
    if res.returncode != 0:
        print("Stub generation failed!")
        sys.exit(res.returncode)

    # Patch grpc stub import for clean packaging
    grpc_stub_path = output_dir / "chat_room_pb2_grpc.py"
    if grpc_stub_path.exists():
        content = grpc_stub_path.read_text(encoding="utf-8")
        target = "import chat_room_pb2 as chat__room__pb2"
        replacement = (
            "try:\n"
            "    from . import chat_room_pb2 as chat__room__pb2\n"
            "except ImportError:\n"
            "    import chat_room_pb2 as chat__room__pb2"
        )
        if target in content:
            content = content.replace(target, replacement, 1)
            grpc_stub_path.write_text(content, encoding="utf-8")
            print("Patched chat_room_pb2_grpc.py for robust relative imports.")

    print(f"Successfully generated gRPC stubs in {output_dir}")


if __name__ == "__main__":
    generate_stubs()
