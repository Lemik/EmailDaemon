from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..data.access.payment_access import PaymentAccess
from ..data.access.agreement_access import AgreementAccess
from ..data.access.cache import DataCache
from ..core.exceptions import AnalysisError
from ..core.constants import PaymentStatus

class PatternRecognizer:
    def __init__(self):
        self.payment_access = PaymentAccess()
        self.agreement_access = AgreementAccess()
        self.cache = DataCache()

    def identify_late_payment_patterns(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Identify patterns in late payments for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of identified patterns
        """
        try:
            # Get historical payments
            payments = []
            current_date = datetime.now() - timedelta(days=365)  # Last year
            while current_date <= datetime.now():
                month_payments = self.payment_access.get_payments_by_period(
                    current_date.month,
                    current_date.year
                )
                payments.extend(month_payments)
                current_date += timedelta(days=32)  # Move to next month
                current_date = current_date.replace(day=1)

            # Filter late payments
            late_payments = [p for p in payments if p['status'] == PaymentStatus.LATE]
            
            # Identify patterns
            patterns = []
            
            # Pattern 1: Consistent late payments
            if len(late_payments) >= 3:
                consecutive_late = self._check_consecutive_late_payments(late_payments)
                if consecutive_late:
                    patterns.append({
                        'type': 'consistent_late',
                        'description': 'Consistent late payments detected',
                        'details': consecutive_late
                    })
            
            # Pattern 2: Increasing lateness
            increasing_late = self._check_increasing_lateness(late_payments)
            if increasing_late:
                patterns.append({
                    'type': 'increasing_late',
                    'description': 'Increasing delay in payments detected',
                    'details': increasing_late
                })
            
            # Pattern 3: Seasonal pattern
            seasonal = self._check_seasonal_pattern(late_payments)
            if seasonal:
                patterns.append({
                    'type': 'seasonal',
                    'description': 'Seasonal pattern in late payments detected',
                    'details': seasonal
                })
            
            return patterns
        except Exception as e:
            raise AnalysisError(f"Failed to identify late payment patterns: {str(e)}")

    def detect_payment_anomalies(self, payment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect unusual payment patterns.
        
        Args:
            payment_data: Current payment data
            
        Returns:
            List of detected anomalies
        """
        try:
            anomalies = []
            
            # Get historical payments for comparison
            historical_payments = self.payment_access.get_payments_by_period(
                payment_data['payment_date'].month,
                payment_data['payment_date'].year
            )
            
            # Check for amount anomaly
            if self._is_amount_anomaly(payment_data, historical_payments):
                anomalies.append({
                    'type': 'amount_anomaly',
                    'description': 'Unusual payment amount detected',
                    'details': {
                        'current_amount': payment_data['amount'],
                        'historical_average': self._calculate_average_amount(historical_payments)
                    }
                })
            
            # Check for timing anomaly
            if self._is_timing_anomaly(payment_data, historical_payments):
                anomalies.append({
                    'type': 'timing_anomaly',
                    'description': 'Unusual payment timing detected',
                    'details': {
                        'current_date': payment_data['payment_date'],
                        'historical_average_days': self._calculate_average_days(historical_payments)
                    }
                })
            
            return anomalies
        except Exception as e:
            raise AnalysisError(f"Failed to detect payment anomalies: {str(e)}")

    def _check_consecutive_late_payments(self, late_payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for consecutive late payments."""
        consecutive = []
        current_streak = []
        
        for payment in sorted(late_payments, key=lambda x: x['payment_date']):
            if not current_streak:
                current_streak.append(payment)
            else:
                last_payment = current_streak[-1]
                if (payment['payment_date'] - last_payment['payment_date']).days <= 35:  # Allow for some variance
                    current_streak.append(payment)
                else:
                    if len(current_streak) >= 3:
                        consecutive.append(current_streak)
                    current_streak = [payment]
        
        if len(current_streak) >= 3:
            consecutive.append(current_streak)
        
        return {
            'streaks': consecutive,
            'total_streaks': len(consecutive)
        }

    def _check_increasing_lateness(self, late_payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for increasing delay in late payments."""
        if len(late_payments) < 3:
            return None
            
        sorted_payments = sorted(late_payments, key=lambda x: x['payment_date'])
        days_late = [(p['payment_date'] - datetime(p['payment_date'].year, p['payment_date'].month, 1)).days 
                    for p in sorted_payments]
        
        # Check if days late are increasing
        increasing = all(days_late[i] <= days_late[i+1] for i in range(len(days_late)-1))
        
        if increasing:
            return {
                'start_date': sorted_payments[0]['payment_date'],
                'end_date': sorted_payments[-1]['payment_date'],
                'days_late_trend': days_late
            }
        return None

    def _check_seasonal_pattern(self, late_payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for seasonal patterns in late payments."""
        if len(late_payments) < 12:  # Need at least a year of data
            return None
            
        monthly_counts = {}
        for payment in late_payments:
            month = payment['payment_date'].month
            if month not in monthly_counts:
                monthly_counts[month] = 0
            monthly_counts[month] += 1
        
        # Check for significant variation
        avg_count = sum(monthly_counts.values()) / len(monthly_counts)
        high_months = [m for m, count in monthly_counts.items() if count > avg_count * 1.5]
        
        if high_months:
            return {
                'high_months': high_months,
                'monthly_counts': monthly_counts,
                'average_count': avg_count
            }
        return None

    def _is_amount_anomaly(self, payment: Dict[str, Any], 
                          historical_payments: List[Dict[str, Any]]) -> bool:
        """Check if payment amount is anomalous."""
        if not historical_payments:
            return False
            
        avg_amount = self._calculate_average_amount(historical_payments)
        std_dev = self._calculate_std_dev(historical_payments, avg_amount)
        
        return abs(payment['amount'] - avg_amount) > 2 * std_dev

    def _is_timing_anomaly(self, payment: Dict[str, Any], 
                          historical_payments: List[Dict[str, Any]]) -> bool:
        """Check if payment timing is anomalous."""
        if not historical_payments:
            return False
            
        avg_days = self._calculate_average_days(historical_payments)
        std_dev = self._calculate_std_dev_days(historical_payments, avg_days)
        
        payment_day = (payment['payment_date'] - datetime(payment['payment_date'].year, 
                                                        payment['payment_date'].month, 1)).days
        return abs(payment_day - avg_days) > 2 * std_dev

    def _calculate_average_amount(self, payments: List[Dict[str, Any]]) -> float:
        """Calculate average payment amount."""
        return sum(p['amount'] for p in payments) / len(payments) if payments else 0

    def _calculate_std_dev(self, payments: List[Dict[str, Any]], mean: float) -> float:
        """Calculate standard deviation of payment amounts."""
        if not payments:
            return 0
        variance = sum((p['amount'] - mean) ** 2 for p in payments) / len(payments)
        return variance ** 0.5

    def _calculate_average_days(self, payments: List[Dict[str, Any]]) -> float:
        """Calculate average days into month for payments."""
        days = [(p['payment_date'] - datetime(p['payment_date'].year, p['payment_date'].month, 1)).days 
               for p in payments]
        return sum(days) / len(days) if days else 0

    def _calculate_std_dev_days(self, payments: List[Dict[str, Any]], mean: float) -> float:
        """Calculate standard deviation of payment days."""
        if not payments:
            return 0
        days = [(p['payment_date'] - datetime(p['payment_date'].year, p['payment_date'].month, 1)).days 
               for p in payments]
        variance = sum((day - mean) ** 2 for day in days) / len(days)
        return variance ** 0.5 