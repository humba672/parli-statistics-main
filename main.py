import requests
from bs4 import BeautifulSoup
import statistics
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QPushButton, QFileDialog
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

path = ''

def getPath():
    global path
    path = str(QFileDialog.getExistingDirectory(window, "Select Directory to Write File to"))
    select_file.setText(path)
    select_file.adjustSize()

def doThings():
    global path
    try:
        url = url_entry.text()
        num_rounds = int(r_entry.text())

        data_data = []

        judge_data = {}

        judge_names = []

        first = True

        for j in range(num_rounds):
            turl = int(url.split('round_id=')[1])
            if not first:
                turl += 1
            else:
                first = False
            url = url.split('round_id=')[0] + 'round_id=' + str(turl)
            r = requests.get(url)

            soup = BeautifulSoup(r.content, 'html5lib')

            table = soup.find('tbody')

            matches = table.find_all('td')

            all_data = []

            for i in range(int(len(matches)/6)):
                all_data.append({})
                fails = 0
                try:
                    all_data[i][matches[4 + 6*i].div.span.span.nextSibling.strip()] = float(matches[4 + 6*i].div.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                    all_data[i][matches[4 + 6*i].div.nextSibling.nextSibling.span.span.nextSibling.strip()] = float(matches[4 + 6*i].div.nextSibling.nextSibling.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                    all_data[i][matches[5 + 6*i].div.span.span.nextSibling.strip()] = float(matches[5 + 6*i].div.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                    all_data[i][matches[5 + 6*i].div.nextSibling.nextSibling.span.span.nextSibling.strip()] = float(matches[5 + 6*i].div.nextSibling.nextSibling.span.nextSibling.nextSibling.span.div.decode_contents().strip())

                except:
                    gov = False
                    try:
                        float(matches[4 + 6*i].div.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                    except:
                        gov = True
                        fails += 1
                    try:
                        float(matches[5 + 6*i].div.nextSibling.nextSibling.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                    except:
                        gov = False
                        fails += 1
                    if fails == 2:
                        continue
                    if gov:
                        mav_name = matches[6*i]['title'].strip()
                        nm = mav_name.split(' ')[0][0].upper() + mav_name.split(' ')[1]
                        all_data[i][nm] = float(matches[4+6*i].div.span.div.decode_contents().strip())
                        all_data[i][matches[5 + 6*i].div.span.span.nextSibling.strip()] = float(matches[5 + 6*i].div.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                        all_data[i][matches[5 + 6*i].div.nextSibling.nextSibling.span.span.nextSibling.strip()] = float(matches[5 + 6*i].div.nextSibling.nextSibling.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                    else:
                        mav_name = matches[1+6*i]['title'].strip()
                        nm = mav_name.split(' ')[0][0].upper() + mav_name.split(' ')[1]
                        all_data[i][nm] = float(matches[5+6*i].div.span.div.decode_contents().strip())
                        all_data[i][matches[4 + 6*i].div.span.span.nextSibling.strip()] = float(matches[4 + 6*i].div.span.nextSibling.nextSibling.span.div.decode_contents().strip())
                        all_data[i][matches[4 + 6*i].div.nextSibling.nextSibling.span.span.nextSibling.strip()] = float(matches[4 + 6*i].div.nextSibling.nextSibling.span.nextSibling.nextSibling.span.div.decode_contents().strip())

                judge_name = matches[2 + 6*i].div.span.nextSibling.strip()

                if judge_name not in judge_names:
                    judge_names.append(judge_name)

                if not judge_name in judge_data:
                    judge_data[judge_name] = []

                for val in all_data[i].values():
                    judge_data[judge_name].append(val)

                all_data[i]['judge'] = judge_names.index(judge_name) + 1000

            data_data.append(all_data)

            all_data = []

        final_data = {}

        final = []

        judge_stdevs = {}

        for judge in judge_data:
            judge_stdevs[judge] = statistics.stdev(judge_data[judge])

        for k in data_data:
            for match in k:
                scores = sorted(list(match.values()))[::-1]
                for name in list(match.keys()):
                    if name == 'judge':
                        continue
                    score = match[name]
                    temp = [name]
                    temp.append(score)
                    temp.append(scores.index(score))
                    temp.append(score-min(scores))
                    temp.append((score-statistics.fmean(judge_data[judge_names[match['judge']-1000]]))/judge_stdevs[judge_names[match['judge']-1000]])
                    final.append(temp)

        # name, score, placement, diff from min, z-score
        # agg z-score, avg placement, avg diff from min, mean(self) - mean(judges) 

        for p in final:
            if not p[0] in final_data:
                final_data[p[0]] = [0, [0,0], [0,0], [0,0]]
            final_data[p[0]][0] += p[4]
            # final_data[p[0]][1] += p[2]
            # final_data[p[0]][2] += p[3]
            final_data[p[0]][1][0] += p[2]
            final_data[p[0]][1][1] += 1
            final_data[p[0]][2][0] += p[3]
            final_data[p[0]][2][1] += 1
            final_data[p[0]][3][0] += p[1]
            final_data[p[0]][3][1] += 1

        judge_mean = 0

        for judge in judge_data:
            judge_mean += statistics.fmean(judge_data[judge])

        judge_mean /= len(judge_data)

        for p in final_data:
            pmean = final_data[p][3][0]/final_data[p][3][1]
            final_data[p][3] = round(pmean - judge_mean,2)
            final_data[p][0] = round(final_data[p][0],2)
            tmean = final_data[p][1][0]/final_data[p][1][1]
            final_data[p][1] = round(tmean, 2)
            tmean = final_data[p][2][0]/final_data[p][2][1]
            final_data[p][2] = round(tmean,2)

        # agg z-score, agg placement, agg diff from min, mean(self) - mean(judges) 

        with open(os.path.join(path, x_entry.text()), 'w') as f:
            f.write('Name, Aggregate Z-Score, Average Placement, Average Points Above Minimum, Mean Score - Judge Mean\n')
            for person in final_data:
                p = final_data[person]
                f.write(f'{person}, {p[0]}, {p[1]}, {p[2]}, {p[3]}\n')

        success_indicator.setText('Success! Data written to ' + path + '/' + x_entry.text())
        success_indicator.adjustSize()
    except Exception as e:
        print(e)
        success_indicator.setText("Error! Please send me the error in the command \nprompt (or read it yourself).")        
        success_indicator.adjustSize()


app = QApplication([])

window = QWidget()
window.setWindowTitle("Parli Statistics")
window.setGeometry(100, 300, 400, 350)
helloMsg = QLabel("<h1>Parli Statistics</h1>", parent=window)
helloMsg.move(110, 15)
url_label = QLabel("Enter URL (from round 1 on the results page): ",parent=window).move(10,50)
url_entry = QLineEdit(parent=window)
url_entry.move(10,80)
r_label = QLabel("Enter the number of rounds there are in the tournament: ", parent=window).move(10,110)
r_entry = QLineEdit(parent=window)
r_entry.move(10,140)
x_label = QLabel("Enter the name of the file you'd like to write to (should be .csv \nand file does not need to already exist):", parent=window).move(10,170)
x_entry = QLineEdit(parent=window)
x_entry.move(10,210)
select_file = QPushButton("Select folder to save file in", parent=window)
select_file.move(150, 205)
select_file.clicked.connect(getPath)
submit = QPushButton("Submit", parent=window)
# 160
submit.move(155, 250)
submit.clicked.connect(doThings)
success_indicator = QLabel(parent=window)
success_indicator.move(10, 310)
window.show()
sys.exit(app.exec())