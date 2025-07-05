# examples/custom_rules_demo.py
"""
Custom Rules and Configuration Demo

This example demonstrates how to create and use custom safety rules
for domain-specific requirements and business logic.
"""

from llm_guard import SafetyGuard
import re
from typing import List, Dict, Any


def create_business_rules_guard() -> SafetyGuard:
    """Create a SafetyGuard instance with custom business rules."""
    guard = SafetyGuard(log_file="custom_rules_demo.log")
    
    # Business-specific rules
    guard.add_custom_rule(
        name="competitor_mention",
        pattern=r"\b(CompetitorA|CompetitorB|RivalCorp|OtherVendor)\b",
        action="block",
        message="Competitor mention detected - redirecting to our solutions"
    )
    
    guard.add_custom_rule(
        name="pricing_inquiry",
        pattern=r"\b(price|cost|pricing|expensive|cheap|budget)\b",
        action="flag",
        message="Pricing inquiry detected - route to sales team"
    )
    
    guard.add_custom_rule(
        name="internal_codes",
        pattern=r"\b(INTERNAL-\d+|CONF-\w+|SECRET-\w+)\b",
        action="redact",
        replacement="[INTERNAL_CODE]",
        message="Internal code reference redacted"
    )
    
    guard.add_custom_rule(
        name="support_escalation",
        pattern=r"\b(angry|frustrated|terrible|awful|worst|hate)\b.*\b(service|support|help)\b",
        action="flag",
        message="Potential escalation - route to senior support"
    )
    
    return guard


def create_content_moderation_guard() -> SafetyGuard:
    """Create a SafetyGuard for content moderation with custom rules."""
    guard = SafetyGuard()
    
    # Content moderation rules
    guard.add_custom_rule(
        name="spam_patterns",
        pattern=r"\b(buy now|limited time|act fast|click here|free money)\b",
        action="block",
        message="Spam pattern detected"
    )
    
    guard.add_custom_rule(
        name="self_promotion",
        pattern=r"\b(my website|my product|my service|check out my)\b",
        action="flag",
        message="Self-promotion detected"
    )
    
    guard.add_custom_rule(
        name="contact_sharing",
        pattern=r"\b(whatsapp|telegram|discord|dm me|contact me)\b",
        action="flag",
        message="Contact sharing attempt"
    )
    
    return guard


def create_educational_content_guard() -> SafetyGuard:
    """Create a SafetyGuard for educational content with age-appropriate rules."""
    guard = SafetyGuard()
    
    # Educational content rules
    guard.add_custom_rule(
        name="inappropriate_topics",
        pattern=r"\b(violence|drugs|alcohol|gambling|adult content)\b",
        action="block",
        message="Inappropriate for educational setting"
    )
    
    guard.add_custom_rule(
        name="homework_cheating",
        pattern=r"\b(do my homework|write my essay|solve this for me|give me answers)\b",
        action="flag",
        message="Potential academic dishonesty"
    )
    
    guard.add_custom_rule(
        name="encourage_learning",
        pattern=r"\b(help me understand|explain|teach me|how does)\b",
        action="allow",
        message="Learning-focused inquiry"
    )
    
    return guard


def demonstrate_business_rules():
    """Demonstrate business-specific custom rules."""
    print("\n🏢 Business Rules Demo")
    print("=" * 50)
    
    guard = create_business_rules_guard()
    
    test_cases = [
        "How does your product compare to CompetitorA?",
        "What's the price of your premium plan?",
        "I'm working on project INTERNAL-12345",
        "Your service is terrible and I hate the support team",
        "Can you help me integrate your API?",
        "I heard RivalCorp has better features"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{text}\"")
        result = guard.check(text, return_details=True)
        
        if result.is_safe:
            print("   ✅ APPROVED")
        else:
            print(f"   ❌ BLOCKED: {result.reason}")
        
        # Check for flags (warnings that don't block)
        if hasattr(result, 'flags') and result.flags:
            for flag in result.flags:
                print(f"   🚩 FLAG: {flag}")


