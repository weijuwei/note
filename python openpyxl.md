参考：

> https://openpyxl.readthedocs.io/en/stable/tutorial.html

### 1、Excel文档相关定义
- 工作簿(workbook)： 一个 Excel 电子表格文档；
- 工作表(sheet)： 每个工作簿可以包含多个表, 如： sheet1， sheet2等;
- 活动表(active sheet)： 用户当前查看的表;
- 列(column): 列地址是从 A 开始的;
- 行(row): 行地址是从 1 开始的;
- 单元格(cell)： 特定行和列的方格；
### 2、安装openpyxl模块
```shell
# pip3 install openpyxl
Collecting openpyxl
  Downloading https://files.pythonhosted.org/packages/ba/06/b899c8867518df19e242d8cbc82d4ba210f5ffbeebb7704c695e687ab59c/openpyxl-2.6.2.tar.gz (173kB)
    100% |████████████████████████████████| 174kB 581kB/s
Collecting jdcal (from openpyxl)
  Downloading https://files.pythonhosted.org/packages/a0/38/dcf83532480f25284f3ef13f8ed63e03c58a65c9d3ba2a6a894ed9497207/jdcal-1.4-py2.py3-none-any.whl
Collecting et_xmlfile (from openpyxl)
  Downloading https://files.pythonhosted.org/packages/22/28/a99c42aea746e18382ad9fb36f64c1c1f04216f41797f2f0fa567da11388/et_xmlfile-1.0.1.tar.gz
Installing collected packages: jdcal, et-xmlfile, openpyxl
  Running setup.py install for et-xmlfile ... done
  Running setup.py install for openpyxl ... done
Successfully installed et-xmlfile-1.0.1 jdcal-1.4 openpyxl-2.6.2
```
### 3、应用操作
test.xlsx表中的内容：

| 物品   | 单价 | 数量 | 价格 |
| :----- | :--- | :--- | :--: |
| 可乐   | 2.5  | 10   |  25  |
| 橙汁   | 3    | 5    |  15  |
| 牛奶   | 2.5  | 10   |  25  |
| 矿泉水 | 2    | 20   |  4   |

#### （1）工作簿 workbook
创建一个excel文件需要从openpyxl中导入*Workbook*类
```python
>>> from openpyxl import Workbook
>>> wb = Workbook()
```
一个工作簿被创建时，至少有一个工作表，可以通过*Workbook.active*获取
```python
>>> ws = wb.active
```
创建一个新的工作表，使用*Workbook.create_sheet*()方法
```python
#创建一个名为Mysheet的工作表，插入到最后
>>> ws1 = wb.create_sheet('Mysheet')

#创建一个工作表，放置在第一个
>>> ws2 = wb.create_sheet('Mysheet1',0)
```
通过*Worksheet.title*修改工作表名字
```python
>>> ws1.title = "Sheet1"
ws1
<Worksheet "Sheet1">

>>> print(wb.sheetnames)
['Mysheet1', 'Sheet', 'Sheet1']

>>> for sheet in wb:
...      print(sheet.title)
Mysheet1
Sheet
Sheet1
```

打开已有的excel表
```python
>>> wb = openpyxl.load_workbook("test.xlsx")
```
保存excel表
```python
#操作会覆盖已存在的文件
>>> wb.save("test.xlsx")
```
#### (2)数据操作
##### 访问一个单元格Cell
```python
>>> c= ws['A4']
>>> ws['A4'] = 4
##为B4赋值为10
d = ws.cell(row=4, column=2, value=10)
```
##### 访问多个单元格cells

sheet.rows为生成器, 里面是每一行的数据，每一行又由一个tuple包裹。
sheet.columns类似，不过里面是每个tuple是每一列的单元格。

```python
#以元组格式输出列
>>> tuple(ws.columns)
((<Cell 'Sheet1'.A1>, <Cell 'Sheet1'.A2>, <Cell 'Sheet1'.A3>, <Cell 'Sheet1'.A4>, <Cell 'Sheet1'.A5>), (<Cell 'Sheet1'.B1>, <Cell 'Sheet1'.B2>, <Cell 'Sheet1'.B3>, <Cell 'Sheet1'.B4>, <Cell 'Sheet1'.B5>), (<Cell 'Sheet1'.C1>, <Cell 'Sheet1'.C2>, <Cell 'Sheet1'.C3>, <Cell 'Sheet1'.C4>, <Cell 'Sheet1'.C5>), (<Cell 'Sheet1'.D1>, <Cell 'Sheet1'.D2>, <Cell 'Sheet1'.D3>, <Cell 'Sheet1'.D4>, <Cell 'Sheet1'.D5>))
#以元组格式输出行
>>> tuple(ws.rows)
((<Cell 'Sheet1'.A1>, <Cell 'Sheet1'.B1>, <Cell 'Sheet1'.C1>, <Cell 'Sheet1'.D1>), (<Cell 'Sheet1'.A2>, <Cell 'Sheet1'.B2>, <Cell 'Sheet1'.C2>, <Cell 'Sheet1'.D2>), (<Cell 'Sheet1'.A3>, <Cell 'Sheet1'.B3>, <Cell 'Sheet1'.C3>, <Cell 'Sheet1'.D3>), (<Cell 'Sheet1'.A4>, <Cell 'Sheet1'.B4>, <Cell 'Sheet1'.C4>, <Cell 'Sheet1'.D4>), (<Cell 'Sheet1'.A5>, <Cell'Sheet1'.B5>, <Cell 'Sheet1'.C5>, <Cell 'Sheet1'.D5>))
```

读取数据
```python
for row in ws.values:
	for value in row:
		print(value)
```
举例：
```python
#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import openpyxl

#加载指定工作簿
wb = openpyxl.load_workbook("test.xlsx")
#选择指定工作表
ws = wb['Sheet1']

for rows in ws.values:
    for value in rows:
        print(value,end="\t")
    print()

#按行循环遍历表中数据，并输出到控制台
for row in ws.rows:
    for cell in row:
        print(cell.value,end="\t")
    print()
#按列循环
for column in ws.columns:
    for cell in column:
        print(cell.value,end="\t")
    print()
```