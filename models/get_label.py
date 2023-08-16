import os
import csv

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

def calculate_score(list):
    score = 0
    for i in range(0, len(list)):
        score += int(list[i][1])
    return score

#define finallabel from score
def define_label(score):
    if score > 0:
        return 'Tích cực'
    elif score < 0 and score > -10:
        return 'tiêu cực'
    elif score == 0:
        return 'không xác định'
    else:
        return 'nghiêm trọng'
    
#get all label in script
def get_label(script):
    checkList = []
    path = os.path.join(CURRENT_PATH, "data/badword.csv")
    with open(path) as f:
        reader = csv.reader(f)
        idword = [row for row in reader]
    for i in range(0, len(idword)):
        if script.upper().find(str(idword[i][0])) >= 0:
            checkList.append(idword[i])
    return define_label(calculate_score(checkList))