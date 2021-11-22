'''
    python3.8 -m venv venv
    source venv/bin/activate
'''

import cv2
import numpy as np
import pandas as pd
from pandas.core import frame
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from PIL import Image
import PIL.ImageOps
import os, ssl, time

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl,'_create_unverified_context',None)):
    ssl._create_default_https_context = ssl._create_unverified_context


X = np.load('image.npz')['arr_0']
y = pd.read_csv('https://raw.githubusercontent.com/whitehatjr/datasets/master/C%20122-123/labels.csv')['labels']
classes = ['a', 'b', 'c','d', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
nclasses = len(classes)

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=9, train_size=7500, test_size=2500)

X_train_scaled = X_train/255.0
X_test_scaled = X_test/255.0

clf = LogisticRegression(solver='saga', multi_class='multinomial').fit(X_train_scaled, y_train)
y_pred = clf.predict(X_test_scaled)

cap = cv2.VideoCapture("0")
while(True):
    try:
        ret, frame = cap.read()
        
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        height, width = grey.shape
        upper_left = (int(width / 2 - 56), int(height / 2 - 56)) 
        bottom_right = (int(width / 2 + 56), int(height / 2 + 56))
        cv2.rectangle(grey, upper_left, bottom_right, (0, 255, 0), 2)
        
        roi = grey[upper_left[1]:bottom_right[1], upper_left[0]:bottom_right[0]]
        
        im_pil = Image.fromarray(roi)
        image_bw = im_pil.convert('L')
        image_bw_resized = image_bw.resize((28,28), Image.ANTIALIAS)
        
        image_bw_resized_inverted = PIL.ImageOps.invert(image_bw_resized) 
        pixel_filter = 20 
        min_pixel = np.percentile(image_bw_resized_inverted, pixel_filter) 
        image_bw_resized_inverted_scaled = np.clip(image_bw_resized_inverted-min_pixel, 0, 255) 
        max_pixel = np.max(image_bw_resized_inverted) 
        image_bw_resized_inverted_scaled = np.asarray(image_bw_resized_inverted_scaled)/max_pixel 
        test_sample = np.array(image_bw_resized_inverted_scaled).reshape(1,784) 
        test_pred = clf.predict(test_sample) 
        print("Predicted class is: ", test_pred)
        cv2.imshow('frame',grey) 
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    except Exception as e:
        pass
    
cap.release()
cv2.destroyAllWindows()