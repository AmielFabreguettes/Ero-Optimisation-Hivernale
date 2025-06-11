# ❄️ Optimisation hivernale

The solver offers two operating modes:
- **Snow plow mode**: Optimizes snow removal routes for ground vehicles
- **Drone mode**: Calculates optimal routes for surveillance or intervention drones


### Basic syntax

```bash
python main.py [OPTIONS]
```

### Available options

| Option | Type | Default value | Description |
|--------|------|---------------|-------------|
| `--mode` | `drone` \| `snow_plow` | `snow_plow` | Type of problem to solve |
| `--sector` | Montreal sector | `Outremont` | Geographic sector to process |
| `--video` | Flag | Disabled | Enable video rendering of results |
| `--time_limit` | Float | `2.0` | Time limit in hours for the snow plow problem |

### Supported sectors

- **Outremont**
- **Verdun** 
- **Anjou**
- **Rivière-des-prairies-pointe-aux-trembles**
- **Le Plateau-Mont-Royal**

## Usage examples

### Basic example
```bash
python main.py
```
Runs the solver in snow plow mode for the Outremont sector.

### Drone mode with visualization
```bash
python main.py --mode drone --sector "Le Plateau-Mont-Royal" --video
```

### Custom time limit
```bash
python main.py --sector Verdun --time_limit 3.5
```

### Complete processing with video and custom time limit
```bash
python main.py --mode snow_plow --sector Anjou --video --time_limit 1.5
```