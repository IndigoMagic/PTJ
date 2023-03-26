# PTJ
postman脚本（json）转jmeter脚本（jmx），支持Mac和Windows图形界面操作，已经打包成可执行文件。

目前仅支持GET和POST请求，如需支持其他请求，可修改代码的转换逻辑和xml模板。

使用方法：

1.postman导出postman_collection.json文件和postman_environment.json文件。

2.把上述两个json文件和convert_postman_to_jmeter.py（或同名可执行文件）、template.xml放在同一个文件夹下。

3.运行convert_postman_to_jmeter.py或者同名可执行文件。

4.点击转换按钮。

5.点击打开所在文件夹，即可看到转换完成的jmeter脚本。

注意：

1.postman导出文件请选择v2.1。

2.请注意软件版本提示。

3.postman_environment.json文件可以不选，postman_collection.json文件一定要选。

4.使用前请删除demo文件以免影响使用。

5.postman_environment.json文件和postman_collection.json文件可以使用默认路径下的，也可以自己选择。

![image](https://user-images.githubusercontent.com/37242294/227765921-a66bad6e-08b1-49c1-8ead-b4a3a399de8c.png)
![image](https://user-images.githubusercontent.com/37242294/227765894-86eab7eb-7b6b-4edc-aaf3-8646c072e685.png)
![image](https://user-images.githubusercontent.com/37242294/227765906-cb7caaff-c412-4165-b970-77441653af42.png)
<img width="392" alt="image" src="https://user-images.githubusercontent.com/37242294/227765916-988984df-385e-42f9-83f0-b05f66175d4f.png">
