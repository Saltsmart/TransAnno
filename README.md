# TransAnno
Translate Chinese Annotations in Python to English. 快速翻译Package中所有**py**的中文注释到英文，方便发布为公共包。修改`trans.py`中的`"from"`和`"to"`，可以修改语言设置。

目前采用有道翻译API，Google翻译需安装googletrans包，参见[Link](https://py-googletrans.readthedocs.io/en/latest/#googletrans.models.Translated)。

使用：
```python
a = AnnoTranslator()
a.anno_translate(rsc : str, bak : str)  # package所在的文件夹, 备份文件夹
```
会将rsc中所有py文件中的中文注释('''*块注释*'''，"""*块注释*"""和#*行注释*)原位转为英文并加上"TRANS: "标记，便于进一步修改
