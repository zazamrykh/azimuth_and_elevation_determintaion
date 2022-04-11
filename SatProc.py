from skyfield.api import load, Topos
from datetime import timedelta


# Начальные данные для функции flyover_data
def get_flyover_data(sat_names, observation_duration, latitude, longitude, UTC_time,
                     calculation_interval_between_flyovers, calculation_interval_during_flyovers):
    # sat_names - лист спутников, observation_duration - время наблюдения в днях, latitude и longitude -
    # широта и долгота соответственно формат - '60.0067 N' и '30.3796 E' , например, UTC_time - часовое время, МСК - 3
    # _________________________________________________
    location = Topos(latitude, longitude)  # Локация с которой мы наблюдаем
    satellite_flyover = [[] for _ in sat_names]  # Содержит информацию о пролетах спутника
    time_flyover = [[] for _ in sat_names]  # Содержит длительность пролетов
    time_start_flyover = [[] for _ in sat_names]  # Содержит начальные данные о пролете

    # Загружаем данные
    tle_file = "https://celestrak.com/NORAD/elements/active.txt"  # Сайт с TLE
    satellites = load.tle(tle_file)  # Загрузка TLE с сайта

    # Получения информации о пролетах спутников в формате: время    азимут  элевация
    # После этого цикла она получается неотсортированная
    for sat_num in range(len(sat_names)):
        # Находим наш спутник по имени в данных
        print("loaded {} sats from {}".format(len(satellites), tle_file))  # Индикатор загрузки TLE
        satellite = satellites[sat_names[sat_num]]

        # Получение текущего времени (по UTC)
        ts = load.timescale()
        instant_time = ts.now()

        remaining_observation_time = observation_duration * 24 * 60 * 60  # Перевод времени наблюдения в секунды
        iterator = calculation_interval_between_flyovers  # Итератор уменьшиает время наблюдения до нуля
        flyover_num = 0  # Счетчик пролетов
        # Дефолтные значения времени начала и конца пролета
        time_in_beginning_of_flyover = ts.now()
        time_at_the_end_of_flyover = ts.utc(instant_time.utc_datetime() + timedelta(seconds=remaining_observation_time))
        satellite_over_the_horizon = False  # Если спутник начал прохождение над Землёй,
        # то satellite_over_the_horizon = True, если нет, то satellite_over_the_horizon = False
        # Условие satellite_over_the_horizon == True в главном цикле нужно, чтобы программа выполнилась до конца
        # в случае, когда окончание времени наблюдения приходится на незаконченный пролет спутника
        while remaining_observation_time > 0 or satellite_over_the_horizon:  # Пока время наблюдения не прошло
            # и не закончилась запись последнего пролета
            # Находим азимут, элевацию и расстояние
            difference = satellite - location
            topocentric = difference.at(instant_time)
            alt, az, distance = topocentric.altaz()

            if not satellite_over_the_horizon and alt.degrees > 0:  # Попадаем после выхода спутника из-за горизонта
                satellite_over_the_horizon = True  # Индикатор satellite_over_the_horizon изменился на True,
                satellite_flyover[sat_num].append([])  # Значит спутник выше горизонта
                time_start_flyover[sat_num].append([])
                time_start_flyover[sat_num][flyover_num] = ts.utc(instant_time.utc_datetime())
                time_at_the_end_of_flyover = ts.utc(instant_time.utc_datetime())
            if alt.degrees > 0:
                iterator = calculation_interval_during_flyovers
                # Устанавливается значение итератора после выхода спутника из-за горизонта
                satellite_flyover[sat_num][flyover_num].append(
                    str(instant_time.utc_datetime() + timedelta(hours=UTC_time)) + '    ' + "%16s" % str(az) +
                    '    ' + "%16s" % str(alt))
            if alt.degrees < 0:  # Спутник за горизонтом
                if satellite_over_the_horizon:  # Сюда попадаем один раз после последнего пролета
                    time_passage = (time_in_beginning_of_flyover - time_at_the_end_of_flyover) * 24 * 60 * 60
                    time_flyover[sat_num].append(time_passage)
                    flyover_num += 1
                iterator = calculation_interval_between_flyovers
                # Устанавливается значение итератора после захода спутника за горизонт
                satellite_over_the_horizon = False
            remaining_observation_time -= iterator
            instant_time = ts.utc(instant_time.utc_datetime() + timedelta(seconds=iterator))
            if alt.degrees > 0:
                time_in_beginning_of_flyover = instant_time

    # Общие массивы со спутниками
    all_satellite_flyover = []
    all_time_flyover = []
    all_time_start_flyover = []
    all_satellite_names = []

    for sat_num in range(len(sat_names)):
        for flyover_num in range(len(satellite_flyover[sat_num])):
            all_satellite_flyover.append(satellite_flyover[sat_num][flyover_num])
            all_time_start_flyover.append(time_start_flyover[sat_num][flyover_num])
            all_time_flyover.append(time_flyover[sat_num][flyover_num])
            all_satellite_names.append(sat_names[sat_num])

    iterator_in_sort = 1  # Сортировка листов пролетов, имен, продолжительности, начальных времен
    for i in range(len(all_satellite_flyover)):
        for j in range(len(all_satellite_flyover) - iterator_in_sort):
            if all_time_start_flyover[j + 1].utc_datetime() < all_time_start_flyover[j].utc_datetime():
                all_time_start_flyover[j + 1], all_time_start_flyover[j] = [all_time_start_flyover[j],
                                                                            all_time_start_flyover[j + 1]]
                all_time_flyover[j + 1], all_time_flyover[j] = all_time_flyover[j], all_time_flyover[j + 1]
                all_satellite_flyover[j + 1], all_satellite_flyover[j] = [all_satellite_flyover[j],
                                                                          all_satellite_flyover[j + 1]]
                all_satellite_names[j + 1], all_satellite_names[j] = all_satellite_names[j], all_satellite_names[j + 1]
        iterator_in_sort += 1

    return all_satellite_names, all_time_start_flyover, all_satellite_flyover, all_time_flyover


