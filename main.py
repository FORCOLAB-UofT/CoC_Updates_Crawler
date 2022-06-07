from pydriller import Repository
import os
import pandas as pd
import subprocess
# import os
import json
import subprocess
import time
from datetime import datetime as dt


def save_json(update_di):
    print('called')
    start = dt.now()
    jstring = json.dumps(update_di, indent=4, sort_keys=True, default=str)

    # with open("../data/repo_updates.json", "w+") as fp:
    with open("../data/repo_updates.json", "a") as fp:
        fp.write(jstring)
        fp.close()
    print("saving alone took: ", dt.now()-start, ' seconds')
       # update_df.to_csv('../data/GiHub_repo_with_coc_updates.csv')


def print_fields():
    pass
    # print(i.modified_files[0].old_path)
    # print(i.modified_files[0].new_path)
    # print(i.modified_files[0].filename)
    # print(i.modified_files[0].added_lines)
    #
    # print(i.modified_files[0].complexity)
    # print(i.modified_files[0].deleted_lines)
    # print(i.modified_files[0].diff_parsed)
    # print(i.modified_files[0].language_supported)
    #
    # print(i.modified_files[0].nloc)
    # print(i.modified_files[0].token_count)
    #
    # print(i.hash) # str
    # print(i.lines) # int
    # for j in i.modified_files:
    #     print(j.filename) # str
    # print(i.project_name) # str
    # print(i.msg) # str
    # print(i.project_path) #str
    # print(i.parents) #list
    # print(i.insertions) # int
    # print(i.deletions) # itn
    # print(i.in_main_branch) #bool
    # print(i.files) # int
    # print(i.dmm_unit_size) # None
    # print(i.dmm_unit_interfacing)# None
    # print(i.dmm_unit_complexity)# None
    # print(i.author_date)  # str
    # print(i.author.name) # name/email
    # print(i.author_timezone) # int
    # print(i.merge) # bool
    # print(i.branches)# dictionary
    # print(i.committer_date) # str
    # print(i.committer.email) # name/email
    # print(i.committer_timezone) # int


if __name__ == "__main__":
    #
    # start = dt.now()
    # # Repository('https://github.com/tensorflow/tensorflow', clone_repo_to=True)
    # print()
    # print("driller cloning took: ", dt.now()-start)

    repos = pd.read_csv('data/GitHub_sorted_issue_commit_all.csv', nrows=5)['repository']
    # for repo in repos:

    # update_df = pd.DataFrame({key: [] for key in ['hash', 'lines']})
    repos = ['tensorflow/tensorflow']

    for repo in repos:
    # getting the repositroy

        start = dt.now()
        os.system('git clone "https://github.com/'+repo+'"')
        print("cloning along took: ", dt.now()-start, ' seconds')

        os.chdir(repo.split('/')[1])

        # using grep
        # start = dt.now()

        # checking file title with grep
        os.system("git ls-tree -r HEAD | grep -i -E 'code\s*_?-?of\s*_?-?conduct' > ../out.txt")
        f = open("../out.txt", "r")
        # print("saving to txt and opening it took: ", dt.now()-start, " seconds")

        paths = list()
        for line in f.readlines():
            print(line)
            print(type(line))
            res = line.replace('\t',' ').replace('\n','').split(' ')
            paths.append(' '.join(res[3:]))

        print(paths)
        # checking file content with below command
        os.system('grep -i -E "code\s*_?-?of\s*_?-?conduct" * > ../out.txt')
        f = open("../out.txt", "r")

        cont_res = f.read()

        # print(cont_res)
        # cont_res = cont
        # assumption for string matching:
        #   1. that the file path will end in: ".file_extension:"

        start = dt.now()
        for path in paths:
            print(path)
            for r in Repository('.', filepath=path).traverse_commits():

                update_di = {'repository': repo, 'hash': r.hash, 'lines':r.lines, 'project_name':r.project_name,\
                              'msg':r.msg, 'project_path':r.project_path, 'parents':r.parents, 'insertions':r.insertions,\
                              'deletions': r.deletions, 'in_main_branch':r.in_main_branch, 'files':r.files, 'author_date':r.author_date,\
                              'author_timezone': r.author_timezone, 'author_name':r.author.name, 'author_email':r.author.email,\
                              'committer_date': r.committer_date, 'committer_timezone':r.committer_timezone,\
                              'committer_email': r.committer.email, 'committer_name':r.committer.name, 'merge':r.merge,\
                              'branches': r.branches}

                files = list()

                for i in range(len(r.modified_files)):

                    file_di = {'old_path': r.modified_files[i].old_path, \
                            'new_path': r.modified_files[i].new_path, 'filename': r.modified_files[i].filename, \
                            'added_lines': r.modified_files[i].added_lines, 'complexity': r.modified_files[i].complexity, \
                            'deleted_lines': r.modified_files[i].deleted_lines, 'diff_parsed': r.modified_files[i].diff_parsed, \
                            'language_supported': r.modified_files[i].language_supported, 'nloc': r.modified_files[i].nloc, \
                            'token_count': r.modified_files[i].token_count}

                    files.append(file_di)

                update_di['file'] = files
                save_json(update_di)

        print("one repo data field extraction and saving took: ", dt.now()-start, " seconds")

        os.chdir("..")
        os.system('rm -rf '+repo.split('/')[1])


