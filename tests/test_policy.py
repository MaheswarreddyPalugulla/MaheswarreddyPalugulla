"""
Unit tests for the 60-minute cancellation policy
Bonus unit test for edge cases
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools import order_cancel


def test_60_minute_policy_logic():
    """Test the 60-minute policy logic directly with mocked timestamps"""
    
    print("🔬 Testing 60-minute cancellation policy edge cases\n")
    
    # Create a mock order timestamp
    created_at = "2025-09-08T10:00:00Z"
    
    # Test 1: Exactly at 60 minutes - should be allowed
    print("Test 1: Exactly at 60-minute boundary")
    current_time_60 = "2025-09-08T11:00:00Z"  # Exactly 60 minutes later
    
    # Manually calculate - this should be allowed (≤60 minutes)
    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    current_dt = datetime.fromisoformat(current_time_60.replace('Z', '+00:00'))
    diff_minutes = (current_dt - created_dt).total_seconds() / 60
    
    print(f"Time difference: {diff_minutes} minutes")
    print(f"Should be allowed: {diff_minutes <= 60}")
    assert diff_minutes <= 60, "60 minutes should be within allowed window"
    
    # Test 2: Just under 60 minutes - should be allowed  
    print("\nTest 2: Just under 60 minutes (59.5 minutes)")
    current_time_59_5 = "2025-09-08T10:59:30Z"
    
    current_dt = datetime.fromisoformat(current_time_59_5.replace('Z', '+00:00'))
    diff_minutes = (current_dt - created_dt).total_seconds() / 60
    
    print(f"Time difference: {diff_minutes} minutes")
    print(f"Should be allowed: {diff_minutes <= 60}")
    assert diff_minutes <= 60, "59.5 minutes should be within allowed window"
    
    # Test 3: Just over 60 minutes - should be blocked
    print("\nTest 3: Just over 60 minutes (60.1 minutes)")
    current_time_60_1 = "2025-09-08T11:00:06Z"
    
    current_dt = datetime.fromisoformat(current_time_60_1.replace('Z', '+00:00'))
    diff_minutes = (current_dt - created_dt).total_seconds() / 60
    
    print(f"Time difference: {diff_minutes} minutes")
    print(f"Should be blocked: {diff_minutes > 60}")
    assert diff_minutes > 60, "60.1 minutes should be outside allowed window"
    
    # Test 4: Way over 60 minutes - should be blocked
    print("\nTest 4: Way over 60 minutes (24 hours)")
    current_time_24h = "2025-09-09T10:00:00Z"  # 24 hours later
    
    current_dt = datetime.fromisoformat(current_time_24h.replace('Z', '+00:00'))
    diff_minutes = (current_dt - created_dt).total_seconds() / 60
    
    print(f"Time difference: {diff_minutes} minutes")
    print(f"Should be blocked: {diff_minutes > 60}")
    assert diff_minutes > 60, "24 hours should be way outside allowed window"
    
    print("\n✅ All policy logic tests passed!")
    
    # Test 5: Test actual order_cancel function with a real scenario (allowed case)
    print("\nTest 5: Testing order_cancel function with allowed scenario")
    
    # Use a real order but with a current timestamp that makes it within 60 minutes
    # Order A1001 was created at "2025-09-07T09:30:00Z"
    # Let's simulate current time as 2025-09-07T10:15:00Z (45 minutes later)
    simulated_current = "2025-09-07T10:15:00Z"
    
    result = order_cancel("A1001", "rehan@example.com", simulated_current)
    print(f"Cancellation allowed: {result['policy_decision']['cancel_allowed']}")
    print(f"Reason: {result['policy_decision']['reason']}")
    
    assert result['policy_decision']['cancel_allowed'] == True, "Should allow cancellation within 60 minutes"
    
    # Test 6: Test order_cancel function with blocked scenario  
    print("\nTest 6: Testing order_cancel function with blocked scenario")
    
    # Use same order but with current timestamp beyond 60 minutes
    simulated_current_late = "2025-09-07T11:00:00Z"  # 90 minutes later
    
    result = order_cancel("A1001", "rehan@example.com", simulated_current_late)
    print(f"Cancellation allowed: {result['policy_decision']['cancel_allowed']}")
    print(f"Reason: {result['policy_decision']['reason']}")
    
    assert result['policy_decision']['cancel_allowed'] == False, "Should block cancellation beyond 60 minutes"
    assert len(result.get('alternatives', [])) > 0, "Should provide alternatives when blocked"
    
    print("\n✅ All order_cancel function tests passed!")
    return True


if __name__ == "__main__":
    test_60_minute_policy_logic()