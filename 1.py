from bilibili_api import video, Verify, exceptions, user

#from tkinter import *
import tkinter as tk
from tkinter import scrolledtext
import tkinter.messagebox

from PIL import Image, ImageTk
import requests as req
from io import BytesIO
from selenium import webdriver
import webbrowser

from time import sleep
import re
import pickle

window = tk.Tk()
window.title('111')
window.geometry('1000x700')

ver = None
lb = None

var_sess = tk.StringVar()
var_sess.set("")
var_csrf = tk.StringVar()
var_csrf.set("")
var_bvid = tk.StringVar()
var_bvid.set("BV1uv411q7Mv")
var_upid = tk.StringVar()
var_upid.set("384521381")
var_progress = tk.StringVar()


def get_bili_cookies():
    browser = webdriver.Firefox(executable_path="D:\GeckoDriver\geckodriver")
    browser.get("https://passport.bilibili.com/login")
    while True:
        sleep(3)
        while browser.current_url == "https://www.bilibili.com/":
            bili_cookies = browser.get_cookies()
            browser.quit()
            cookies = {}
            for item in bili_cookies:
                cookies[item['name']] = item['value']
            with open('biliCookies.pickle', 'wb') as new_pickle:
                pickle.dump(cookies, new_pickle)
            return cookies['SESSDATA'], cookies['bili_jct']


def get_s_c():
    global ver
    input_sessdata = var_sess.get()
    input_csrf = var_csrf.get()
    ver = Verify(sessdata=input_sessdata, csrf=input_csrf)

    ret = ver.check()['code']
    if ret == 0:
        tkinter.messagebox.showinfo(message='验证成功！')
    elif ret == -1:
        tkinter.messagebox.showwarning(message='csrf 校验失败')
    elif ret == -2:
        tkinter.messagebox.showwarning(message='SESSDATA值有误')


def get_sc_button():
    try:
        open('biliCookies.pickle')
    except FileNotFoundError:
        sc = get_bili_cookies()
        var_sess.set(sc[0])
        var_csrf.set(sc[1])

    else:
        with open('biliCookies.pickle', 'rb') as file:
            data = pickle.load(file)
            var_sess.set(data['SESSDATA'])
            var_csrf.set(data['bili_jct'])


def get_pic(url, size_x=-1, size_y=-1):
    img_res = req.get(url)
    video_image = Image.open(BytesIO(img_res.content))
    if size_x != -1 and size_y != -1:
        video_image_rsz = video_image.resize((size_x, size_y))
    return ImageTk.PhotoImage(video_image_rsz)


def up_confirm():
    try:
        up_info = user.get_user_info(uid=var_upid.get(), verify=ver)
    except exceptions.BilibiliException as msg:
        if msg.code == -400 or -10:
            tkinter.messagebox.showwarning(message='up主id错误！')
    else:

        info_window = tk.Toplevel()
        info_window.title('up主详情')
        info_window.geometry('1000x800')

        render_face = get_pic(up_info['face'], 200, 200)
        img_display = tk.Label(info_window, image=render_face)
        img_display.place(x=50, y=50)

        name_label = tk.Label(info_window, text=up_info['name'],
                              font=("微软雅黑", 14, "bold"),  height=1)
        name_label.place(x=300, y=50)
        sign_label = tk.Label(info_window, text="签名:  " + up_info['sign'],
                              font=("微软雅黑", 12), height=3)
        sign_label.place(x=300, y=100)

        label_temp = tk.Label(info_window, text="投稿视频信息: ",
                              font=("微软雅黑", 20, "bold"),  height=1)
        label_temp.place(x=50, y=275)

        v_list = user.get_videos(uid=var_upid.get(), verify=ver)
        if v_list is None:
            label_temp = tk.Label(info_window, text="该up尚未投稿哦~ ",
                                  font=("微软雅黑", 14), height=1)
            label_temp.place(x=350, y=450)
        else:
            lb = tk.Listbox(info_window, width=40, height=20)
            for i in range(len(v_list)):
                lb.insert('end', str(i) + '.' + v_list[i]['title'])

            def open_url(event):
                temp = lb.curselection()[0]
                bv = v_list[temp]['bvid']
                url = 'https://www.bilibili.com/video/' + bv
                webbrowser.open(url, new=0)

            title = tk.Label(info_window, text='', cursor='hand2',
                             font=("微软雅黑", 13, "bold"), height=2)
            title.place(x=320, y=180)
            title.bind("<Button-1>", open_url)
            title.bind("<Enter>", lambda event: title.config(underline=True))
            title.bind("<Leave>", lambda event: title.config(underline=False))

            def video_info(self):
                i = lb.curselection()[0]

                render_sel_video = get_pic('http:' + v_list[i]['pic'], 500, 300)
                img_sel_display = tk.Label(info_window, image=render_sel_video)
                img_sel_display.place(x=350, y=250)

                describe = scrolledtext.ScrolledText(info_window, font=("微软雅黑", 10),
                                                     width=70, height=9)
                describe.config(state=tk.NORMAL)
                describe.insert(tk.INSERT, v_list[i]['description'])
                describe.config(state=tk.DISABLED)
                describe.place(x=350, y=570)
                title.config(text=v_list[i]['title'] + '  <-点击进入网页查看...')

                info_window.mainloop()

            lb.place(x=20, y=350)
            lb.bind(sequence='<<ListboxSelect>>',
                    func=video_info)

        info_window.mainloop()


