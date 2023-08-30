import cv2
import pytesseract
import numpy as np
import re
import fasttext
import csv
import os
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

model = fasttext.load_model("C:/Users/293740/Desktop/New folder/lid.176.bin")

x_start = 1965

#test_image = cv2.imread("C:/Users/293740/Desktop/New folder/test_image2.jpg")


def conviction_extraction(test_image, start_y, threshold=0.03, area_increment=10):
    height, width = test_image.shape[:2]
    extraction_area = 100  # Initial extraction area
    region = None
    while True:
        if extraction_area >= height - start_y:
            # Stop increasing the extraction area if it reaches the bottom of the available range
            break

        # Define the extraction region
        x1 = 0  # Start from the leftmost pixel
        x2 = width  # End at the rightmost pixel
        y1 = start_y
        y2 = start_y + extraction_area

        # Extract the region from the image
        region = test_image[y1:y2, x1:x2]
        #print(region)
        # Check the bottom rectangle for empty pixels
        bottom_rect = region[-100:, :]  # Assuming the bottom rectangle height is 100 pixels
        empty_pixels = np.sum(bottom_rect == 255)

        total_pixels = bottom_rect.size
        error_margin = threshold * total_pixels
        
        if empty_pixels >= total_pixels - error_margin:
            # Stop increasing the extraction area if the bottom rectangle is entirely empty
            break

        extraction_area += area_increment
   
    #print(region)
    return region






def section_extraction(specific_img, threshold=0.01, area_increment=1):

    specific_img = cv2.resize(specific_img, None, fx=1, fy=1.5, interpolation=cv2.INTER_CUBIC)
    specific_img =cv2.cvtColor(specific_img, cv2.COLOR_BGR2GRAY)
    height, width = specific_img.shape[:2]
    extraction_area = 50  # Initial extraction area
    region = None
    regions_list = []
    top_rect = 0

    while top_rect < height:
        # Define the extraction region
        x1 = 0  # Start from the leftmost pixel
        x2 = width  # End at the rightmost pixel
        y1 = top_rect
        y2 = y1 + extraction_area # Limit y2 to the height of the image
 
        # Extract the region from the image
        region = specific_img[y1:y2, x1:x2]

        # Check the bottom rectangle for empty pixels
        bottom_rect = region[-10:y2, :]  
        empty_pixels = np.sum(bottom_rect == 255)
        
        total_pixels = bottom_rect.size
        error_margin = threshold * total_pixels
      
        if empty_pixels >= total_pixels - error_margin:
            regions_list.append(region)
            top_rect = y2 
            extraction_area = 50 
        else:
            extraction_area += area_increment
        if y2 >= height:
            regions_list.append(region)
            break
    return regions_list


def preprocessing(specified_img_region):

    #resized = cv2.resize(specified_img_region, None, fx=2, fy=2, interpolation=cv2.INTER_AREA)

    gaussian_img = cv2.GaussianBlur(specified_img_region,(0,0),3)

    custom_config = r'--psm 6'

    text = pytesseract.image_to_string(gaussian_img, config=custom_config)

    return text

def french(input):
    predictions = model.predict(input, k=1)
    language = predictions[0][0].replace('__label__', '')
    return (language)

def separate_text(input_text):
    lowercase_txt = input_text.lower()
    lines = lowercase_txt.split('\n')
    sections = []

    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace
        if french(line) == 'fr':  # Skip French text
            continue

        else:
            sections.append(line)

    return sections


def data_seperator(lst):
    medical_procedure_list = []
    medical_date_list = []
    conviction_list = []

    previous_entry = None

    for line in lst:
        if re.match(r'^[a-zA-Z\s]+$', line) or re.match(r'^[a-zA-Z\'"”\s]+$', line):
            medical_procedure_list.append(line)
        
        elif re.match(r'^\d{2}/\d{2}/\d{2} [a-zA-Z\s._-]+$', line):
            conviction_list.append(line)
            previous_entry = line
            continue
        elif re.match(r'^[a-zA-Z\s]+ \d{4}/\d{2}/\d{2}$', line) and 'offence date' not in line:
            medical_date_list.append(line)
       
        elif previous_entry != None:
            if re.match(r'^\d{2}/\d{2}/\d{2} [a-zA-Z\s._-]+$', previous_entry) and 'offence date' in line:
                conviction_list[-1] += ' ' + line
                previous_entry = None
           
    return medical_procedure_list, medical_date_list, conviction_list

