
import re
import os
import easyquotation
from easyquotation.basequotation import BaseQuotation

from pprint import pprint
import pickle

class MyQuotation(BaseQuotation):
	"""新浪免费行情获取"""
	max_num = 800
	grep_detail = re.compile(r'(\d+)=([^\s][^,]+?)%s%s' % (r',([\.\d]+)' * 29, r',([-\.\d:]+)' * 2))
	stock_api = 'http://hq.sinajs.cn/?format=text&list='

	def format_response_data(self, rep_data):
		stocks_detail = ''.join(rep_data)
		result = self.grep_detail.finditer(stocks_detail)
		stock_dict = dict()
		for stock_match_object in result:
			stock = stock_match_object.groups()
			stock_dict[stock[0]] = dict(
				date=stock[31],
				time=stock[32],
				raw =','.join(str(i) for i in stock)
			)
		return stock_dict

def main():
	path = '/home/liusida/code/stock/grab'
	quotation = MyQuotation()
	a = quotation.all
	for i,v in a.items():
		if (i[:3]=='600'):
			pathname = os.path.join(path, i)
			if not os.path.isdir(pathname):
				os.mkdir(pathname)


			filename = v['date'] + '_' + v['time'][:5] + '.csv'
			filename = re.sub(r'(-|:)', '_', filename)
			filename = os.path.join(pathname, filename)
			
			line = v['raw']
			
			with open(filename, 'a') as f:
				print(line, file=f)
			
			#pprint(v)

			

	#with open('a','wb') as f:
	#	pickle.dump(a,f)
		

main()