def video_confirm():
    bv = var_bvid.get()
    if bv is None:
        tkinter.messagebox.showwarning(message='请填写bv号')
    elif ver is None:
        tkinter.messagebox.showwarning(message='请先验证！')
    else:
        if bv[:4] == 'http' or bv[:3] == 'www':
            bv = re.search("/BV[\w]*\?", bv).group()[1:-1]
        comp_info = video.get_video_info(bvid=bv, is_simple=False, verify=ver)
        render = get_pic(comp_info['pic'], 400, 250)

        info_window = tk.Toplevel()
        info_window.title('视频详情')
        info_window.geometry('800x800')

        img_display = tk.Label(info_window, image=render)
        img_display.place(x=20, y=50)

        title = tk.Label(info_window, text='标题： ' + comp_info['title'], font=("微软雅黑", 14, "bold"), height=1)

        describe = scrolledtext.ScrolledText(info_window, font=("微软雅黑", 10), height=7)
        describe.insert(tk.INSERT, comp_info['desc'])
        describe.config(state=tk.DISABLED)
        describe.place(x=50, y=380)

        tag = tk.Label(info_window, text='标签：' + comp_info['tname'], font=("微软雅黑", 10, "bold"), height=2)
        describe_label = tk.Label(info_window, text='简介：', font=("微软雅黑", 12, "bold"), height=2)
        dynamic = tk.Label(info_window, text='动态：' + comp_info['dynamic'], font=("微软雅黑", 10, "bold"), height=2)
        likes = str(comp_info['stat']['like'])
        coins = str(comp_info['stat']['coin'])
        fav = str(comp_info['stat']['favorite'])  #
        state = tk.Label(info_window, text='点赞:' + likes + '    硬币:' +
                                           coins + '    收藏:' + fav, font=("微软雅黑", 10, "bold"), height=2)
        title.pack()
        describe_label.place(x=325, y=320)
        tag.place(x=450, y=50)
        dynamic.place(x=450, y=100)
        state.place(x=450, y=150)

        button_c_s = tk.Button(info_window, text="点赞", command=b_set_like)
        button_c_s.place(x=100, y=520)

        button_c_s = tk.Button(info_window, text="投币", command=b_add_coin)
        button_c_s.place(x=200, y=520)

        button_c_s = tk.Button(info_window, text="获取收藏列表", command=lambda: set_fav_list(info_window))
        button_c_s.place(x=300, y=520)

        info_window.mainloop()


def update_progress(cur, total):
    var_progress.set('处理进度：' + str(cur) + '/' + str(total))
    if cur == total:
        var_progress.set('处理完毕！')


def b_set_like():
    if video.is_liked(bvid=var_bvid.get(), verify=ver):
        tkinter.messagebox.showwarning(message='已经赞过了！')
    else:
        video.set_like(bvid=var_bvid.get(), status=True, verify=ver)


def set_like_all(id):
    try:
        v_list = user.get_videos(uid=id, verify=ver)
    except exceptions.BilibiliException as msg:
        if msg.code == -400 or -10:
            tkinter.messagebox.showwarning(message='up主id错误！')
    else:
        if v_list is None:
            tkinter.messagebox.showwarning(message='该up主未投稿！')
        else:
            is_liked = 0
            liked = 0
            for i in range(len(v_list)):
                bvid = v_list[i]['bvid']
                if video.is_liked(bvid=bvid, verify=ver):
                    is_liked += 1
                else:
                    video.set_like(bvid=bvid, status=True, verify=ver)
                    liked += 1

                update_progress(i + 1, len(v_list))
                window.update()

            tkinter.messagebox.showinfo(message='之前已点赞：' + str(is_liked)
                                        + '      本次点赞：' + str(liked))


