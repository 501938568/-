import tkinter as tk
ver = None
lb = None

root = tk.Tk()
var_sess = tk.StringVar()
var_sess.set("")
var_csrf = tk.StringVar()
var_csrf.set("")

var_bvid = tk.StringVar()
var_bvid.set("BV1uv411q7Mv")

var_upid = tk.StringVar()
var_upid.set("384521381")

var_progress = tk.StringVar()

var_up_cover_path = tk.StringVar()
var_up_video_path = tk.StringVar()

# 投稿默认信息
data = {
    "copyright": 1,
    "source": "",
    "cover": '',
    "desc": "",
    "desc_format_id": 0,
    "dynamic": "",
    "interactive": 0,
    "no_reprint": 1,
    "subtitles":  {
        "lan": "",
        "open": 0
    },
    "tag": "",
    "tid": 22,
    "title": "",
    "videos": [
        {
            "desc": "",
            "filename": '',
            "title": "P1"
        }
    ]
}
