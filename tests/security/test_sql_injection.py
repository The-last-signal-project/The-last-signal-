"""
PROFESSIONAL-LEVEL SECURITY AUDIT
==================================

Advanced exploitation techniques targeting:
- Binary protocol vulnerabilities (packet manipulation)
- SQL injection in parameterized queries (parser bypass)
- Business logic flaws (race conditions, state manipulation)
- Cryptographic weaknesses (timing attacks)
- Authentication bypass (logic errors)

Target: Rust server using SQLite with sqlx parameterized queries.

This test is INVASIVE and designed to expose real vulnerabilities.
Database: THROWAWAY - Safe for destructive testing
Generated code: NOT committed - Ephemeral test artifacts
"""

import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Tuple, List
import socket
import struct
import threading
import time
import os
import pytest

DATABASE_PATH = os.getenv("DATABASE_PATH")

if DATABASE_PATH is None:
    raise RuntimeError("DATABASE_PATH n'est pas définie")
DATABASE_PATH = Path(DATABASE_PATH)



SENSITIVE_TABLES = {
    "users",
    "accounts",
    "clients",
    "sessions",
    "bansperm",
    "bansferme",
    "bansursis",
    "login_attempts",
}


class AdvancedPayloads:
    """High-level attack vectors"""

    # ================================================================
    # BINARY PROTOCOL ATTACKS (Direct server exploitation)
    # ================================================================

    class BinaryProtocol:
        """Exploit the binary protocol layer"""

        PACKET_TYPE_LOGIN = 2
        PACKET_TYPE_SIGNUP = 6
        PACKET_TYPE_PING = 1

        @staticmethod
        def craft_login_packet(email: str, password: str) -> bytes:
            """Craft a login packet matching parser.rs format"""
            email_bytes = email.encode('utf-8')
            password_bytes = password.encode('utf-8')

            # Format: [email_len:2BE][email][password_len:2BE][password]
            payload = (
                struct.pack(">H", len(email_bytes)) + email_bytes +
                struct.pack(">H", len(password_bytes)) + password_bytes
            )

            # Packet: [size:4BE][type:2BE][payload]
            packet_type = struct.pack(">H", AdvancedPayloads.BinaryProtocol.PACKET_TYPE_LOGIN)
            size = struct.pack(">I", 2 + len(payload))

            return size + packet_type + payload

        @staticmethod
        def craft_signup_packet(email: str, password: str) -> bytes:
            """Craft a signup packet"""
            email_bytes = email.encode('utf-8')
            password_bytes = password.encode('utf-8')

            payload = (
                struct.pack(">H", len(email_bytes)) + email_bytes +
                struct.pack(">H", len(password_bytes)) + password_bytes
            )

            packet_type = struct.pack(">H", AdvancedPayloads.BinaryProtocol.PACKET_TYPE_SIGNUP)
            size = struct.pack(">I", 2 + len(payload))

            return size + packet_type + payload

        @staticmethod
        def send_packet(host: str, port: int, packet: bytes) -> bytes:
            """Send packet to server and get response"""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))
                sock.sendall(packet)
                
                # Read size header
                size_header = sock.recv(4)
                if len(size_header) < 4:
                    sock.close()
                    return b""
                
                size = struct.unpack(">I", size_header)[0]
                response = sock.recv(size + 2)
                sock.close()
                
                return response
            except Exception as e:
                return b""

    # ================================================================
    # UTF-8 ENCODING EXPLOITS
    # ================================================================

    class EncodingExploits:
        """Exploit UTF-8 encoding in email/password fields"""

        PAYLOADS = [
            # Unicode lookalikes
            {
                "name": "Unicode single quote (U+2019)",
                "email": "test\u2019 OR \u20181\u2019=\u20181@test.com",  # ' OR '1'='1
                "password": "test",
            },
            # Null byte injection (if not filtered)
            {
                "name": "Null byte injection",
                "email": "test\x00admin@test.com",
                "password": "test",
            },
            # Invalid UTF-8 sequences
            {
                "name": "Invalid UTF-8",
                "email": "test\xff\xfe@test.com",
                "password": "test",
            },
            # Control characters
            {
                "name": "Control characters (bell, etc)",
                "email": "test\x07\x08\x09@test.com",
                "password": "test",
            },
            # Bidirectional text
            {
                "name": "Bidirectional override (U+202E)",
                "email": "test\u202e@test.com",
                "password": "test",
            },
        ]

    # ================================================================
    # PARSER EDGE CASES
    # ================================================================

    class ParserExploits:
        """Exploit parser.rs vulnerabilities"""

        @staticmethod
        def craft_oversized_length() -> bytes:
            """Send length larger than actual data"""
            # Claim email is 10000 bytes but send less
            packet_type = struct.pack(">H", 2)  # LOGIN
            payload = struct.pack(">H", 10000) + b"short"  # Mismatch
            size = struct.pack(">I", 2 + len(payload))
            return size + packet_type + payload

        @staticmethod
        def craft_zero_length() -> bytes:
            """Send zero-length email/password"""
            packet_type = struct.pack(">H", 2)  # LOGIN
            payload = (
                struct.pack(">H", 0) +  # email length = 0
                struct.pack(">H", 0)    # password length = 0
            )
            size = struct.pack(">I", 2 + len(payload))
            return size + packet_type + payload

        @staticmethod
        def craft_max_length() -> bytes:
            """Send maximum u16 length"""
            packet_type = struct.pack(">H", 2)  # LOGIN
            payload = (
                struct.pack(">H", 65535) +  # Max u16
                b"x"
            )
            size = struct.pack(">I", 2 + len(payload))
            return size + packet_type + payload

        @staticmethod
        def craft_incomplete_packet() -> bytes:
            """Send incomplete packet (size > actual data)"""
            packet_type = struct.pack(">H", 2)
            payload = struct.pack(">H", 100)  # Claim 100 bytes
            size = struct.pack(">I", 2 + len(payload) + 100)  # Lie about size
            return size + packet_type + payload

    # ================================================================
    # DATABASE-LEVEL ATTACKS
    # ================================================================

    class DatabaseExploits:
        """Direct SQLite injection tests"""

        # These test if sqlx can be bypassed through the parser
        INJECTION_PAYLOADS = [
            # Basic OR injection
            ("' OR '1'='1", "Basic OR injection"),
            ("admin' --", "Comment bypass"),
            ("' OR 1=1 --", "Numeric OR"),
            
            # Case variations
            ("' OR 'a'='a", "Literal comparison"),
            ("1' OR '1'='1", "Numeric start"),
            
            # Double quote variations
            ('" OR "1"="1', "Double quote variant"),
            
            # UNION attacks
            ("' UNION SELECT user_id, password_hash, '', '', '' FROM users --", "UNION SELECT"),
            
            # Data exfiltration
            ("' || (SELECT password_hash FROM users LIMIT 1) || '", "Concatenation exfil"),
        ]

    # ================================================================
    # RACE CONDITION ATTACKS
    # ================================================================

    class RaceConditions:
        """Exploit timing/race conditions"""

        @staticmethod
        def concurrent_login_same_account(
            host: str,
            port: int,
            email: str,
            password: str,
            threads: int = 20
        ) -> Tuple[int, int]:
            """Try simultaneous logins on same account"""
            successes = 0
            failures = 0
            lock = threading.Lock()

            def login_thread():
                nonlocal successes, failures
                packet = AdvancedPayloads.BinaryProtocol.craft_login_packet(
                    email, password
                )
                response = AdvancedPayloads.BinaryProtocol.send_packet(
                    host, port, packet
                )
                
                if b"authentifi" in response.lower():
                    with lock:
                        successes += 1
                else:
                    with lock:
                        failures += 1

            thread_list = []
            for _ in range(threads):
                t = threading.Thread(target=login_thread)
                t.daemon = True
                thread_list.append(t)
                t.start()

            for t in thread_list:
                t.join(timeout=10)

            return successes, failures

        @staticmethod
        def concurrent_ban_manipulation(
            connection: sqlite3.Connection,
            user_id: str,
            threads: int = 10
        ) -> Tuple[bool, str]:
            """Concurrent ban status manipulation"""
            results = []
            lock = threading.Lock()

            def ban_toggle():
                try:
                    for _ in range(5):
                        connection.execute(
                            "DELETE FROM bansferme WHERE user_id = ?",
                            (user_id,)
                        )
                        connection.commit()
                        time.sleep(0.001)
                        
                        connection.execute(
                            "INSERT OR IGNORE INTO bansferme (user_id, auteur, raison, date_ban, date_deban) VALUES (?, 'test', 'test', CURRENT_TIMESTAMP, datetime(CURRENT_TIMESTAMP, '+1 hour'))",
                            (user_id,)
                        )
                        connection.commit()
                    
                    with lock:
                        results.append(True)
                except:
                    with lock:
                        results.append(False)

            thread_list = []
            for _ in range(threads):
                t = threading.Thread(target=ban_toggle)
                t.daemon = True
                thread_list.append(t)
                t.start()

            for t in thread_list:
                t.join(timeout=10)

            success = any(results)
            return success, f"Race manipulation: {len(results)} threads completed"

    # ================================================================
    # TIMING ATTACKS
    # ================================================================

    class TimingAttacks:
        """Exploit timing variations"""

        @staticmethod
        def measure_query_timing(
            connection: sqlite3.Connection,
            email: str,
            test_passwords: List[str]
        ) -> List[float]:
            """Measure time for password verification"""
            timings = []

            for pwd in test_passwords:
                start = time.time()
                try:
                    # Simulate what server does
                    cursor = connection.execute(
                        "SELECT password_hash FROM users WHERE email = ? LIMIT 1",
                        (email,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        # In real server, verify_password() is called
                        # We can't directly test that without running server
                        pass
                
                except:
                    pass
                
                elapsed = time.time() - start
                timings.append(elapsed)

            return timings

    # ================================================================
    # CRYPTOGRAPHIC ATTACKS
    # ================================================================

    class CryptoAttacks:
        """Exploit weak cryptography"""

        @staticmethod
        def analyze_password_hashes(
            connection: sqlite3.Connection
        ) -> Tuple[str, bool]:
            """Analyze password hash strength"""
            try:
                cursor = connection.execute(
                    "SELECT password_hash FROM users LIMIT 1"
                )
                row = cursor.fetchone()

                if not row:
                    return "No hashes found", False

                hash_val = row[0]

                if hash_val.startswith("$argon2"):
                    return "Argon2 (STRONG)", False
                elif hash_val.startswith("$2"):
                    return "Bcrypt (STRONG)", False
                elif hash_val.startswith("$6$"):
                    return "SHA-512 crypt (MEDIUM)", True
                elif len(hash_val) == 32:
                    return "MD5 (WEAK)", True
                elif len(hash_val) == 40:
                    return "SHA1 (WEAK)", True
                elif len(hash_val) == 64:
                    return "SHA256 (WEAK)", True
                else:
                    return f"Unknown type: {hash_val[:30]}", None

            except Exception as e:
                return str(e), False


def open_database(path: Path) -> sqlite3.Connection:
    """Open test database"""
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
def resolve_database_file(path: Path) -> Path:
    """Résout le chemin vers le fichier .db, que DATABASE_PATH pointe
    vers un fichier ou vers un dossier le contenant."""
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")

    if path.is_file():
        return path

    if path.is_dir():
        # Cherche un fichier .db dans le dossier
        db_files = list(path.glob("*.db"))
        if len(db_files) == 1:
            return db_files[0]
        elif len(db_files) > 1:
            raise RuntimeError(
                f"Plusieurs fichiers .db trouvés dans {path} : {db_files}\n"
                f"Impossible de déterminer lequel utiliser."
            )
        else:
            raise FileNotFoundError(
                f"Aucun fichier .db trouvé dans le dossier : {path}"
            )

    raise RuntimeError(f"Chemin invalide (ni fichier ni dossier) : {path}")


def create_test_database() -> Tuple[Path, tempfile.TemporaryDirectory]:
    """Create throwaway database copy"""
    db_file = resolve_database_file(DATABASE_PATH)

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name) / "the_last_signal_attack.db"
    shutil.copy2(db_file, temp_path)

    return temp_path, temp_dir



def get_row_count(connection: sqlite3.Connection, table: str) -> int:
    """Get row count"""
    result = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()
    return int(result[0]) if result else 0


def get_tables(connection: sqlite3.Connection) -> List[str]:
    """Get all tables"""
    cursor = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    )
    return [row[0] for row in cursor.fetchall()]


