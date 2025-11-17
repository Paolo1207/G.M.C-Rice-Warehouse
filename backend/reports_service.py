# reports_service.py
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

class ReportsService:
    """
    Service for generating various reports (sales, stock, forecasts)
    """
    
    def __init__(self):
        pass
    
    def generate_sales_report(self, transactions: List[Dict], report_type: str = "daily") -> Dict:
        """
        Generate sales report with different time periods
        """
        if not transactions:
            return self._empty_report("sales", report_type)
        
        # Convert to DataFrame-like structure
        df = []
        for t in transactions:
            df.append({
                'date': datetime.strptime(t['transaction_date'], '%Y-%m-%d %H:%M:%S').date(),
                'branch_name': t['branch_name'],
                'product_name': t['product_name'],
                'quantity_sold': t['quantity_sold'],
                'unit_price': t['unit_price'],
                'total_amount': t['total_amount'],
                'customer_name': t.get('customer_name', 'N/A')
            })
        
        # Group by date and calculate totals
        daily_totals = {}
        branch_totals = {}
        product_totals = {}
        
        total_revenue = 0
        total_quantity = 0
        
        for row in df:
            date = row['date']
            branch = row['branch_name']
            product = row['product_name']
            quantity = row['quantity_sold']
            amount = row['total_amount']
            
            # Daily totals
            if date not in daily_totals:
                daily_totals[date] = {'revenue': 0, 'quantity': 0, 'transactions': 0}
            daily_totals[date]['revenue'] += amount
            daily_totals[date]['quantity'] += quantity
            daily_totals[date]['transactions'] += 1
            
            # Branch totals
            if branch not in branch_totals:
                branch_totals[branch] = {'revenue': 0, 'quantity': 0, 'transactions': 0}
            branch_totals[branch]['revenue'] += amount
            branch_totals[branch]['quantity'] += quantity
            branch_totals[branch]['transactions'] += 1
            
            # Product totals
            if product not in product_totals:
                product_totals[product] = {'revenue': 0, 'quantity': 0, 'transactions': 0}
            product_totals[product]['revenue'] += amount
            product_totals[product]['quantity'] += quantity
            product_totals[product]['transactions'] += 1
            
            total_revenue += amount
            total_quantity += quantity
        
        # Calculate averages
        avg_transaction_value = total_revenue / len(df) if df else 0
        avg_daily_revenue = total_revenue / len(daily_totals) if daily_totals else 0
        
        return {
            "report_type": f"sales_{report_type}",
            "period": self._get_period_string(report_type),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_quantity_sold": round(total_quantity, 2),
                "total_transactions": len(df),
                "avg_transaction_value": round(avg_transaction_value, 2),
                "avg_daily_revenue": round(avg_daily_revenue, 2)
            },
            "daily_totals": daily_totals,
            "branch_totals": branch_totals,
            "product_totals": product_totals,
            "transactions": df
        }
    
    def generate_stock_report(self, inventory_items: List[Dict], forecasts: List[Dict] = None) -> Dict:
        """
        Generate stock report with current levels and forecasts
        """
        if not inventory_items:
            return self._empty_report("stock", "current")
        
        # Analyze stock levels
        total_products = len(inventory_items)
        low_stock_count = 0
        out_of_stock_count = 0
        total_stock_value = 0
        
        stock_analysis = {}
        branch_stock = {}
        
        for item in inventory_items:
            stock_kg = item.get('stock', 0)
            unit_price = item.get('price', 0)
            product_name = item.get('product_name', 'Unknown')
            branch_name = item.get('branch_name', 'Unknown')
            warn_level = item.get('warn', 0)
            
            # Calculate stock value
            stock_value = stock_kg * unit_price
            total_stock_value += stock_value
            
            # Determine stock status
            if stock_kg <= 0:
                status = "out_of_stock"
                out_of_stock_count += 1
            elif warn_level and stock_kg < warn_level:
                status = "low_stock"
                low_stock_count += 1
            else:
                status = "available"
            
            # Product analysis
            if product_name not in stock_analysis:
                stock_analysis[product_name] = {
                    'total_stock': 0,
                    'total_value': 0,
                    'branches': 0,
                    'low_stock_branches': 0,
                    'out_of_stock_branches': 0
                }
            
            stock_analysis[product_name]['total_stock'] += stock_kg
            stock_analysis[product_name]['total_value'] += stock_value
            stock_analysis[product_name]['branches'] += 1
            
            if status == "low_stock":
                stock_analysis[product_name]['low_stock_branches'] += 1
            elif status == "out_of_stock":
                stock_analysis[product_name]['out_of_stock_branches'] += 1
            
            # Branch analysis
            if branch_name not in branch_stock:
                branch_stock[branch_name] = {
                    'total_products': 0,
                    'total_stock': 0,
                    'total_value': 0,
                    'low_stock_products': 0,
                    'out_of_stock_products': 0
                }
            
            branch_stock[branch_name]['total_products'] += 1
            branch_stock[branch_name]['total_stock'] += stock_kg
            branch_stock[branch_name]['total_value'] += stock_value
            
            if status == "low_stock":
                branch_stock[branch_name]['low_stock_products'] += 1
            elif status == "out_of_stock":
                branch_stock[branch_name]['out_of_stock_products'] += 1
        
        # Calculate percentages
        low_stock_percentage = (low_stock_count / total_products * 100) if total_products > 0 else 0
        out_of_stock_percentage = (out_of_stock_count / total_products * 100) if total_products > 0 else 0
        
        return {
            "report_type": "stock_analysis",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_products": total_products,
                "total_stock_value": round(total_stock_value, 2),
                "low_stock_count": low_stock_count,
                "out_of_stock_count": out_of_stock_count,
                "low_stock_percentage": round(low_stock_percentage, 2),
                "out_of_stock_percentage": round(out_of_stock_percentage, 2)
            },
            "stock_analysis": stock_analysis,
            "branch_stock": branch_stock,
            "inventory_items": inventory_items,
            "forecasts": forecasts or []
        }
    
    def generate_forecast_report(self, forecasts: List[Dict]) -> Dict:
        """
        Generate forecast report with predictions and trends
        """
        if not forecasts:
            return self._empty_report("forecast", "weekly")
        
        # Analyze forecasts
        total_forecasts = len(forecasts)
        model_types = {}
        accuracy_scores = []
        predicted_demands = []
        
        forecast_analysis = {}
        branch_forecasts = {}
        
        for forecast in forecasts:
            model_type = forecast.get('model_type', 'Unknown')
            accuracy = forecast.get('accuracy_score', 0)
            predicted_demand = forecast.get('predicted_demand', 0)
            branch_name = forecast.get('branch_name', 'Unknown')
            product_name = forecast.get('product_name', 'Unknown')
            forecast_date = forecast.get('forecast_date', '')
            
            # Model type analysis
            if model_type not in model_types:
                model_types[model_type] = 0
            model_types[model_type] += 1
            
            accuracy_scores.append(accuracy)
            predicted_demands.append(predicted_demand)
            
            # Product analysis
            if product_name not in forecast_analysis:
                forecast_analysis[product_name] = {
                    'total_forecasts': 0,
                    'avg_predicted_demand': 0,
                    'avg_accuracy': 0,
                    'branches': set()
                }
            
            forecast_analysis[product_name]['total_forecasts'] += 1
            forecast_analysis[product_name]['branches'].add(branch_name)
            
            # Branch analysis
            if branch_name not in branch_forecasts:
                branch_forecasts[branch_name] = {
                    'total_forecasts': 0,
                    'avg_predicted_demand': 0,
                    'avg_accuracy': 0,
                    'products': set()
                }
            
            branch_forecasts[branch_name]['total_forecasts'] += 1
            branch_forecasts[branch_name]['products'].add(product_name)
        
        # Calculate averages
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        avg_predicted_demand = sum(predicted_demands) / len(predicted_demands) if predicted_demands else 0
        
        # Convert sets to counts
        for product in forecast_analysis:
            forecast_analysis[product]['branches'] = len(forecast_analysis[product]['branches'])
        
        for branch in branch_forecasts:
            branch_forecasts[branch]['products'] = len(branch_forecasts[branch]['products'])
        
        return {
            "report_type": "forecast_analysis",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_forecasts": total_forecasts,
                "avg_accuracy_score": round(avg_accuracy, 3),
                "avg_predicted_demand": round(avg_predicted_demand, 2),
                "model_types_used": model_types
            },
            "forecast_analysis": forecast_analysis,
            "branch_forecasts": branch_forecasts,
            "forecasts": forecasts
        }
    
    def export_to_csv(self, report_data: Dict, report_type: str) -> str:
        """
        Export report data to CSV format
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        if report_type == "sales":
            # Write sales report CSV
            writer.writerow(['Date', 'Branch', 'Product', 'Quantity Sold', 'Unit Price', 'Total Amount', 'Customer'])
            
            for transaction in report_data.get('transactions', []):
                writer.writerow([
                    transaction['date'],
                    transaction['branch_name'],
                    transaction['product_name'],
                    transaction['quantity_sold'],
                    transaction['unit_price'],
                    transaction['total_amount'],
                    transaction['customer_name']
                ])
        
        elif report_type == "stock":
            # Write stock report CSV
            writer.writerow(['Branch', 'Product', 'Current Stock (kg)', 'Unit Price', 'Stock Value', 'Warning Level', 'Status'])
            
            for item in report_data.get('inventory_items', []):
                stock_kg = item.get('stock', 0)
                warn_level = item.get('warn', 0)
                
                if stock_kg <= 0:
                    status = "Out of Stock"
                elif warn_level and stock_kg < warn_level:
                    status = "Low Stock"
                else:
                    status = "Available"
                
                writer.writerow([
                    item.get('branch_name', ''),
                    item.get('product_name', ''),
                    stock_kg,
                    item.get('price', 0),
                    stock_kg * item.get('price', 0),
                    warn_level,
                    status
                ])
        
        elif report_type == "forecast":
            # Write forecast report CSV
            writer.writerow(['Date', 'Branch', 'Product', 'Predicted Demand', 'Confidence Lower', 'Confidence Upper', 'Model Type', 'Accuracy Score'])
            
            for forecast in report_data.get('forecasts', []):
                writer.writerow([
                    forecast.get('forecast_date', ''),
                    forecast.get('branch_name', ''),
                    forecast.get('product_name', ''),
                    forecast.get('predicted_demand', 0),
                    forecast.get('confidence_interval_lower', 0),
                    forecast.get('confidence_interval_upper', 0),
                    forecast.get('model_type', ''),
                    forecast.get('accuracy_score', 0)
                ])
        
        return output.getvalue()
    
    def _empty_report(self, report_type: str, period: str) -> Dict:
        """Return empty report structure"""
        return {
            "report_type": f"{report_type}_{period}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_revenue": 0,
                "total_quantity": 0,
                "total_transactions": 0,
                "avg_transaction_value": 0
            },
            "daily_totals": {},
            "branch_totals": {},
            "product_totals": {},
            "transactions": []
        }
    
    def _get_period_string(self, report_type: str) -> str:
        """Get period string for report"""
        if report_type == "daily":
            return f"Last 7 days ({datetime.now().strftime('%Y-%m-%d')})"
        elif report_type == "weekly":
            return f"Last 4 weeks ({datetime.now().strftime('%Y-%m-%d')})"
        elif report_type == "monthly":
            return f"Last 12 months ({datetime.now().strftime('%Y-%m-%d')})"
        else:
            return f"Custom period ({datetime.now().strftime('%Y-%m-%d')})"

# Global instance
reports_service = ReportsService()
