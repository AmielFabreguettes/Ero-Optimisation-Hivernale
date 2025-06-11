from typing import Dict, List, Tuple

class VehicleOpti:
    def __init__(self, taille_km: float):
        self.speed_len = taille_km
        self.vehicles = {
            'I': {
                'cout_fixe': 500,
                'par_km': 1.1,
                'vitesse': 10,          # km/h
                'taux_horaire': [1.1, 1.3]  # [8 premières heures, le reste]
            },
            'II': {
                'cout_fixe': 800,
                'par_km': 1.3,
                'vitesse': 20,
                'taux_horaire': [1.3, 1.5]
            }
        }
    
    def calcul_dep(self, max_hours: float) -> Dict:
        """Trouver le mélange opti de Type I et Type II dans le tps imparti"""
        options = []
        
        for type_I in range(0, 10):
            for type_II in range(0, 5):
                tot_speed = type_I * self.vehicles['I']['vitesse'] + \
                              type_II * self.vehicles['II']['vitesse']
                if tot_speed == 0:
                    continue
                    
                time_need = self.speed_len / tot_speed
                if time_need <= max_hours:
                    cost = self._calc_cost(type_I, type_II, time_need)
                    options.append({
                        'type_I': type_I,
                        'type_II': type_II,
                        'time': time_need,
                        'cost': cost
                    })
        
        if not options:
            raise ValueError(f"Cannot complete route in {max_hours} hours with reasonable fleet size")
        
        optimal = min(options, key=lambda x: x['cost'])
        return optimal
    
    def _calc_cost(self, type_I: int, type_II: int, time_hours: float) -> float:
        """Calculate total cost for a vehicle combination"""
        cost = 0
        
        cost += type_I * self.vehicles['I']['cout_fixe']
        cost += type_II * self.vehicles['II']['cout_fixe']
        
        cost += self.speed_len * (type_I * self.vehicles['I']['par_km'] + 
                                    type_II * self.vehicles['II']['par_km'])
        
        for count, v_type in [(type_I, 'I'), (type_II, 'II')]:
            if count == 0:
                continue
                
            regular_hours = min(8, time_hours)
            overtime = max(0, time_hours - 8)
            
            cost += count * (
                regular_hours * self.vehicles[v_type]['taux_horaire'][0] +
                overtime * self.vehicles[v_type]['taux_horaire'][1]
            )
        
        return cost

def optimization(main_path: List[Tuple], sector: str, time_limit_hours: float, length):
    total_length_km = length / 1000
    
    optimizer = VehicleOpti(total_length_km)
    solution = optimizer.calcul_dep(time_limit_hours)
    time = '{0:02.0f}:{1:02.0f}'.format(*divmod(solution['time'] * 60, 60))
    max_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(time_limit_hours * 60, 60))
    
    print(f"\n=== Optimal Deployment for {sector} ({time_limit_hours}h limit) ===")
    print(f"Type I snowplows: {solution['type_I']}")
    print(f"Type II snowplows: {solution['type_II']}")
    print(f"Estimated time: {time} hours")
    print(f"Total cost: ${solution['cost']:.2f}")
    print(f"Total km length: {total_length_km}")
    print("="*53 + "\n")
    
    return solution