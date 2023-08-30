import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

image = cv2.imread("C:/Users/293740/Desktop/New folder/silver_springs_asbestos_page-0001.jpg")
image_region = image[:500, :]
img = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)

def preprocessing(specified_img_region):

    #gray_image = cv2.cvtColor(specified_img_region, cv2.COLOR_BGR2GRAY)
 
    gaussian_img = cv2.GaussianBlur(specified_img_region,(0,0),3)
  
    ret, img = cv2.threshold(gaussian_img, 185, 255, cv2.THRESH_BINARY )

    denoised = cv2.GaussianBlur(img,(0,0), 3)

    return denoised

def capture_region(img):

    ret, mask = cv2.threshold(img, 180,255, cv2.THRESH_BINARY)

    img_final = cv2.bitwise_and(img, img, mask=mask)

    ret, new_img = cv2.threshold(img_final, 180, 255, cv2.THRESH_BINARY_INV)


    kernal =  cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

    dilated = cv2.dilate(new_img, kernal, iterations=11)

    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    extracted_text = []
    for contour in contours:
        #Rect-Bounding Contour
        [x, y, width, height] = cv2.boundingRect(contour)
        #Ignore false positives
        if width < 100 or height < 75:
            continue

        coordinates = [x, y, width, height]

        # ocr_image = img[y:y+height, x:x+width]

        # cv2.imshow('Img', preprocessing(ocr_image)[1])
        # cv2.waitKey(0)
        # #print(preprocessing(ocr_image)[0])
        # extracted_text.append(preprocessing(ocr_image)[0])
        #cv2.rectangle(img, (x, y), (x + width, y + height), (0,0,0),2)

    return coordinates

x, y, width, height = capture_region(img)
new_img = img[y:y+height, x:x+width]
new_img = preprocessing(new_img)
cv2.namedWindow("Sharp Image", cv2.WINDOW_NORMAL)
cv2.imshow("Sharp Image",new_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(pytesseract.image_to_string(new_img))