# ================================================================
# MAIN TEST SUITE
# ================================================================
@pytest.mark.security
def test_advanced_attacks_database():
    """
    Professional-level database attack testing.
    Tests SQLi resistance through direct database access.
    """
    print("\n" + "=" * 80)
    print("PROFESSIONAL SECURITY AUDIT - DATABASE LEVEL")
    print("=" * 80)

    test_db, temp_dir = create_test_database()

    print(f"\n[SETUP]")
    print(f"Original: {DATABASE_PATH}")
    print(f"Testbed : {test_db}")

    try:
        
        conn = open_database(test_db)
        print("Database:", test_db)
        print("Tables:", get_tables(conn))

        try:
            # ========== BASELINE ==========
            print("\n[BASELINE]")
            tables = get_tables(conn)
            print(f"✓ Tables: {len(tables)}")

            for table in tables[:5]:
                count = get_row_count(conn, table)
                marker = "⚠️ " if table in SENSITIVE_TABLES else "○"
                print(f"  {marker} {table:20s} | {count} rows")

            # ========== SQLi PAYLOAD TESTS ==========
            print("\n[SQL INJECTION PAYLOADS]")
            print("Testing direct database injection...\n")

            payloads = AdvancedPayloads.DatabaseExploits.INJECTION_PAYLOADS

            injection_count = 0
            for payload, description in payloads:
                try:
                    query = f"SELECT * FROM users WHERE email = '{payload}' LIMIT 1"
                    cursor = conn.execute(query)
                    result = cursor.fetchone()

                    if result:
                        injection_count += 1
                        print(f"  ✓ INJECTABLE | {description}")
                        print(f"              | Payload: {payload[:50]}")
                    else:
                        print(f"  ○ No match | {description}")

                except sqlite3.Error as e:
                    if "syntax" in str(e).lower():
                        injection_count += 1
                        print(f"  ✓ SYNTAX ACCEPTED | {description}")
                    else:
                        print(f"  ✗ ERROR | {description}: {str(e)[:40]}")

            print(f"\n  Total injectable: {injection_count}/{len(payloads)}")

            # ========== CRYPTOGRAPHIC ANALYSIS ==========
            print("\n[CRYPTOGRAPHIC ANALYSIS]")

            hash_type, is_weak = AdvancedPayloads.CryptoAttacks.analyze_password_hashes(conn)
            
            if is_weak is True:
                print(f"  ⚠️  WEAK HASHING: {hash_type}")
            elif is_weak is False:
                print(f"  ✓ STRONG HASHING: {hash_type}")
            else:
                print(f"  ? UNKNOWN: {hash_type}")

            # ========== TIMING ATTACK SIMULATION ==========
            print("\n[TIMING ATTACK POTENTIAL]")

            test_emails = []
            cursor = conn.execute("SELECT email FROM users LIMIT 3")
            for row in cursor.fetchall():
                test_emails.append(row[0])

            if test_emails:
                test_passwords = ["a", "aa", "aaa", "aaaa", "aaaaa"]
                timings = AdvancedPayloads.TimingAttacks.measure_query_timing(
                    conn, test_emails[0], test_passwords
                )
                
                if timings:
                    variance = max(timings) - min(timings)
                    print(f"  ○ Timing variance: {variance:.6f}s")
                    if variance > 0.001:
                        print(f"  ⚠️  Detectable timing difference!")

            # ========== AUTHENTICATION STATE TESTS ==========
            print("\n[AUTHENTICATION LOGIC]")

            # Check if users table has required fields
            cursor = conn.execute("PRAGMA table_info(users)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            required = ["user_id", "email", "password_hash", "status"]
            missing = [col for col in required if col not in columns]
            
            if not missing:
                print(f"  ✓ Required fields present")
            else:
                print(f"  ⚠️  Missing fields: {missing}")

            # Check ban tables
            ban_tables = ["bansperm", "bansferme", "bansursis"]
            existing_ban_tables = [t for t in ban_tables if t in tables]
            print(f"  ○ Ban tables: {len(existing_ban_tables)}/{len(ban_tables)}")

            # ========== RACE CONDITION SIMULATION ==========
            print("\n[RACE CONDITION POTENTIAL]")

            # Test concurrent ban manipulation
            cursor = conn.execute("SELECT user_id FROM users LIMIT 1")
            user_row = cursor.fetchone()
            
            if user_row:
                user_id = user_row[0]
                success, msg = AdvancedPayloads.RaceConditions.concurrent_ban_manipulation(
                    conn, user_id, threads=5
                )
                print(f"  ○ Ban manipulation: {msg}")

            # ========== PARSER EDGE CASE SIMULATION ==========
            print("\n[PARSER EDGE CASES]")
            print("  ○ Zero-length payload: Requires server running")
            print("  ○ Oversized length fields: Requires server running")
            print("  ○ Invalid UTF-8 sequences: Requires server running")

            # ========== FINAL REPORT ==========
            print("\n[VULNERABILITY ASSESSMENT]")

            vulns = []
            if injection_count > 0:
                vulns.append(f"SQL Injection ({injection_count} vectors)")
            if is_weak is True:
                vulns.append("Weak password hashing")

            if vulns:
                print(f"  ⚠️  VULNERABILITIES FOUND:")
                for v in vulns:
                    print(f"      - {v}")
            else:
                print(f"  ✓ No immediate vulnerabilities detected")

            print("\n" + "=" * 80)
            print("AUDIT COMPLETE - Database level only")
            print("For protocol-level attacks, run against live server at 127.0.0.1:5000")
            print("=" * 80)

        finally:
            conn.close()

    finally:
        temp_dir.cleanup()

@pytest.mark.security
def test_binary_protocol_attacks():
    """
    Protocol-level attacks on running server.
    REQUIRES: Server running on 127.0.0.1:5000
    """
    print("\n" + "=" * 80)
    print("PROTOCOL-LEVEL ATTACKS (LIVE SERVER)")
    print("=" * 80)

    HOST = "127.0.0.1"
    PORT = 5000

    print(f"\n[CONNECTING TO {HOST}:{PORT}]")

    try:
        # Test connection
        test_packet = AdvancedPayloads.BinaryProtocol.craft_login_packet(
            "test@example.com", "test"
        )
        response = AdvancedPayloads.BinaryProtocol.send_packet(HOST, PORT, test_packet)

        if not response:
            print("  ✗ Server not responding. Skipping protocol tests.")
            print("    (Start server with: cargo run)")
            return

        print("  ✓ Server is responding")

    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return

    # ========== ENCODING ATTACKS ==========
    print("\n[UTF-8 ENCODING EXPLOITS]")

    for payload_dict in AdvancedPayloads.EncodingExploits.PAYLOADS:
        try:
            packet = AdvancedPayloads.BinaryProtocol.craft_login_packet(
                payload_dict["email"],
                payload_dict["password"]
            )
            response = AdvancedPayloads.BinaryProtocol.send_packet(HOST, PORT, packet)

            if b"authentifi" in response.lower():
                print(f"  ✓ VULNERABLE | {payload_dict['name']}")
            else:
                print(f"  ✗ BLOCKED | {payload_dict['name']}")

        except Exception as e:
            print(f"  ? ERROR | {payload_dict['name']}: {str(e)[:40]}")

    # ========== PARSER EXPLOITS ==========
    print("\n[PARSER EDGE CASES]")

    parser_tests = [
        ("Zero-length fields", AdvancedPayloads.ParserExploits.craft_zero_length()),
        ("Oversized length", AdvancedPayloads.ParserExploits.craft_oversized_length()),
        ("Max length (u16)", AdvancedPayloads.ParserExploits.craft_max_length()),
        ("Incomplete packet", AdvancedPayloads.ParserExploits.craft_incomplete_packet()),
    ]

    for name, packet in parser_tests:
        try:
            response = AdvancedPayloads.BinaryProtocol.send_packet(HOST, PORT, packet)
            
            if len(response) > 0:
                print(f"  ? Response received | {name} (may indicate handling)")
            else:
                print(f"  ✗ Rejected | {name}")

        except Exception as e:
            print(f"  ✗ Error | {name}: {str(e)[:30]}")

    # ========== RACE CONDITIONS (LIVE) ==========
    print("\n[RACE CONDITIONS ON LIVE SERVER]")

    try:
        successes, failures = AdvancedPayloads.RaceConditions.concurrent_login_same_account(
            HOST, PORT, "test@example.com", "test", threads=10
        )

        if successes > 1:
            print(f"  ⚠️  CONCURRENT LOGINS ALLOWED | {successes} simultaneous logins succeeded!")
        else:
            print(f"  ✓ Protected | Only {successes} out of 10 concurrent logins succeeded")

    except Exception as e:
        print(f"  ? Could not test race conditions: {str(e)[:40]}")

    print("\n" + "=" * 80)
    print("PROTOCOL AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    # Run database tests (don't require server)
    test_advanced_attacks_database()

    # Try to run protocol tests (requires running server)
    test_binary_protocol_attacks()
