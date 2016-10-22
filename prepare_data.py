import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import pickle
import cv2

def L(*args):
	if len(args)==2:
		print("\n========[",args[0],"]========")
		print(args[1])
	else:
		print(*args)

class PrepareData(object):

	def LoadStockData(self, str_stock_code, normalize=True, n_year=2007):
		#read stock data from csv file which is download free from a taobao seller.
		try:
			df_stock = pd.read_csv('data/china/'+str(n_year)+'/SH'+str_stock_code+'.csv', header=0, index_col=False, names=['Date','Time','Open','High','Low','Close','Volumn','Amount'])
		except:
			print("Error: CSV file not found. Please make sure you have the csv files in the right path.")
			return pd.DataFrame()
		
		#normally, if one section stands for 5 mins, there will be 48 sections in one day.
		#let get the well recorded days first.
		df_byday = df_stock.groupby('Date').count().query('Time==48')
		df_byday.reset_index(level=0, inplace=True)
		df_byday.pop('Time')
		df_byday.pop('Open')
		df_byday.pop('High')
		df_byday.pop('Low')
		df_byday.pop('Close')
		df_byday.pop('Volumn')
		df_byday.pop('Amount')
		#how many well recorded days totally
		n_days = len(df_byday)
		#pick any day, to get the record time array
		d_first_day = df_byday['Date'][0]
		df_first_day = df_stock.query('Date==\''+d_first_day+'\'')
		arr_time = df_first_day['Time'].values

		#start fill df_ret with recorded data
		df_ret = df_byday
		for i, time in enumerate(arr_time):
			#Record time start at 09:35
			df_bytime = df_stock.query('Time==\''+time+'\'')
			df_bytime.pop('Time')
			df_bytime.pop('Volumn')
			df_bytime.pop('Amount')
			df_bytime.columns = ['Date', 'Open_'+str(i), 'High_'+str(i), 'Low_'+str(i), 'Close_'+str(i)]
			df_ret = pd.merge(df_ret, df_bytime, on='Date')
		df_ret.insert(1,'StockCode',str_stock_code)
		df_ret.insert(2,'Day_Open',df_ret['Open_0'])

		if (normalize):
			for i in range(48):
				tmp = ['Open','Close','High','Low']
				for t in tmp:
					df_ret[t+'_'+str(i)] = df_ret[t+'_'+str(i)].div(df_ret['Day_Open'], axis="index")*10-10
				#df_ret['Volumn_'+str(i)] = df_ret['Volumn_'+str(i)] / 1000
			#L(df_ret.div(df_day_open['Open'].values, axis=0))
			pass

		return df_ret

	def LoadAllStockData(self, maxCount=200, normalize=True, n_year=2007):
		print('Info: This will take a few minutes.')
		n = 1
		df_ret = None

		for root, dirs, files in os.walk('data/china/'+str(n_year)+'/'):
			if maxCount>len(files):
				n_total = len(files)
			else:
				n_total = maxCount
			for file in files:
				if file[:5]=='SH600':
					df = self.LoadStockData(file[2:8], normalize=normalize, n_year=n_year)
					L( str(n)+'/'+str(n_total), file[2:8] )
					n += 1
					if len(df.columns)!=195:
						L('Warning','Not 195 columns!')
					
					if type(df_ret)==type(None):
						df_ret = df
					else:
						df_ret = pd.concat([df,df_ret], ignore_index=True)

				if n > maxCount:
					#pass
					break
		return df_ret
	def dataset(self, maxCount=200, train_percentage=0.7, n_year=2007):
		df = PrepareData().LoadAllStockData(maxCount=maxCount, n_year=n_year)
		df = df.sort('Date')
		#df = df.reindex(np.random.permutation(df.index))
		df_data = df.filter(regex='(Open|Volumn)_(\d|1\d)$')
		#df_label = df.filter(regex='High_\d\d$').max(axis=1)
		df['increase'] = 1
		df.loc[df['Close_47'] - df['Close_19'] <= 0.2, 'increase'] =0
		#df.loc[df['Close_37'] - df['Close_19'] <= 0.2, 'increase'] =0
		
		L("INCREASE", df['increase'].sum(), " / ", len(df))
		df_label = pd.get_dummies(df['increase'])

		train_len = int(len(df_data) * train_percentage)
		train_data = df_data.iloc[0:train_len].values
		test_data = df_data.iloc[train_len:].values
		train_label = df_label.iloc[0:train_len].values
		test_label = df_label.iloc[train_len:].values
		return [train_data, train_label, test_data, test_label, df, train_len]





if __name__=='__main__':
	a,b,c,d,e,f = PrepareData().dataset(1,n_year=2007)
	print(a.shape, b.shape, c.shape, d.shape)
	print(b[-1], d[0])
	print()