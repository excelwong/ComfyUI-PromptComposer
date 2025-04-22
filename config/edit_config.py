"""
prompt_config_editor.py - 紧凑布局版本
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox

class CompactConfigEditor:
    def __init__(self, master):
        self.master = master
        self.config_path = "prompt_config.txt"
        self.group_path = "prompt_group.txt"
        
        # 初始化数据结构
        self.config_data = {}
        self.group_data = {}
        self.value_map = {}
        self.widgets = {}
        
        self.load_data()
        self.create_ui()
        self.adjust_window_size()  # 新增窗口尺寸调整
        
    def load_data(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            with open(self.group_path, 'r', encoding='utf-8') as f:
                self.group_data = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"文件加载失败: {str(e)}")
            exit()

    def create_ui(self):
        """创建紧凑布局界面"""
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动区域容器
        canvas = tk.Canvas(main_frame, width=600)  # 限制画布宽度
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)
        
        # 滚动配置
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建配置项
        row = 0
        for key in self.config_data:
            self.create_compact_row(key, row)
            row += 1
            
        # 操作按钮
        btn_frame = ttk.Frame(self.master)
        ttk.Button(btn_frame, text="重置", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存", command=self.save_config).pack(side=tk.LEFT)
        
        # 布局管理
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        btn_frame.pack(side=tk.BOTTOM, pady=5)
        
        # 列宽设置
        self.scroll_frame.grid_columnconfigure(0, minsize=120)  # 固定标签列宽
        self.scroll_frame.grid_columnconfigure(1, weight=1, minsize=300)  # 下拉框最小宽度

    def create_compact_row(self, key, row):
        """创建紧凑布局的行"""
        # 标签（固定宽度）
        label = ttk.Label(self.scroll_frame, text=key, anchor=tk.W)
        label.grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
        
        # 下拉框（动态宽度）
        current_value = self.config_data[key]
        options = self.group_data.get(key, [])
        
        display_options = ["-1: 随机"]
        value_options = [-1]
        for idx, opt in enumerate(options):
            display_options.append(f"{idx}: {opt[:40]}")  # 截断长文本
            value_options.append(idx)
        
        self.value_map[key] = value_options
        
        combobox = ttk.Combobox(
            self.scroll_frame,
            values=display_options,
            state="readonly",
            width=35  # 减小控件宽度
        )
        
        if current_value == -1:
            combobox.set(display_options[0])
        elif 0 <= current_value < len(options):
            combobox.set(display_options[current_value + 1])
        else:
            combobox.set(display_options[0])
            
        combobox.grid(row=row, column=1, padx=5, pady=2, sticky=tk.EW)
        self.widgets[key] = combobox

    def adjust_window_size(self):
        """自动调整窗口尺寸"""
        self.master.update_idletasks()  # 更新布局计算
        
        # 计算所需宽度
        label_width = 120
        combobox_width = 300
        scrollbar_width = 20
        total_width = label_width + combobox_width + scrollbar_width + 40

        # 设置窗口尺寸
        self.master.geometry(f"{total_width}x786")  # 固定宽度和高度
        self.master.resizable(False, False)  # 禁止垂直调整，禁止水平调整

    def reset_config(self):
        """重置配置"""
        self.load_data()
        for key in self.widgets:
            cb = self.widgets[key]
            current_value = self.config_data[key]
            options = self.group_data.get(key, [])
            
            display_options = ["-1: 随机"]
            for idx, opt in enumerate(options):
                display_options.append(f"{idx}: {opt[:40]}")
            
            cb['values'] = display_options
            if current_value == -1:
                cb.set(display_options[0])
            elif 0 <= current_value < len(options):
                cb.set(display_options[current_value + 1])
            else:
                cb.set(display_options[0])

    def save_config(self):
        """保存配置"""
        new_config = {}
        for key, cb in self.widgets.items():
            selected_index = cb.current()
            actual_value = self.value_map[key][selected_index]
            new_config[key] = actual_value
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("保存成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("保存失败", f"错误信息: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("紧凑版prompt_config.txt编辑器")
    CompactConfigEditor(root)
    root.mainloop()