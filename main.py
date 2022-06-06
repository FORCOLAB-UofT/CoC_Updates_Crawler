from pydriller import Repository
import os
import pandas as pd
import subprocess
# import os
import subprocess
try:
    os.environ.pop('PYTHONIOENCODING')
except KeyError:
    pass

if __name__ == "__main__":

    repos = pd.read_csv('data/GitHub_sorted_issue_commit_all.csv')['repository']
    # for repo in repos:
    # os.system('gclonecd() {   git clone "$1" && cd "$(basename "$1" .git)"; }')
    # os.system("declare -f")
    os.system('git clone "https://github.com/sympy/sympy"')
    os.chdir('sympy')
    f = open("..output.txt", "r")
    print(f.read())
    res = f.read()

    res = res.split(' ')[2:]
    #
    # for i in Repository('Octlearner', filepath='code of conduct.md').traverse_commits():
    #     # print('in here')
    #     print(i.hash) # str
    #     print(i.lines) # int
    #     for j in i.modified_files:
    #         print(j.filename) # str
    #     print(i.project_name) # str
    #     print(i.msg) # str
    #     print(i.project_path) #str
    #     print(i.parents) #list
    #     print(i.insertions) # int
    #     print(i.deletions) # itn
    #     print(i.in_main_branch) #bool
    #     print(i.files) # int
    #     print(i.dmm_unit_size) # None
    #     print(i.dmm_unit_interfacing)# None
    #     print(i.dmm_unit_complexity)# None
    #     print(i.committer_timezone) # int
    #     print(i.author_date)  # str
    #     print(i.author.name) # name/email
    #     print(i.merge) # bool
    #     print(i.branches)# dictionary
    #     print(i.committer_date) # str
    #     print(i.author_timezone) # int
    #     print(i.committer.email) # name/email