# Mini Agentic Commerce Assignment

> 🛍️ **EvoAI Commerce Agent** - A LangGraph-powered shopping assistant with strict policy enforcement
>
> 🎯 **Assignment**: Build an agent that handles product recommendations and order management with a 60-minute cancellation policy
>
> 🔧 **Stack**: LangGraph, Python, JSON tools

## Features

✅ **Product Assist**: Search, compare, size recommendations, ETA by zip  
✅ **Order Management**: Secure lookup with strict 60-minute cancellation policy  
✅ **Policy Enforcement**: Automated guardrails and helpful alternatives  
✅ **JSON Tracing**: Full decision traces for every interaction

## Quick Start

### Setup
```bash
# Clone and setup
git clone <repository-url>
cd MaheswarreddyPalugulla

# Install dependencies
pip install -r requirements.txt

# Optional: Set up OpenAI API key
cp .env.example .env
# Edit .env with your OPENAI_API_KEY (tests work without it)
```

### Run Tests
```bash
# Run all 4 required test scenarios
python -m tests.run_tests

# Tests cover:
# 1. Product Assist (wedding guest dress under $120)
# 2. Order Help - Allowed (recent order cancellation)
# 3. Order Help - Blocked (old order cancellation)
# 4. Guardrail (invalid discount code request)
```

## Project Structure

```
/src/                 # Agent implementation
  graph.py           # LangGraph nodes & workflow
  tools.py           # Commerce tools & logic
/data/               # Mock data
  products.json      # Product catalog
  orders.json        # Order database
/prompts/            # System prompts
  system.md          # Agent instructions & few-shots
/tests/              # Test scenarios
  run_tests.py       # 4 required test cases
```

## Agent Architecture

```mermaid
flowchart LR
  U[User] --> R[Router]
  R -->|product_assist| TS[ToolSelector]
  R -->|order_help| TS
  TS --> Tools[(Tools)]
  Tools --> PG[PolicyGuard]
  PG --> RESP[Responder]
  RESP --> U2[Reply]
```

### Core Components

- **Router**: Classifies intent (product_assist | order_help | other)
- **ToolSelector**: Chooses appropriate tools based on user request
- **PolicyGuard**: Enforces 60-minute cancellation rule & other policies
- **Responder**: Composes final response with JSON trace

### Available Tools

- `product_search(query, price_max, tags)` - Find products from catalog
- `size_recommender(user_inputs)` - M vs L sizing guidance  
- `eta(zip)` - Delivery time estimation
- `order_lookup(order_id, email)` - Secure order retrieval
- `order_cancel(order_id, timestamp)` - Policy-enforced cancellation

## Key Policies

🕐 **60-Minute Rule**: Orders can only be cancelled within 60 minutes of creation  
🛡️ **Guardrails**: No fake discount codes, helpful alternatives offered  
📊 **Price Compliance**: Product recommendations respect user's budget  
🎯 **Accuracy**: No hallucinated product facts, evidence-based responses

## Sample Output

```json
{
  "intent": "product_assist",
  "tools_called": ["product_search", "size_recommender", "eta"],
  "evidence": [
    {"id": "P1", "title": "Midi Wrap Dress", "price": 119},
    {"size_recommendation": {"recommended_size": "M", "rationale": "..."}}
  ],
  "policy_decision": null,
  "final_message": "Here are 2 great options for you..."
}
```

## Author

**Venkata MaheswarReddy Palugulla**  
AI/ML Engineer | IIT Jodhpur '26  
📧 [b22bb029@iitj.ac.in](mailto:b22bb029@iitj.ac.in)  
🔗 [LinkedIn](https://www.linkedin.com/in/maheswarreddy-palugulla-b76b28268/)

---

*EvoAI Assignment - Demonstrating production-ready agent design with policy enforcement*