def b_add_coin():
    try:
        video.add_coins(bvid=var_bvid.get(), verify=ver, num=1)
    except exceptions.BilibiliApiException as msg:
        if msg.code == 34005:
            tkinter.messagebox.showwarning(message='超过投币上限啦~')
        if msg.code == -605:
            tkinter.messagebox.showwarning(message='速度答题成为正式会员')
        if msg.code == -104:
            tkinter.messagebox.showwarning(message='硬币不足！')
    else:
        tkinter.messagebox.showinfo(message='已投币 +1')


def add_coin_all(id):
    try:
        v_list = user.get_videos(uid=id, verify=ver)
    except exceptions.BilibiliException as msg:
        if msg.code == -400 or -10:
            tkinter.messagebox.showwarning(message='up主id错误！')
    else:
        if v_list is None:
            tkinter.messagebox.showwarning(message='该up主未投稿！')
        else:
            count = len(v_list)
            money = user.get_self_info(ver)['money']
            ans = tk.messagebox.askyesno('提示', '视频总数：' + str(count)
                                         + '       硬币总数：' + str(money)
                                         + '\n' + '要继续吗？')
            if ans is False:
                return
            else:
                coin = 0
                filled = 0
                for i in range(count):
                    bvid = v_list[i]['bvid']
                    try:
                        video.add_coins(bvid=bvid, verify=ver, num=1)
                    except exceptions.BilibiliApiException as msg:
                        if msg.code == 34005:
                            filled += 1
                    else:
                        coin += 1

                    update_progress(i + 1, len(v_list))
                    window.update()

                tk.messagebox.showinfo(message='本次共投' + str(coin) + '个硬币'
                                       + '\n' + str(filled) + '之前投满')


def set_favorite(info_window):
    dic = video.get_favorite_list(bvid=var_bvid.get(), verify=ver)
    temp = lb.curselection()[0]
    if video.is_favoured(bvid=var_bvid.get(), verify=ver):
        tkinter.messagebox.showwarning(message='已经在本收藏夹中了！')
    else:
        video.operate_favorite(bvid=var_bvid.get(), verify=ver, add_media_ids=[dic['list'][temp]['id']])
        tkinter.messagebox.showinfo(message='收藏成功')
    display_fav_list(info_window)


def del_favorite(info_window):
    dic = video.get_favorite_list(bvid=var_bvid.get(), verify=ver)
    temp = lb.curselection()[0]
    video.operate_favorite(bvid=var_bvid.get(), verify=ver, del_media_ids=[dic['list'][temp]['id']])
    tkinter.messagebox.showinfo(message='删除成功！')
    display_fav_list(info_window)


def display_fav_list(info_window, x=100, y=570, state=0):#state 来判断用于哪个lb
    global lb
    dic = video.get_favorite_list(bvid=var_bvid.get(), verify=ver)
    lb = tk.Listbox(info_window)
    for i in range(dic['count']):
        if dic['list'][i]['fav_state'] == 1:
            if state == 0:
                lb.insert('end', str(i) + '.' + dic['list'][i]['title'] + '(已收藏)')
            else:
                lb.insert('end', str(i) + '.' + dic['list'][i]['title'])

        else:
            lb.insert('end', str(i) + '.' + dic['list'][i]['title'])
    lb.place(x=x, y=y)


def set_fav_list(info_window):
    display_fav_list(info_window)
    set_fav = tk.Button(info_window, text='收藏在该收藏夹中', command=lambda: set_favorite(info_window))
    set_fav.place(x=300, y=600)
    del_fav = tk.Button(info_window, text='取消该文件夹中的收藏', command=lambda: del_favorite(info_window))
    del_fav.place(x=300, y=650)


def set_fav_list_all(info_window):
    display_fav_list(info_window, 100, 400, 1)
    set_fav = tk.Button(info_window, text='全部收藏在该收藏夹中', command=set_favorite_all)
    set_fav.place(x=300, y=500)