def count_pixels(region):
    # Count the number of empty (white) pixels
    pixels = np.sum(region <= 127)

    return pixels

csv_file = open("C:/Users/293740/Desktop/New folder (2)/output5.csv", "w", newline="")
writer = csv.writer(csv_file)
header = [
    "Name", "License", "DoB", "Sex", "Height", "Class", "Condition",
    "Early License Date", "Expiry Date", "Status", "Demerit",
    "Medical Procedure List", "Medical Date List", "Conviction List"
]
writer.writerow(header)

directory = "C:/Users/293740/Desktop/New folder (4)"

# Create a list to store the file paths
file_paths = []

# Loop over the files in the directory
for filename in os.listdir(directory):
    # Check if the file is an image file
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        # Create the full file path
        file_path = os.path.join(directory, filename)
        # Add the file path to the list
        file_paths.append(file_path)

for file in file_paths:
    height = 95
    test_image = cv2.imread(file)
    #Collect all relavent data from image

    specific_img = test_image[1600:3030, 1970:]

    lst = section_extraction(specific_img)

    extracted_regions_lst = lst

    extracted_regions_lst = list(filter(lambda arr: count_pixels(arr) > 600, lst))

    print(f'File name: {file} Length: {len(extracted_regions_lst)}')

    name_image, license_num_image, DoB_image, sex_image, height_image, class_image, condition_image, early_license_date_image, expiry_date_image, status_image = extracted_regions_lst[:10]

    convictions_image = conviction_extraction(test_image, start_y=3360, threshold=0.03, area_increment=10)

    demerit_start_y = convictions_image.shape[0]+ 3360

    demerit_img = test_image[demerit_start_y:demerit_start_y+height, 3360:3600]

    #Preprocess all info and extracts text
    p_name = preprocessing(name_image)

    p_license = preprocessing(license_num_image)

    p_DoB = preprocessing(DoB_image)

    p_sex = preprocessing(sex_image)

    p_height = preprocessing(height_image)

    p_class = preprocessing(class_image)

    p_condition = preprocessing(condition_image)

    p_early = preprocessing(early_license_date_image)

    p_expiry = preprocessing(expiry_date_image)

    p_status = preprocessing(status_image)

    p_convictions = pytesseract.image_to_string(convictions_image)

    p_demerit = preprocessing(demerit_img)

    sections = separate_text(p_convictions)

    medical_procedure_list, medical_date_list, conviction_list = data_seperator(sections)

    #Cleaning up data
    p_name = re.sub(r'[^A-Z,0]', '', p_name)
    p_DoB = re.sub(r'[^0-9/]', '', p_DoB)
    p_sex = re.sub(r'[^A-Z,/]', '', p_sex)
    p_early = re.sub(r'[^0-9/]', '', p_early)
    p_expiry = re.sub(r'[^0-9/]', '', p_expiry)
    p_status = p_status.split('/',1)[0]
    p_class = re.sub(r'[^A-Z]', '', p_class)
    p_condition = p_condition.replace('\n','')
    p_license = p_license.replace('\n','')
    p_license = re.sub(r'[^A-Z0-9]','',p_license)
    p_height = p_height.replace('\n','')
    p_height = re.sub(r'[^A-Z0-9]','',p_height)
    p_demerit = p_demerit.replace('\n','')


    extracted_data = [
        p_name, p_license, p_DoB, p_sex, p_height, p_class, 
        p_condition, p_early, p_expiry, p_status, p_demerit,
        medical_procedure_list, medical_date_list, conviction_list ]

    for i in extracted_data[-3:]:
        if len(i) == 0:
            i.append('No results')

    writer.writerow(extracted_data)

csv_file.close()
    
