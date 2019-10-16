import ftplib
import csv
import numpy as np
import pandas as pd
from tensorflow import name_scope
from os import listdir
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib
from datetime import time
from PIL import Image



class Data:

    def __init__(self):
        pass

    def download_data(self):
        data = 0

        server, username, passwd = self.get_credentials()
        ftp = ftplib.FTP(server)
        ftp.login(user=username, passwd=passwd)

        ftp.cwd("/asi16_data/asi_16124") #cam 1
        files  = ftp.nlst()

        for f in files:
            print(f)
            ftp.cwd(("/asi16_data/asi_16124/" + str(f)))

            f_ = ftp.nlst()
            for i in f_:
                file_name = (str(i))
                #if image
                if('.jpg' in i):
                    tmp_name = ('image/' + str(i))
                    image = open(tmp_name, 'wb')
                    ftp.retrbinary('RETR ' + file_name, image.write, 1024)
                    image.close()
                    #TODO now you can do pre_processing

                elif('.csv' in i):
                    tmp_name = ('csv/' + str(i))
                    csv = open(tmp_name, 'wb')
                    ftp.retrbinary('RETR ' + file_name, csv.write, 1024)
                    self.process_csv(tmp_name)

        return data

    def process_csv(self, csv_name):
        # colums = ["SQNR", "DATE", "TIME", "TMPA", "PIRA"]
        tmp = pd.read_csv(csv_name, sep=';', header=None)
        if(len(tmp.columns) > 1):
            arr = pd.read_csv(csv_name, sep=';', header=None, usecols=[0, 1, 2, 4, 15])

            #remove rows containing c,v,r not sure what it means..
            arr = arr[arr[0] != 'V-----']
            arr = arr[arr[0] != 'C-----']
            arr = arr[arr[0] != 'R-----']

            c = [0, 1, 2, 4, 15]
            for index, row in arr.iterrows():
                for i in c:
                    try:
                        vals = row[i].split('=')
                        row[i] = vals[1]
                    except:
                        print(row[i])

            arr.to_csv(csv_name)

        del tmp

    def get_credentials(self):
        f = open('cred.txt', 'r')
        lines = f.read().split(',')
        f.close()
        # print(lines)
        return lines[0], lines[1], lines[2]


    def images_information(self):
        server, username, passwd = self.get_credentials()
        ftp = ftplib.FTP(server)
        ftp.login(user=username, passwd=passwd)

        ftp.cwd("/asi16_data/asi_16124")  # cam 1
        files = ftp.nlst()
        del files[0]

        start_times = []
        stop_times = []
        times = [] # no way
        todo = len(files)
        done = 0

        for f in files:
            ftp.cwd(("/asi16_data/asi_16124/" + str(f)))
            f_ = ftp.nlst()
            start_times.append(self.extract_time_less_accurate(f_[0]))
            stop_times.append(self.extract_time_less_accurate(f_[-2]))

            done += 1
            print(str(done) + '/' + str(todo))

        start_dict = self.wordListToFreqDict(sorted(start_times))
        stop_dict = self.wordListToFreqDict(sorted(stop_times))

        print(start_dict)
        print(stop_dict)

        self.plot_freq(start_dict, 'Frequency start times')
        self.plot_freq(stop_dict, 'Frequency stop times')


    def extract_time(self, time_str):
        return(time_str[8:14])

    def exract_formatted_time(self, time_str):
        s = time_str[8:14]
        return s[0:2] + ':' + s[2:4] + ':' + s[4:6]

    def extract_time_less_accurate(self, time_str):
        return(time_str[8:12])


    def pre_process(self):
        pass

    def sample(self):
        pass




    def wordListToFreqDict(self, wordlist):
        wordfreq = [wordlist.count(p) for p in wordlist]
        return dict(zip(wordlist, wordfreq))

    def plot_freq(self, dict, title):
        ax = plt.axes()
        plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='right', fontsize='x-small')
        plt.bar(dict.keys(), dict.values(), 0.75, color='b')

        plt.title(title)
        plt.xlabel('times')
        plt.ylabel('frequency')
        plt.tight_layout()

        plt.show()

    def resize_image(self,img, height, width):
        # setting dim of the resize
        # name = ('image/20190716084100_11.jpg')
        # img = cv2.imread(name)
        # image = cv2.resize(np.float32(img), (800, 800), interpolation=cv2.INTER_LINEAR)
        # cv2.imwrite(name + str('._prep.jpg'), image)
        return cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)

    def get_avg_var_by_minute(self, df, hour, minute):
        # rows = df[(np.where((df[:3] == hour) & (df[:4] == minute)))]

        rows = df[df[:,3] == hour] # first statement
        # print(rows)
        rows = rows[rows[:,4] == minute] # second statement
        # print(rows)
        means = np.mean(rows[:,6:8], axis=0)
        var = np.var(rows[:,6:8], axis=0)
        # print(means)
        return means, var


    def plot_avg_per_month(self, month, start, end):
        df = self.get_df_csv_month(month, start, end)
        hours = list(range(start, end))
        minutes = list(range(0, 60, 5))
        times = []
        avg_temp = []
        var_temp = []
        avg_ghi = []
        var_ghi = []
        tick_times = []

        for h in hours:
            tick_times.append(time(h, 0, 0))
            tick_times.append(time(h, 30, 0))
            for m in minutes:
                tmp_avg, tmp_var = self.get_avg_var_by_minute(df, h, m)
                tmp_time = time(h, m, 0)
                times.append(tmp_time)
                avg_temp.append(tmp_avg[0])
                var_temp.append(tmp_var[0])
                avg_ghi.append(tmp_avg[1])
                var_ghi.append(tmp_var[1])

        self.plot_time_avg(tick_times, times, avg_temp, 'time', 'temp. in celsius',
                           'avg. temp. in month ' + str(month))

        self.plot_time_avg(tick_times, times, var_temp, 'time', 'Variance temp.',
                           'var. temp. in month ' + str(month))

        self.plot_time_avg(tick_times, times, avg_ghi, 'time', 'Global horizon irradiace',
                           'avg. ghi in month ' + str(month))

        self.plot_time_avg(tick_times, times, var_ghi, 'time', 'Variance GHI',
                           'var. ghi in month ' + str(month))


    def plot_time_avg(self, tick_times, times, values, lx, ly, title):
        plt.xticks(tick_times)
        ax = plt.axes()
        plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize='x-small')
        plt.plot(times, values, linestyle=':')

        plt.title(title)
        plt.xlabel(lx)
        plt.ylabel(ly)

        plt.show()

    def get_df_csv_month(self, month, start, end):

        folders = listdir('asi_16124')  # select cam
        del folders[0:3]  # first 3 are bad data
        index = 0
        queries = int(31 * ((end - start)*60/5))
        df = np.empty([queries, 8]) #create df

        for folder in folders: #fill df
            if(int(folder[4:6]) == month): #only check for month

                path = 'asi_16124/' + str(folder) + '/'
                files = listdir(path)

                self.process_csv(path + files[-1])  # process csv
                tmp_df = pd.read_csv(path + files[-1], sep=',', header=0, usecols=[2, 3, 4, 5])  # load csv

                for row in tmp_df.iterrows():
                    if( int(row[1].values[1][6:8]) == 0 and int(row[1].values[1][3:5])%5 == 0 and int(row[1].values[1][0:2]) > start and int(row[1].values[1][0:2]) < end):
                        df[index][0:8] = np.array([row[1].values[0][0:2], row[1].values[0][3:5], row[1].values[0][6:8],
                                                   row[1].values[1][0:2], row[1].values[1][3:5], row[1].values[1][6:8],
                                                   row[1].values[2], row[1].values[3]])  # set csv data to df
                        index += 1
                        # print(index)
        # # YEAR, MONTH, DAY, HOURS, MINUTES, SECONDS, TEMP, IRRADIANCE, IMAGE
        print('filled queries: ' + str(index) + 'out of: ' + str(queries))
        return df[0:index].astype(int)

    def build_df(self, queries):
        # size 0 means al images
        index = 0
        tmp_img = cv2.imread('asi_16124/20191006/20191006060800_11.jpg')  # random image assume here they are all the same
        height, width, channels = tmp_img.shape
        size_of_row = 8 + height*width*channels
        df = np.empty([queries, size_of_row])

        folders = listdir('asi_16124')#select cam
        del folders[0:3] #first 3 are bad data

        for folder in folders:
            if index == queries:
                break

            path = 'asi_16124/' + str(folder) + '/'
            files = listdir(path)

            self.process_csv(path + files[-1])  # process csv
            tmp_df = pd.read_csv(path + files[-1], sep=',', header=0, usecols=[2,3,4,5])  #load csv
            # print(tmp_df)
            for file in files:
                if index == queries: #cancel if dataframe is full
                    break

                arr = tmp_df[tmp_df['2'] == self.exract_formatted_time(file)] #find image in cvs by time
                if(arr.empty): #means if image is not in csv file
                    continue

                data = arr.to_numpy().flatten()
                #index in csv, seconds, year, month, day, hours, minutes, seconds, temp, irriadiance. then image
                df[index][0:8] = np.array([data[0][0:2], data[0][3:5], data[0][6:8], data[1][0:2], data[1][3:5], data[1][6:8], data[2], data[3]]) #set csv data to df
                df[index][8:] = cv2.imread(path + file).flatten() #set img data to df
                index += 1
                print(index)

        #YEAR, MONTH, DAY, HOURS, MINUTES, SECONDS, TEMP, IRRADIANCE, IMAGE
        print('filled queries: ' + str(index) + 'out of: ' + str(queries))
        return df.astype(int)


#
d = Data()
# df = d.build_df(2)
# d.images_information()
d.plot_avg_per_month(9, 3, 22)
# print(df[0][0:12])
# # d.download_data()

#make df ready for future predictions
#filter unnesacasru dtuff out
#normalization
#simple features?
#save df


