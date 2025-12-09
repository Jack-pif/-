import flet as ft
import time
import datetime
import threading

def main(page: ft.Page):
    # --- 0. 页面全局设置 ---
    page.title = "UniLife Mate"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = ft.colors.GREY_50  # 对应 bg-gray-50

    # --- 1. 状态管理 (State) ---
    # 问候语逻辑
    def get_greeting():
        h = datetime.datetime.now().hour
        if h < 9: return "早八人，加油！"
        elif h < 12: return "上午好，效率拉满！"
        elif h < 18: return "下午好，坚持就是胜利！"
        else: return "晚上好，记得劳逸结合。"

    # --- 2. 核心 UI 组件构建 ---

    # 顶部 Header (对应 React 的 Header 部分)
    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("UNILIFE MATE", size=12, color=ft.colors.INDIGO_200, weight=ft.FontWeight.BOLD),
                    ft.Text(get_greeting(), size=24, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                ]),
                ft.Container(
                    content=ft.Icon(ft.icons.emoji_events, color=ft.colors.YELLOW_300),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                    padding=8,
                    border_radius=50,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]),
        bgcolor=ft.colors.INDIGO_600,
        padding=ft.padding.only(left=24, right=24, top=50, bottom=24),
        border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.with_opacity(0.2, ft.colors.BLACK))
    )

    # ================= 模块 1: 专注番茄钟 (FocusModule) =================
    class FocusView(ft.Container):
        def __init__(self):
            super().__init__()
            self.mode = "study" # study or rest
            self.time_left = 25 * 60
            self.is_running = False
            self.padding = 20
            
            # 圆环进度条
            self.progress_ring = ft.ProgressRing(
                width=240, height=240, stroke_width=15, value=0,
                color=ft.colors.INDIGO_500, bgcolor=ft.colors.GREY_100
            )
            
            # 时间显示文本
            self.timer_text = ft.Text("25:00", size=60, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_GREY_800)
            self.status_text = ft.Text("准备好了吗？", color=ft.colors.GREY_400)
            
            # 按钮
            self.btn_start = ft.ElevatedButton(
                text="开始", on_click=self.toggle_timer,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=15),
                    padding=20,
                    bgcolor=ft.colors.INDIGO_600,
                    color=ft.colors.WHITE,
                ),
                width=150
            )
            
            # 模式切换按钮组
            self.btn_mode_study = ft.Container(
                content=ft.Text("深度学习", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_600),
                bgcolor=ft.colors.WHITE, padding=ft.padding.symmetric(horizontal=20, vertical=10),
                border_radius=20, shadow=ft.BoxShadow(blur_radius=2, color=ft.colors.GREY_300),
                on_click=lambda e: self.switch_mode("study")
            )
            self.btn_mode_rest = ft.Container(
                content=ft.Text("课间休息", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_500),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                border_radius=20,
                on_click=lambda e: self.switch_mode("rest")
            )

            # 组装 UI
            self.content = ft.Column([
                ft.Container(height=20), # Spacer
                ft.Container(
                    content=ft.Row([self.btn_mode_study, self.btn_mode_rest], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=ft.colors.GREY_200, border_radius=30, padding=4, width=220
                ),
                ft.Container(height=40),
                ft.Stack([
                    self.progress_ring,
                    ft.Container(
                        content=ft.Column([self.timer_text, self.status_text], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        alignment=ft.alignment.center, width=240, height=240
                    )
                ], width=240, height=240),
                ft.Container(height=40),
                ft.Row([
                    self.btn_start,
                    ft.IconButton(icon=ft.icons.REFRESH, on_click=self.reset_timer, bgcolor=ft.colors.GREY_200, icon_color=ft.colors.GREY_600)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ft.Container(height=30),
                ft.Container(
                    content=ft.Row([ft.Icon(ft.icons.BOOK, size=16, color=ft.colors.BLUE_600), ft.Text("Tips: 手机翻面放在一边，效率提升50%", size=12, color=ft.colors.BLUE_600)], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=ft.colors.BLUE_50, padding=10, border_radius=10
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def update_ui(self):
            mins, secs = divmod(self.time_left, 60)
            self.timer_text.value = "{:02d}:{:02d}".format(mins, secs)
            total_time = 25 * 60 if self.mode == "study" else 5 * 60
            self.progress_ring.value = (total_time - self.time_left) / total_time
            self.update()

        def switch_mode(self, mode):
            self.mode = mode
            self.is_running = False
            self.time_left = 25 * 60 if mode == "study" else 5 * 60
            # 更新按钮样式
            if mode == "study":
                self.progress_ring.color = ft.colors.INDIGO_500
                self.btn_start.style.bgcolor = ft.colors.INDIGO_600
                self.btn_mode_study.bgcolor = ft.colors.WHITE
                self.btn_mode_study.shadow = ft.BoxShadow(blur_radius=2, color=ft.colors.GREY_300)
                self.btn_mode_rest.bgcolor = None
                self.btn_mode_rest.shadow = None
            else:
                self.progress_ring.color = ft.colors.GREEN_500
                self.btn_start.style.bgcolor = ft.colors.GREEN_500
                self.btn_mode_rest.bgcolor = ft.colors.WHITE
                self.btn_mode_rest.shadow = ft.BoxShadow(blur_radius=2, color=ft.colors.GREY_300)
                self.btn_mode_study.bgcolor = None
                self.btn_mode_study.shadow = None
            
            self.btn_start.text = "开始"
            self.status_text.value = "准备好了吗？"
            self.update_ui()

        def reset_timer(self, e):
            self.is_running = False
            self.switch_mode(self.mode)

        def toggle_timer(self, e):
            if self.is_running:
                self.is_running = False
                self.btn_start.text = "继续"
                self.status_text.value = "已暂停"
                self.update()
            else:
                self.is_running = True
                self.btn_start.text = "暂停"
                self.status_text.value = "保持专注..." if self.mode == "study" else "放松大脑..."
                self.update()
                # 开启线程倒计时
                threading.Thread(target=self.run_timer, daemon=True).start()

        def run_timer(self):
            while self.is_running and self.time_left > 0:
                time.sleep(1)
                if not self.is_running: break
                self.time_left -= 1
                self.update_ui()
            
            if self.time_left == 0 and self.is_running:
                self.is_running = False
                self.btn_start.text = "完成"
                self.status_text.value = "时间到！"
                page.snack_bar = ft.SnackBar(ft.Text("时间到啦！"))
                page.snack_bar.open = True
                self.update_ui()
                page.update()

    # ================= 模块 2: 待办事项 (TaskModule) =================
    class TaskView(ft.Column):
        def __init__(self):
            super().__init__()
            self.padding = 20
            self.spacing = 15
            self.tasks = [
                {"id": 1, "text": "完成高数作业 (第三章)", "tag": "学习", "done": False},
                {"id": 2, "text": "社团活动报名", "tag": "社团", "done": True},
            ]
            self.input_text = ft.TextField(hint_text="添加新任务...", expand=True, height=45, content_padding=10, text_size=14)
            self.tag_dropdown = ft.Dropdown(
                width=80, value="学习", height=45, content_padding=5, text_size=12,
                options=[ft.dropdown.Option("学习"), ft.dropdown.Option("生活"), ft.dropdown.Option("社团")]
            )
            self.task_list_col = ft.Column(spacing=10)
            
            self.controls = [
                self.build_stats(),
                self.task_list_col,
                ft.Container(height=60) # 底部留白防止被遮挡
            ]
            self.render_tasks()

        def build_stats(self):
            return ft.Row([
                ft.Container(
                    content=ft.Column([ft.Text(str(len([t for t in self.tasks if not t['done']])), size=24, weight="bold"), ft.Text("待完成", size=10, color="grey")]),
                    bgcolor="white", padding=15, border_radius=15, expand=True, shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_200)
                ),
                ft.Container(
                    content=ft.Column([ft.Text(str(len([t for t in self.tasks if t['done']])), size=24, weight="bold", color="green"), ft.Text("已完成", size=10, color="grey")]),
                    bgcolor="white", padding=15, border_radius=15, expand=True, shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.GREY_200)
                ),
            ])

        def render_tasks(self):
            self.task_list_col.controls.clear()
            if not self.tasks:
                self.task_list_col.controls.append(ft.Container(content=ft.Text("好清闲的一天 ~", color="grey"), alignment=ft.alignment.center, padding=20))
            
            for task in self.tasks:
                # 标签颜色映射
                tag_color = ft.colors.INDIGO_100 if task['tag'] == "学习" else (ft.colors.PINK_100 if task['tag'] == "社团" else ft.colors.ORANGE_100)
                tag_text_color = ft.colors.INDIGO_600 if task['tag'] == "学习" else (ft.colors.PINK_600 if task['tag'] == "社团" else ft.colors.ORANGE_600)
                
                # 任务卡片
                card = ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.icons.CHECK_CIRCLE if task['done'] else ft.icons.RADIO_BUTTON_UNCHECKED,
                            icon_color=ft.colors.GREEN_500 if task['done'] else ft.colors.GREY_400,
                            on_click=lambda e, t=task: self.toggle_task(t)
                        ),
                        ft.Column([
                            ft.Text(task['text'], decoration=ft.TextDecoration.LINE_THROUGH if task['done'] else None, color="grey" if task['done'] else "black", weight="bold"),
                            ft.Container(content=ft.Text(task['tag'], size=10, color=tag_text_color), bgcolor=tag_color, padding=ft.padding.symmetric(horizontal=6, vertical=2), border_radius=5)
                        ], spacing=2, expand=True),
                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color="red", icon_size=18, on_click=lambda e, id=task['id']: self.delete_task(id))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="white", padding=10, border_radius=15, border=ft.border.all(1, ft.colors.GREY_100),
                    opacity=0.6 if task['done'] else 1.0
                )
                self.task_list_col.controls.append(card)
            self.update()

        def add_task_ui(self):
            # 返回一个底部输入栏
            return ft.Container(
                content=ft.Row([
                    self.tag_dropdown,
                    self.input_text,
                    ft.IconButton(icon=ft.icons.ADD_CIRCLE, icon_color=ft.colors.INDIGO_600, icon_size=30, on_click=self.add_task)
                ]),
                bgcolor="white", padding=10, border_radius=ft.border_radius.only(top_left=20, top_right=20),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.GREY_300)
            )

        def add_task(self, e):
            if self.input_text.value:
                self.tasks.append({"id": int(time.time()), "text": self.input_text.value, "tag": self.tag_dropdown.value, "done": False})
                self.input_text.value = ""
                self.render_tasks()
                # 更新统计数据需要重新构建controls，这里简单处理只刷新列表
                # 实际开发中可以优化刷新逻辑
                self.controls[0] = self.build_stats() # 刷新统计
                self.update()

        def toggle_task(self, task):
            task['done'] = not task['done']
            self.render_tasks()
            self.controls[0] = self.build_stats()
            self.update()

        def delete_task(self, id):
            self.tasks = [t for t in self.tasks if t['id'] != id]
            self.render_tasks()
            self.controls[0] = self.build_stats()
            self.update()


    # ================= 模块 3: 生活费记账 (MoneyModule) =================
    class MoneyView(ft.Column):
        def __init__(self):
            super().__init__()
            self.padding = 20
            self.spacing = 20
            self.budget = 2000
            self.transactions = [
                {"id": 1, "title": "食堂午饭", "amount": -15, "date": "今日"},
                {"id": 2, "title": "兼职收入", "amount": 120, "date": "10月5日"},
            ]
            
            # 余额卡片组件
            self.balance_text = ft.Text("¥ 0.00", size=30, weight="bold", color="white")
            self.progress_bar = ft.ProgressBar(value=0, color=ft.colors.TEAL_300, bgcolor=ft.colors.BLUE_GREY_700, height=8)
            self.progress_text = ft.Text("0%", size=12, color=ft.colors.BLUE_GREY_200)
            
            self.card = ft.Container(
                content=ft.Column([
                    ft.Row([ft.Text("本月剩余可用", color=ft.colors.BLUE_GREY_200, size=12), ft.Icon(ft.icons.SETTINGS, color=ft.colors.BLUE_GREY_200, size=16)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    self.balance_text,
                    ft.Container(height=10),
                    ft.Row([ft.Text(f"预算进度 ({self.budget})", size=10, color=ft.colors.BLUE_GREY_200), self.progress_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    self.progress_bar
                ]),
                gradient=ft.LinearGradient(colors=[ft.colors.BLUE_GREY_800, ft.colors.SLATE_900], begin=ft.alignment.top_left, end=ft.alignment.bottom_right),
                padding=25, border_radius=25, shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLUE_GREY_200)
            )

            # 记账输入
            self.input_title = ft.TextField(hint_text="项目 (如: 奶茶)", expand=2, height=40, text_size=12, content_padding=10)
            self.input_amount = ft.TextField(hint_text="金额", expand=1, height=40, text_size=12, content_padding=10, keyboard_type=ft.KeyboardType.NUMBER)
            
            self.trans_list = ft.Column(spacing=10)
            
            self.controls = [
                self.card,
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.icons.TRENDING_UP, size=16), ft.Text("记一笔", weight="bold")]),
                        ft.Row([self.input_title, self.input_amount]),
                        ft.Row([
                            ft.ElevatedButton("支出", style=ft.ButtonStyle(bgcolor=ft.colors.RED_50, color="red"), expand=True, on_click=lambda e: self.add_trans(-1)),
                            ft.ElevatedButton("收入", style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_50, color="green"), expand=True, on_click=lambda e: self.add_trans(1)),
                        ])
                    ]),
                    bgcolor="white", padding=15, border_radius=15, border=ft.border.all(1, ft.colors.GREY_100)
                ),
                ft.Text("最近明细", size=12, weight="bold", color="grey"),
                self.trans_list,
                ft.Container(height=60)
            ]
            self.refresh_data()

        def refresh_data(self):
            total = sum(t['amount'] for t in self.transactions)
            remaining = self.budget + total
            percentage = min(max((remaining / self.budget), 0), 1)
            
            self.balance_text.value = f"¥ {remaining:.2f}"
            self.progress_bar.value = percentage
            self.progress_text.value = f"{int(percentage*100)}%"
            self.progress_bar.color = ft.colors.RED_400 if percentage < 0.2 else ft.colors.TEAL_300
            
            self.trans_list.controls.clear()
            for t in self.transactions:
                is_expense = t['amount'] < 0
                item = ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.icons.COFFEE if is_expense else ft.icons.ACCOUNT_BALANCE_WALLET, size=16, color="red" if is_expense else "green"),
                                bgcolor=ft.colors.RED_50 if is_expense else ft.colors.GREEN_50, padding=8, border_radius=8
                            ),
                            ft.Column([ft.Text(t['title'], weight="bold"), ft.Text(t['date'], size=10, color="grey")], spacing=2)
                        ]),
                        ft.Text(f"{'+' if not is_expense else ''}{t['amount']}", weight="bold", color="black" if is_expense else "green")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="white", padding=12, border_radius=12, border=ft.border.all(1, ft.colors.GREY_50)
                )
                self.trans_list.controls.append(item)
            self.update()

        def add_trans(self, multiplier):
            if not self.input_title.value or not self.input_amount.value: return
            try:
                val = float(self.input_amount.value)
                self.transactions.insert(0, {
                    "id": int(time.time()), 
                    "title": self.input_title.value, 
                    "amount": val * multiplier, 
                    "date": "刚刚"
                })
                self.input_title.value = ""
                self.input_amount.value = ""
                self.refresh_data()
            except:
                pass

    # --- 3. 页面布局与导航 ---
    
    # 实例化三个视图
    focus_view = FocusView()
    task_view = TaskView()
    money_view = MoneyView()

    # 内容区域 (用 AnimatedSwitcher 做简单的切换动画，或者直接替换 content)
    body_content = ft.Container(content=focus_view, expand=True)
    
    # 底部输入栏容器 (仅在 Task 页面显示)
    bottom_action_container = ft.Container(content=None)

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            body_content.content = focus_view
            bottom_action_container.content = None
        elif idx == 1:
            body_content.content = ft.ListView([task_view], expand=True, padding=0) # 列表需可滚动
            bottom_action_container.content = task_view.add_task_ui()
        elif idx == 2:
            body_content.content = ft.ListView([money_view], expand=True, padding=0)
            bottom_action_container.content = None
        page.update()

    # 底部导航栏
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.ACCESS_TIME, label="专注"),
            ft.NavigationDestination(icon=ft.icons.CHECK_BOX_OUTLINED, label="待办"),
            ft.NavigationDestination(icon=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED, label="记账"),
        ],
        selected_index=0,
        on_change=on_nav_change,
        bgcolor=ft.colors.WHITE,
        indicator_color=ft.colors.INDIGO_100,
        surface_tint_color=ft.colors.WHITE,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.with_opacity(0.1, ft.colors.BLACK))
    )

    # 最终页面结构
    page.add(
        ft.Column([
            header,
            ft.Container(content=body_content, expand=True, padding=ft.padding.only(left=0, right=0, bottom=0)), # 主体
            bottom_action_container, # 悬浮输入框 (用于Task)
            nav_bar
        ], expand=True, spacing=0)
    )

ft.app(target=main)