def set_favorite_all():
    dic = video.get_favorite_list(bvid=var_bvid.get(), verify=ver)
    temp = lb.curselection()[0]
    try:
        v_list = user.get_videos(uid=var_upid.get(), verify=ver)
    except exceptions.BilibiliException as msg:
        if msg.code == -400 or -10:
            tkinter.messagebox.showwarning(message='up主id错误！')
    else:
        if v_list is None:
            tkinter.messagebox.showwarning(message='该up主未投稿！')
        else:
            is_favared = 0
            for i in range(len(v_list)):
                bvid = v_list[i]['bvid']
                if video.is_favoured(bvid=bvid, verify=ver):
                    is_favared += 1
                else:
                    video.operate_favorite(bvid=bvid, verify=ver,
                                           add_media_ids=[dic['list'][temp]['id']])

                update_progress(i + 1, len(v_list))
                window.update()

            sleep(0.3)
            tkinter.messagebox.showinfo(message='收藏成功，' + str(is_favared) +
                                        '视频之前已收藏过。')

#  ---------------------------------main window--------------------------------------------------------#


def main_window():
    bili_img_1 = Image.open('1.png')
    render_1 = ImageTk.PhotoImage(bili_img_1)
    img_1 = tk.Label(window, image=render_1)
    img_1.place(x=600, y=0)

    bili_img_2 = Image.open('2.png')
    bili_img_2_rsz = bili_img_2.resize((500, 80))
    render_2 = ImageTk.PhotoImage(bili_img_2_rsz)
    img_2 = tk.Label(window, image=render_2)
    img_2.place(x=0, y=0)

    label = tk.Label(window, text='sess: ', font=("微软雅黑", 14),  height=1)
    label.place(x=40, y=95)
    label = tk.Label(window, text='crsf: ', font=("微软雅黑", 14),  height=1)
    label.place(x=40, y=135)

    sep1 = tk.Canvas(window, width=600, height=10)
    sep1.create_line(0, 15, 600, 15, width=10, fill='#1f1e33')
    sep1.place(x=0, y=175)

    label = tk.Label(window, text='bv/url: ', font=("微软雅黑", 14),  height=1)
    label.place(x=25, y=200)

    entry_sess = tk.Entry(window, textvariable=var_sess, font=('Arial', 14))
    entry_sess.place(x=100, y=100)
    entry_csrf = tk.Entry(window, textvariable=var_csrf, font=('Arial', 14))
    entry_csrf.place(x=100, y=150)
    entry_bvid = tk.Entry(window, textvariable=var_bvid, font=('Arial', 14))
    entry_bvid.place(x=100, y=200)

    button_c_s = tk.Button(window, text="获取cookie", command=get_sc_button)
    button_c_s.place(x=350, y=100)
    button_c_s = tk.Button(window, text="重新登陆", command=get_bili_cookies)
    button_c_s.place(x=450, y=100)
    button_c_s = tk.Button(window, text="确认", command=get_s_c)
    button_c_s.place(x=350, y=150)
    button_c_s = tk.Button(window, text="确认视频信息", command=video_confirm)
    button_c_s.place(x=350, y=200)

    sep2 = tk.Canvas(window, width=600, height=10)
    sep2.create_line(0, 15, 600, 15, width=10, fill='#1f1e33')
    sep2.place(x=0, y=235)

    label_sanlian_all = tk.Label(window, text='全部三连: ', font=("微软雅黑", 14, "bold"),  height=1)
    label_sanlian_all.place(x=160, y=255)

    label = tk.Label(window, text='upid: ', font=("微软雅黑", 14),  height=1)
    label.place(x=40, y=300)
    entry_upid = tk.Entry(window, textvariable=var_upid, font=('Arial', 14))
    entry_upid.place(x=100, y=300)

    button_c_s = tk.Button(window, text="一键点赞", command=lambda: set_like_all(var_upid.get()))
    button_c_s.place(x=350, y=300)
    button_c_s = tk.Button(window, text="一键投币", command=lambda: add_coin_all(var_upid.get()))
    button_c_s.place(x=350, y=335)
    button_c_s = tk.Button(window, text="一键收藏", command=lambda: set_fav_list_all(window))
    button_c_s.place(x=350, y=370)
    button_c_s = tk.Button(window, text="详细信息...", command=up_confirm)
    button_c_s.place(x=100, y=340)

    sep3 = tk.Canvas(window, width=600, height=10)
    sep3.create_line(0, 15, 600, 15, width=10, fill='#1f1e33')
    sep3.place(x=0, y=400)

    progress = tk.Label(window, textvariable=var_progress, font=("微软雅黑", 14, "bold"),  height=1)
    progress.place(x=20, y=650)

    window.mainloop()

# ------------------------------------------------------------------------------- #


if __name__ == '__main__':
    main_window()
