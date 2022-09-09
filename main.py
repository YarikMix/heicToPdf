import os
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
import piexif
import re
register_heif_opener()

dir_of_interest = os.getcwd()
filenames = os.listdir(dir_of_interest)

# Extract files of interest
HEIC_files = []
for index, filename in enumerate([re.search("\.HEIC$|\.heic$", f) for f in filenames]):
	if filename:
		HEIC_files.append(filenames[index])

JPEG_files = []
for index, filename in enumerate([re.search("\.JPG$|\.jpg$", f) for f in filenames]):
	if filename:
		jpeg_path = os.path.join(dir_of_interest, filenames[index])
		JPEG_files.append(jpeg_path)

# Convert files to jpg while keeping the timestamp
for heic_filename in HEIC_files:
	heic_path = os.path.join(dir_of_interest, heic_filename)
	image = Image.open(heic_path)
	image_exif = image.getexif()
	if image_exif:
		# Make a map with tag names and grab the datetime
		exif = { ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes }
		date = datetime.strptime(exif['DateTime'], '%Y:%m:%d %H:%M:%S')

		# Load exif data via piexif
		exif_dict = piexif.load(image.info["exif"])

		# Update exif data with orientation and datetime
		exif_dict["0th"][piexif.ImageIFD.DateTime] = date.strftime("%Y:%m:%d %H:%M:%S")
		exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
		exif_bytes = piexif.dump(exif_dict)

		jpg_path = dir_of_interest + "/" + os.path.splitext(heic_filename)[0] + ".jpg"
		# Save image as jpeg
		image.save(jpg_filename, "jpeg", exif= exif_bytes)
		JPEG_files.append(jpg_filename);
	else:
		print(f"Unable to get exif data for {heic_filename}")

JPEG_files.sort(key=lambda i: int(os.path.splitext(os.path.basename(i))[0]))

images = [Image.open(f) for f in JPEG_files]

pdf_name = "p"
pdf_path = dir_of_interest + f"/{pdf_name}.pdf"

images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])

for f in HEIC_files:
	os.remove(f)

for filename in os.listdir(dir_of_interest):
	jpg_path = os.path.join(dir_of_interest, filename)
	if os.path.isfile(jpg_path) and filename.lower().endswith((".jpg", ".jpeg")):
		try:
			os.unlink(file_path)
		except:
			pass