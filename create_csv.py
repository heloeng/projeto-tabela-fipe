import csv
from datetime import datetime, timedelta

# Definições
id_user = 2
id_store = 1
id_vehicles = [1,2,4,5,6,33,205,236,237,238,239,240,241,242,243,244,245,246,247,248,249]  # De 1 a 21
start_year = 2020
end_year = 2025
output_file = "vehicles_data.csv"

# Gerar os dados
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["id_user", "id_store", "id_vehicle", "year_man", "price", "reg_date"])  # Cabeçalho
    
    for id_vehicle in id_vehicles:
        for year in range(start_year, end_year + 1):
            for i in range(3):  # 3 linhas por mês
                for j in range(1,10):
                    year_man = year + i  # Ano de fabricação aumentando a cada linha
                    price = round(30000 + (id_vehicle * 500) + (i * 1000), 2)  # Preço fictício variando
                    reg_date = f"{year}-0{j}-{(i+1)*1:02d}"  # Datas fixas dentro do mês
                    writer.writerow([id_user, id_store, id_vehicle, year_man, price, reg_date])
                for j in range(10,13):
                    year_man = year + i  # Ano de fabricação aumentando a cada linha
                    price = round(30000 + (id_vehicle * 500) + (i * 1000), 2)  # Preço fictício variando
                    reg_date = f"{year}-{j}-{(i+1)*1:02d}"  # Datas fixas dentro do mês
                    writer.writerow([id_user, id_store, id_vehicle, year_man, price, reg_date])


print(f"Arquivo '{output_file}' gerado com sucesso!")