def remove_collision(sat_names, time_start_flyovers, satellite_flyovers, duration_flyovers):
    for sat_num in range(len(satellite_flyovers)):
        remove_was = True
        # remove_was = True, если было удаление элемента, в начале True, чтобы зашло дальше в цикл
        # remove_was нужен чтобы в случае удаления элемента из листа, еще раз пройтись по этому же месту
        while remove_was:
            remove_was = False
            if sat_num + 1 < len(satellite_flyovers):
                if (time_start_flyovers[sat_num].utc_datetime() < time_start_flyovers[sat_num + 1].utc_datetime() <
                        time_start_flyovers[sat_num].utc_datetime() + timedelta(seconds=duration_flyovers[sat_num])):
                    if duration_flyovers[sat_num] < duration_flyovers[sat_num + 1]:
                        satellite_flyovers.pop(sat_num)
                        time_start_flyovers.pop(sat_num)
                        duration_flyovers.pop(sat_num)
                        sat_names.pop(sat_num)
                    else:
                        satellite_flyovers.pop(sat_num + 1)
                        time_start_flyovers.pop(sat_num + 1)
                        duration_flyovers.pop(sat_num + 1)
                        sat_names.pop(sat_num + 1)
                    remove_was = True
    return sat_names, time_start_flyovers, satellite_flyovers, duration_flyovers


def get_flyover_data_without_collision(sat_names, observation_duration, latitude, longitude, UTC_time,
                                       calculation_interval_between_flyovers, calculation_interval_during_flyovers):
    sat_names, time_start_flyovers, satellite_flyovers, duration_flyovers = get_flyover_data(sat_names,
                                                                                             observation_duration,
                                                                                             latitude, longitude,
                                                                                             UTC_time,
                                                                                calculation_interval_between_flyovers,
                                                                                calculation_interval_during_flyovers)
    return remove_collision(sat_names, time_start_flyovers, satellite_flyovers, duration_flyovers)
