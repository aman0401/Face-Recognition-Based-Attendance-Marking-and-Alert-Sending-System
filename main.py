import cv2

import numpy as np

import face_recognition ##from dlib

import os ##to read the images

from datetime import datetime

import pandas as pd

import pyttsx3#speaking

import pyperclip

from time import sleep

from selenium import webdriver, common#whatsapp messages automation

from selenium.webdriver.common.keys import Keys

engine = pyttsx3.init()

#function to speak out the text given during calling
def speak(txt):
    engine.say(txt)
    engine.runAndWait()

#reading images

path ='images'
images=[]  #images will go into this list
PersonName=[]
mylist = os.listdir(path) #images have been put into list
print(mylist)

for cu_img in mylist:
    current_img = cv2.imread(f'{path}/{cu_img}')
    images.append(current_img)#putting the images into the list
    PersonName.append(os.path.splitext(cu_img)[0]) #putting the names in the path into the list
print(PersonName)

#face encoding(dlib encodes our face based on 128 unique features) function

def faceEncodings(images):
    speak('please wait, while the faces are being encoded.')
    encodelist=[]

    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    return encodelist

#print(faceEncodings(images))##HOG ALGORITHM

encodeListKnown =faceEncodings(images)
speak('all encodings are completed')
print("all encodings are completed!!!!!")


#marking the attendece

def attendence(name):
    with open('attendance.csv','r+') as f:
        mydatalist = f.readlines()
        namelist = []
        for line in mydatalist:
            entry = line.split(',')#split the data using ','
            namelist.append(entry[0])

            if name not in namelist:
                time_now = datetime.now()
                tstr = time_now.strftime('%H:%M:%S')
                dstr = time_now.strftime('%d/%m/%y')
                f.writelines(f'\n{name},{tstr},{dstr}')

#opening the webcam of laptop

cap = cv2.VideoCapture(0)
lst=[]

while True:
    ret, frame = cap.read()
    faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)#adjusting the frame
    faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

    facesCurrentFrame = face_recognition.face_locations(faces)#all the faces of the current frame will be put into a separate variable
    encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

    for encodeFace, faceloc in zip(encodesCurrentFrame, facesCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)#if distance is more face doesnt match if distance is less then face matches

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = PersonName[matchIndex].upper()

            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(frame, (x1, y1), (x2, y2),(0,255,0),2)#displaying rectangle on the face
            cv2.rectangle(frame, (x1, y2-35), (x2, y2), (0,255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1 , (0, 0, 255), 2)#displaying name below the face

            if name in lst:
                continue
            speak('{} , you have been marked present'.format(name))
            attendence(name)
            lst.append(name)
            print(lst)

    cv2.imshow("Camera", frame)#creating camera frame
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break

#cap.release()


dataframe = pd.read_csv("attendance.csv")
print('*'*100)
print(" "*40 + 'please copy this attendance' + " "*40)
speak("please copy this attendance")
y=dataframe.drop_duplicates('Name')
y.reset_index(drop=True, inplace=True)
#dataframe.reset_index(drop=True, inplace=True)
speak('attendance is being printed')
print(y)
y.to_csv('attendance2.csv')

global browser
browser = webdriver.Chrome()
browser.get("https://web.whatsapp.com/")
sleep(10)
speak("please enter target no.")
target_no = int(input("please enter target no."))
browser.find_element_by_css_selector("._13NKt.copyable-text.selectable-text").send_keys(target_no)#search button

sleep(3)
ele_found = "False"
while True:
    try:
        first_ele = browser.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[3]/div/div[2]/div[1]/div/div/div[7]/div/div/div[2]/div[1]/div[1]")
        first_ele.click()
        ele_found = "True"
    except:
        print("trying again")
        continue
    if ele_found:
       break

browser.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[4]/div[1]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]").send_keys(Keys.CONTROL,'v')#pasting on typing bar
browser.find_element_by_css_selector("._4sWnG").click() #send button
print("msg sent done")







