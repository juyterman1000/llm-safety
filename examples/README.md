# 📚 LLM Guard Examples

This directory contains comprehensive examples demonstrating how to use LLM Guard in various scenarios. Each example is designed to be educational, practical, and ready to run.

## 🚀 Quick Start

If you're new to LLM Guard, start here:

### 1. **[quick_start.py](quick_start.py)** - Installation & Basic Usage
```bash
python examples/quick_start.py
```
- ✅ Verify installation
- 🧪 Test basic functionality  
- 🔍 Run safety detection tests
- 🔒 Test PII redaction
- 📊 Perfect for first-time users

## 📖 Comprehensive Examples

### 2. **[comprehensive_demo.py](comprehensive_demo.py)** - Full Feature Showcase
```bash
python examples/comprehensive_demo.py
```
- 🛡️ Multi-category safety detection
- 🔒 PII detection and redaction
- ⚙️ Custom rule creation
- 📈 Performance metrics
- 📝 Comprehensive logging

### 3. **[basic_integration.py](basic_integration.py)** - Real-World Integration
```bash
python examples/basic_integration.py
```
- 🤖 Complete chatbot example
- 🔄 Input/output safety pipeline
- 📊 Safety statistics tracking
- 💡 Production-ready patterns
- 🏗️ Architecture best practices

### 4. **[custom_rules_demo.py](custom_rules_demo.py)** - Advanced Customization
```bash
python examples/custom_rules_demo.py
```
- 🏢 Business-specific rules
- 🛡️ Content moderation
- 🎓 Educational content filtering
- ⚖️ Rule priorities
- 🔄 Dynamic rule management

## 📋 Example Overview

| Example | Purpose | Complexity | Best For |
|---------|---------|------------|----------|
| `quick_start.py` | Getting started & verification | ⭐ Beginner | New users, testing installation |
| `comprehensive_demo.py` | Feature showcase | ⭐⭐ Intermediate | Understanding all capabilities |
| `basic_integration.py` | Real integration patterns | ⭐⭐⭐ Advanced | Production implementation |
| `custom_rules_demo.py` | Advanced customization | ⭐⭐⭐ Expert | Domain-specific requirements |

## 🎯 Use Case Examples

### For Chatbots & Conversational AI
- **Start with**: `basic_integration.py`
- **Learn**: Input validation, response filtering, conversation safety

### For Content Moderation
- **Start with**: `custom_rules_demo.py`
- **Learn**: Custom rules, content filtering, moderation workflows

### For Educational Platforms
- **Start with**: `custom_rules_demo.py` (educational section)
- **Learn**: Age-appropriate filtering, academic integrity

### For Business Applications
- **Start with**: `custom_rules_demo.py` (business section)
- **Learn**: Competitor mentions, internal data protection

## 🔧 Running the Examples

### Prerequisites
```bash
pip install llm-guard
```

### Run Individual Examples
```bash
# Quick verification
python examples/quick_start.py

# Full feature demo
python examples/comprehensive_demo.py

# Integration example
python examples/basic_integration.py

# Custom rules demo
python examples/custom_rules_demo.py
```

### Run All Examples
```bash
# From the repository root
for example in examples/*.py; do
    echo "Running $example..."
    python "$example"
    echo "---"
done
```

## 📊 Expected Output

Each example provides:
- ✅ **Clear status indicators** (✅ SAFE, ❌ BLOCKED, 🚩 FLAGGED)
- ⏱️ **Performance metrics** (latency measurements)
- 📝 **Detailed explanations** of what's being tested
- 🎯 **Practical insights** for your implementation

## 🛠️ Customization

### Modify Examples for Your Use Case

1. **Change test inputs**: Edit the `test_cases` arrays in any example
2. **Add custom rules**: Follow patterns in `custom_rules_demo.py`
3. **Adjust thresholds**: Modify SafetyGuard initialization parameters
4. **Enable logging**: Set `log_file` parameter for detailed logs

### Example Customization
```python
# Customize for your domain
guard = SafetyGuard(
    log_file="my_app_safety.log",
    metrics_enabled=True,
    toxicity_threshold=0.8,  # Adjust sensitivity
    pii_detection_enabled=True
)

# Add your business rules
guard.add_custom_rule(
    name="my_custom_rule",
    pattern=r"your_pattern_here",
    action="block",
    message="Custom rule triggered"
)
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: Ensure LLM Guard is installed: `pip install llm-guard`
2. **Permission Error**: Check file permissions for log files
3. **Performance Issues**: Reduce test cases or disable logging for faster execution

### Getting Help

- 📖 Check the main [README](../README.md) for installation help
- 🐛 Report issues on [GitHub Issues](https://github.com/juyterman1000/llm-safety/issues)
- 💬 Join discussions on [GitHub Discussions](https://github.com/juyterman1000/llm-safety/discussions)

## 🚀 Next Steps

After running these examples:

1. **Integrate into your app**: Use patterns from `basic_integration.py`
2. **Create custom rules**: Follow `custom_rules_demo.py` patterns
3. **Monitor performance**: Implement metrics tracking
4. **Scale up**: Consider batch processing for high-volume applications

## 📄 License

These examples are part of LLM Guard and are licensed under the MIT License.

---

**Ready to make your LLM applications safer?** Start with `quick_start.py` and work your way through the examples! 🛡️
