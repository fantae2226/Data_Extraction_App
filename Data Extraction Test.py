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
        print(region)
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

def preprocessing(specified_img_region): #Function takes an image, cleans it up, and processes it into text

    constant = 5

    resized = cv2.resize(specified_img_region, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    img = cv2.medianBlur(resized,11)

    h,w = resized.shape[:2]

    block_size = int(min(h, w) * 0.6)

    block_size = max(block_size, 7)  # Set minimum block size to 10
    if block_size % 2 == 0:
        block_size += 1

    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    kernal = np.ones((1, 1), np.uint8)
    img = cv2.dilate(gray_image,kernal, iterations=1)
    img = cv2.erode(img,kernal,iterations=1)
    
    binary_img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, constant)


    sharpened_img = cv2.addWeighted(binary_img, 1.8, binary_img, -0.8, 0)  # Adjust the weights as per desired effect


    custom_config = r'--psm 6'

    text = pytesseract.image_to_string(sharpened_img, config=custom_config)

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


csv_file = open("C:/Users/293740/Desktop/New folder (2)/output2.csv", "w", newline="")
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

    name_image = test_image[1700-height:1700, 1965:3500]

    license_num_image = test_image[2100-height:2100,1965:3500]

    DoB_image = test_image[2200-height:2200,1965:3500]

    sex_image = test_image[2300-height:2300,1965:3500]

    height_image = test_image[2400-height:2400,1965:3500]

    class_image = test_image[2500-height:2500,1965:3500]

    condition_image = test_image[2600-height:2600,1965:3500]

    early_license_date_image = test_image[2800-height:2800,1965:3500]

    expiry_date_image = test_image[2900-height:2900,1965:3500]

    status_image = test_image[3000-height:3000,1965:3500]

    start_y = 3360

    convictions_image = conviction_extraction(test_image, start_y=3360, threshold=0.03, area_increment=10)

    demerit_start_y = convictions_image.shape[0]+ start_y

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
    
#print(extracted_data[-3:])
# print("Name:",p_name)
# print("L #:", p_license)
# print("DoB:",p_DoB)
# print("Sex:", p_sex)
# print("Height:",p_height)
# print("Class:",p_class)
# print("Condition:",p_condition)
# print("Early L Date:",p_early)
# print("Expiry Date:",p_expiry)
# print("Status:",p_status)
# print("Demerit:", p_demerit)
# print("Medical Procedure List:", medical_procedure_list)
# print("Medical Date List:", medical_date_list)
# print("Conviction List:", conviction_list)