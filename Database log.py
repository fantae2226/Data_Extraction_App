import cv2
import pytesseract
import numpy as np
import re
import fasttext
from PIL import Image
# def quicksort(arr):
#     if len(arr) <= 1:
#         return arr
    
#     pivot = arr[len(arr) // 2]
#     left = [i for i in arr if i < pivot]
#     middle = [i for i in arr if i == pivot]
#     right = [i for i in arr if i > pivot]

#     return quicksort(left) + middle + quicksort(right)

database = {

    "Name":[],
    "License Number":[],
    "Date of Birth":[],
    "Sex":[],
    "Height":[],
    "Class":[],
    "Condition":[],
    "Earliest License Date":[],
    "Expiry Date":[],
    "Status":[],
    "Convictions":[],
    "Demerit Points":[]
}



pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

model = fasttext.load_model("C:/Users/293740/Desktop/New folder/lid.176.bin")

x_start = 1965
#width = 700
height = 95
image = cv2.imread("C:/Users/293740/Desktop/New folder (4)/driverRecord_3.jpg")

specific_img = image[1600:3030, 1970:]

# test = cv2.medianBlur(specific_img,7)
# ugh = cv2.resize(test,(3000,120))
specific_img = cv2.resize(specific_img,  None, fx=3, fy=4.5, interpolation=cv2.INTER_CUBIC)

specific_img =cv2.cvtColor(specific_img, cv2.COLOR_BGR2GRAY)

specific_img = cv2.GaussianBlur(specific_img,(0,0),3)

cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
cv2.imshow("Sharp Image",specific_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(pytesseract.image_to_string(specific_img))


def section_extraction(specific_img, threshold=0.01, area_increment=10):
    height, width = specific_img.shape[:2]
    print(height, width)
    extraction_area = 250  # Initial extraction area
    region = None
    regions_list = []
    top_rect = 0

    while top_rect < height:
        # Define the extraction region
        x1 = 0  # Start from the leftmost pixel
        x2 = width  # End at the rightmost pixel
        y1 = top_rect
        y2 = y1 + extraction_area # Limit y2 to the height of the image
        # print(top_rect)
        # print(y2)
        # Extract the region from the image
        region = specific_img[y1:y2, x1:x2]

        # Check the bottom rectangle for empty pixels
        bottom_rect = region[-25:y2, :]  
        empty_pixels = np.sum(bottom_rect == 255)
        
        total_pixels = bottom_rect.size
        error_margin = threshold * total_pixels
        #print(f'Empty pixels: {empty_pixels}  Total Pixles - Error : {total_pixels - error_margin}')
        if empty_pixels >= total_pixels - error_margin:
            #y2 += 10
            regions_list.append(region)
            #top_rect = y2 + 10
            extraction_area = 250 
        else:
            extraction_area += area_increment
        if y2 >= height:
            regions_list.append(region)
            break
    return regions_list


lst = section_extraction(specific_img)

def count_pixels(region):
    # Convert the region to grayscale
    # gray_image = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

    # Count the number of empty (white) pixels
    pixels = np.sum(region <= 127)

    return pixels


extracted_regions_lst = lst

#extracted_regions_lst = list(filter(lambda arr: count_pixels(arr) > 700, lst))

for i,region in enumerate(extracted_regions_lst):
    # Count the number of empty pixels in the region
    pixel_count = count_pixels(region)

    print(f"Region {i} Pixels:", pixel_count)

#print(len(extracted_regions_lst))

# for i in range(len(extracted_regions_lst)):
#     cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
#     cv2.imshow("Sharp Image",extracted_regions_lst[i])
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()


def preprocessing(specified_img_region):

    constant = 4

    #resized = cv2.resize(specified_img_region, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
    gray_image = cv2.cvtColor(specified_img_region, cv2.COLOR_BGR2GRAY)
    #resized = cv2.filter2D(resized, -1,np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) )
    
    h,w = specified_img_region.shape[:2]
    print(h,w)
    block_size = int(min(h, w) * 0.5)

    block_size = max(block_size, 9)  # Set minimum block size to 3
    if block_size % 2 == 0:
        block_size += 1

    gaussian_img = cv2.GaussianBlur(gray_image,(0,0),3)

    #binary_img = cv2.adaptiveThreshold(gaussian_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, constant)
  
    ret, img = cv2.threshold(gaussian_img, 185, 255, cv2.THRESH_BINARY )

    denoised = cv2.GaussianBlur(img,(0,0), 3)

    #gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # kernal = np.ones((1, 1), np.uint8)
    # img = cv2.dilate(gaussian_img,kernal, iterations=1)
    # img = cv2.erode(img,kernal,iterations=1)
    
    # laplacian = cv2.Laplacian(img, cv2.CV_8U)
 
    # sharpened_img = cv2.addWeighted(img, 1, laplacian, -0.25, 0)  # Adjust the weights as per desired effect

    #gray_img = cv2.cvtColor(sharpened_img, cv2.COLOR_BGR2GRAY)


    # #median_img = cv2.medianBlur(binary_img,3)
    # #denoised_image = cv2.GaussianBlur(binary_img, (3, 3), 0) # Apply Gaussian blur

    # kernal = np.array([[-1,-1,-1],
    #                  [-1, 9,-1],
    #                  [-1,-1,-1]])
    
    

    # weighted_img = cv2.addWeighted(specified_img_region, 1.7, gaussian_img, -0.7, 0)

    # sharp_img = cv2.filter2D(weighted_img,-1,kernal)

    custom_config = r'--psm 7'

    text = pytesseract.image_to_string(denoised, config=custom_config)

    return text, denoised

# for region in extracted_regions_lst:
#     print(preprocessing(region)[0])

# # # cv2.namedWindow("Help", cv2.WINDOW_NORMAL)
# # # cv2.imshow("Help", ugh)
# # # print(pytesseract.image_to_string(ugh, config='--psm 6'))
# # # print(preprocessing(specific_img)[0])
#     cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
#     cv2.imshow("Sharp Image", preprocessing(region)[1])
#     cv2.waitKey(800)
#     cv2.destroyAllWindows()