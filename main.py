import argparse
import json
import sys
from pathlib import Path

from attacks.brute import brute_force_attack
from attacks.dictionary import dictionary_attack
from attacks.hash_cracker import crack_hash
from attacks.hybrid import hybrid_attack
from defense.lockout import LockoutPolicy
from defense.rate_limit import RateLimiter
from utils.logger import log_event
from utils.strength import evaluate_password_strength
from utils.wordlist_gen import generate_wordlist, save_wordlist

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
except Exception:  # pragma: no cover
    class _Dummy:
        RESET_ALL = ""

    class _Fore:
        GREEN = ""
        RED = ""
        CYAN = ""
        YELLOW = ""

    Fore = _Fore()
    Style = _Dummy()


def pretty(result):
    status = result.get("status")
    color = Fore.GREEN if status == "cracked" else Fore.RED
    print(color + json.dumps(result, indent=2) + Style.RESET_ALL)


def run_dictionary(args):
    result = dictionary_attack(args.target, args.wordlist)
    log_event(result)
    pretty(result)


def run_bruteforce(args):
    result = brute_force_attack(
        target_password=args.target,
        min_length=args.min_len,
        max_length=args.max_len,
        workers=args.workers,
    )
    log_event(result)
    pretty(result)


def run_hybrid(args):
    result = hybrid_attack(args.target, args.wordlist, args.max_suffix)
    log_event(result)
    pretty(result)


def run_hash(args):
    result = crack_hash(args.hash, args.algorithm, args.wordlist)
    log_event(result)
    pretty(result)


def run_strength(args):
    result = evaluate_password_strength(args.password)
    result.update({"attack": "strength_check", "status": "analyzed"})
    log_event(result)
    print(Fore.CYAN + json.dumps(result, indent=2) + Style.RESET_ALL)


def run_wordlist(args):
    words = generate_wordlist(args.name, args.dob, args.extras or [])
    output_path = save_wordlist(words, args.output)
    result = {
        "attack": "wordlist_generate",
        "status": "generated",
        "count": len(words),
        "output": output_path,
    }
    log_event(result)
    print(Fore.YELLOW + json.dumps(result, indent=2) + Style.RESET_ALL)


def run_login_demo(args):
    # Defensive controls demo for recruiter showcase.
    limiter = RateLimiter(max_requests=args.max_requests, window_seconds=args.window)
    lockout = LockoutPolicy(threshold=args.threshold, lock_seconds=args.lock_seconds)
    stored_password = args.real_password
    user = args.user

    for i in range(1, args.attempts + 1):
        candidate = f"{args.base_guess}{i}"
        if lockout.is_locked(user):
            result = {"attack": "login_demo", "status": "locked", "user": user, "attempt": i}
            log_event(result)
            print(Fore.RED + f"[{i}] Account locked for user={user}" + Style.RESET_ALL)
            continue

        if not limiter.allow(user):
            result = {"attack": "login_demo", "status": "rate_limited", "user": user, "attempt": i}
            log_event(result)
            print(Fore.YELLOW + f"[{i}] Rate limit triggered for user={user}" + Style.RESET_ALL)
            continue

        if candidate == stored_password:
            lockout.reset(user)
            result = {"attack": "login_demo", "status": "success", "user": user, "attempt": i}
            log_event(result)
            print(Fore.GREEN + f"[{i}] Login success with {candidate}" + Style.RESET_ALL)
            break
        else:
            locked = lockout.record_failure(user)
            result = {
                "attack": "login_demo",
                "status": "failed_locked" if locked else "failed",
                "user": user,
                "attempt": i,
            }
            log_event(result)
            print(Fore.RED + f"[{i}] Invalid password: {candidate}" + Style.RESET_ALL)


def build_parser():
    parser = argparse.ArgumentParser(description="Password Attack & Defense Lab")
    sub = parser.add_subparsers(dest="command", required=True)

    p_dict = sub.add_parser("dictionary", help="Run dictionary attack")
    p_dict.add_argument("--target", required=True)
    p_dict.add_argument("--wordlist", default="wordlists/common.txt")
    p_dict.set_defaults(func=run_dictionary)

    p_brute = sub.add_parser("brute", help="Run brute-force attack")
    p_brute.add_argument("--target", required=True)
    p_brute.add_argument("--min-len", type=int, default=1)
    p_brute.add_argument("--max-len", type=int, default=4)
    p_brute.add_argument("--workers", type=int, default=8)
    p_brute.set_defaults(func=run_bruteforce)

    p_hybrid = sub.add_parser("hybrid", help="Run hybrid attack")
    p_hybrid.add_argument("--target", required=True)
    p_hybrid.add_argument("--wordlist", default="wordlists/common.txt")
    p_hybrid.add_argument("--max-suffix", type=int, default=500)
    p_hybrid.set_defaults(func=run_hybrid)

    p_hash = sub.add_parser("hash", help="Crack md5/sha256 hash with wordlist")
    p_hash.add_argument("--hash", required=True, dest="hash")
    p_hash.add_argument("--algorithm", choices=["md5", "sha256"], default="md5")
    p_hash.add_argument("--wordlist", default="wordlists/common.txt")
    p_hash.set_defaults(func=run_hash)

    p_strength = sub.add_parser("strength", help="Evaluate password strength")
    p_strength.add_argument("--password", required=True)
    p_strength.set_defaults(func=run_strength)

    p_word = sub.add_parser("wordlist", help="Generate personalized wordlist")
    p_word.add_argument("--name", required=True)
    p_word.add_argument("--dob", required=True, help="DOB format YYYY-MM-DD")
    p_word.add_argument("--extras", nargs="*", default=[])
    p_word.add_argument("--output", default="wordlists/custom.txt")
    p_word.set_defaults(func=run_wordlist)

    p_login = sub.add_parser("login-demo", help="Defense simulation with lockout + rate limiting")
    p_login.add_argument("--user", default="demo_user")
    p_login.add_argument("--real-password", default="admin7")
    p_login.add_argument("--base-guess", default="admin")
    p_login.add_argument("--attempts", type=int, default=10)
    p_login.add_argument("--threshold", type=int, default=5)
    p_login.add_argument("--lock-seconds", type=int, default=20)
    p_login.add_argument("--max-requests", type=int, default=3)
    p_login.add_argument("--window", type=int, default=1)
    p_login.set_defaults(func=run_login_demo)

    return parser


def main():
    Path("reports").mkdir(exist_ok=True)
    Path("wordlists").mkdir(exist_ok=True)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
