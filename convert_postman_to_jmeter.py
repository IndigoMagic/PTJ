import sys
import jinja2
import json
import re
import os
import glob
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


# 获取可执行文件或脚本的绝对路径
if getattr(sys, 'frozen', False):
    exe_path = os.path.dirname(sys.executable)
else:
    exe_path = os.path.dirname(os.path.abspath(__file__))

# 更改工作目录为可执行文件所在目录
os.chdir(exe_path)


def get_export_path():
    """
    返回输出jmx文件路径
    :return:
    output_jmx_file_path: 输出的jmx文件接口
    """
    # current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录的绝对路径
    current_path = exe_path  # 获取当前文件所在目录的绝对路径

    output_path = os.path.join(current_path, "output")  # 拼接output文件夹的路径
    output_jmx_file_path = ""
    if not os.path.exists(output_path):  # 判断output文件夹是否存在
        os.mkdir(output_path)  # 如果不存在，则创建output文件夹
        print("output文件夹创建成功！")
        print(output_path)
        output_jmx_file_path = output_path + "/" + \
                               glob.glob(
                                   '*postman_collection.json')[0].split(".postman_collection.json")[0] + ".jmx"
    else:
        print("output文件夹已存在。")
        output_jmx_file_path = output_path + "/" + \
                               glob.glob(
                                   '*postman_collection.json')[0].split(".postman_collection.json")[0] + ".jmx"
    return output_jmx_file_path


def read_json(json_path):
    """
    读取json文件
    :param json_path: json文件路径
    :return: json文件数据
    """
    with open(json_path, "r+", encoding='utf-8') as f:
        data_from_file = json.load(f)
    return data_from_file


def recursion_traverse_json_req_list(data_from_file, request_list):
    """
    递归遍历json数据里的全部请求并写入一个列表
    :param data_from_file: 解析后的json数据
    :param request_list: 请求列表，[]
    :return:
    """
    for dic in data_from_file["item"]:
        if "item" in dic:
            print("文件夹名称：：" + dic["name"])
            recursion_traverse_json_req_list(dic, request_list)
        else:
            print(dic)
            domain = ".".join(dic["request"]["url"]["host"])
            req_path = "/" + "/".join(dic["request"]["url"]["path"])
            req_body = ""
            if dic["request"]["method"] == "POST":
                for key in dic["request"].keys():
                    if key == "body":
                        if dic["request"]["body"]["mode"] == "raw":
                            req_body = dic["request"]["body"]["raw"]
            to_j_dic = {
                "req_name": dic["name"],
                "req_body": req_body,
                "domain": domain,
                "req_path": req_path,
                "method": dic["request"]["method"],
                "query_list": dic["request"]["url"]["query"]
            }
            request_list.append(to_j_dic)


def write_to_template(json_api_data, jmx_template_path, out_path):
    """
    jinja2渲染模板,把json接口数据写入模板，生成jmx文件
    :param json_api_data: 从postman解析出的接口数据
    :param jmx_template_path: jmx模板路径
    :param out_path: jmx文件输出路径
    :return:
    """
    # 读取模板
    with open(jmx_template_path, encoding='utf-8') as f:
        tpl = f.read()
    # jinja2渲染模板,把json接口数据写入模板，生成jmx
    jmx = jinja2.Template(tpl).render(json_api_data)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(jmx)


def read_ev_json(data_from_file):
    """
    读取环境变量，输出环境变量参数列表和环境变量名
    :param data_from_file:从json文件读取出的环境变量json原始数据
    :return:
    arg_parent_dict_list: 用于写入jmx模板的环境变量参数列表
    environment_name: 用于写入jmx模板的环境变量名
    """
    arg_parent_dict_list = []
    for dic in data_from_file["values"]:
        arg_parent_dict_list.append(
            {dic["key"]: [dic["key"], dic["value"], "描述"]})
    environment_name = data_from_file["name"]
    return arg_parent_dict_list, environment_name


def replace_placeholder(data):
    """
    把从postman文件读取出的json数据的{{}}替换为${}
    :param data: 从postman文件读取出的原始json数据
    :return:replaced_json: 替换后的json数据
    """
    json_str = json.dumps(data, ensure_ascii=False)
    strinfo = re.compile('{{(.+?)}}')
    for i in strinfo.findall(json_str):
        json_str = strinfo.sub('${%s}' % i, json_str, 1)
    replaced_json = json.loads(json_str)
    return replaced_json


