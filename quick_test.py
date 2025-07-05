#!/usr/bin/env python
"""Quick test after setup"""
try:
    from llm_guard import SafetyGuard
    guard = SafetyGuard()
    result = guard.check("Hello world")
    print("✅ LLM Guard is working!" if result.is_safe else "❌ Something went wrong")
except ImportError:
    print("❌ LLM Guard not installed. Run: pip install -e .")
except Exception as e:
    print(f"❌ Error: {e}")
