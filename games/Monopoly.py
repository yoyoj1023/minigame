import tkinter as tk
from tkinter import messagebox
import random


class Player:
    def __init__(self, name, money=1500):
        self.name = name
        self.money = money
        self.position = 0
        self.alive = True

    def move(self, steps, board_size):
        """玩家移動。如果超出棋盤格數，則從頭繞回。"""
        self.position = (self.position + steps) % board_size

    def pay(self, amount):
        """玩家支付金錢。如果不足則破產。"""
        if self.money >= amount:
            self.money -= amount
        else:
            self.money = 0
            self.alive = False

    def receive(self, amount):
        """玩家收款。"""
        self.money += amount


class Tile:
    def __init__(self, name, price=0, toll=0):
        self.name = name
        self.price = price
        self.toll = toll
        self.owner = None  # 紀錄哪位玩家擁有這個地

    def landed_on(self, player, buy_callback):
        """
        玩家停在此格子時觸發的行為：
         - 若沒有擁有者且價格>0，詢問玩家是否要購買。（呼叫 buy_callback）
         - 若已有人持有且不是自己，需支付過路費。
        """
        if self.owner is None and self.price > 0:
            buy_callback(self, player)
        elif self.owner is not None and self.owner != player:
            # 必須支付過路費
            player.pay(self.toll)
            # 若付款後還在遊戲中，地主收錢
            if player.alive:
                self.owner.receive(self.toll)


def roll_dice():
    """擲兩顆六面骰，回傳總和。"""
    return random.randint(1, 6) + random.randint(1, 6)


class MonopolyGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("大富翁小遊戲 - Tkinter版")

        # 建立玩家與棋盤資料
        self.players = []
        self.board = self.create_board()
        self.board_size = len(self.board)
        self.current_player_index = 0
        self.round_number = 1

        # 先簡單地預設兩位玩家，你可以改寫成在 GUI 上輸入玩家資訊
        self.players.append(Player("玩家A"))
        self.players.append(Player("玩家B"))

        # 建立主視窗的 Frame
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(padx=10, pady=10)

        # 棋盤顯示區（簡單用一列或多列的 label 展示）
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack()

        self.tile_labels = []  # 儲存棋盤上每個格子的 Label (用來更新顯示)
        for i, tile in enumerate(self.board):
            lbl = tk.Label(self.board_frame, text=f"{i}\n{tile.name}",
                           width=14, height=3, relief="groove", bg="white")
            lbl.grid(row=0, column=i, padx=5, pady=5)
            self.tile_labels.append(lbl)

        # 顯示玩家資訊的區域
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(pady=10)

        self.info_label = tk.Label(self.info_frame, text="", font=("Arial", 12))
        self.info_label.pack()

        # 操作按鈕區域
        self.btn_frame = tk.Frame(self.main_frame)
        self.btn_frame.pack()

        # 擲骰子按鈕
        self.roll_button = tk.Button(self.btn_frame, text="擲骰子", command=self.roll_dice_action)
        self.roll_button.pack(side=tk.LEFT, padx=5)

        # 結束回合按鈕
        self.end_turn_button = tk.Button(self.btn_frame, text="結束回合", command=self.end_turn_action)
        self.end_turn_button.pack(side=tk.LEFT, padx=5)

        # 初始化畫面
        self.update_ui()

    def create_board(self):
        """建立示範用的 10 格小棋盤。"""
        return [
            Tile("起點", price=0, toll=0),
            Tile("台北車站", price=100, toll=10),
            Tile("中正紀念堂", price=200, toll=20),
            Tile("免費停留", price=0, toll=0),
            Tile("101大樓", price=300, toll=40),
            Tile("龍山寺", price=150, toll=15),
            Tile("淡水老街", price=200, toll=20),
            Tile("免費停留", price=0, toll=0),
            Tile("士林夜市", price=250, toll=30),
            Tile("大安森林", price=350, toll=50),
        ]

    def update_ui(self):
        """更新棋盤與玩家資訊顯示。"""
        # 更新棋盤格子的顯示
        for i, tile in enumerate(self.board):
            owner_text = ""
            if tile.owner is not None:
                owner_text = f"\n擁有者: {tile.owner.name}"
            # 先重置背景色
            bg_color = "white"

            # 如果有玩家在這個位置，顯示玩家名稱
            player_names_on_tile = []
            for p in self.players:
                if p.alive and p.position == i:
                    player_names_on_tile.append(p.name)

            if player_names_on_tile:
                bg_color = "lightgreen"  # 若有玩家在此格，就上個顏色

            text_display = (f"{i}\n{tile.name}"
                            f"{owner_text}\n"
                            f"{'/'.join(player_names_on_tile)}")

            self.tile_labels[i].config(text=text_display, bg=bg_color)

        # 更新玩家資訊文字
        alive_players_str = []
        for p in self.players:
            status = f"{p.name}: $ {p.money}"
            if not p.alive:
                status += " (破產)"
            alive_players_str.append(status)

        current_player = self.players[self.current_player_index]
        info_text = (f"第 {self.round_number} 回合 - {current_player.name} 的回合\n\n" +
                     "\n".join(alive_players_str))
        self.info_label.config(text=info_text)

    def roll_dice_action(self):
        """點擊擲骰子按鈕時，觸發此事件。"""
        current_player = self.players[self.current_player_index]
        if not current_player.alive:
            return  # 若玩家已破產，不操作

        dice_value = roll_dice()
        messagebox.showinfo("擲骰子", f"{current_player.name} 擲出了 {dice_value} 點！")

        # 移動玩家
        old_position = current_player.position
        current_player.move(dice_value, self.board_size)
        new_position = current_player.position

        # 停在的新格子
        landed_tile = self.board[new_position]

        # 執行格子事件
        def buy_callback(tile, player):
            """當需要詢問玩家是否購買土地時的回呼函式。"""
            if player.money < tile.price:
                messagebox.showinfo("無法購買", f"{player.name} 資金不足，無法購買 {tile.name}")
                return
            # 跳出對話框，詢問是否購買
            buy = messagebox.askyesno("購買土地", f"{player.name} 要購買 {tile.name} 嗎？\n價格: {tile.price}")
            if buy:
                player.pay(tile.price)
                tile.owner = player
                messagebox.showinfo("成功購買", f"{player.name} 購買了 {tile.name}！")

        landed_tile.landed_on(current_player, buy_callback)

        # 若繳過路費後破產，釋放該玩家土地
        if not current_player.alive:
            messagebox.showinfo("破產退場", f"{current_player.name} 無法支付費用，已破產！")
            # 釋放該玩家所有地產
            for tile in self.board:
                if tile.owner == current_player:
                    tile.owner = None

        self.update_ui()

    def end_turn_action(self):
        """結束回合，換下一位玩家。"""
        # 切換到下一位玩家
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.round_number += 1

        # 若只剩最後一名玩家alive，就結束遊戲
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) == 1:
            winner = alive_players[0]
            messagebox.showinfo("遊戲結束", f"最後的贏家是：{winner.name}")
            # 結束整個視窗
            self.master.destroy()
            return

        # 更新介面
        self.update_ui()


def main():
    root = tk.Tk()
    app = MonopolyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()