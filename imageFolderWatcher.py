import piexif
import sys
import json
import os
import shutil
import glob

from datetime import datetime

pid = str(os.getpid())
pidfile = "/tmp/imageFolderWatcher.pid"

if os.path.isfile(pidfile):
    print(str(datetime.now()) + " [INFO] %s already exists, exiting" % pidfile)
    sys.exit()

open(pidfile, 'w').write(pid)

try:

	base_path = "/mnt/DroboNAS/Shares/Photos/Photos Backup"
	image_location = "/mnt/DroboNAS/Shares/Photos/Import Folder/"

	if len(sys.argv) == 2:
		if os.path.isdir(sys.argv[1]):
			image_location = sys.argv[1]

	date_of_image = {}

	print(str(datetime.now()) + " [INFO] Checking folder contents " + str(image_location))
	extensions = ("*.jpg","*.JPG", "*.JPEG", "*.jpeg")
	folder_contents = []
	for extension in extensions:
		folder_contents.extend(glob.glob(image_location+"/**/"+extension))


	if len(folder_contents) > 0:
		print(str(datetime.now()) + " [INFO] Found " + str(len(folder_contents)) + " Images to process")

		for image_location in folder_contents:

			if os.path.isfile(image_location):

				exif_dict = piexif.load(image_location)

				for ifd in ("0th", "Exif", "GPS", "1st"):
					for tag in exif_dict[ifd]:

						if piexif.TAGS[ifd][tag]["name"] == "DateTime":
							date_of_image["DateTime"] = exif_dict[ifd][tag].decode("utf-8")
						
						if piexif.TAGS[ifd][tag]["name"] == "DateTimeOriginal":
							date_of_image["DateTimeOriginal"] = exif_dict[ifd][tag].decode("utf-8")

				if "DateTimeOriginal" in date_of_image:
					img_date = datetime.strptime(date_of_image["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
				elif "DateTime" in date_of_image:	  
					img_date = datetime.strptime(date_of_image["DateTime"], "%Y:%m:%d %H:%M:%S")  

				if img_date:

					month_backup = img_date.strftime("%m %B")
					year_backup = img_date.strftime("%Y")

					if month_backup and year_backup:
						directory = base_path + "/" + year_backup + "/" + month_backup 

						if not os.path.exists(directory):
							print(str(datetime.now()) + " [INFO] making dir " + directory)
							os.makedirs(directory)

						file_path = directory + "/" + os.path.basename(image_location)

						if os.path.isfile(file_path):
							print(str(datetime.now()) + " [INFO] The following image exists at backup location ' - removing from dir" + str(os.path.basename(image_location)))
							os.remove(image_location)

						else:
							print("[OK] Moving Image to " + file_path)
							shutil.move(image_location, file_path)
				else:
					print(str(datetime.now()) + " [ERROR] Could not generate a datetime from Image")
					print(str(datetime.now()) + " [INFO] " + image_location)
			else:
				print(str(datetime.now()) + " [ERROR] Image does not exist")
	else:
		print(str(datetime.now()) + " [INFO] Nothing to do")
		
		## if nothing to do remove empty dirs

		contains_dir = os.listdir(image_location)

		for directory in contains_dir:
			directory_name = image_location + "/" + directory
			if os.path.isdir(directory_name):
				print(str(datetime.now()) + " [INFO] tidy up old folder " + directory_name )
				os.rmdir(directory_name)


finally:
    os.unlink(pidfile)
