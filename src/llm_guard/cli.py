# src/llm_guard/cli.py
"""Command-line interface for LLM Guard"""

import argparse
import sys
import json
from typing import Optional
from pathlib import Path

from llm_guard import SafetyGuard, __version__


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="LLM Guard - Safety toolkit for LLM applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"LLM Guard {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check text safety")
    check_parser.add_argument("text", help="Text to check")
    check_parser.add_argument("--checks", help="Comma-separated list of checks", default=None)
    check_parser.add_argument("--detailed", action="store_true", help="Show detailed analysis")
    check_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive safety checking")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize SafetyGuard
    guard = SafetyGuard()
    
    if args.command == "check":
        check_text(guard, args)
    elif args.command == "interactive":
        interactive_mode(guard)


def check_text(guard: SafetyGuard, args):
    """Check text safety"""
    checks = args.checks.split(",") if args.checks else None
    
    if args.detailed:
        result = guard.analyze(args.text)
    else:
        result = guard.check(args.text, checks=checks)
    
    if args.json:
        output = {
            "is_safe": result.is_safe,
            "reason": result.reason,
            "latency_ms": result.latency_ms
        }
        if args.detailed:
            output["scores"] = result.scores
            output["details"] = result.details
        print(json.dumps(output, indent=2))
    else:
        if result.is_safe:
            print("✅ SAFE")
        else:
            print(f"❌ UNSAFE: {result.reason}")
        
        if args.detailed and result.scores:
            print("\nScores:")
            for check, score in result.scores.items():
                print(f"  {check}: {score:.2f}")
        
        print(f"\nLatency: {result.latency_ms:.1f}ms")


def interactive_mode(guard: SafetyGuard):
    """Interactive safety checking mode"""
    print("🛡️  LLM Guard Interactive Mode")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    while True:
        try:
            text = input("\n> ").strip()
            
            if not text:
                continue
            
            if text.lower() == 'quit':
                print("Goodbye!")
                break
            
            result = guard.check(text)
            if result.is_safe:
                print("✅ SAFE")
            else:
                print(f"❌ UNSAFE: {result.reason}")
                    
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
