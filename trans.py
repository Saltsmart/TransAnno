from urllib import parse, request
from json import loads
import re
import os
from shutil import copy
from googletrans import Translator


class WrappedTrans:
    def __init__(self, use="youdao"):
        self.url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
        self.header_keys = ["User-Agent"]
        self.header_vals = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"]
        self.trans = None
        if use == "Google":
            try:
                # Google翻译API，详见https://py-googletrans.readthedocs.io/en/latest/#googletrans.models.Translated
                self.trans = Translator()
            except:
                self.trans = None

    def _create_data(self, content):
        data = {
            "i": content,  # 翻译内容
            "from": "zh-CHS",  # 原始语言
            "to": "en",  # 目标语言
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": "1517200217152",
            "sign": "fc8a26607798294e102f7b4e60cc2686",
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_CLICKBUTTION",
            "typoResult": "true"
        }
        return data

    def _add_headers(self, req):
        for key, val in zip(self.header_keys, self.header_vals):
            req.add_header(key, val)
        return req

    def _youdao_trans(self, content):
        data = self._create_data(content)
        data = parse.urlencode(data).encode("utf-8")
        req = request.Request(self.url, data)
        req = self._add_headers(req)
        response = request.urlopen(req)
        html = response.read().decode("utf-8")

        target = loads(html)
        ## target的正常结构：{"translateResult":[[{"tgt":"translation","src":"翻译"}],[{"tgt":"There is no","src":"没有"}]],"errorCode":0,"type":"zh-CHS2en"}
        ## target的异常结构中只有errorCode
        resString = "TRANS: "
        if "translateResult" not in target:
            print("Translating Failed. Return:" + target)
        else:
            if len(target["translateResult"]) == 0:
                pass
            elif len(target["translateResult"]) == 1:
                resString += target["translateResult"][0][0]["tgt"]
            else:
                for i in target["translateResult"]:  # 打开第一层括号，i = [{"tgt":"translation","src":"翻译"}]
                    for j in i:  # 打开第二层括号，j = {"tgt":"translation","src":"翻译"}
                        if(j["tgt"] != None):
                            resString += j["tgt"] + "\n"
        return resString

    def translate(self, content):
        if isinstance(self.trans, Translator):
            self.trans(content, src="en", dst="zh-cn")
            return self.trans.text
        else:
            return self._youdao_trans(content)


# ### TEST WrappedTrans ####
# a = WrappedTrans()
# print(a.translate("你好。\n你坏！"))
# print(a.translate("aaa。\n你坏！"))


class AnnoTranslator:
    def __init__(self):
        self.translator = WrappedTrans()

    def _get_py(self, dir):
        py_file_list = []
        for detail in os.listdir(dir):  # 遍历整个文件夹
            path = os.path.join(dir, detail)
            if os.path.isfile(path) and os.path.splitext(path)[1] == ".py":  # 判断是否为py文件，排除文件夹
                py_file_list.append(path)
            elif os.path.isdir(path):
                newdir = path
                py_file_list.extend(self._get_py(newdir))
        return py_file_list

    def _is_Chinese(self, word):
        for ch in word:
            if "\u4e00" <= ch <= "\u9fff":
                return True
        return False

    def anno_translate(self, src, bak):
        py_file_list = self._get_py(src)
        for i, py_file in enumerate(py_file_list):
            with open(py_file, "r", encoding="utf-8") as file:
                file_text = file.read()

                anno_list = []
                block_anno_1 = re.findall(r'(?<=""")[\s\S]*(?=""")', file_text, re.S)
                block_anno_2 = re.findall(r"(?<=''')[\s\S]*(?=''')", file_text, re.S)
                line_anno = re.findall(r"(?<=#).*(?=)", file_text)

                if len(block_anno_1) > 0:
                    anno_list.extend(filter(self._is_Chinese, block_anno_1))
                if len(block_anno_2) > 0:
                    anno_list.extend(filter(self._is_Chinese, block_anno_2))
                if len(line_anno) > 0:
                    anno_list.extend(filter(self._is_Chinese, line_anno))
                if len(anno_list) == 0:
                    continue  # 没有中文，无需翻译，跳到下一个文件

            new_file_read = file_text
            if not os.path.exists(bak + "/" + str(i) + "/"):
                os.makedirs(bak + "/" + str(i) + "/")
            copy(py_file, bak + "/" + str(i) + "/")  # 备份修改的文件
            for anno_to_trans in anno_list:
                new_file_read = new_file_read.replace(anno_to_trans, self.translator.translate(anno_to_trans))

            with open(py_file, "w", encoding="utf-8") as file:  # 全部改好后再写入原文件
                file.write(new_file_read)


### TEST AnnoTranslator ###
# a = AnnoTranslator()
# # print(a._get_py("dddd"))
# # print(a._is_Chinese("chhh"))
# # print(a._is_Chinese("chh中"))
# # print(a._is_Chinese("中hhh"))
# a.anno_translate("dddd", "dddd_backup")
