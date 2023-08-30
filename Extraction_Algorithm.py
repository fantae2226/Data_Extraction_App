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





def preprocessing(specified_img_region):

    #gray_image = cv2.cvtColor(specified_img_region, cv2.COLOR_BGR2GRAY)
 
    gaussian_img = cv2.GaussianBlur(specified_img_region,(0,0),3)
  
    ret, img = cv2.threshold(gaussian_img, 185, 255, cv2.THRESH_BINARY )

    denoised = cv2.GaussianBlur(img,(0,0), 3)

    custom_config = r'--psm 6'

    text = pytesseract.image_to_string(denoised, config=custom_config)

    return text


def capture_region(img):

    ret, mask = cv2.threshold(img, 180,255, cv2.THRESH_BINARY)

    img_final = cv2.bitwise_and(img, img, mask=mask)

    ret, new_img = cv2.threshold(img_final, 180, 255, cv2.THRESH_BINARY_INV)


    kernal =  cv2.getStructuringElement(cv2.MORPH_CROSS, (9,3))

    dilated = cv2.dilate(new_img, kernal, iterations=11)

    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    extracted_top_page_text = []

    for contour in contours:
        #Rect-Bounding Contour
        [x, y, width, height] = cv2.boundingRect(contour)
        #Ignore false positives
        if width < 100 or height < 75:
            continue

        #cv2.rectangle(img, (x, y), (x + width, y + height), (0,0,0),2)

        ocr_image = img[y:y+height, x:x+width]

        extracted_top_page_text.append(preprocessing(ocr_image))
        
    #print(extracted_top_page_text)
    return extracted_top_page_text

def french(input):
    predictions = model.predict(input, k=1)
    language = predictions[0][0].replace('__label__', '')
    return (language)

def separate_text(input_text):
    lowercase_txt = list(map(str.lower, input_text))
    # lines = lowercase_txt.split('\n')
    sections = []

    for line in lowercase_txt:
        line = line.replace("\n",'') #Get rid of any sneaky \n newline characters
        line = line.strip()  # Remove leading and trailing whitespace
        if re.fullmatch(r"\d+", line): #Check for demerits cause fasttext for some reason thinks numbers are french
            sections.append(line)
            continue
        if french(line) == 'fr':  # Skip French text
            continue
        if 'demerit' in line:
            continue
        if '*' in line:
            continue

        else:
            sections.append(line)

    return sections


def demerit_finder(lst):
    processed_demerit = '00'
    for line in lst:
       if re.fullmatch(r"\d+", line):
            processed_demerit = line
    return processed_demerit


if __name__ == "__main__":

    csv_file = open("C:/Users/293740/Desktop/New folder (12)/license_imgs_test6.csv", "w", newline="")
    writer = csv.writer(csv_file)
    header = [
        "File","Name", "License", "DoB", "Sex", "Height", "Class", "Condition",
        "Early License Date", "Expiry Date", "Status", "Demerit", "Conviction List"
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

        specific_img = test_image[1600:3030, 1850:]

        specific_img = cv2.resize(specific_img, None, fx = 1, fy = 1.5, interpolation=cv2.INTER_CUBIC)

        specific_img = cv2.cvtColor(specific_img, cv2.COLOR_BGR2GRAY)

        extracted_regions_lst = capture_region(specific_img)

        regions_without_periods = [s.replace('.','') for s in extracted_regions_lst]

        # extracted_regions_lst = list(filter(lambda arr: count_pixels(arr) > 600, lst))

        print(f'File name: {file} Length: {len(extracted_regions_lst)}')

        try:
            processed_name, processed_license, processed_DoB, processed_sex, processed_height, processed_class, processed_condition, processed_early_license_date, processed_expiry, processed_status = regions_without_periods[::-1]
        except ValueError:
            print(f'File name: {file} has a value error, please enter data manually')
            continue

        convition_img = test_image[3360:5000, :]
        convition_img = cv2.cvtColor(convition_img,cv2.COLOR_BGR2GRAY)
        results = capture_region(convition_img)
        bottom_page_text = results[::-1]
        
        #Preprocess all info and extracts text


        sections = separate_text(bottom_page_text)

        processed_demerit = demerit_finder(sections)

        sections = [item for item in sections if not item.isnumeric()]
        convictions = " ,".join(sections)
        #Cleaning up data
        processed_name = re.sub(r'[^A-Z0-9, ]', '', processed_name)
        processed_DoB = re.sub(r'[^0-9/]', '', processed_DoB)
        processed_sex = re.sub(r'[^A-Z,/]', '', processed_sex)
        processed_early_license_date = re.sub(r'[^0-9/]', '', processed_early_license_date)
        processed_expiry = re.sub(r'[^0-9/]', '', processed_expiry)
        processed_status = processed_status.split('/',1)[0]
        processed_class = re.sub(r'[^A-Z0-9]', '', processed_class)
        processed_condition = processed_condition.replace('\n','')
        processed_license = processed_license.replace('\n','')
        processed_license = re.sub(r'[^A-Z0-9]','',processed_license)
        processed_license = processed_license + "@"
        processed_height = processed_height.replace('\n','')
        processed_height = re.sub(r'[^A-Z0-9]','',processed_height)
        processed_demerit = processed_demerit.replace('\n','')


        extracted_data = [
            file, processed_name, processed_license, processed_DoB, processed_sex, processed_height, processed_class, 
            processed_condition, processed_early_license_date, processed_expiry, processed_status, processed_demerit,
            convictions]

        # for i in extracted_data[-3:]:
        #     if len(i) == 0:
        #         i.append('No results')

        #print(extracted_data)
        writer.writerow(extracted_data)

    csv_file.close()
    
