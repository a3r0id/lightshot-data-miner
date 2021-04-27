import face_recognition
from PIL import Image, ImageDraw
from os import getcwd

imLocation = getcwd() + "\\tests\\test.jpg"

resultLocation = getcwd() + "\\tests\\faces\\"

image = face_recognition.load_image_file(imLocation)
face_locations = face_recognition.face_locations(image)
face_landmarks = face_recognition.face_landmarks(image)

im = Image.open(imLocation) 

width, height = im.size

index = 0
for face in face_locations:

    # get a drawing context
    drawingsLayer = ImageDraw.Draw(im)

    landmarks = face_landmarks[index]

    for mark in landmarks:
        for pointArray in landmarks[mark]:
            cords = pointArray + pointArray
            drawingsLayer.line(cords, fill=(255,0,0,255), width=3)

    # crop (left, top, right, bottom)
    # face (top, right, bottom, left)
    imageBuffer = im.crop((face[3], face[0], face[1], face[2]))
    imageBuffer.save("%s%s.png" % (resultLocation, str(index),)) 
    
    #imageBuffer.show()
    #im.show()

    index += 1
