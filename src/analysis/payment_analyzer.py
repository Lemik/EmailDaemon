from typing import Dict, Any, List
from datetime import datetime
from ..data.access.payment_access import PaymentAccess
from ..data.access.agreement_access import AgreementAccess
from ..data.access.cache import DataCache
from ..core.exceptions import AnalysisError
from ..core.constants import PaymentStatus

class PaymentAnalyzer:
    def __init__(self):
        self.payment_access = PaymentAccess()
        self.agreement_access = AgreementAccess()
        self.cache = DataCache()

    def analyze_payment_timeliness(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze if payment was made on time.
        
        Args:
            payment_data: Payment data dictionary
            
        Returns:
            Analysis results
        """
        try:
            # Get agreement details
            agreement_id = payment_data.get('agreement_id')
            if not agreement_id:
                raise AnalysisError("Agreement ID required")
            agreement = self.agreement_access.get_agreement_by_id(str(agreement_id))
            if not agreement:
                raise AnalysisError("Agreement not found")

            # Calculate due date (typically 1st of the month)
            payment_date = payment_data['payment_date']
            due_date = datetime(payment_date.year, payment_date.month, 1)
            
            # Determine status
            if payment_date <= due_date:
                status = PaymentStatus.ON_TIME
            else:
                status = PaymentStatus.LATE

            pid = payment_data.get('id_payment_history')
            tid = payment_data.get('tenant_id')
            return {
                'payment_id': pid,
                'tenant_id': tid,
                'due_date': due_date,
                'payment_date': payment_date,
                'status': status,
                'days_late': (payment_date - due_date).days if status == PaymentStatus.LATE else 0
            }
        except Exception as e:
            raise AnalysisError(f"Failed to analyze payment timeliness: {str(e)}")

    def analyze_payment_amounts(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze if payment amount matches agreement.
        
        Args:
            payment_data: Payment data dictionary
            
        Returns:
            Analysis results
        """
        try:
            # Get agreement details
            agreement_id = payment_data.get('agreement_id')
            if not agreement_id:
                raise AnalysisError("Agreement ID required")
            agreement = self.agreement_access.get_agreement_by_id(str(agreement_id))
            if not agreement:
                raise AnalysisError("Agreement not found")

            expected_amount = agreement['amount']
            actual_amount = payment_data['amount']
            
            # Determine status
            if actual_amount == expected_amount:
                status = PaymentStatus.ON_TIME
            elif actual_amount < expected_amount:
                status = PaymentStatus.PARTIAL
            else:
                status = PaymentStatus.INCORRECT

            pid = payment_data.get('id_payment_history')
            tid = payment_data.get('tenant_id')
            return {
                'payment_id': pid,
                'tenant_id': tid,
                'expected_amount': expected_amount,
                'actual_amount': actual_amount,
                'status': status,
                'difference': actual_amount - expected_amount
            }
        except Exception as e:
            raise AnalysisError(f"Failed to analyze payment amounts: {str(e)}")

    def generate_payment_trends(self, tenant_id: str) -> Dict[str, Any]:
        """
        Generate payment behavior trends for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Trend analysis results
        """
        try:
            # Check cache first
            cache_key = f"trends_{tenant_id}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data

            # Get historical payments
            payments = self.payment_access.get_payments_by_period(
                datetime.now().month,
                datetime.now().year
            )

            # Calculate trends
            total_payments = len(payments)
            on_time_payments = sum(1 for p in payments if p['status'] == PaymentStatus.ON_TIME)
            late_payments = sum(1 for p in payments if p['status'] == PaymentStatus.LATE)
            
            trends = {
                'total_payments': total_payments,
                'on_time_percentage': (on_time_payments / total_payments * 100) if total_payments > 0 else 0,
                'late_percentage': (late_payments / total_payments * 100) if total_payments > 0 else 0,
                'average_days_late': sum(
                    (p['payment_date'] - datetime(p['payment_date'].year, p['payment_date'].month, 1)).days
                    for p in payments if p['status'] == PaymentStatus.LATE
                ) / late_payments if late_payments > 0 else 0
            }

            # Cache results
            self.cache.set(cache_key, trends)
            
            return trends
        except Exception as e:
            raise AnalysisError(f"Failed to generate payment trends: {str(e)}") 