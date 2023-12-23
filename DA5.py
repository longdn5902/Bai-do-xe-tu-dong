import cv2
from pytesseract import pytesseract 
from PIL import Image
import mysql.connector
import datetime

def connectdb():
    con =  mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        database = 'baixe'
    )
    return con

def checkNp(number_plate):
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT * FROM info WHERE Numcar = %s"
    cursor.execute(sql,(number_plate,))
    cursor.fetchall()
    result = cursor._rowcount
    con.close()
    cursor.close()
    return result

def checkNpStatus(number_plate):
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT * FROM info WHERE Numcar = %s ORDER BY date_in DESC LIMIT 1"
    cursor.execute(sql,(number_plate,))
    result = cursor.fetchone()
    con.close()
    cursor.close()

def insertNp(number_plate):
    con = connectdb()
    cursor = con.cursor()
    sql = "INSERT INTO info(Numcar,status,date_in) VALUE(%s,%s,%s)"
    now = datetime.datetime.now()
    date_in = now.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute(sql,(number_plate,'0',date_in))
    con.commit()
    cursor.close()
    con.close()
    print("Vao Bai Xe")

def updateNp(Id):
    con = connectdb()
    cursor =con.cursor()
    sql = "UPDATE info SET status = 0, date_out = %s WHERE Id = %s "
    now = datetime.datetime.now()
    date_out = now.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute(sql,(date_out,Id))
    con.commit()
    cursor.close()
    con.close()
    print("ra bai")


def readnumberplate():
    pytesseract.tesseract_cmd = r"C:\Users\User\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    img = Image.open(r"C:\Users\User\Desktop\DA5\img\number.jpg")
    text = pytesseract.image_to_string(img,lang="eng")

    number_plate = ''
    for char in str(text):
        if(char.isspace()==False):
            number_plate+=char
    print("-------------------------------------------")
    print("xe co bien so: " + number_plate)
    print("--------------------------------------------")
    if(number_plate!=""):
        check = checkNp(number_plate)
        if(check==0):
            insertNp(number_plate)
        else:
            check2 = checkNpStatus(number_plate)
            if(check2[2] ==1 ):
                updateNp(check2[0])
            else:
                insertNp(number_plate)
    else:
        print("Bien so ko xac dinh!")

    
cam = cv2.VideoCapture(0)
while True:
    ref,frame = cam.read()
    framegray = cv2.cvtColor(frame,cv2.COLOR_BGR2BGRA) 
    n_plate_detector = cv2.CascadeClassifier("haarcascade_russian_plate_number.xml")
    detections = n_plate_detector.detectMultiScale(framegray,scaleFactor=1.05,minNeighbors=3)
    for(x,y,w,h) in detections:
        cv2.rectangle(framegray,(x,y),(x+w,y+h),(0,255,255),2)
        cv2.putText(framegray,"Bien so xe",(x-20,y-10),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,255,255),2)
        number_plate = framegray[y:y+h,x:x+w]
        gray = cv2.cvtColor(number_plate,cv2.COLOR_BGR2GRAY)
        cv2.imshow("Bien so xe",gray)
        key = cv2.waitKey(1)
        if key==ord('s'):
            cv2.imwrite('img/number.jpg',gray)
            readnumberplate()
    if cv2.waitKey(1) == ord('q'):
        break
    cv2.imshow("Cam",framegray)

cam.release()
cv2.destroyAllWindows()