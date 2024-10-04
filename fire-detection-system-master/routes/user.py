import cv2
import time
import threading
from ultralytics import YOLO
import os
import sys

from flask import Blueprint, g, escape, session, redirect, render_template, request, jsonify, Response, flash
from werkzeug.utils import secure_filename

from app import DAO
from Misc.functions import *

from Controllers.UserManager import UserManager
from Controllers.BookManager import BookManager

user_view = Blueprint('user_routes', __name__, template_folder='/templates')

user_manager = UserManager(DAO)
book_manager = BookManager(DAO)


@user_view.route('/', methods=['GET'])
def home():
    g.bg = 1

    user_manager.user.set_session(session, g)
    print(g.user)

    return render_template('home.html', g=g)


@user_view.route('/signin', methods=['GET', 'POST'])
@user_manager.user.redirect_if_login
def signin():
    if request.method == 'POST':
        _form = request.form
        email = str(_form["email"])
        password = str(_form["password"])

        if len(email) < 1 or len(password) < 1:
            return render_template('signin.html', error="Email and password are required")

        d = user_manager.signin(email, hash(password))

        if d and len(d) > 0:
            session['user'] = int(d['id'])

            return redirect("/")

        return render_template('signin.html', error="Email or password incorrect")

    return render_template('signin.html')


@user_view.route('/signup', methods=['GET', 'POST'])
@user_manager.user.redirect_if_login
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if len(name) < 1 or len(email) < 1 or len(password) < 1:
            return render_template('signup.html', error="All fields are required")

        new_user = user_manager.signup(name, email, hash(password))

        if new_user == "already_exists":
            return render_template('signup.html', error="User already exists with this email")

        return render_template('signup.html', msg="You've been registered!")

    return render_template('signup.html')


@user_view.route('/signout/', methods=['GET'])
@user_manager.user.login_required
def signout():
    user_manager.signout()

    return redirect("/", code=302)


@user_view.route('/user/', methods=['GET'])
@user_manager.user.login_required
def show_user(id=None):
    user_manager.user.set_session(session, g)

    if id is None:
        id = int(user_manager.user.uid())

    d = user_manager.get(id)
    mybooks = user_manager.getBooksList(id)

    return render_template("profile.html", user=d, books=mybooks, g=g)


@user_view.route('/user', methods=['POST'])
@user_manager.user.login_required
def update():
    user_manager.user.set_session(session, g)

    _form = request.form
    name = str(_form["name"])
    email = str(_form["email"])
    password = str(_form["password"])
    bio = str(_form["bio"])

    user_manager.update(name, email, hash(password), bio, user_manager.user.uid())

    flash('Your info has been updated!')
    return redirect("/user/")


sys.path.append(os.path.join(os.path.dirname(__file__)))
import lalerts
from file_handler import save_uploaded_file

current_dir = os.path.dirname(os.path.abspath(__file__))
personModel = YOLO(os.path.join(current_dir, 'yolov8s.pt'))
fireModel = YOLO(os.path.join(current_dir, 'best (2).pt'))
# fireModel = YOLO('fire_detection_model.pt')
# fireModel = YOLO('mybest.pt')


