import cv2
import pyfirmata

#/Arduinoを使うための初期設定
port = 'COM15'                      #ポートの設定
board = pyfirmata.Arduino(port)
it = pyfirmata.util.Iterator(board)
it.start()
pin1 = board.get_pin('d:12:s')       #ピンの設定
#/

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') #顔判定用のカスケードファイルを指定,同じ階層にいるので名前を指定

#/arduinoのmap関数みたいなものを実装
def map(value:float, before_MIN:float, before_MAX:float, after_MIN:float, after_MAX:float) -> float:
    return after_MIN + (after_MAX - after_MIN) * ((value - before_MIN) / (before_MAX - before_MIN))
#/

capture = cv2.VideoCapture(0)    #キャプチャの準備
while capture.isOpened():
    rect, frame = capture.read() #読み込み
    mh, mw = frame.shape[:2]

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                 #顔認識ようにグレースケールを用意する

    faces = face_cascade.detectMultiScale(frame_gray, minSize=(120,120)) #顔認識

    #/顔認識が出来なかった時にFAILを表示
    if len(faces) == 0:
        print('FAIL')
        continue
    #/
    #/サーボモーター用の角度補正用(決め打ち)
    correct_val = 15 #補正用
    unuse_ang = 50 #0~unuse_ang,180~180-unuse_ang
    b_MIN = 0 + 100
    b_MAX = mw - 100
    a_MIN = unuse_ang
    a_MAX = 180 - unuse_ang - correct_val #反転用
    #/

    for x, y, w, h in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) #顔を囲む四角を描画
        face_center_x = x + w / 2
        cv2.drawMarker(frame, (int(face_center_x), int(y + h / 2)), (255, 0, 0)) #顔の中心のマーカーを描画

        ang = a_MAX - int(map(face_center_x, b_MIN, b_MAX, a_MIN, a_MAX)) + unuse_ang #疑似map関数を使って顔の中心の画面位置からサーボの角度を出す
        pin1.write(ang)
        print(ang)
        
        frip_lr = cv2.flip(frame, 1)
        cv2.imshow('face_detect', frip_lr)
        cv2.waitKey(1)