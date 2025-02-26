import pandas as pd

def check_required_columns(df):
    """
    Check if the DataFrame has all the required columns based on the project summary.
    Expected columns: date, atom_leased, photon_leased, spin_leased, workloads_executed, total_daily_cost.
    """
    expected_columns = [
        'date', 
        'new_blocks_atom', 
        'new_blocks_photon', 
        'new_blocks_spin', 
        'workloads_older_blocks',
        'workloads_new_blocks',
        'total_daily_cost'
    ]
    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        print("Missing required columns:", missing)
        return False
    print("All required columns are present.")
    return True

def check_date_range_six_months(df):
    """
    Check that the 'date' column covers approximately 6 months.
    For example, the range should be roughly between 170 and 190 days.
    """
    df['date'] = pd.to_datetime(df['date'])
    min_date = df['date'].min()
    max_date = df['date'].max()
    num_days = (max_date - min_date).days
    if num_days < 170 or num_days > 190:
        print(f"Date range is {num_days} days, which is not approximately 6 months.")
        return False
    print(f"Date range is {num_days} days, which is approximately 6 months.")
    return True

def check_blocks_leased_range(df):
    """
    Check that the total number of QPU blocks leased per day is within the expected range (1,000 to 10,000).
    This is calculated by summing the daily leased blocks across Atom, Photon, and Spin.
    """
    df['total_blocks_leased'] = df['new_blocks_atom'] + df['new_blocks_photon'] + df['new_blocks_spin']
    if not df['total_blocks_leased'].between(1000, 10000).all():
        print("Some days have total blocks leased outside the expected range (1,000 - 10,000).")
        return False
    print("All days have total blocks leased within the expected range.")
    return True

def check_workload_range(df):
    """
    Check that the number of workloads executed per day is within the expected range (1,000,000 to 50,000,000).
    """
    if not df['total_workloads'].between(1_000_000, 50_000_000).all():
        print("Some days have workloads executed outside the expected range (1M - 50M).")
        return False
    print("All days have workloads executed within the expected range.")
    return True

def check_equal_distribution(df, tolerance=0.05):
    """
    Check that by the end of the 6-month period the cumulative number of leased blocks is equally
    distributed among the three categories (Atom, Photon, Spin). This function sums each column over all days
    and verifies that the difference from the average is within a given tolerance (default is 5%).
    """
    total_atom = df['new_blocks_atom'].sum()
    total_photon = df['new_blocks_photon'].sum()
    total_spin = df['new_blocks_spin'].sum()
    avg = (total_atom + total_photon + total_spin) / 3
    diff_atom = abs(total_atom - avg)
    diff_photon = abs(total_photon - avg)
    diff_spin = abs(total_spin - avg)
    
    if diff_atom > tolerance * avg or diff_photon > tolerance * avg or diff_spin > tolerance * avg:
        print("Cumulative distribution among Atom, Photon, and Spin is not equal within tolerance.")
        print(f"Atom: {total_atom}, Photon: {total_photon}, Spin: {total_spin}, Expected average: {avg:.2f}")
        return False
    print("Cumulative QPU block distribution among Atom, Photon, and Spin is equal within tolerance.")
    return True

def check_workload_assignment(df):
    """
    Check that the daily workload assignment follows the constraint:
      a. 50-60% of the workloads should be assigned to QPC blocks leased today.
      b. 40-50% should be assigned to QPC blocks from the older pool.
    
    This function assumes the DataFrame includes:
      - workloads_executed: total workloads executed for the day.
      - workloads_today: workloads executed on QPC blocks leased today.
      - workloads_older: workloads executed on QPC blocks from the older pool.
    
    Returns True if all days meet the constraints, otherwise prints details and returns False.
    """
    required_cols = ['total_workloads', 'workloads_new_blocks', 'workloads_older_blocks']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print("Missing required columns for workload assignment check:", missing)
        return False

    # Verify that the split adds up to the total workloads
    if not (df['workloads_new_blocks'] + df['workloads_older_blocks'] == df['total_workloads']).all():
        print("Mismatch: The sum of workloads_today and workloads_older does not equal workloads_executed on some days.")
        return False

    ratio_today = df['workloads_new_blocks'] / df['total_workloads']
    ratio_older = df['workloads_older_blocks'] / df['total_workloads']

    # Check that today's workload ratio is between 50% and 60%
    if not ratio_today.between(0.50, 0.60).all():
        print("Some days do not meet the constraint: 50-60% of workloads assigned to today's leased blocks.")
        return False

    # Check that the older pool workload ratio is between 40% and 50%
    if not ratio_older.between(0.40, 0.50).all():
        print("Some days do not meet the constraint: 40-50% of workloads assigned to older pool blocks.")
        return False

    print("All days meet the workload assignment constraints (50-60% for today's and 40-50% for older pool).")
    return True

def run_all_checks(file_path):
    """
    Load the CSV file and run all the checks.
    """
    df = pd.read_csv(file_path)
    print("Checking required columns...")
    cols_ok = check_required_columns(df)
    print("Checking date range...")
    date_ok = check_date_range_six_months(df)
    print("Checking blocks leased per day...")
    blocks_ok = check_blocks_leased_range(df)
    print("Checking workloads executed per day...")
    workload_ok = check_workload_range(df)
    print("Checking equal distribution of leased blocks...")
    distribution_ok = check_equal_distribution(df)
    
    all_checks = cols_ok and date_ok and blocks_ok and workload_ok and distribution_ok
    if all_checks:
        print("All checks passed.")
    else:
        print("Some checks failed.")
    return all_checks

# Example usage:
# file_path = 'simulated_qpu_data.csv'
# run_all_checks(file_path)

run_all_checks("simulated_qpu_data.csv")