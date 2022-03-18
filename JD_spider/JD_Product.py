'''
运行文件输入商品关键字
起始、结束页数：表示从哪个页数开始爬取、到哪个页数结束
'''
import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from time import sleep
from lxml import html, etree
import csv
import urllib3

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
}


class JD_Product_Spider():

    def __init__(self, keyword, first_category_id, second_category_id, end_page, second_category_name):
        self.start_page = 0  # 开始页码
        self.end_page = end_page  # 结束页码
        self.keyword = keyword  # 商品搜索关键词
        self.first_category_id = first_category_id  # 所属一级类目ID
        self.second_category_id = second_category_id  # 所属二级类目ID
        self.second_category_name = second_category_name  # 二级类目名称
        self.allIDs = []  # 用于去重复
        option = ChromeOptions()
        option.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})  # 禁止图片加载，加快速度
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')  # 设置无头浏览器
        option.add_argument(
            'user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"')
        self.bro = webdriver.Chrome(options=option)
        self.bro.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })  # 可能失效

    def Parser_Profuct_Data(self):
        html = etree.HTML(self.bro.page_source)
        li_list = html.xpath('//ul[@class="gl-warp clearfix"]/li')
        for li in li_list:
            dic = {}
            try:
                data_lazy_img = li.xpath('./div/div[@class="p-img"]/a/img/@data-lazy-img')
                img_src = li.xpath('./div/div[@class="p-img"]/a/img/@src')
                if data_lazy_img[0] == 'done' and len(img_src) > 0:
                    img_path = img_src[0]
                else:
                    img_path = data_lazy_img[0]
                dic["img"] = img_path.split('//')[1]  # 图片路径
            except:
                dic["img"] = ""
                print("img error")
            try:
                name = li.xpath('./div/div[@class="p-name p-name-type-2"]/a/em//text()')  # 商品名称
                spuName = ""
                for str in name:
                    if str == '京东超市':
                        continue
                    str = str.replace('\n', '').replace('\t', '')
                    spuName = spuName + str
                dic["title"] = spuName
            except:
                dic["title"] = ""
                print("title error")
            try:
                dic["commit"] = li.xpath('./div/div[@class="p-commit"]/strong/a/text()')[0]  # 销量
            except:
                dic["commit"] = ""
                print("commit error")
            # try:
            #     dic["shop"] = li.xpath('./div/div[@class="p-shop"]/span/a/text()')[0]  # 店铺名称
            # except:
            #     print("shopName error")
            #     print(li.xpath('./div/div[@class="p-shop"]/span/a/text()')[0])
            #     dic["shop"] = ""
            try:
                dic["price"] = li.xpath('./div/div[@class="p-price"]/strong/i/text()')[0]  # 价格
            except:
                dic["price"] = ""
                print("price error")
            try:
                dic["details"] = "https:" + li.xpath('./div/div[@class="p-name p-name-type-2"]/a/@href')[0]  # 商品平台地址
            except:
                dic["details"] = ""
                print("details error")
            try:
                dic["productId"] = li.xpath('./@data-sku')[0]  # 商品平台唯一ID
            except:
                dic["productId"] = ""
                print("productId error")
            dic["first_category_id"] = self.first_category_id  # 一级类目ID
            dic["second_category_id"] = self.second_category_id  # 二级类目ID
            dic["second_category_name"] = self.second_category_name  # 二级类目名称
            dic["media_type"] = "JD"  # 媒体ID【途径】
            if dic["productId"] in self.allIDs:
                continue
            else:
                self.allIDs.append(dic["productId"])
                with open("./spider_product_msg/" + self.keyword + ".csv", "a+", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, dic.keys())
                    writer.writerow(dic)
                    f.close()

    def Get_Product_Data(self):
        self.bro.maximize_window()  # 最大化浏览器
        url = "https://search.jd.com/Search?keyword=%s" % self.keyword
        self.bro.get(url)

        # Debug开启
        # urllib3.disable_warnings()
        # r = requests.get(url, verify=False)
        # print(r.text)
        # if r.text == "<script>window.location.href='https://passport.jd.com/uc/login'</script>":
        #     self.Get_Product_Data()

        # page_text = requests.get(url=url, headers=headers).text
        # print(page_text)

        self.bro.execute_script('window.scrollTo(0, document.body.scrollHeight)')  # 向下滑动一屏
        sleep(1)
        page = self.bro.find_element_by_xpath('//span[@class="p-skip"]/em/b').text
        # page = self.bro.find_element_by_xpath('/div').text
        endPage = int(self.end_page)
        print("%s检索到共%s页数据" % (self.keyword, page))
        if int(page) < endPage:
            endPage = int(page)
            print("小于截止页面，采用新endPage:", endPage)
        for i in range(int(self.start_page), int(endPage) + 1):
            sleep(5)
            print("-" * 30 + "已获取第%s页数据" % (i) + "-" * 30)
            url = "https://search.jd.com/Search?keyword=%s&page=%d" % (self.keyword, i * 2 - 1)
            self.bro.get(url)
            self.Parser_Profuct_Data()
        self.bro.quit()


if __name__ == "__main__":
    Spider = JD_Product_Spider("防身棍", 63, 1631, 30, "防身棍")
    Spider.Get_Product_Data()
    Spider = JD_Product_Spider("养生茶", 49, 1501, 30, "养生茶")
    Spider.Get_Product_Data()
    Spider = JD_Product_Spider("小提琴", 66, 1649, 30, "小提琴")
    Spider.Get_Product_Data()
