import argparse
from drone.drone import main as solve_drone
from snow_plows.undirected import main as solve_snow_plow

parser = argparse.ArgumentParser(description="Solve the Montreal snow plow problem")
parser.add_argument('--mode', choices=['drone', 'snow_plow'], default='snow_plow', help="Problem to solve (default: snow_plow)")
parser.add_argument('--sector', choices=["Outremont", "Verdun", "Anjou", 
            "Rivière-des-prairies-pointe-aux-trembles", 
            "Le Plateau-Mont-Royal"], default='Outremont', help="Sector to process (default: Outremont)")
parser.add_argument('--video', action='store_true', help="Activate video rendering")
parser.add_argument('--time_limit', type=float, help='The time limit in hours for the snow plow problem', default=2.0)

args = parser.parse_args()
print("====================================================")
print(f"Mode: {args.mode}")
if args.mode == 'snow_plow':
    print(f"Sector: {args.sector}")
    print(f"Time limit: {args.time_limit} hours")
if args.video:
    print("Video rendering is enabled")

if args.mode == 'drone':
    print("Solving drone problem...")
    solve_drone(args.video)
elif args.mode == 'snow_plow':
    print(f"Solving snow plow problem for sector: {args.sector}")
    solve_snow_plow(args.sector, args.video, args.time_limit)
else:
    raise ValueError(f"Unknown mode: {args.mode}")

