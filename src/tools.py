"""
Commerce Tools - Product search, sizing, ETA, and order management
"""
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


def load_json_data(filename: str) -> List[Dict]:
    """Load JSON data from the data directory"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r') as f:
        return json.load(f)


def product_search(query: str = "", price_max: float = float('inf'), tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Search products by query, price limit, and tags.
    Returns list of matching products.
    """
    products = load_json_data('products.json')
    
    if tags is None:
        tags = []
    
    # Normalize query for case-insensitive search
    query_lower = query.lower()
    
    results = []
    for product in products:
        # Check price constraint
        if product['price'] > price_max:
            continue
            
        # Check tags if provided
        if tags and not any(tag.lower() in [t.lower() for t in product['tags']] for tag in tags):
            continue
            
        # Check query match in title or tags (more flexible matching)
        if query:
            # Split query into words and check if any match
            query_words = [word for word in query_lower.split() if len(word) > 2]
            if query_words:
                title_matches = any(word in product['title'].lower() for word in query_words)
                tag_matches = any(any(word in tag.lower() for tag in product['tags']) for word in query_words)
                if not (title_matches or tag_matches):
                    continue
                
        results.append(product)
    
    # Sort by price (ascending)
    results.sort(key=lambda x: x['price'])
    
    return results


def size_recommender(user_inputs: Dict[str, Any]) -> Dict[str, str]:
    """
    Simple size recommendation based on user preferences.
    Returns recommendation with rationale.
    """
    # Simple heuristic: if user mentions they're "between M/L" or similar
    user_text = str(user_inputs.get('text', '')).lower()
    
    if 'between m' in user_text and 'l' in user_text:
        return {
            "recommended_size": "M",
            "rationale": "For midi dresses, M typically offers a more tailored fit. You can always size up to L if you prefer a looser drape."
        }
    elif 'loose' in user_text or 'relaxed' in user_text:
        return {
            "recommended_size": "L", 
            "rationale": "L size recommended for a more relaxed, comfortable fit."
        }
    elif 'fitted' in user_text or 'tight' in user_text:
        return {
            "recommended_size": "M",
            "rationale": "M size recommended for a more fitted silhouette."
        }
    else:
        return {
            "recommended_size": "M",
            "rationale": "M is typically the most versatile size for midi dresses with good fit balance."
        }


def eta(zip_code: str) -> Dict[str, str]:
    """
    Calculate estimated delivery time based on zip code.
    Simple rule-based system.
    """
    zip_code = str(zip_code).strip()
    
    # Simple heuristic based on zip code patterns
    if zip_code.startswith('1') or zip_code.startswith('0'):  # Northeast
        days = "2-3"
        region = "Northeast"
    elif zip_code.startswith('2') or zip_code.startswith('3'):  # Southeast  
        days = "3-4"
        region = "Southeast"
    elif zip_code.startswith('4') or zip_code.startswith('5'):  # Central
        days = "3-5"
        region = "Central"
    elif zip_code.startswith('6') or zip_code.startswith('7'):  # South Central
        days = "4-5"
        region = "South Central"
    elif zip_code.startswith('8') or zip_code.startswith('9'):  # West
        days = "4-6"
        region = "West"
    else:
        days = "3-5"
        region = "Standard"
    
    return {
        "eta_days": days,
        "region": region,
        "zip": zip_code
    }


def order_lookup(order_id: str, email: str) -> Optional[Dict[str, Any]]:
    """
    Look up order by ID and email.
    Returns order details if found and email matches.
    """
    orders = load_json_data('orders.json')
    
    for order in orders:
        if order['order_id'] == order_id and order['email'].lower() == email.lower():
            return order
    
    return None


def order_cancel(order_id: str, email: str, current_timestamp: Optional[str] = None) -> Dict[str, Any]:
    """
    Attempt to cancel an order with 60-minute policy enforcement.
    Returns cancellation result with policy decision.
    """
    # Look up the order first
    order = order_lookup(order_id, email)
    
    if not order:
        return {
            "success": False,
            "reason": "Order not found or email mismatch",
            "policy_decision": {
                "cancel_allowed": False,
                "reason": "Order not found"
            }
        }
    
    # Parse order creation time
    created_at = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00'))
    
    # Use provided timestamp or current time
    if current_timestamp:
        current_time = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
    else:
        current_time = datetime.now(timezone.utc)
    
    # Calculate time difference in minutes
    time_diff = (current_time - created_at).total_seconds() / 60
    
    if time_diff <= 60:
        # Cancellation allowed
        return {
            "success": True,
            "reason": f"Order cancelled successfully. Cancelled {time_diff:.1f} minutes after creation.",
            "policy_decision": {
                "cancel_allowed": True,
                "reason": f"Within 60-minute window ({time_diff:.1f} minutes)"
            },
            "order": order
        }
    else:
        # Cancellation blocked
        return {
            "success": False,
            "reason": f"Cancellation not allowed. Order was created {time_diff:.1f} minutes ago (policy allows 60 minutes max).",
            "policy_decision": {
                "cancel_allowed": False,
                "reason": f"Beyond 60-minute window ({time_diff:.1f} minutes)"
            },
            "order": order,
            "alternatives": [
                "Edit shipping address if order hasn't shipped",
                "Exchange for store credit",
                "Contact customer support for special assistance"
            ]
        }