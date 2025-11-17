#!/usr/bin/env python3
"""
Test the dashboard API endpoints to ensure real data integration works
"""

import requests
import json
from datetime import date, timedelta

def test_api_endpoints():
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Dashboard API Endpoints")
    print("=" * 50)
    
    # Test 1: KPI endpoint without branch filter (admin view)
    print("\n1. Testing KPI endpoint (Admin view - all branches)")
    try:
        response = requests.get(f"{base_url}/admin/api/dashboard/kpis")
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                kpis = data['kpis']
                print(f"✅ Today's Sales: ₱{kpis['today_sales']:,.2f}")
                print(f"✅ Month Sales: ₱{kpis['month_sales']:,.2f}")
                print(f"✅ Low Stock Items: {kpis['low_stock_count']}")
                print(f"✅ Forecast Accuracy: {kpis['forecast_accuracy']}%")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 2: KPI endpoint with branch filter (manager view)
    print("\n2. Testing KPI endpoint (Manager view - branch 1)")
    try:
        response = requests.get(f"{base_url}/admin/api/dashboard/kpis?branch_id=1")
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                kpis = data['kpis']
                print(f"✅ Today's Sales (Branch 1): ₱{kpis['today_sales']:,.2f}")
                print(f"✅ Month Sales (Branch 1): ₱{kpis['month_sales']:,.2f}")
                print(f"✅ Low Stock Items (Branch 1): {kpis['low_stock_count']}")
                print(f"✅ Forecast Accuracy (Branch 1): {kpis['forecast_accuracy']}%")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 3: Charts endpoint without branch filter
    print("\n3. Testing Charts endpoint (Admin view - all branches)")
    try:
        response = requests.get(f"{base_url}/admin/api/dashboard/charts?days=7")
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                charts = data['charts']
                print(f"✅ Sales Trend Data Points: {len(charts['sales_trend'])}")
                print(f"✅ Forecast vs Actual Data Points: {len(charts['forecast_vs_actual'])}")
                print(f"✅ Top Products: {len(charts['top_products'])}")
                
                # Show sample data
                if charts['sales_trend']:
                    sample_sales = charts['sales_trend'][0]
                    print(f"   Sample Sales Data: {sample_sales}")
                
                if charts['top_products']:
                    sample_product = charts['top_products'][0]
                    print(f"   Top Product: {sample_product['name']} - {sample_product['quantity']} kg")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 4: Charts endpoint with branch filter
    print("\n4. Testing Charts endpoint (Manager view - branch 1)")
    try:
        response = requests.get(f"{base_url}/admin/api/dashboard/charts?branch_id=1&days=7")
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                charts = data['charts']
                print(f"✅ Sales Trend Data Points (Branch 1): {len(charts['sales_trend'])}")
                print(f"✅ Forecast vs Actual Data Points (Branch 1): {len(charts['forecast_vs_actual'])}")
                print(f"✅ Top Products (Branch 1): {len(charts['top_products'])}")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")

if __name__ == "__main__":
    test_api_endpoints()
