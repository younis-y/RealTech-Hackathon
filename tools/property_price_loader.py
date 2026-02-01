
import csv
import os
from typing import Dict, List, Optional
from statistics import mean, median

class PropertyPriceLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.year_files = {
            "2023": "pp-2023.csv",
            "2024": "pp-2024.csv",
            "2025": "pp-2025.csv"
        }

    def get_price_data(self, postcode_sector: str) -> Dict:
        """
        Get price statistics for a postcode sector (e.g., 'SW1A 1').
        
        Args:
            postcode_sector: The start of the postcode (e.g. "SW1A 1")
            
        Returns:
            Dict with average prices, volumes, and trends.
        """
        # Normalise input: remove extra spaces, ensuring uppercase
        target_sector = postcode_sector.strip().upper()
        
        results = {
            "years": {},
            "overall_avg": 0,
            "total_volume": 0
        }

        all_prices = []

        for year, filename in self.year_files.items():
            path = os.path.join(self.data_dir, filename)
            if not os.path.exists(path):
                continue
                
            year_prices = []
            
            try:
                # CSV format based on checking the header earlier:
                # 0: Transaction ID
                # 1: Price
                # 2: SQL Date
                # 3: Postcode (e.g. "NR9 5FP")
                # ...
                
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row or len(row) < 4:
                            continue
                            
                        # Check postcode match
                        # We want to match "NR9 5" against "NR9 5FP"
                        row_postcode = row[3].strip().upper()
                        
                        if not row_postcode.startswith(target_sector):
                            continue
                            
                        try:
                            price = int(row[1])
                            year_prices.append(price)
                        except ValueError:
                            continue
                            
                if year_prices:
                    results["years"][year] = {
                        "avg": int(mean(year_prices)),
                        "median": int(median(year_prices)),
                        "volume": len(year_prices),
                        "min": min(year_prices),
                        "max": max(year_prices)
                    }
                    all_prices.extend(year_prices)
                    
            except Exception as e:
                print(f"Error reading {filename}: {e}")

        if all_prices:
            results["overall_avg"] = int(mean(all_prices))
            results["total_volume"] = len(all_prices)
            
        return results

# Example usage
if __name__ == "__main__":
    # Test with a dummy directory path or the actual one if running in the right env
    loader = PropertyPriceLoader("/Users/yo84/Documents/Github/RealTech-Hackathon/Property_Price_Data")
    # Using a partial postcode from the earlier head command: "NR9 5"
    data = loader.get_price_data("NR9 5")
    print(data)
