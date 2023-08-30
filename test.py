import cv2
import pytesseract
import numpy as np
import re
import fasttext
from PIL import Image


pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

model = fasttext.load_model("C:/Users/293740/Desktop/New folder/lid.176.bin")


def preprocessing(specified_img_region):

    #gray_image = cv2.cvtColor(specified_img_region, cv2.COLOR_BGR2GRAY)
 
    gaussian_img = cv2.GaussianBlur(specified_img_region,(0,0),3)
  
    ret, img = cv2.threshold(gaussian_img, 185, 255, cv2.THRESH_BINARY )

    denoised = cv2.GaussianBlur(img,(0,0), 3)

    custom_config = r'--psm 6'

    text = pytesseract.image_to_string(denoised, config=custom_config)

    return text, denoised


def capture_region(img):

    ret, mask = cv2.threshold(img, 180,255, cv2.THRESH_BINARY)

    img_final = cv2.bitwise_and(img, img, mask=mask)

    ret, new_img = cv2.threshold(img_final, 180, 255, cv2.THRESH_BINARY_INV)


    kernal =  cv2.getStructuringElement(cv2.MORPH_CROSS, (9,3))

    dilated = cv2.dilate(new_img, kernal, iterations=11)

    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    extracted_text = []
    for contour in contours:
        #Rect-Bounding Contour
        [x, y, width, height] = cv2.boundingRect(contour)
        #Ignore false positives
        if width < 100 or height < 75:
            continue

        

        ocr_image = img[y:y+height, x:x+width]

        cv2.imshow('Img', preprocessing(ocr_image)[1])
        cv2.waitKey(0)
        #print(preprocessing(ocr_image)[0])
        extracted_text.append(preprocessing(ocr_image)[0])
        cv2.rectangle(img, (x, y), (x + width, y + height), (0,0,0),2)

    return img, extracted_text
# capture_region(specific_img)

image = cv2.imread("C:/Users/293740/Desktop/New folder (9)/driverRecord_642.jpg")

# for i in range(25,27):
#     image = cv2.imread(f"C:/Users/293740/Desktop/New folder (4)/driverRecord_{i}.jpg")

#     specific_img = image[3360:5000, :]
#     #specific_img = image[1600:3040, 1970:]
#     specific_img = cv2.resize(specific_img, None, fx = 1, fy = 1.5, interpolation=cv2.INTER_CUBIC)


#     specific_img =cv2.cvtColor(specific_img, cv2.COLOR_BGR2GRAY)
#     print(i)
#     cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
#     cv2.imshow("Sharp Image",capture_region(specific_img))
#     cv2.waitKey(0)
#     # cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
#     # cv2.imshow("Sharp Image",capture_region(specific_img)[1])
#     # cv2.waitKey(0)
#     cv2.destroyAllWindows()

specific_img = image[1600:3040, 1850:]
#specific_img = image[3360:5000, :]
specific_img = cv2.cvtColor(specific_img,cv2.COLOR_BGR2GRAY)
results = capture_region(specific_img)[1]
print(results[::-1])
cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
cv2.imshow("Sharp Image",capture_region(specific_img)[0])
cv2.waitKey(0)
cv2.destroyAllWindows()

def french(input):
    predictions = model.predict(input, k=1)
    language = predictions[0][0].replace('__label__', '')
    return (language)

def separate_text(input_text):
    lowercase_txt = list(map(str.lower, input_text))
    print(lowercase_txt)
    # lines = lowercase_txt.split('\n')
    sections = []

    for line in lowercase_txt:
        line = line.replace("\n",'')
        line = line.strip()  # Remove leading and trailing whitespace
        if re.fullmatch(r"\d+", line):
            sections.append(line)
            continue
        if french(line) == 'fr':  # Skip French text
            print(f"This line {line} is french!")
            continue
        if 'demerit' in line:
            continue
        if '*' in line:
            continue

        else:
            sections.append(line)

    return sections


# def data_seperator(lst):
#     processed_demerit = '00'
#     medical_procedure_list = []
#     medical_date_list = []
#     conviction_list = []

#     previous_entry = None

#     for line in lst:
#         if re.match(r'^[a-zA-Z\s]+$', line) or re.match(r'^[a-zA-Z\'"”\s]+$', line):
#             medical_procedure_list.append(line)
        
#         elif (re.match(r'^\d{2}/\d{2}/\d{2} [a-zA-Z\s._-]+$', line)) or (re.match(r"[\w\-.]+", line)):
#             conviction_list.append(line)
#             previous_entry = line
#             continue
#         elif re.match(r'^[0-9]',line):
#             processed_demerit = line
#         elif re.match(r'^[a-zA-Z\s]+ \d{4}/\d{2}/\d{2}$', line) and 'offence date' not in line:
#             medical_date_list.append(line)
       
#         elif previous_entry != None:
#             if (re.match(r'^\d{2}/\d{2}/\d{2} [a-zA-Z\s._-]+$', previous_entry) and 'offence date' in line) or (re.match(r"[\w\-.]+", previous_entry) and 'offence' in line):
#                 conviction_list[-1] += ' ' + line
#                 previous_entry = None
           
#     return medical_procedure_list, medical_date_list, conviction_list, processed_demerit

def demerit_finder(lst):
    processed_demerit = '00'
    for line in lst:
       if re.fullmatch(r"\d+", line):
            processed_demerit = line
    return processed_demerit

sections = separate_text(results[::-1])
print(sections)
processed_demerit = demerit_finder(sections)
sections = [item for item in sections if not item.isnumeric()]
#print(" ,".join(sections))
print(processed_demerit)

# data = data_seperator(sections)
# print(data)

# cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
# cv2.imshow("Sharp Image",capture_region(specific_img)[0])
# cv2.waitKey(0)
# cv2.destroyAllWindows()
