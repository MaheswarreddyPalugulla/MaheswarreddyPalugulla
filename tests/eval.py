"""
Simple evaluation script for trace validation
Bonus evaluation stub for JSON schema validation
"""
import json
import sys
import os

# Add src to path for imports  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import CommerceAgent


def validate_trace_schema(trace: dict) -> tuple[bool, list]:
    """Validate that trace follows required schema"""
    errors = []
    
    # Required fields
    required_fields = ["intent", "tools_called", "evidence", "policy_decision", "final_message"]
    for field in required_fields:
        if field not in trace:
            errors.append(f"Missing required field: {field}")
    
    # Intent validation
    if "intent" in trace:
        valid_intents = ["product_assist", "order_help", "other"]
        if trace["intent"] not in valid_intents:
            errors.append(f"Invalid intent: {trace['intent']}. Must be one of {valid_intents}")
    
    # Tools called validation
    if "tools_called" in trace:
        if not isinstance(trace["tools_called"], list):
            errors.append("tools_called must be a list")
        else:
            valid_tools = ["product_search", "size_recommender", "eta", "order_lookup", "order_cancel"]
            for tool in trace["tools_called"]:
                if tool not in valid_tools:
                    errors.append(f"Invalid tool: {tool}. Must be one of {valid_tools}")
    
    # Evidence validation
    if "evidence" in trace:
        if not isinstance(trace["evidence"], list):
            errors.append("evidence must be a list")
    
    # Final message validation  
    if "final_message" in trace:
        if not isinstance(trace["final_message"], str) or len(trace["final_message"]) == 0:
            errors.append("final_message must be a non-empty string")
    
    return len(errors) == 0, errors


def run_eval():
    """Run evaluation on test cases"""
    print("🔍 Running Trace Schema Validation\n")
    print("=" * 50)
    
    agent = CommerceAgent()
    
    test_cases = [
        "Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?",
        "Cancel order A1003 — email mira@example.com.",
        "Cancel order A1002 — email alex@example.com.", 
        "Can you give me a discount code that doesn't exist?"
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case[:50]}...")
        
        result = agent.process_message(test_case)
        trace = result["trace"]
        
        # Validate schema
        is_valid, errors = validate_trace_schema(trace)
        
        if is_valid:
            print("✅ Schema validation: PASSED")
        else:
            print("❌ Schema validation: FAILED")
            for error in errors:
                print(f"   - {error}")
            all_passed = False
        
        # Additional semantic checks
        if trace["intent"] == "product_assist":
            if "product_search" not in trace["tools_called"]:
                print("⚠️  Warning: Product assist should call product_search")
        
        if trace["intent"] == "order_help" and "cancel" in test_case.lower():
            if "order_cancel" not in trace["tools_called"]:
                print("⚠️  Warning: Order cancellation should call order_cancel")
        
        print(f"📊 Trace summary: {len(trace['tools_called'])} tools called, {len(trace['evidence'])} evidence items")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All trace schema validations PASSED!")
    else:
        print("⚠️  Some validations FAILED - check logs above")
    
    return all_passed


if __name__ == "__main__":
    success = run_eval()
    sys.exit(0 if success else 1)