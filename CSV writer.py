import csv
import os

extracted_data = [['Name', 'License Number', 'Date of Birth', 'Sex', 'Height', 'Class', 'Condition','Earliest License Date','Expiry Date', 'Status','Demerit', 'Medical Procedures', 'Medical Date', 'Convictions']
                  
                  
                  ]

folder_path = "C:/Users/293740/Desktop/New folder (10)"

base_name = "driverRecord_"
extension = ".jpg"
start_index = 790

files = os.listdir(folder_path)

for i, file_name in enumerate(files, start=start_index):
    new_file_name = f"{base_name}{i}{extension}"

    os.rename(os.path.join(folder_path, file_name), os.path.join(folder_path, new_file_name))

    print(f"Renamed File: {file_name} -> {new_file_name}")

#print(files)