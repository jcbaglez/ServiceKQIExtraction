########################################################################################################################
# Author: O.S. Penaherrera
# Institution: University of Malaga
# Date: 07/2020
########################################################################################################################

import csv
import re
from pathlib import Path


class LogMetrics:
    params = ['Video bitrate', 'Audio latency', 'Estimated host PC frame rate', 'Incoming frame rate from network',
              'Decoding frame rate', 'Rendering frame rate', 'Frames dropped by your network connection',
              'Frames dropped due to network jitter', 'Average receive time', 'Average decoding time',
              'Average frame queue delay', 'Average rendering time (including monitor V-sync latency)']

    paramsMask = ['Video bitrate', 'Audio latency', 'Host frame rate', 'Incoming frame rate from network',
                  'Decoding frame rate', 'Server frame rate', 'Frames dropped by network connection',
                  'Frames dropped due to network jitter', 'Network latency', 'Decoding time',
                  'Frame queue delay', 'Average rendering time (including monitor V-sync latency)']

    def __init__(self, name, path, resolution, fps):
        self.game = ''
        self.numl = 0  # Line index from list, which contains data
        self.param_num = 0  # Parameters List index (param_header)
        self.param_header = {self.numl: ["Time", "Parameter", "Value", 'Unit']}
        self.dictionary = {}.fromkeys(self.params)
        self.set_name(name)
        self.path = path
        self.res = resolution
        self.fps = fps
        self.file = self.get_file(self.filter_dir(self.read_dir(path)))
        self.get_metrics()
        self.timeStamp = ''

    @staticmethod
    def read_dir(path_dir):
        return [obj.name for obj in Path(path_dir).iterdir()]

    @staticmethod
    def filter_dir(list_directories):
        list_f = []
        for eachFile in list_directories:
            if eachFile.startswith('Moonlight') and not eachFile.__contains__("Client"):
                list_f.append(eachFile)
        return list_f

    def get_file(self, filtered_list):
        list_stamp = []
        for eachFile in filtered_list:
            pos = eachFile.find('-')
            list_stamp.append(int(eachFile[pos + 1: eachFile.find('.')]))
        self.timeStamp = str(max(list_stamp))
        return self.path + '/Moonlight-' + self.timeStamp + '.log'

    def set_name(self, name):
        self.game = name

    def get_metrics(self):

        file = self.file
        #print("Log file path: " + file + '\n')
        f = open(file)

        line = f.readline()  # Inicializar el lector del fichero con primeros datos
        self.numl += 1
        time_old = line[:8]

        while line != "":  # Mientras el fichero entrgue una linea con datos
            ban = False
            time = time_old
            while not ban:  # Retencion para que itere hasta encontrar un parametro de params. Si no finaliza ciclo
                if line.find(
                        self.params[self.param_num]) < 0:  # Si no encuentra parametro, buscar siguiente elem en params
                    self.param_num += 1
                    if self.param_num >= len(self.params):
                        ban = True
                else:  # Si encuentra parametros, construir lista [tiempo, parametro, valor]
                    num = line.find(self.params[self.param_num])
                    parameter = line[num:num + len(self.params[self.param_num])]
                    aux = line[num + len(self.params[self.param_num]) + 2:len(line) - 1]
                    if len(re.findall(r"\d+\.\d+", aux)) > 0:
                        value = str(re.findall(r"\d+\.\d+", aux)[0])
                    else:
                        value = str(re.findall(r"\d+", aux)[0])
                    unit = line[num + len(self.params[self.param_num]) + 2 + len(value):len(line) - 1]
                    self.param_header[self.numl] = [time, parameter, value, unit]
                    self.numl += 1
                    ban = True
            if (line[:8].count(
                    ":") > 1):  # Parameters without timestamp are associated with previous parameters with it
                time_old = line[:8]
            else:
                time_old = time_old
            line = f.readline()
            self.param_num = 0
            # ban = False

        f.close()


        salidacsv = open(self.timeStamp + '_EventBasedData_' + self.game + self.res + '.csv', 'w',
                         newline="\n")  # Open file 'Datos.csv' and write 'w'
        # New line
        salida = csv.writer(salidacsv, 'excel')  # solo cuando exista un caracter \n

        #print("\n----------------------------------\nCSV time/value/parameter data\n----------------------------------")
        elem = ''
        lista = []  # Each line to be written must be an iterable
        listalista = []  # Save 'all-lines' register (not mandatory)
        for i in range(0, len(self.param_header)):
            value = self.param_header[i]
            for j in range(0, len(value)):  # For each value in parameters vector
                if j == len(value) - 1:  # If last element, then not create any new column
                    elem = elem + value[j]
                else:
                    elem = elem + value[j] + ";"  # ';' Create a new column in csv file
            lista.append(elem)
            #print(lista)
            listalista.append(lista)
            salida.writerow(lista)  # Write each line in file
            lista = []
            elem = ''

        salidacsv.close()

        salida2csv = open(self.timeStamp + '_TimeBasedData_' + self.game + self.res + '.csv', 'w', newline='\n')
        salida2 = csv.writer(salida2csv, 'excel')

        lista = []
        aux = ['None;'] * (len(self.params) + 1)
        elem = ''
        time = ''

        for i in range(0, len(listalista)):  # For each element in the previous vector
            if i == 0:  # Write header in csv file
                elem = 'Time;'
                for j in range(0, len(self.params)):
                    elem = elem + str(self.params[j]) + ";"
                lista.append(elem)
                salida2.writerow(lista)
            else:  # If is not header, then extract event timestamp
                time = listalista[i][0][:8]
                aux[0] = time + ';'
                for j in range(0, len(self.params)):  # For each element from 'params', search its position
                    elem = listalista[i][0]  # And write its value in index 'aux' vector
                    num = elem.find(self.params[j])
                    if num > 1:
                        if j + 1 == len(aux) - 1:
                            aux[j + 1] = elem[
                                         num + len(self.params[j]) + 1: elem.find(";", num + len(self.params[j]) + 1,
                                                                                  len(elem))]
                        else:
                            aux[j + 1] = elem[
                                         num + len(self.params[j]) + 1: elem.find(";", num + len(self.params[j]) + 1,
                                                                                  len(elem))] + ';'

            if i == len(listalista) - 1:  # Si es el ultimo elemento, escribir en fichero csv
                elem = ''
                lista = []
                for e in aux:
                    elem = elem + e
                lista.append(elem)
                salida2.writerow(lista)
                lista = []
                aux = ['None;'] * (len(self.params) + 1)
            else:  # if is not, analyze if next parameter correspond to another event. If it is, then write csv
                lista = []
                time_new = listalista[i + 1][0][:8]  # if is not, then keep aux vector for next element
                if time != time_new and i > 0:  # Parameter
                    elem = ''
                    for e in aux:
                        elem = elem + e
                    lista.append(elem)
                    salida2.writerow(lista)
                    aux = ['None;'] * (len(self.params) + 1)
                    elem = ''
        salida2csv.close()

    def get_dictionary(self):
        iter_num = self.param_header.__len__()
        for key in range(1, iter_num):
            data = self.param_header.get(key)
            param = data[1]
            value = float(data[2])
            index = self.params.index(param)
            param_key = self.params[index]
            previous_value = self.dictionary.get(param_key)
            if not previous_value:
                previous_value = [value]
            else:
                previous_value.append(value)

            self.dictionary[param_key] = previous_value
        self.dictionary['Resolution'] = self.res
        self.dictionary['fps'] = self.fps

        # Convert list with only 1 item to value
        for metric in self.dictionary.items():
            if type(metric[1]) == list and len(metric[1]) == 1:
                self.dictionary[metric[0]] = metric[1][0]

        return self.dictionary
