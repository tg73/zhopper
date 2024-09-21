import random
import argparse


def generate_z_moves_gcode(filename, num_moves=100, z_pos=1, z_home_position=0):
    with open(filename, 'w') as f:
        # Write the header for the G-code file
        f.write('; G-code to test for Z drift\n')
        for i in range(num_moves):
            if i % 10 == 0: 
              dwell=1000
            else:
              dwell=0
            
            f.write(f'G0 Z{z_pos}\n')
 #           if dwell != 0: f.write(f'G4 P{dwell}\n')
            f.write(f'G0 Z{z_home_position}\n')
            if dwell != 0: 
               f.write(f'M117 {i}\n')
               f.write(f'G4 P{dwell}\n')
               
        f.write('M400 ; Wait for all movements to finish\n')
        f.write('; Test complete\n')


# Parameters

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate G-code for Z-axis testing.")
    # Add arguments for number of Z moves and Z position
    parser.add_argument('--out', type=str, default="z.gcode", help='Output filename for the G-code')
    parser.add_argument('--count', type=int, default=10, help='Number of Z moves to generate')
    parser.add_argument('--zpos', type=float, default=1, help='Z position for the moves')
    
    # Parse the arguments
    args = parser.parse_args()
    

# Generate the G-code
generate_z_moves_gcode(filename=args.out, num_moves=args.count, z_pos=args.zpos)