from SatProc import get_flyover_data_without_collision

# Начальные данные
sat_names = ["ISS (ZARYA)", "CALSPHERE 1", "NOAA 19"]  # Названия спутников, за которыми мы будем наблюдать
observation_duration = 1  # Время наблюдения в днях
latitude = '60.0067 N'  # Широта места наблюдения
longitude = '30.3796 E'  # Долгота места наблюдения
UTC_time = 3  # Часовой пояс
calculation_interval_between_flyovers = 30  # Интервал времени расчета между пролетов спутника
calculation_interval_during_flyovers = 1  # Интервал времени расчета во время пролета спутника

# Рассчет
sat_names, time_start_flyovers, satellite_flyovers, duration_flyovers = get_flyover_data_without_collision(
    sat_names, observation_duration, latitude, longitude, UTC_time, calculation_interval_between_flyovers,
    calculation_interval_during_flyovers)

# Запись данных в файл
# 32 символа приходится на дату, затем 4 пробела, затем 16 на азимут, затем 4 символа пробел, затем 16 на элевацию
file_out_with_sorted_flyovers = open('sorted_satellite_flyovers.txt', 'w')
for flyover_num in range(len(satellite_flyovers)):
    print(sat_names[flyover_num], file=file_out_with_sorted_flyovers)
    for num_instantaneous_satellite_coordinates in range(len(satellite_flyovers[flyover_num])):
        print(satellite_flyovers[flyover_num][num_instantaneous_satellite_coordinates],
              file=file_out_with_sorted_flyovers)
    print(duration_flyovers[flyover_num], file=file_out_with_sorted_flyovers)
    print('\n\n\n', file=file_out_with_sorted_flyovers)
print("Файл sorted_satellite_flyovers.txt с данными о пролетах получен")
