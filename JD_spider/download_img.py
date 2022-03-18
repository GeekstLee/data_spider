import requests


def download_img(img_url, img_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.json.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }
    r = requests.get(img_url, headers=headers, stream=True)
    # print(r.status_code) # 返回状态码
    if r.status_code == 200:
        # 截取图片文件名
        # img_name = img_url.split('/').pop()
        with open("./spider_img/" + img_name + ".jpg", 'wb') as f:
            f.write(r.content)
        return True
    with open("error_img_id", 'a') as f:
        f.write(img_name + "\n")


if __name__ == '__main__':
    # 下载要的图片
    img_url = "xxx"
    ret = download_img(img_url, "test")
    if not ret:
        print("下载失败")
    print("下载成功")