@user_view.route('/detect/', methods=['POST'])
@user_manager.user.login_required
def detect():

    # Kiểm tra xem file có trong request không
    if 'video' not in request.files:
        return 'Không có file nào được tải lên'

    file = request.files['video']

    if file.filename == '':
        return 'Không có file nào được chọn'

    filename = secure_filename(file.filename)
    file_path = save_uploaded_file(file, filename)
    print(f'File đã được tải lên: {filename}, đường dẫn trên server: {file_path}')


    recipients = book_manager.getAllEmail()

    # status
    status = ['', 'canhbao', 'nguy co', 'nguy hiem']

    # set fps
    fps = 30  # kiểm tra bao nhiêu khung hình trên một giây < lấy gần bằng>

    conf_fire = 0.3  # hệ số cài đặt nhận diện lửa
    conf_per = 0.6  # hệ số cài đặt nhân diện con người

    frame_count = 0  # số frame để tính fps
    start_time = time.time()  # thời gian chương trình bắt đầu chạy < lấy đây là gốc tương đối so sánh các mốc thời gian khác, có thể xóa nếu vào chương trình thật>
    time_notication = 0

    # rate fire and person
    rate_fire = False  # dùng để kiểm tra điều kiện hiển thị thông báo
    rate_person = False

    # count_detected fire and person
    count_frame_fire = 0  # số frame detect lửa, sẽ set về 0 lại trong nhiều trường hợp
    count_frame_person = 0  # số frame detect con người, sẽ set lại về 0 trong nhiều trường hợp

    # time_reset_all
    global start_time_fire  # thời gi bắt đầu phát hiện ngọn lửa đầu tiên
    start_time_fire = 0
    start_time_person = 0

    # mediate_setting
    mediate_fire = False  # các biến trung gian, là nguồn dẫn điều kiện để thực hiện các điều kiện khác trong vòng lạp while
    mediate_notication = False
    mediate_person = False
    canh_bao = False

    # time setting
    time_fire_danger = 10  # thoi gian gui canh bao dau tien
    time_fire_danger2 = 10

    # check gui email 1 lan
    check1 = True
    check2 = True
    check3 = True

    cap = cv2.VideoCapture(file_path)
    # cap = cv2.VideoCapture(os.path.join(current_dir, 'otofaster.mp4'))
    # cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 10)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

    def wait_10s():
        time.sleep(time_fire_danger2)
        global canh_bao
        canh_bao = True

    while True:
        ret, frame = cap.read()
        frame_count += 1  # dùng để tính fps

        # test code
        print("-----------mediate_fire", mediate_fire)
        print("-----------time run realtime: ", time.time() - start_time)
        ##handle with detected fire
        fireDetected = fireModel.predict(frame, show=False, conf=conf_fire)  # model phát hiện lửa

        # get position each fire
        for results in fireDetected[0].boxes:  # xử lý trong những ngọn lửa

            ##start handle with detectfire = true
            if (mediate_fire == False):

                if (count_frame_fire != 0):
                    mediate_person = True
                    mediate_fire = True
                    start_time_fire = time.time()
                    count_frame_person = 0
                    print('--------Time check fire start counting!')

            if (mediate_fire == True):
                print('-----------------time check fire: ', time.time() - start_time_fire)
                print("-----------------------rate_fire: ",
                      count_frame_fire / ((time.time() - start_time_fire + 1) * fps))

            count_frame_fire += 1 / len(fireDetected[0].boxes)
            print(count_frame_fire)
            print(count_frame_person)

            # print(i[0])
            for box in results:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cv2.putText(frame, "Fire", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)

        if (time.time() - start_time_fire > time_fire_danger and time.time() - start_time_fire < time_fire_danger + 10):
            print("-----------------------rate_fire: ", count_frame_fire / ((time.time() - start_time_fire + 1) * fps))
            if (count_frame_fire / ((time.time() - start_time_fire + 1) * fps) > 0.6):
                print(' gui loi canh bao toi nguoi dung ------------------------------')
                rate_fire = True
            mediate_fire = False
            count_frame_fire = 0
            if (count_frame_person / ((time.time() - start_time_fire + 1) * fps) > 0.6):
                rate_person = True
            count_frame_person = 0
            start_time_fire = 0

        if (rate_fire):

            if (rate_person == False):
                if canh_bao == True:
                    cv2.putText(frame, 'Nguy hiem', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    if (check1):
                        lalerts.sendEmail("Nguy hiểm có nguy cơ xảy ra hỏa hoạn", "NGUY HIỂM", recipients)
                        check1 = False
                else:
                    cv2.putText(frame, 'Canh bao', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    t = threading.Thread(target=wait_10s)
                    t.start()
                    if (check2):
                        lalerts.sendEmail("Cảnh báo có xuất hiện đám cháy", "CẢNH BÁO", recipients)
                        check2 = False


            else:
                cv2.putText(frame, 'can than', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                if (check3):
                    lalerts.sendEmail("Cẩn thận tránh xa khỏi đám cháy đó", "CẨN THẬN", recipients)
                    check3 = False

            if (mediate_notication == False):
                time_notication = time.time()
                mediate_notication = True
                print('-----------------------------------------------------------------')
            elif (time.time() - time_notication > 5 and time.time() - time_notication < 10):
                rate_fire = False
                mediate_notication = False

        print('rate_person: ', rate_person)
        print('person frame: ', count_frame_person)

        ##handle with detecd person

        personDetected = personModel.predict(frame, classes=0, show=False, conf=conf_per)
        # get position each person

        for results in personDetected[0].boxes:

            count_frame_person += 1 / len(personDetected[0].boxes)

            for box in results:
                # start handle person with detectperson = True
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 5)
                cv2.putText(frame, "Person", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)

        fps = frame_count / (time.time() - start_time)
        cv2.putText(frame, "FPS: {:.2f}".format(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow('nhan dien ngon lua canh bao hoa hoan!', frame)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()


    # return fireModel.imgs[0]
    return render_template("home.html")


@user_view.route('/camera/', methods=['GET'])
@user_manager.user.login_required
def camera():


    # status
    status = ['', 'canhbao', 'nguy co', 'nguy hiem']

    # set fps
    fps = 30  # kiểm tra bao nhiêu khung hình trên một giây < lấy gần bằng>

    conf_fire = 0.3  # hệ số cài đặt nhận diện lửa
    conf_per = 0.6  # hệ số cài đặt nhân diện con người

    frame_count = 0  # số frame để tính fps
    start_time = time.time()  # thời gian chương trình bắt đầu chạy < lấy đây là gốc tương đối so sánh các mốc thời gian khác, có thể xóa nếu vào chương trình thật>
    time_notication = 0

    # rate fire and person
    rate_fire = False  # dùng để kiểm tra điều kiện hiển thị thông báo
    rate_person = False

    # count_detected fire and person
    count_frame_fire = 0  # số frame detect lửa, sẽ set về 0 lại trong nhiều trường hợp
    count_frame_person = 0  # số frame detect con người, sẽ set lại về 0 trong nhiều trường hợp

    # time_reset_all
    global start_time_fire  # thời gi bắt đầu phát hiện ngọn lửa đầu tiên
    start_time_fire = 0
    start_time_person = 0

    # mediate_setting
    mediate_fire = False  # các biến trung gian, là nguồn dẫn điều kiện để thực hiện các điều kiện khác trong vòng lạp while
    mediate_notication = False
    mediate_person = False
    canh_bao = False

    # time setting
    time_fire_danger = 10  # thoi gian gui canh bao dau tien
    time_fire_danger2 = 10

    # check gui email 1 lan
    check1 = True
    check2 = True
    check3 = True


    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 10)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

    def wait_10s():
        time.sleep(time_fire_danger2)
        global canh_bao
        canh_bao = True

    while True:
        ret, frame = cap.read()
        frame_count += 1  # dùng để tính fps

        # test code
        print("-----------mediate_fire", mediate_fire)
        print("-----------time run realtime: ", time.time() - start_time)
        ##xử lý khi phát hiện cháy
        fireDetected = fireModel.predict(frame, show=False, conf=conf_fire)  # model phát hiện lửa

        # lấy vị trí mỗi đám cháy
        for results in fireDetected[0].boxes:  # xử lý trong những ngọn lửa

            ##bắt đầu xử lý với detectfire = true
            if (mediate_fire == False):

                if (count_frame_fire != 0):
                    mediate_person = True
                    mediate_fire = True
                    start_time_fire = time.time()
                    count_frame_person = 0
                    print('--------Time check fire start counting!')

            if (mediate_fire == True):
                print('-----------------time check fire: ', time.time() - start_time_fire)
                print("-----------------------rate_fire: ",
                      count_frame_fire / ((time.time() - start_time_fire + 1) * fps))

            count_frame_fire += 1 / len(fireDetected[0].boxes)
            print(count_frame_fire)
            print(count_frame_person)

            # print(i[0])
            for box in results:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cv2.putText(frame, "Fire", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)

        if (time.time() - start_time_fire > time_fire_danger and time.time() - start_time_fire < time_fire_danger + 10):
            print("-----------------------rate_fire: ", count_frame_fire / ((time.time() - start_time_fire + 1) * fps))
            if (count_frame_fire / ((time.time() - start_time_fire + 1) * fps) > 0.6):
                print(' gui loi canh bao toi nguoi dung ------------------------------')
                rate_fire = True
            mediate_fire = False
            count_frame_fire = 0
            if (count_frame_person / ((time.time() - start_time_fire + 1) * fps) > 0.6):
                rate_person = True
            count_frame_person = 0
            start_time_fire = 0

        if (rate_fire):

            if (rate_person == False):
                if canh_bao == True:
                    cv2.putText(frame, 'Nguy hiem', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    if (check1):
                        lalerts.sendEmail("Nguy hiểm có nguy cơ xảy ra hỏa hoạn", "NGUY HIỂM")
                        check1 = False
                else:
                    cv2.putText(frame, 'Canh bao', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    t = threading.Thread(target=wait_10s)
                    t.start()
                    if (check2):
                        lalerts.sendEmail("Cảnh báo có xuất hiện đám cháy", "CẢNH BÁO")
                        check2 = False


            else:
                cv2.putText(frame, 'can than', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                if (check3):
                    lalerts.sendEmail("Cẩn thận tránh xa khỏi đám cháy đó", "CẨN THẬN")
                    check3 = False

            if (mediate_notication == False):
                time_notication = time.time()
                mediate_notication = True
                print('-----------------------------------------------------------------')
            elif (time.time() - time_notication > 5 and time.time() - time_notication < 10):
                rate_fire = False
                mediate_notication = False

        print('rate_person: ', rate_person)
        print('person frame: ', count_frame_person)

        ##handle with detecd person

        personDetected = personModel.predict(frame, classes=0, show=False, conf=conf_per)
        # get position each person

        for results in personDetected[0].boxes:

            count_frame_person += 1 / len(personDetected[0].boxes)

            for box in results:
                # start handle person with detectperson = True
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 5)
                cv2.putText(frame, "Person", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)

        fps = frame_count / (time.time() - start_time)
        cv2.putText(frame, "FPS: {:.2f}".format(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow('nhan dien ngon lua canh bao hoa hoan!', frame)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()


    # return fireModel.imgs[0]
    return render_template("home.html")