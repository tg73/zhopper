import random
import argparse


def generate_gcode(filename, num_reps=100):
    with open(filename, 'w') as f:
        # Write the header for the G-code file
        f.write('; G-code to test for Z drift\n')
        for i in range(num_reps):
            f.write(f'PROBE_ACCURACY SAMPLE_RETRACT_DIST=10 samples=10\n')
            f.write(f'M118 {i}\n')
               
       

# Parameters

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate G-code for Z-axis testing.")
    # Add arguments for number of Z moves and Z position
    parser.add_argument('--out', type=str, default="z.gcode", help='Output filename for the G-code')
    parser.add_argument('--count', type=int, default=10, help='Number of Z moves to generate')
     
    # Parse the arguments
    args = parser.parse_args()
    

# Generate the G-code
generate_gcode(filename=args.out, num_reps=args.count)