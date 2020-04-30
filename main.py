import sys
import threading
import time

from PyQt5.QtWidgets import QMainWindow, QApplication
from selenium import webdriver

from view import mainwindow


class MainWindow(mainwindow.Ui_MainWindow, QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.driver = webdriver.Chrome()
        self.video_num = 0
        self.cookies = []
        self.setupUi(self)
        self.exit_button.setVisible(False)
        self.exit_button.setEnabled(False)
        self.start.clicked.connect(self.button_start_video)
        self.exit_button.clicked.connect(self.button_exit)

    def button_exit(self):
        self.driver.close()
        sys.exit()

    def start_video(self):
        threading.Thread(target=self.before_play).start()

    def button_start_video(self):
        self.start.setVisible(False)
        self.start.setEnabled(False)
        self.exit_button.setVisible(True)
        self.exit_button.setEnabled(True)
        threading.Thread(target=self.play_video).start()

    def load_cookies(self, driver):
        driver.delete_all_cookies()
        for cookie in self.cookies:
            if 'expiry' in cookie.keys():
                del cookie['expiry']
            driver.add_cookie(cookie)
        return driver

    def login(self):

        self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/a[1]").click()
        self.cookies = self.driver.get_cookies()
        time.sleep(2)
        try:
            self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/ul/li[2]/a").click()
        except:
            pass
        threading.Thread(target=self.is_exist).start()
        threading.Thread(target=self.is_pause).start()
        threading.Thread(target=self.is_need_fresh).start()
        self.print("成功登陆...")
        self.driver.maximize_window()
        time.sleep(2)

    def print(self, mes):
        self.textBrowser.append(mes)  # 在指定的区域显示提示信息
        self.cursot = self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.cursot.End)

    def check_status(self):
        time.sleep(2)
        # noinspection PyBroadException
        try:
            self.driver.find_element_by_xpath("/html/body/div/div[3]/div[3]/div[2]/div/a/b").click()
        except:
            pass
        time.sleep(2)
        # 必修模块
        elements = self.driver.find_elements_by_xpath("/html/body/div/div[2]/div[2]/div[2]/div/div[2]//div")
        for element in elements:
            if len(element.find_elements_by_xpath(".//div[2]/div[3]")) != 0:
                if element.find_elements_by_xpath(".//div[2]/div[3]")[0].text == "未完成":
                    son = element.find_elements_by_xpath(".//div[2]/div[2]/a")
                    son[0].click()
                    self.video_from_right_bar()
                    return True
        # 选修模块
        elements = self.driver.find_elements_by_xpath("/html/body/div/div[2]/div[2]/div[2]/div/div[3]//div")
        for element in elements:
            if len(element.find_elements_by_xpath(".//div[2]/div[3]")) != 0:
                if element.find_elements_by_xpath(".//div[2]/div[3]")[0].text == "未完成":
                    son = element.find_elements_by_xpath(".//div[2]/div[2]/a")
                    son[0].click()
                    self.video_from_right_bar()
                    return True

        return False

    def video_from_right_bar(self):
        big_lesson_end = False
        while not big_lesson_end:
            elements = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div[4]/ul//li")
            big_lesson_end = True
            for element in elements:
                style: str
                style = element.find_element_by_xpath(".//a").get_attribute('style')
                self.print("进入当前还未完成的课时...")
                if style.find("red") == -1:
                    self.video_num += 1
                    self.print(f"这是你观看的第{self.video_num}个视频..")
                    element.find_element_by_xpath(".//a").click()
                    time.sleep(2)
                    self.is_end()
                    big_lesson_end = False
                    break

        # go back to the status page
        self.print(f"已完成该大课... \n正在进入下一个大课... \n目前你已观看{self.video_num}个视频")
        self.driver.find_element_by_xpath("/html/body/div[2]/div[1]/a").click()
        time.sleep(2)
        self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/ul/li[2]/a").click()
        time.sleep(2)
        return

    def is_pause(self):
        while True:
            time.sleep(3)
            if len(self.driver.find_elements_by_xpath("/html/body/div[2]/div[3]/div/button")) != 0:
                # noinspection PyBroadException
                try:
                    self.driver.find_element_by_xpath("/html/body/div[2]/div[3]/div/div[1]/video/source").click()
                except:
                    pass

    def is_exist(self):
        while True:
            time.sleep(3)
            if len(self.driver.find_elements_by_xpath("/html/body/div[5]/div[3]/a")) != 0:
                self.print("发现窗口！")

                # noinspection PyBroadException
                try:
                    if self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/a").text == "从头开始":
                        self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/a[2]").click()
                    elif (self.driver.find_element_by_xpath(
                            "/html/body/div[5]/div[2]/p[1]").text.strip() == "视频已暂停，点击按钮后继续学习！".strip()) or (
                            self.driver.find_element_by_xpath(
                                "/html/body/div[5]/div[2]/p[1]").text.strip() == '您需要完整观看一遍课程视频，才能>获取本课学时，'
                                                                                 '看到视频播放完毕提示框即为完成，然后视频可以拖动播放。'.strip()):
                        self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/a").click()
                    self.print("成功关闭窗口！")
                    time.sleep(20)
                except:
                    pass

    def is_need_fresh(self):
        while True:
            time.sleep(3)
            if len(self.driver.find_elements_by_xpath(
                    '/html/body/div[4]/div[@class="layui-layer-content layui-layer-loading2"]')) != 0:
                time.sleep(10)
                if len(self.driver.find_elements_by_xpath(
                        '/html/body/div[4]/div[@class="layui-layer-content layui-layer-loading2"]')) != 0:
                    self.driver.refresh()

    def is_end(self):
        while True:
            time.sleep(3)
            if len(self.driver.find_elements_by_xpath(
                    "/html/body/div[5]/div[3]/a")) != 0 and self.driver.find_element_by_xpath(
                "/html/body/div[5]/div[2]/p[1]").text.strip() == "当前视频播放完毕！".strip():
                self.print("视频播放完毕...")
                # noinspection PyBroadException
                try:
                    self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/a").click()
                    time.sleep(2)
                    self.print("关闭结束提示窗口...")
                except:
                    pass

                # elements = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div[4]/ul//li")
                # for element in elements:
                #     style: str
                #     style = element.find_element_by_xpath(".//a").get_attribute('style')
                #     if style.find("red") == -1:
                #         element.find_element_by_xpath(".//a").click()
                # self.driver.find_element_by_xpath("/html/body/div[2]/div[1]/a").click()
                # time.sleep(2)
                # self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/ul/li[2]/a").click()
                # time.sleep(2)
                return

    def before_play(self):
        self.driver.get("http://172.21.98.150/user/lesson")
        self.driver.maximize_window()

    def play_video(self):
        self.login()
        is_continue = True
        while is_continue:
            is_continue = self.check_status()
            self.print("进入下一个大课...")
        self.print("恭喜你！你完成了所有课时！")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    ui.start_video()
    sys.exit(app.exec_())
