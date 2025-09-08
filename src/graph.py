"""
Mini Agentic Commerce - Simplified Implementation
Mock LangGraph-style agent without external dependencies for demonstration
"""
import json
import os
import re
from typing import Dict, List, Any
from datetime import datetime, timezone

from tools import product_search, size_recommender, eta, order_lookup, order_cancel


class CommerceState:
    def __init__(self):
        self.intent = ""
        self.tools_called = []
        self.evidence = []
        self.policy_decision = {}
        self.final_message = ""
        self.user_input = ""
        self.trace = {}


class CommerceAgent:
    """Mock LangGraph implementation for demonstration purposes"""
    
    def __init__(self, api_key: str = None):
        """Initialize the commerce agent"""
        pass
    
    def router_node(self, state: CommerceState) -> CommerceState:
        """Router node - classifies intent as product_assist, order_help, or other"""
        user_input = state.user_input.lower()
        
        # Simple keyword-based classification
        order_keywords = ["order", "cancel", "cancellation", "refund", "return"]
        product_keywords = ["dress", "wedding", "guest", "midi", "price", "size", "eta", "zip", "recommend"]
        discount_keywords = ["discount", "code", "coupon", "promo"]
        
        if any(keyword in user_input for keyword in order_keywords):
            state.intent = "order_help"
        elif any(keyword in user_input for keyword in product_keywords):
            state.intent = "product_assist"
        elif any(keyword in user_input for keyword in discount_keywords):
            state.intent = "other"
        else:
            state.intent = "other"
        
        return state
    
    def tool_selector_node(self, state: CommerceState) -> CommerceState:
        """Tool selector node - decides which tools to call based on intent"""
        intent = state.intent
        user_input = state.user_input
        
        if intent == "product_assist":
            # Extract search parameters
            price_match = re.search(r'under\s*\$?(\d+)', user_input)
            zip_match = re.search(r'(\d{5,6})', user_input)
            
            price_max = float(price_match.group(1)) if price_match else float('inf')
            zip_code = zip_match.group(1) if zip_match else "10001"
            
            # Determine tags from keywords
            tags = []
            if "wedding" in user_input.lower():
                tags.append("wedding")
            if "midi" in user_input.lower():
                tags.append("midi")
            if "party" in user_input.lower():
                tags.append("party")
            if "day" in user_input.lower():
                tags.append("daywear")
            
            # Call product search
            products = product_search(query=user_input, price_max=price_max, tags=tags)
            state.tools_called.append("product_search")
            
            # Get top 2 products under price cap
            valid_products = [p for p in products if p['price'] <= price_max][:2]
            state.evidence.extend(valid_products)
            
            if valid_products:
                # Get size recommendation
                size_rec = size_recommender({"text": user_input})
                state.tools_called.append("size_recommender")
                state.evidence.append({"size_recommendation": size_rec})
                
                # Get ETA
                eta_info = eta(zip_code)
                state.tools_called.append("eta")
                state.evidence.append({"eta": eta_info})
        
        elif intent == "order_help":
            # Extract order ID and email
            order_id_match = re.search(r'order\s+([A-Z]\d+)', user_input, re.IGNORECASE)
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', user_input)
            
            if order_id_match and email_match:
                order_id = order_id_match.group(1)
                email = email_match.group(1)
                
                # Look up order
                order = order_lookup(order_id, email)
                state.tools_called.append("order_lookup")
                
                if order:
                    state.evidence.append({"order": order})
                    
                    # If cancellation requested
                    if "cancel" in user_input.lower():
                        # Use current time for cancellation check
                        current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        cancel_result = order_cancel(order_id, email, current_time)
                        state.tools_called.append("order_cancel")
                        state.evidence.append({"cancellation": cancel_result})
                else:
                    state.evidence.append({"order": None, "error": "Order not found or email mismatch"})
        
        return state
    
    def policy_guard_node(self, state: CommerceState) -> CommerceState:
        """Policy guard node - enforces 60-minute cancellation rule and other policies"""
        intent = state.intent
        evidence = state.evidence
        
        if intent == "order_help":
            # Check for cancellation in evidence
            for item in evidence:
                if "cancellation" in item:
                    cancel_result = item["cancellation"]
                    state.policy_decision = cancel_result["policy_decision"]
                    break
            
            if not state.policy_decision and any("order" in item for item in evidence):
                # Order lookup without cancellation
                state.policy_decision = {"action": "lookup_only"}
        
        elif intent == "other":
            # Handle discount code requests and other guardrails
            user_input = state.user_input.lower()
            if "discount" in user_input or "code" in user_input or "coupon" in user_input:
                state.policy_decision = {
                    "refuse": True,
                    "reason": "non-existent discount codes",
                    "alternatives": ["Sign up for newsletter for 10% off first order", "Check our sale section"]
                }
        
        return state
    
    def responder_node(self, state: CommerceState) -> CommerceState:
        """Responder node - composes final user reply from structured data"""
        intent = state.intent
        evidence = state.evidence
        policy_decision = state.policy_decision
        tools_called = state.tools_called
        
        final_message = ""
        
        if intent == "product_assist":
            # Build product recommendation response
            products = [item for item in evidence if "id" in item and item.get("title")]
            size_rec = next((item.get("size_recommendation") for item in evidence if "size_recommendation" in item), None)
            eta_info = next((item.get("eta") for item in evidence if "eta" in item), None)
            
            if products:
                final_message = "Here are 2 great options for you:\n\n"
                for i, product in enumerate(products, 1):
                    final_message += f"{i}. **{product['title']}** - ${product['price']}\n"
                    final_message += f"   Color: {product['color']}, Sizes: {', '.join(product['sizes'])}\n\n"
                
                if size_rec:
                    final_message += f"**Size Recommendation:** {size_rec['recommended_size']} - {size_rec['rationale']}\n\n"
                
                if eta_info:
                    final_message += f"**Delivery ETA:** {eta_info['eta_days']} business days to {eta_info['zip']}\n"
            else:
                final_message = "I couldn't find any products matching your criteria. Please try adjusting your price range or preferences."
        
        elif intent == "order_help":
            # Handle order-related responses
            order_info = next((item.get("order") for item in evidence if "order" in item), None)
            cancel_info = next((item.get("cancellation") for item in evidence if "cancellation" in item), None)
            
            if cancel_info:
                if cancel_info["success"]:
                    final_message = f"✅ {cancel_info['reason']}\n\nYour refund will be processed within 3-5 business days."
                else:
                    final_message = f"❌ {cancel_info['reason']}\n\n**Available options:**\n"
                    for alt in cancel_info.get("alternatives", []):
                        final_message += f"• {alt}\n"
            elif order_info:
                final_message = f"Found your order {order_info['order_id']}:\n"
                final_message += f"Created: {order_info['created_at']}\n"
                final_message += f"Items: {len(order_info['items'])} item(s)\n"
                final_message += "How can I help you with this order?"
            else:
                final_message = "Order not found. Please check your order ID and email address."
        
        elif intent == "other":
            if policy_decision.get("refuse"):
                final_message = f"I can't provide {policy_decision['reason'].lower()}.\n\n**Here are some legitimate ways to save:**\n"
                for alt in policy_decision.get("alternatives", []):
                    final_message += f"• {alt}\n"
                final_message += "\nIs there anything else I can help you with regarding our products or your orders?"
            else:
                final_message = "I'm here to help with product recommendations and order management. How can I assist you today?"
        
        state.final_message = final_message
        
        # Create the JSON trace
        state.trace = {
            "intent": intent,
            "tools_called": tools_called,
            "evidence": evidence,
            "policy_decision": policy_decision if policy_decision else None,
            "final_message": final_message
        }
        
        return state
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process a user message through the graph and return trace + response"""
        
        state = CommerceState()
        state.user_input = user_input
        
        # Run through the nodes sequentially (simulating LangGraph)
        state = self.router_node(state)
        state = self.tool_selector_node(state)
        state = self.policy_guard_node(state)
        state = self.responder_node(state)
        
        return {
            "trace": state.trace,
            "final_message": state.final_message
        }