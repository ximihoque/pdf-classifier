import os 
from pdf2image import convert_from_path
import sys
from tqdm import tqdm
import sys, glob
import os,os.path
import PyPDF2
from multiprocessing import Queue, Pool
import logging
logging.basicConfig(level=logging.DEBUG)

def export(pdf_file, in_dir=False, q=None):
	"""
	export function importing pdf_file_name as pdf_file huntiong for .pdf in dir and converting 
	.pdf into img 
	"""

	pages = convert_from_path(pdf_file, 300)
	pdf_name = pdf_file.strip(".pdf")

	def export_pages(page):	
		if in_dir==True:		
			if not os.path.exists(pdf_name):
				os.mkdir(pdf_name)

			saving_path = os.path.join(pdf_name, "{}-{}.jpg".format(pdf_name.split('/')[-1],pages.index(page)))	
		else:
			saving_path = os.path.join("{}-{}.jpg".format(pdf_name,pages.index(page)))
		
		logging.debug("PDF to JPG: {}".format(saving_path))
		page.save(saving_path,"JPEG")
	
	
	map(lambda page: export_pages(page), pages)
	if q:
		q.put(pdf_file)
		

def pdf2img(path,in_dir=False,q=None):
	for path_class in map(lambda dir_:os.path.join(path, dir_), os.listdir(path)): 
		pdf_files = glob.glob(os.path.join(path_class, "*.pdf"))
		map(lambda pdf_file: export(pdf_file, in_dir, q), pdf_files)
		
"""				
if __name__ == '__main__':
	pdf2img("Samples_old", True)	# calling main function to convert pdf2img
"""