def convert_postman_to_jmeter(postman_colection_path, postman_ev_colection_path):
    output_jmx_file_path = get_export_path()
    # 获取到postman文件路径和输出文件路径
    json_data = read_json(json_path=postman_colection_path)
    # 从postman_collection.json 接口文件读取出json原始数据
    replaced_json = replace_placeholder(json_data)
    # 把json原始数据中的{{}}替换成${}
    rlist = []
    recursion_traverse_json_req_list(replaced_json, rlist)
    # 把替换后的json接口数据解析并把请求写入一个空列表
    print(rlist)
    if postman_ev_colection_path != "":
        ev_json_data = read_json(json_path=postman_ev_colection_path)
        # 读取环境变量参数
        arg_parent_dict_list, environment_name = read_ev_json(
            data_from_file=ev_json_data)
        # 输出环境变量参数列表和环境变量名称
    else:
        arg_parent_dict_list = []
        environment_name = "环境变量demo"
    to_template_dict = {
        "testname": json_data["info"]["name"],
        "xcz_name": json_data["info"]["name"] + "线程组",
        "default_domain": "",
        "arg_parent_dict_list": arg_parent_dict_list,
        "environment_name": environment_name,
        "request_dict_list": rlist
    }
    # 拼装即将写入jmx模板的字典
    template_path = None
    if glob.glob("template.xml"):
        template_path = './template.xml'
    else:
        print("template.xml不存在")
        messagebox.showerror("错误", "template.xml文件不存在")
    write_to_template(to_template_dict, template_path, output_jmx_file_path)
    # 把拼装好的接口字典写入jmx模板，生成jmx脚本
    print("OK")


class App:
    def __init__(self, master):
        self.master = master
        self.file1_path = ''
        self.file2_path = ''

        # 创建左侧两个文件选择组件
        self.file1_label = tk.Label(master, text="postman_collection：")
        self.file1_label.grid(row=0, column=0, padx=10, pady=10)

        self.file1_entry = tk.Entry(master, width=50)
        self.file1_entry.grid(row=0, column=1, padx=10, pady=10)

        self.file1_button = tk.Button(master, text="选择文件", command=self.choose_file1)
        self.file1_button.grid(row=0, column=2, padx=10, pady=10)

        self.file2_label = tk.Label(master, text="postman_environment：")
        self.file2_label.grid(row=1, column=0, padx=10, pady=10)

        self.file2_entry = tk.Entry(master, width=50)
        self.file2_entry.grid(row=1, column=1, padx=10, pady=10)

        self.file2_button = tk.Button(master, text="选择文件", command=self.choose_file2)
        self.file2_button.grid(row=1, column=2, padx=10, pady=10)

        # 设置备注标签
        self.remark_label = tk.Label(master, text="注:postman至少支持:8.4.0, jmeter至少支持:5.4.1,postman导出json2文件的时候请选择v2.1")
        self.remark_label.grid(row=5, column=1, pady=10, sticky=tk.S + tk.E + tk.W)


        # 设置默认文件路径
        if glob.glob("*postman_collection.json"):
            self.colection_path = os.path.join(
                exe_path, glob.glob('*postman_collection.json')[0])
        else:
            print("postman_collection文件不存在")
            messagebox.showerror("错误", "postman_collection文件不存在")
        if glob.glob("*postman_environment.json"):
            self.ev_colection_path = os.path.join(
                exe_path, glob.glob('*postman_environment.json')[0])
        else:
            print("postman_environment文件不存在")
            self.ev_colection_path = ""
            # messagebox.showerror("错误", "postman_environment文件不存在")
        self.file1_entry.insert(0, self.colection_path)
        self.file2_entry.insert(0, self.ev_colection_path)

        # 创建转换按钮
        self.convert_button = tk.Button(master, text="转换", command=self.convert)
        self.convert_button.grid(row=2, column=1, padx=10, pady=10)

    def choose_file1(self):
        # 打开文件选择对话框，选择文件1
        self.file1_path = filedialog.askopenfilename()
        if self.file1_path:
            self.file1_entry.delete(0, tk.END)
            self.file1_entry.insert(0, self.file1_path)

    def choose_file2(self):
        # 打开文件选择对话框，选择文件2
        self.file2_path = filedialog.askopenfilename()
        if self.file2_path:
            self.file2_entry.delete(0, tk.END)
            self.file2_entry.insert(0, self.file2_path)

    def convert(self):
        file1 = self.file1_path if self.file1_path else self.colection_path
        file2 = self.file2_path if self.file2_path else self.ev_colection_path
        convert_postman_to_jmeter(file1, file2)
        # 创建“打开所在文件夹”按钮
        self.open_folder_button = tk.Button(
            self.master, text="打开所在文件夹", command=self.open_folder)
        self.open_folder_button.grid(row=3, column=1, padx=10, pady=10)

    def open_folder(self):
        # 打开output文件夹所在目录
        output_dir = 'output'
        if os.path.exists(output_dir):
            # 根据操作系统类型打开文件夹
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS
                os.system(f"open {os.path.abspath(output_dir)}")



if __name__ == '__main__':
    root = tk.Tk()
    root.title("postman转jmeter")
    # 创建应用程序
    app = App(root)
    # 进入事件循环
    root.mainloop()
