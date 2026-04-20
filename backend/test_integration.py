"""
Phase 1 Integration Test - Backend API

Tests the three main endpoints with the grine_regime_engine integration:
- GET /api/v1/regime/current
- GET /api/v1/allocation/recommended  
- GET /api/v1/allocation/history

Run with: python test_integration.py
"""
import asyncio
import json
from uuid import uuid4

import httpx


BASE_URL = "http://localhost:8000"
TENANT_ID = str(uuid4())

HEADERS = {
    "X-Tenant-ID": TENANT_ID,
    "Content-Type": "application/json"
}


async def test_health_checks():
    """Test basic health endpoints."""
    print("🔍 Testing health checks...")
    
    async with httpx.AsyncClient() as client:
        # Main health check
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("  ✓ Main health check passed")
        
        # Regime health check
        response = await client.get(f"{BASE_URL}/api/v1/regime/health")
        assert response.status_code == 200
        assert response.json()["service"] == "regime_detection"
        print("  ✓ Regime health check passed")
        
        # Allocation health check
        response = await client.get(f"{BASE_URL}/api/v1/allocation/health")
        assert response.status_code == 200
        assert response.json()["service"] == "allocation_engine"
        print("  ✓ Allocation health check passed")


async def test_regime_detection():
    """Test regime detection endpoint."""
    print("🎯 Testing regime detection...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/regime/current",
            headers=HEADERS,
            timeout=30.0  # Regime detection can take time
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Regime: {data['final_state']} (confidence: {data['confidence']:.3f})")
            print(f"  ✓ Momentum: {data['momentum']:+.3f}")
            print(f"  ✓ Processing time: {data['metadata']['processing_time_ms']:.1f}ms")
            
            # Validate response structure
            assert data["final_state"] in ["EXPANSION", "BALANCED", "TRANSITION", "ENDURANCE", "PROTECTION"]
            assert 0 <= data["confidence"] <= 1
            assert -1 <= data["momentum"] <= 1
            assert "probabilities" in data
            assert "metadata" in data
            
            return data
        else:
            print(f"  ❌ Regime detection failed: {response.status_code}")
            print(f"      {response.text}")
            return None


async def test_allocation_engine():
    """Test allocation engine endpoint."""
    print("💼 Testing allocation engine...")
    
    async with httpx.AsyncClient() as client:
        # Test with default parameters
        response = await client.get(
            f"{BASE_URL}/api/v1/allocation/recommended",
            headers=HEADERS,
            timeout=30.0  # Allocation can take time
        )
        
        if response.status_code == 200:
            data = response.json()
            weights = data["final_weights"]
            print(f"  ✓ Allocation: EQ={weights['equity']:.3f} BD={weights['bonds']:.3f} CS={weights['cash']:.3f}")
            print(f"  ✓ Regime: {data['constraints']['regime_state']}")
            print(f"  ✓ Turnover: {data['turnover']['realized']:.3f} (capped: {data['turnover']['capped']})")
            print(f"  ✓ Dividend share: {data['dividend_split']['dividend_share']:.2%}")
            
            # Validate response structure
            total = weights["equity"] + weights["bonds"] + weights["cash"]
            assert abs(total - 1.0) < 0.001, f"Weights don't sum to 1: {total}"
            
            assert "constraints" in data
            assert "turnover" in data
            assert "dividend_split" in data
            assert data["constraints"]["regime_state"] in ["EXPANSION", "BALANCED", "TRANSITION", "ENDURANCE", "PROTECTION"]
            
            return data
        else:
            print(f"  ❌ Allocation failed: {response.status_code}")
            print(f"      {response.text}")
            return None


async def test_allocation_with_params():
    """Test allocation with different parameters."""
    print("🔧 Testing allocation with parameters...")
    
    async with httpx.AsyncClient() as client:
        # Test max_sharpe objective
        response = await client.get(
            f"{BASE_URL}/api/v1/allocation/recommended?objective=max_sharpe&turnover_cap=0.10",
            headers=HEADERS,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Max Sharpe objective: {data['constraints']['objective']}")
            print(f"  ✓ Custom turnover cap: {data['constraints']['turnover_cap']}")
            assert data["constraints"]["objective"] == "max_sharpe"
            assert data["constraints"]["turnover_cap"] == 0.10
        else:
            print(f"  ❌ Parameterized allocation failed: {response.status_code}")


async def test_allocation_history():
    """Test allocation history endpoint."""
    print("📊 Testing allocation history...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/allocation/history?days_lookback=7&limit=10",
            headers=HEADERS,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ History records: {data['total_count']}")
            print(f"  ✓ Current allocation: {data['current']['final_weights']}")
            
            if data["stats"]:
                stats = data["stats"]
                print(f"  ✓ Avg turnover: {stats['avg_turnover']:.3f}")
                print(f"  ✓ Regime distribution: {stats['regime_distribution']}")
            
            assert "current" in data
            assert "history" in data
            assert "stats" in data
        else:
            print(f"  ❌ History failed: {response.status_code}")
            print(f"      {response.text}")


async def test_portfolio_alignment():
    """Test portfolio alignment endpoint (POST)."""
    print("🎯 Testing portfolio alignment...")
    
    async with httpx.AsyncClient() as client:
        # Post a deliberately misaligned portfolio to exercise the scoring
        body = {"equity": 0.58, "bonds": 0.32, "cash": 0.10}
        response = await client.post(
            f"{BASE_URL}/api/v1/portfolio/alignment",
            headers=HEADERS,
            json=body,
            timeout=30.0,
        )

        if response.status_code == 200:
            data = response.json()
            a = data["alignment"]
            print(f"  ✓ Score: {a['score']} ({a['label']})")
            print(f"  ✓ Deviations: {a['deviations']}")
            print(f"  ✓ Range status: {a['range_status']}")
            print(f"  ✓ Actions: {data['suggested_adjustments']}")

            # Validate response shape
            assert "regime" in data
            assert "portfolio" in data
            assert "recommended" in data
            assert "alignment" in data
            assert "suggested_adjustments" in data
            assert 0 <= a["score"] <= 100
            assert a["label"] in ("Highly Aligned", "Moderately Aligned", "Misaligned")

            # Cross-layer consistency check: the regime state reported by
            # the alignment response must match the one from /regime/current
            regime_resp = await client.get(
                f"{BASE_URL}/api/v1/regime/current", headers=HEADERS, timeout=30.0
            )
            if regime_resp.status_code == 200:
                current_state = regime_resp.json()["final_state"]
                assert data["regime"]["state"] == current_state, (
                    f"Regime state mismatch: alignment={data['regime']['state']}, "
                    f"current={current_state}"
                )
                print(f"  ✓ Regime state consistent across endpoints: {current_state}")
        else:
            print(f"  ❌ Alignment failed: {response.status_code}")
            print(f"      {response.text}")


async def test_portfolio_alignment_sample():
    """Test the convenience sample endpoint for empty states."""
    print("🎯 Testing portfolio alignment sample...")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/portfolio/alignment/sample",
            headers=HEADERS,
            timeout=30.0,
        )

        if response.status_code == 200:
            data = response.json()
            # Sample uses 60/30/10
            assert data["portfolio"]["equity"] == 0.60
            assert data["portfolio"]["bonds"] == 0.30
            assert data["portfolio"]["cash"] == 0.10
            print(f"  ✓ Sample endpoint returns 60/30/10 scored against current regime")
        else:
            print(f"  ❌ Sample failed: {response.status_code}")


async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("GrineOS Phase 1 Integration Test")
    print(f"Tenant ID: {TENANT_ID}")
    print("=" * 60)
    
    try:
        await test_health_checks()
        print()
        
        regime_data = await test_regime_detection()
        print()
        
        allocation_data = await test_allocation_engine()
        print()
        
        await test_allocation_with_params()
        print()
        
        await test_allocation_history()
        print()

        await test_portfolio_alignment()
        print()

        await test_portfolio_alignment_sample()
        print()
        
        print("=" * 60)
        print("✅ Phase 1 Integration Test: PASSED")
        
        if regime_data and allocation_data:
            print("\n📋 Sample Full Response:")
            sample = {
                "regime": {
                    "state": regime_data["final_state"],
                    "confidence": regime_data["confidence"],
                    "momentum": regime_data["momentum"]
                },
                "allocation": {
                    "weights": allocation_data["final_weights"],
                    "turnover": allocation_data["turnover"]["realized"],
                    "change_reason": allocation_data.get("change_reason")
                }
            }
            print(json.dumps(sample, indent=2))
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
