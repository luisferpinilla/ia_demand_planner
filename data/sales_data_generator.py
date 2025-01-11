import csv
import random
from datetime import datetime, timedelta

# Define the file path
file_path = 'data/ventas.csv'

# Create the data directory if it doesn't exist
# import os
# os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Define the products, clients, and date range
products = [f'P{i:03d}' for i in range(1, 21)]
clients = [f'C{i:03d}' for i in range(1, 11)]
start_date = datetime.strptime('202001', '%Y%m')
end_date = datetime.strptime('202412', '%Y%m')

# Generate the data
data = []


for product in products:
    sale_price = round(random.uniform(10, 100), 2)
    for client in clients: 
        current_date = start_date        
        while current_date <= end_date:   
            quantity_sold = random.randint(1, 100)            
            data.append([product, client, current_date.strftime('%Y%m'), quantity_sold, sale_price, quantity_sold*sale_price])
        
            current_date += timedelta(days=30)  # Approximate month increment

# Write the data to the CSV file
with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['CodigoProducto', 'CodigoCliente', 'Fecha', 'CantidadVendida', 'PrecioVenta', 'IngresoGenerado' ])
    writer.writerows(data)

print(f'Data written to {file_path}')