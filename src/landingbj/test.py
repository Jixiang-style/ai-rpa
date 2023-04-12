# import tkinter as tk

# 方法三（参考）
# import tkinter as tk
#
# def process_input(*args):
#     input_text = input_box.get()
#     processed_text = input_text.upper()
#     result_box.configure(state='normal')
#     result_box.delete('1.0', tk.END)
#     result_box.insert(tk.END, processed_text)
#     result_box.configure(state='disabled')
#
# root = tk.Tk()
# root.geometry("400x400")
#
# input_text = tk.StringVar()
# input_box_label = tk.Label(root, text="Input Text:")
# input_box_label.pack(pady=5)
# input_box = tk.Entry(root, textvariable=input_text)
# input_text.trace("w", process_input)
# input_box.pack(pady=5)
#
# result_box_label = tk.Label(root, text="Processed Text:")
# result_box_label.pack(pady=5)
# result_box = tk.Text(root, height=5, state='disabled')
# result_box.pack(pady=5)

# root.mainloop()

# 方法四：
# import tkinter as tk
#
# def process_input():
#     input_text = input_box.get()
#     processed_text = input_text.upper()
#     result_box.configure(state='normal')
#     result_box.delete('1.0', tk.END)
#     result_box.insert(tk.END, processed_text)
#     result_box.configure(state='disabled')
#
# root = tk.Tk()
# # root.geometry("400x200")
#
# input_box_label = tk.Label(root, text="Input Text:")
# input_box_label.pack(pady=5)
# input_box = tk.Entry(root)
# input_box.pack(pady=5)
#
# submit_button = tk.Button(root, text="Submit", command=process_input)
# submit_button.pack(pady=5)
#
# result_box_label = tk.Label(root, text="Processed Text:")
# result_box_label.pack(pady=5)
# result_box = tk.Text(root, height=5, state='disabled')
# result_box.pack(pady=5)
#
# root.mainloop()

# 方法五
import tkinter as tk

# 创建窗口对象
window = tk.Tk()
window.title("文本处理器")

# 创建文本框
input_text = tk.Entry(window)
input_text.pack()

# 创建“处理”按钮
def process_text():
    text = input_text.get() # 获取输入框中的文本
    processed_text = text.upper() # 将文本转换为大写形式
    result_text.insert(tk.END, processed_text + "\n") # 在文本框中显示处理后的结果

process_button = tk.Button(window, text="处理", command=process_text)
process_button.pack()

# 创建结果文本框
result_label = tk.Label(window, text="处理结果：")
result_label.pack()
result_text = tk.Text(window)
result_text.pack()

# 运行窗口循环
window.mainloop()

'''
备注:

我们创建了两个StringVar对象，一个用于输入框中的文本，另一个用于展示框中的文本。
对应的StringVar对象都是通过textvariable属性进行绑定的，这意味着如果其文本值发生更改，那么所有绑定到这个StringVar变量的部件也会相应地刷新。
我们使用trace方法监控StringVar对象中文本变量的变化。trace方法将函数process_input绑定到textvariable的变化事件上，因此每当输入框的内容更改时，它都会自动调用process_input函数进行处理。
这里的process_input函数会获取输入框中的文本，将其转换为大写，然后使用Text组件的insert方法将处理后的文本插入展示框中，最后将展示框置为只读状态。
'''

"""
tkinter的具体用法：

详细讲解python中tkinter库中Frame, TOP, Label, NW, GROOVE, Button, SE, LEFT, END, FLAT, Text, INSERT的具体用法

word count: 26, token estimate: 55

助手
1.Frame：
Frame是Tkinter中的一个容器，它可用于将其他widget组织起来。Frame是一个空的矩形，可以包含其他小组件，如按钮，标签等。以下是使用Frame创建一个新窗口的示例：

复制
import tkinter as tk
root = tk.Tk()
root.title("Frame Example")

# 创建一个父Frame，并将其添加到root窗口
frame1 = tk.Frame(root, bd=5, relief="groove")
frame1.pack(side="top")

# 在frame1中创建一个子Frame
frame2 = tk.Frame(frame1, bd=5, relief="groove")
frame2.pack(side="left")
这里创建了两个Frame组件。Frameframe1作为一个父Frame，从root窗口的顶部开始组织布局，包含子Frameframe2。bd和relief参数用于指定边框的宽度和类型。

2.TOP 和 LEFT：
在Tkinter中，TOP和LEFT是pack()函数的参数，用于指定组件的位置。TOP将组件放在其父组件的顶部，LEFT将组件放置在其父组件的左侧。例如，在Frame中，可以使用以下代码将子组件布局在两个方向上：

复制
frame1.pack(side="top")
frame2.pack(side="left")

3.Label:
Label是Tkinter中的一个组件，用于在窗口上显示文本或图像。可以使用以下代码创建一个Label：

复制
label = tk.Label(root, text="Python Tkinter example")
这里创建了一个Label，并将其添加到了root窗口中。

4.NW 和 SE:
在Tkinter中,NW和SE用于指定anchor参数的值。anchor指定了组件在其所属frame中的位置。NW指定组件的锚点位于左上角，SE指定组件的锚点位于右下角。例如，可以使用以下代码将Label锚定到其父Frame的左上角：

复制
label.pack(anchor='nw')

5.GROOVE 和 FLAT：
relief参数用于在Tkinter中指定组件的边框类型。GROOVE和FLAT是其中两种类型。GROOVE是用于创建带有"凹槽"效果的边框，而FLAT则创建一个没有边框的组件。可以使用以下代码将标签的边框设置为GROOVE：

复制
label = tk.Label(root, text="Label with groove border", bd=5, relief="groove")

6.Button：
Button Widget是Tkinter中的一个常用组件，用于在窗口中添加按钮。可以使用以下代码创建一个Button：

复制
button = tk.Button(root, text="Click Me", command=callback_function)
这里，text参数指定按钮上显示的文本，而 command参数指定要执行的回调函数。当用户单击按钮时，就会执行该回调函数。

7.END和INSERT：
在Tkinter中，END和INSERT可用于在Text Widget中插入文本。INSERT指定插入点在当前光标位置之前插入，END指定插入点在文本的末尾。示例如下：

复制
text_widget = tk.Text(root)
text_widget.insert(tk.END, "This is some text.")
这里创建了一个Text Widget，并在其中插入了文本。

这些是Tkinter中一些常见的组件和功能，通过将它们组合在一起，可以构建出复杂的GUI应用程序。希望这些解释能够帮助您更好地了解Tkinter。

"""