def demonstrate_content_moderation():
    """Demonstrate content moderation rules."""
    print("\n🛡️ Content Moderation Demo")
    print("=" * 50)
    
    guard = create_content_moderation_guard()
    
    test_cases = [
        "Buy now! Limited time offer - act fast!",
        "Check out my amazing new product at my website",
        "Great discussion! Thanks for sharing",
        "DM me on WhatsApp for more details",
        "This is helpful information for everyone"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Content: \"{text}\"")
        result = guard.check(text, return_details=True)
        
        if result.is_safe:
            print("   ✅ APPROVED")
        else:
            print(f"   ❌ BLOCKED: {result.reason}")


def demonstrate_educational_rules():
    """Demonstrate educational content rules."""
    print("\n🎓 Educational Content Demo")
    print("=" * 50)
    
    guard = create_educational_content_guard()
    
    test_cases = [
        "Can you help me understand how photosynthesis works?",
        "Please do my homework for me",
        "Explain the concept of gravity",
        "Tell me about violence in history",
        "How does machine learning work?"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Student Query: \"{text}\"")
        result = guard.check(text, return_details=True)
        
        if result.is_safe:
            print("   ✅ APPROPRIATE")
        else:
            print(f"   ❌ INAPPROPRIATE: {result.reason}")


def demonstrate_rule_priorities():
    """Demonstrate how rule priorities work."""
    print("\n⚖️ Rule Priority Demo")
    print("=" * 50)
    
    guard = SafetyGuard()
    
    # Add rules with different priorities
    guard.add_custom_rule(
        name="general_block",
        pattern=r"\btest\b",
        action="block",
        priority=1,
        message="General test block"
    )
    
    guard.add_custom_rule(
        name="specific_allow",
        pattern=r"\btest case\b",
        action="allow",
        priority=10,  # Higher priority
        message="Specific test case allowed"
    )
    
    test_cases = [
        "This is a test",  # Should be blocked by general rule
        "This is a test case",  # Should be allowed by specific rule
        "Running test scenarios"  # Should be blocked by general rule
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{text}\"")
        result = guard.check(text, return_details=True)
        
        if result.is_safe:
            print(f"   ✅ ALLOWED: {result.reason}")
        else:
            print(f"   ❌ BLOCKED: {result.reason}")


def demonstrate_dynamic_rules():
    """Demonstrate adding and removing rules dynamically."""
    print("\n🔄 Dynamic Rules Demo")
    print("=" * 50)
    
    guard = SafetyGuard()
    test_text = "This contains a keyword"
    
    print(f"Testing: \"{test_text}\"")
    
    # Initial check - should pass
    result = guard.check(test_text)
    print(f"1. Before adding rule: {'SAFE' if result.is_safe else 'BLOCKED'}")
    
    # Add a rule dynamically
    guard.add_custom_rule(
        name="keyword_block",
        pattern=r"\bkeyword\b",
        action="block",
        message="Keyword detected"
    )
    
    result = guard.check(test_text)
    print(f"2. After adding rule: {'SAFE' if result.is_safe else 'BLOCKED'}")
    
    # Remove the rule
    guard.remove_custom_rule("keyword_block")
    
    result = guard.check(test_text)
    print(f"3. After removing rule: {'SAFE' if result.is_safe else 'BLOCKED'}")


def main():
    """Main demonstration function."""
    print("🔧 Custom Rules and Configuration Demo")
    print("=" * 60)
    print("This demo shows how to create domain-specific safety rules")
    
    # Run all demonstrations
    demonstrate_business_rules()
    demonstrate_content_moderation()
    demonstrate_educational_rules()
    demonstrate_rule_priorities()
    demonstrate_dynamic_rules()
    
    print("\n🎯 Summary")
    print("=" * 50)
    print("Custom rules enable you to:")
    print("  ✓ Block domain-specific inappropriate content")
    print("  ✓ Flag content for human review")
    print("  ✓ Redact sensitive business information")
    print("  ✓ Route conversations based on content")
    print("  ✓ Adapt safety checks to your use case")
    print("  ✓ Add and remove rules dynamically")
    
    print("\n💡 Use Cases:")
    print("  • Customer service chatbots")
    print("  • Educational platforms")
    print("  • Content moderation systems")
    print("  • Business communication tools")
    print("  • Community forums")


if __name__ == "__main__":
    main()
