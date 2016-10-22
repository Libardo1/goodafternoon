import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

from prepare_data import PrepareData

import tflearn
import tensorflow as tf

X_train, y_train, X_test, y_test, df, train_len = PrepareData().dataset(maxCount=18, n_year=2008)
#y_train = y_train.reshape(-1,1)
#y_test = y_test.reshape(-1,1)

g = tflearn.input_data(shape=[None, X_train.shape[1]])
g = tflearn.fully_connected(g, 1024)
g = tflearn.fully_connected(g, 2, activation='softmax')

g = tflearn.regression(g, optimizer='adam', metric='accuracy')

model = tflearn.DNN(g)
model.fit(X_train, y_train, n_epoch=50, show_metric=True, snapshot_step=False, batch_size=100)
ret = model.evaluate(X_test, y_test)
print(ret)
#input("ENTER")

y_predict = model.predict(X_test)
right = 0
total = 0
right_index = []
total_index = []
for i,v in enumerate(y_predict):
	if y_predict[i][1]>0.5:
		print(y_predict[i], " <==> ", y_test[i])
		total += 1
		total_index.append(i)
		if y_test[i][1]==1:
			right += 1
			right_index.append(i)

print("Predict Increase Right: ", right, " in ", total)
#input("ENTER")

print(right_index)
df0 = df.loc[df['increase']==1]
df0 = df0.filter(regex='Close_')
df = df.iloc[train_len:]
df1 = df.iloc[total_index].filter(regex='(Date|Stock|Close_)')
df2 = df1.filter(regex='Close_')
df1.to_csv('df1.csv')


ax0 = plt.subplot2grid((2,2),(0,0))
ax0.plot( df0.head(200).values.T )
df4 = df0.apply(lambda row: row-row['Close_19'], axis=1)
ax0 = plt.subplot2grid((2,2),(0,1))
ax0.plot( df4.head(200).values.T )

if (total>0):
	ax1 = plt.subplot2grid((2,2),(1,0))
	ax1.plot( df2.values.T )
	df3 = df2.apply(lambda row: row-row['Close_19'], axis=1)
	ax2 = plt.subplot2grid((2,2),(1,1))
	ax2.plot( df3.values.T )

plt.show()