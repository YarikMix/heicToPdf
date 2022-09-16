import os
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
import piexif
import re
register_heif_opener()

dir_of_interest = os.getcwd()
filenames = os.listdir(dir_of_interest)

HEIC_files = []
for index, filename in enumerate([re.search("\.HEIC$|\.heic$", f) for f in filenames]):
	if filename:
		HEIC_files.append(filenames[index])

JPEG_files = []
for index, filename in enumerate([re.search("\.JPG$|\.jpg$", f) for f in filenames]):
	if filename:
		jpeg_path = os.path.join(dir_of_interest, filenames[index])
		JPEG_files.append(jpeg_path)

for heic_filename in HEIC_files:
	heic_path = os.path.join(dir_of_interest, heic_filename)
	image = Image.open(heic_path)
	image_exif = image.getexif()
	if image_exif:
		exif = { ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes }
		date = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')

		exif_dict = piexif.load(image.info["exif"])
		exif_dict["0th"][piexif.ImageIFD.DateTime] = date.strftime("%Y:%m:%d %H:%M:%S")
		exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
		exif_bytes = piexif.dump(exif_dict)

		jpg_path = dir_of_interest + "/" + os.path.splitext(heic_filename)[0] + ".jpg"
		image.save(jpg_path, "jpeg", exif= exif_bytes)
		JPEG_files.append(jpg_path);
	else:
		print(f"Unable to get exif data for {heic_filename}")

JPEG_files.sort(key=lambda i: int(os.path.splitext(os.path.basename(i))[0].split("_")[1]))

images = [Image.open(f) for f in JPEG_files]

pdf_name = "p"
pdf_path = dir_of_interest + f"/{pdf_name}.pdf"
images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])

for f in HEIC_files:
	os.remove(f)

for filename in os.listdir(dir_of_interest):
	file_path = os.path.join(dir_of_interest, filename)
	if os.path.isfile(file_path) and filename.lower().endswith((".jpg", ".jpeg")):
		try:
			os.unlink(file_path)
		except:
			pass