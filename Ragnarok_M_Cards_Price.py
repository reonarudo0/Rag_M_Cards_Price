import tkinter as tk
import pandas as pd
import requests
import re

class RagCards():
    def __init__(self,master):
        self.master = master
        ###--Settings
        self.master.title('Ragnarok M: Eternal Love Cards Price')
        self.master.geometry('480x330')
        self.master.minsize(width=480, height=330)
        self.master.maxsize(width=550, height=330)
        self.master.resizable(width=True, height=False)

        ###--Data
        self.data = pd.read_excel('Assets\\RagCardsNoPrice.xlsx', sheet_name='Sheet1')
        self.data.drop(['Unnamed: 0'], axis=1, inplace=True)
        self.newData = ''

        ###--Dropdown Lists
        self.equipIn = ['All', 'Weapon', 'Off-Hand', 'Armor', 'Garment', 'Shoes', 'Accessory', 'Headwear']
        self.rarity = ['All', 'White', 'Green', 'Blue', 'Purple', 'None']
        self.priceOptions = ['Lowest','Highest']

        ###--Variables
        self.equipInStr = tk.StringVar()
        self.equipInStr.set(self.equipIn[0])
        self.rarityStr = tk.StringVar()
        self.rarityStr.set(self.rarity[0])
        self.priceOptionsStr = tk.StringVar()
        self.priceOptionsStr.set(self.priceOptions[0])

        ###--Interface
        self.canvasData = tk.Canvas(self.master, width=500, height=350)
        self.canvasData.place(x=10, y=70)

        self.searchNameLabel = tk.Label(self.master, text='Search:')
        self.searchNameLabel.place(x=0, y=5)
        self.searchNameEntry = tk.Entry(self.master)
        self.searchNameEntry.place(x=42, y=5)

        self.equipInLabel = tk.Label(self.master, text='Equip In:')
        self.equipInLabel.place(x=150, y=5)
        self.dropDownEquipIn = tk.OptionMenu(self.master, self.equipInStr, *self.equipIn)
        self.dropDownEquipIn.place(x=200, y=0)

        self.rarityLabel = tk.Label(self.master, text='Rarity:')
        self.rarityLabel.place(x=300, y=5)
        self.dropDownRarity = tk.OptionMenu(self.master, self.rarityStr, *self.rarity)
        self.dropDownRarity.place(x=340, y=0)

        self.priceLabel = tk.Label(self.master, text='Price:')
        self.priceLabel.place(x=5,y=35)
        self.dropDownPrice = tk.OptionMenu(self.master, self.priceOptionsStr, *self.priceOptions)
        self.dropDownPrice.place(x=40,y=30)

        self.searchBtn = tk.Button(self.master, text='Search', command=self.Search)
        self.searchBtn.place(x=140,y=33)

        self.refreshBtn = tk.Button(self.master, text='Refresh Prices', command=self.RefreshPrices)
        self.refreshBtn.place(x=200,y=33)

        ###--Initial Functions
        self.RefreshPrices()
        self.Search()

    def RefreshPrices(self):
        url = 'https://api-global.poporing.life/get_latest_price/'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

        newPrice = []

        for card in self.data['Item Name']:
            strCard = (card.lower()).split(' ')
            strCard = '_'.join(strCard)

            finalUrl = url + strCard

            ultPrice = (requests.get(finalUrl, headers=headers)).content

            newPrice.append(str(ultPrice).split('"price":')[1].split(',')[0])

        self.newData = pd.DataFrame(data={'Item Name': self.data['Item Name'], 'Price': newPrice})

        self.newData = pd.merge(self.newData, self.data, on='Item Name')
        self.newData = self.newData[self.newData['Price'] != 'null']
        self.newData = self.newData[self.newData['Price'] != '0']
        self.newData['Price'] = self.newData['Price'].astype('int32')

    def PrintDataFrame(self,data):
        self.DeleteCanvas()

        row,col,width = 0,0,0
        color = 'White'
        for element in data.iloc[:, col]:
            dataFrameIndex = tk.Label(self.canvasData, text=row, font='Arial 10', relief=tk.RIDGE, width=2, bg=color)
            dataFrameIndex.grid(row=row + 1,column=0)
            row = row + 1
            if(color == 'White'):
                color = '#D3D3D3'
            else:
                color = 'White'
        row,col = 0,0
        while (col != len(data.columns)):
            for element in data.iloc[:, col]:
                if (width == 0):
                    width = len(data.columns[col])
                if (len(str(element)) > width):
                    width = len(str(element))
            dataFrameTitles = tk.Label(self.canvasData, text=data.columns[col], font='Arial 10 bold', relief=tk.RIDGE,width=width + 1,bg='#D3D3D3')
            dataFrameTitles.grid(row=row, column=col + 1)
            row = row + 1
            color = 'White'
            for element in data.iloc[:, col]:
                dataFrameLabel = tk.Label(self.canvasData, text=element, font='Arial 10', relief=tk.RIDGE, width=width + 1,bg=color)
                dataFrameLabel.grid(row=row, column=col + 1)
                row = row + 1
                if (color == 'White'):
                    color = '#D3D3D3'
                else:
                    color = 'White'
            row,width = 0,0
            col = col + 1

    def Search(self):
        if(self.priceOptionsStr.get() == 'Lowest'):
            bool = True
        else:
            bool = False

        if(self.searchNameEntry.get() != ''):
            tempData = self.newData[self.newData['Item Name'].str.contains(self.searchNameEntry.get(), flags=re.IGNORECASE)]
            self.searchNameEntry.delete(0,'end')
            if(len(tempData) < 1):
                self.DeleteCanvas()
                notFoundLabel = tk.Label(self.canvasData, text='Não foi possivel encontrar nenhum resultado.')
                notFoundLabel.place(x=0,y=5)
            else:
                self.CreateSortedData(tempData,bool)

        else:
            tempData = self.newData
            self.CreateSortedData(tempData,bool)

    def CreateSortedData(self,tempData,bool):
        if (self.rarityStr.get() == 'All' and self.equipInStr.get() == 'All'):
            sortedData = (((tempData.sort_values(by='Price', ascending=bool)).reset_index()).drop(['index'], axis=1)).head(10)
            sortedData['Price'] = sortedData.apply(lambda x: '{:,}'.format(x['Price']), axis=1)
        elif (self.rarityStr.get() != 'All' and self.equipInStr.get() == 'All'):
            sortedData = (((tempData[tempData['Rarity'] == self.rarityStr.get()].sort_values(by=['Price'],ascending=bool)).reset_index()).drop(['index'], axis=1)).head(10)
            sortedData['Price'] = sortedData.apply(lambda x: '{:,}'.format(x['Price']), axis=1)
        elif (self.rarityStr.get() != 'All' and self.equipInStr.get() != 'All'):
            sortedData = (((tempData[(tempData['Rarity'] == self.rarityStr.get()) & (tempData['Equip in'] == self.equipInStr.get())].sort_values(by=['Price'], ascending=bool)).reset_index()).drop(['index'], axis=1)).head(10)
            sortedData['Price'] = sortedData.apply(lambda x: '{:,}'.format(x['Price']), axis=1)
        elif (self.rarityStr.get() == 'All' and self.equipInStr.get() != 'All'):
            sortedData = (((tempData[tempData['Equip in'] == self.equipInStr.get()].sort_values(by=['Price'],ascending=bool)).reset_index()).drop(['index'], axis=1)).head(10)
            sortedData['Price'] = sortedData.apply(lambda x: '{:,}'.format(x['Price']), axis=1)

        self.PrintDataFrame(sortedData)

    def DeleteCanvas(self):
        self.canvasData.destroy()
        self.canvasData = tk.Canvas(self.master, width=500, height=350)
        self.canvasData.place(x=10, y=70)

root = tk.Tk()
app = RagCards(root)
root.mainloop()