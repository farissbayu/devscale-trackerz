"""Print the first free TCP port at or after the preferred port (localhost only)."""

import socket
import sys


def is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def main() -> None:
    preferred = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    for port in range(preferred, preferred + 50):
        if is_free(port):
            print(port)
            return
    sys.exit(f"No free port found between {preferred} and {preferred + 49}")


if __name__ == "__main__":
    main()
