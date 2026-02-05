"""
Sample Data Generator and Validator
Generate sample serial data for testing and validation
"""

import random
import time
from data_parser import DataParser


def generate_sample_data(cycles: int = 100, with_errors: bool = False) -> list:
    """
    Generate sample fatigue test data
    
    Args:
        cycles: Number of cycles to generate
        with_errors: Include error conditions
        
    Returns:
        List of sample data strings
    """
    data_lines = []
    
    # Typical starting values
    position_0_base = 180  # 1.80 mm
    force_lower_base = 250  # 25.0 N
    position_upper_base = 790  # 7.90 mm
    force_upper_base = 2200  # 220.0 N
    travel_base = 610  # 6.10 mm
    
    for cycle in range(1, cycles + 1):
        # Add realistic variation
        position_0 = position_0_base + random.randint(-5, 5)
        force_lower = force_lower_base + random.randint(-30, 30)
        travel_lower = random.randint(-3, 3)
        position_upper = position_upper_base + random.randint(-10, 10)
        force_upper = force_upper_base + random.randint(-100, 100)
        travel_upper = random.randint(-5, 5)
        travel_at_upper = travel_base + random.randint(-8, 8)
        
        # Error code
        if with_errors and cycle % 20 == 0:
            # Introduce occasional errors
            error_code = random.choice([0, 11, 12, 13])
        else:
            error_code = 0
        
        # Build data string
        status = "DTA" if cycle < cycles else "END"
        data_line = (f"{status};{cycle};{position_0};{force_lower};"
                    f"{travel_lower};{position_upper};{force_upper};"
                    f"{travel_upper};{travel_at_upper};{error_code};!")
        
        data_lines.append(data_line)
    
    return data_lines


def validate_sample_data(data_lines: list) -> None:
    """
    Validate sample data using the parser
    
    Args:
        data_lines: List of data strings to validate
    """
    parser = DataParser()
    
    print(f"Validating {len(data_lines)} data lines...\n")
    
    valid_count = 0
    error_count = 0
    validation_errors = 0
    
    for i, line in enumerate(data_lines, 1):
        # Parse
        parsed = parser.parse(line)
        
        if parsed is None:
            error_count += 1
            print(f"Line {i}: PARSE FAILED - {line}")
            continue
        
        # Validate
        is_valid, error_msg = parser.validate_data(parsed)
        
        if not is_valid:
            validation_errors += 1
            print(f"Line {i}: VALIDATION FAILED - {error_msg}")
            print(f"  Data: {line}")
        else:
            valid_count += 1
        
        # Show progress every 10 lines
        if i % 10 == 0:
            print(f"Processed {i}/{len(data_lines)} lines...")
    
    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total lines:         {len(data_lines)}")
    print(f"Valid:               {valid_count}")
    print(f"Parse errors:        {error_count}")
    print(f"Validation errors:   {validation_errors}")
    print(f"Success rate:        {(valid_count/len(data_lines)*100):.1f}%")
    print(f"{'='*60}\n")


def create_sample_file(filename: str = "sample_data.txt", cycles: int = 50):
    """
    Create a sample data file
    
    Args:
        filename: Output filename
        cycles: Number of cycles to generate
    """
    data_lines = generate_sample_data(cycles, with_errors=True)
    
    with open(filename, 'w') as f:
        for line in data_lines:
            f.write(line + '\n')
    
    print(f"Created sample file: {filename}")
    print(f"Contains {len(data_lines)} lines of test data")


def demonstrate_parsing():
    """Demonstrate parsing and data extraction"""
    print("PARSING DEMONSTRATION")
    print("=" * 60)
    
    # Sample data line
    sample = "DTA;31422;182;263;0;793;2238;0;611;0;!"
    print(f"Sample data: {sample}\n")
    
    # Parse
    parser = DataParser()
    parsed = parser.parse(sample)
    
    if parsed:
        print("Parsed successfully!")
        print(f"\nExtracted values:")
        print(f"  Status:              {parsed.status}")
        print(f"  Cycles:              {parsed.cycles}")
        print(f"  Position 1:          {parsed.position_1_mm:.2f} mm")
        print(f"  Force Lower:         {parsed.force_lower_n:.1f} N")
        print(f"  Travel 1:            {parsed.travel_1_mm:.2f} mm")
        print(f"  Position 2:          {parsed.position_2_mm:.2f} mm")
        print(f"  Force Upper:         {parsed.force_upper_n:.1f} N")
        print(f"  Travel 2:            {parsed.travel_2_mm:.2f} mm")
        print(f"  Travel at Upper:     {parsed.travel_at_upper_mm:.2f} mm")
        print(f"  Error Code:          {parsed.error_code}")
        print(f"  Loss of Stiffness:   {parsed.calculate_loss_of_stiffness():.2f}%")
        
        # Validate
        is_valid, msg = parser.validate_data(parsed)
        print(f"\nValidation: {'PASSED' if is_valid else 'FAILED'}")
        if not is_valid:
            print(f"  Error: {msg}")
        
        # Convert to dictionary
        print(f"\nAs dictionary (for CSV):")
        data_dict = parsed.to_dict()
        for key, value in data_dict.items():
            print(f"  {key:20s}: {value}")
    else:
        print("Parse FAILED!")
    
    print("=" * 60)


def performance_test(num_lines: int = 10000):
    """
    Test parsing performance
    
    Args:
        num_lines: Number of lines to parse
    """
    print(f"\nPERFORMANCE TEST ({num_lines} lines)")
    print("=" * 60)
    
    # Generate data
    data_lines = generate_sample_data(num_lines)
    
    # Time parsing
    parser = DataParser()
    start_time = time.time()
    
    for line in data_lines:
        parser.parse(line)
    
    elapsed = time.time() - start_time
    rate = num_lines / elapsed
    
    print(f"Parsed {num_lines} lines in {elapsed:.3f} seconds")
    print(f"Rate: {rate:.0f} lines/second")
    print(f"Average time per line: {(elapsed/num_lines)*1000:.3f} ms")
    print("=" * 60)


def main():
    """Main function to demonstrate all features"""
    print("\n" + "=" * 60)
    print("FATIGUE TESTER - SAMPLE DATA GENERATOR & VALIDATOR")
    print("=" * 60 + "\n")
    
    # Demonstrate parsing
    demonstrate_parsing()
    
    # Generate and validate sample data
    print("\nGENERATING SAMPLE DATA")
    print("=" * 60)
    sample_data = generate_sample_data(cycles=20, with_errors=True)
    validate_sample_data(sample_data)
    
    # Create sample file
    create_sample_file("sample_test_data.txt", cycles=100)
    
    # Performance test
    performance_test(10000)
    
    print("\nDone! Check 'sample_test_data.txt' for generated data.")


if __name__ == "__main__":
    main()
