import datetime
from database import get_income_data, get_tenant_agreements, log_analysis_results

def analyze_rental_income():
    """
    Analyze rental income data against tenant agreements.
    """
    # Get the current month and year
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    # Fetch income data and tenant agreements
    income_data = get_income_data(month=current_month, year=current_year)
    tenant_agreements = get_tenant_agreements()

    analysis_results = []

    for tenant in tenant_agreements:
        tenant_id = tenant['id']
        expected_amount = tenant['monthly_rent']
        due_date = tenant['due_date']

        # Filter income data for the tenant
        tenant_income = [entry for entry in income_data if entry['tenant_id'] == tenant_id]

        if not tenant_income:
            # No payment found
            analysis_results.append({
                'tenant_id': tenant_id,
                'status': 'missing',
                'details': f"No payment received for {current_month}/{current_year}."
            })
            continue

        for payment in tenant_income:
            payment_date = payment['date']
            payment_amount = payment['amount']

            if payment_date > due_date:
                status = 'late'
            elif payment_amount != expected_amount:
                status = 'incorrect'
            else:
                status = 'on_time'

            analysis_results.append({
                'tenant_id': tenant_id,
                'status': status,
                'details': f"Payment of {payment_amount} received on {payment_date}."
            })

    # Log the analysis results
    log_analysis_results(analysis_results)

if __name__ == "__main__":
    analyze_rental_income()