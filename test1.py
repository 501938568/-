from bilibili_api import video, Verify, exceptions, user

var_sess = "479cde40%2C1616386900%2C50860*91"
var_csrf = "87977a8b062f49e4ca0fe57c1fb0318c"

ver = Verify(sessdata=var_sess, csrf=var_csrf)
print(ver.check())