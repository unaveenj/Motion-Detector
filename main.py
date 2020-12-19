import cv2, time
from datetime import datetime
from pathlib import Path
import pandas as pd
my_file = Path("BG.jpg") #background static image
first_frame = None #This will act as the groundd truth
video = cv2.VideoCapture(0)
# print(my_file)

status_list = [0,0]
time_list =[]
df = pd.DataFrame(columns=["Start_time","End_time"])

#Before running the code, hide away from the camera to capture the static background for the first frame in this case
while True:
    flag =0
    check,frame = video.read()
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    #Use gaussian blur to remove noise and imrove accuracy of results
    gray =cv2.GaussianBlur(gray,(21,21),0)
    
    
    if not my_file.is_file():
        print("Capturing background...")
        first_frame=gray
        cv2.imwrite('BG.jpg',first_frame)
        continue #start from beginning of loop
    else:
        print(f"Loading background")
        first_frame = cv2.imread(f'{my_file}', cv2.IMREAD_GRAYSCALE)

    #Now we compare each frame with the initial frame i.e. the first frame
    difference = cv2.absdiff(first_frame,gray)


    #Thresholding
    print(difference)#From printing the difference matrix we can see that the difference values shoots up when a moving object is detected
    #Using this we can set a threshold of 50 to get derive a binary image
    thresh_frame = cv2.threshold(difference,150,255,cv2.THRESH_BINARY)[1]
    #Dilate to improve thresholding
    thresh_frame = cv2.dilate(thresh_frame,None,iterations=2) #Remove the holes in the images

    #Find and measure the countour and its corresponding area
    contours, hierarchy = cv2.findContours(thresh_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contours in contours:
        if cv2.contourArea(contours)<10000:
            continue
        flag = 1
        (x,y,w,h) = cv2.boundingRect(contours)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        

    #Update the time list -> flag = 1 when moving object is detected and vice versa
    status_list.append(flag)
    if status_list[-1] == 1 and status_list[-2] == 0: #Trigger to record time
        time_list.append(datetime.now())
    if status_list[-1]==0 and status_list[-2] == 1 : #triggern to record time when object leaves scene
        time_list.append(datetime.now())

    #Outputs
    cv2.imshow("Gray Frame",gray)
    cv2.imshow("Difference frame",difference) #Display the difference frame
    cv2.imshow("Initial Frame",first_frame)
    cv2.imshow("Image after threshold",thresh_frame)
    cv2.imshow("Color Frame",frame)


    key = cv2.waitKey(1)
    print(flag)
    if key==ord('q'):
        #Add a end time here as well
        if flag == 1:
            time_list.append(datetime.now())
        break
video.release()
cv2.destroyAllWindows()
print(status_list)
print(time_list)
for i in range(0,len(time_list),2):
    df=df.append({"Start_time":time_list[i],"End_time":time_list[i+1]},ignore_index=True)

df.to_csv("Timings.csv")

