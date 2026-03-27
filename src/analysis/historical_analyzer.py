from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..data.access.payment_access import PaymentAccess
from ..data.access.agreement_access import AgreementAccess
from ..data.access.cache import DataCache
from ..core.exceptions import AnalysisError
from ..core.constants import PaymentStatus

class HistoricalAnalyzer:
    def __init__(self):
        self.payment_access = PaymentAccess()
        self.agreement_access = AgreementAccess()
        self.cache = DataCache()

    def analyze_historical_trends(self, start_date: datetime, 
                                end_date: datetime) -> Dict[str, Any]:
        """
        Analyze payment trends over a historical period.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Historical trend analysis results
        """
        try:
            # Check cache first
            cache_key = f"historical_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

            # Get all payments in period
            payments = []
            current_date = start_date
            while current_date <= end_date:
                month_payments = self.payment_access.get_payments_by_period(
                    current_date.month,
                    current_date.year
                )
                payments.extend(month_payments)
                current_date += timedelta(days=32)  # Move to next month
                current_date = current_date.replace(day=1)

            # Calculate trends
            total_payments = len(payments)
            on_time_payments = sum(1 for p in payments if p['status'] == PaymentStatus.ON_TIME)
            late_payments = sum(1 for p in payments if p['status'] == PaymentStatus.LATE)
            
            # Calculate monthly averages
            monthly_data = {}
            for payment in payments:
                month_key = f"{payment['payment_date'].year}-{payment['payment_date'].month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'total': 0,
                        'on_time': 0,
                        'late': 0,
                        'amounts': []
                    }
                monthly_data[month_key]['total'] += 1
                if payment['status'] == PaymentStatus.ON_TIME:
                    monthly_data[month_key]['on_time'] += 1
                elif payment['status'] == PaymentStatus.LATE:
                    monthly_data[month_key]['late'] += 1
                monthly_data[month_key]['amounts'].append(payment['amount'])

            # Calculate reliability score
            reliability_score = self.calculate_payment_reliability(payments)

            trends = {
                'total_payments': total_payments,
                'on_time_percentage': (on_time_payments / total_payments * 100) if total_payments > 0 else 0,
                'late_percentage': (late_payments / total_payments * 100) if total_payments > 0 else 0,
                'monthly_breakdown': monthly_data,
                'reliability_score': reliability_score
            }

            # Cache results
            self.cache.set(cache_key, trends)
            
            return trends
        except Exception as e:
            raise AnalysisError(f"Failed to analyze historical trends: {str(e)}")

    def calculate_payment_reliability(self, payments: List[Dict[str, Any]]) -> float:
        """
        Calculate payment reliability score based on historical data.
        
        Args:
            payments: List of payment records
            
        Returns:
            Reliability score (0-100)
        """
        try:
            if not payments:
                return 0.0

            # Calculate weights for different factors
            on_time_weight = 0.6
            amount_weight = 0.4

            # Calculate on-time score
            on_time_payments = sum(1 for p in payments if p['status'] == PaymentStatus.ON_TIME)
            on_time_score = (on_time_payments / len(payments)) * 100

            # Calculate amount accuracy score
            correct_amounts = sum(1 for p in payments if p['status'] != PaymentStatus.INCORRECT)
            amount_score = (correct_amounts / len(payments)) * 100

            # Calculate final score
            reliability_score = (
                (on_time_score * on_time_weight) +
                (amount_score * amount_weight)
            )

            return reliability_score
        except Exception as e:
            raise AnalysisError(f"Failed to calculate reliability score: {str(e)}") 