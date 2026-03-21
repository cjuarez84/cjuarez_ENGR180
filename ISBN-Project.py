import os

# Global data structures as requested
accepted_codes = []
rejected_codes = []  # List of tuples: (invalid_code, correct_code)


def calculate_check_digit(isbn_12):
    """Calculates the 13th digit for a given 12-digit ISBN string."""
    total_sum = 0
    for i, digit in enumerate(isbn_12):
        weight = 1 if i % 2 == 0 else 3
        total_sum += int(digit) * weight

    remainder = total_sum % 10
    check_digit = (10 - remainder) % 10
    return str(check_digit)


def process_isbn_file(filename):
    """Reads the file and populates the valid and invalid lists."""
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return

    with open(filename, 'r') as file:
        for line in file:
            original_code = line.strip()
            if not original_code:
                continue

            # Remove hyphens to work with digits
            clean_code = original_code.replace("-", "")

            if len(clean_code) != 13 or not clean_code.isdigit():
                # Basic format error handling
                continue

            # Separate the first 12 digits and the provided check digit
            first_12 = clean_code[:12]
            provided_check = clean_code[12]

            # Calculate what the check digit SHOULD be
            correct_check = calculate_check_digit(first_12)

            if provided_check == correct_check:
                accepted_codes.append(original_code)
            else:
                # Construct what the correct code should have been
                # We keep the hyphen structure of the original code
                corrected_code = original_code[:-1] + correct_check
                rejected_codes.append((original_code, corrected_code))


def printAcceptedCodes():
    """Prints the list of valid ISBN-13 codes."""
    print(f"The accepted codes are: {accepted_codes}")


def searchCodes(code):
    """
    Looks for a code in both lists.
    Returns the status and the correct version if invalid.
    """
    # Check accepted list
    if code in accepted_codes:
        return f"Code {code} is VALID."

    # Check rejected list
    for invalid, correct in rejected_codes:
        if code == invalid:
            return f"Code {code} is INVALID. It should be: {correct}"

    return "Code not found in the records."

# --- Execution ---
# Note: Ensure 'ISBN-codes.txt' exists in your folder before running
# process_isbn_file('ISBN-codes.txt')
