from pydriller import Repository
import os
import pandas as pd
import subprocess
# import os
import json
import subprocess
import time
from datetime import datetime as dt

num = 9

def save_xlsx(update_df):
    try:
        cur_df = pd.read_excel('_data_/repo_updates'+str(num)+'.xlsx')
        cont_df = pd.concat([cur_df, update_df], ignore_index = True)
        cont_df.to_excel('_data_/repo_updates'+str(num)+'.xlsx')
    except FileNotFoundError:
        update_df.to_excel('_data_/repo_updates'+str(num)+'.xlsx')
    return


def save_csv(update_df):
    try:
        cur_df = pd.read_csv('_data_/repo_updates.csv')
        cont_df = pd.concat([cur_df, update_df], ignore_index = True)
        cont_df.to_csv('_data_/repo_updates.csv')
    except pd.errors.EmptyDataError:
        update_df.to_csv('_data_/repo_updates.csv')
    return

def save_json(update_di):
    # print('called')
    start = dt.now()
    jstring = json.dumps(update_di, indent=4, sort_keys=True, default=str)

    # with open("../_data_/tensorflow_repo_updates.json", "w+") as fp:
    with open("_data_/repo_updates.json", "a") as fp:
        fp.write(jstring)
        fp.close()
    print("saving alone took: ", dt.now()-start, ' seconds')
       # update_df.to_csv('../_data_/GiHub_repo_with_coc_updates.csv')

def extract():

    repos = pd.read_csv('_data_/extracted_coc_issue_commits_'+str(num)+'.csv')['repository']


    update_df = pd.DataFrame({key: [] for key in ['repository', 'project_name', 'msg', 'hash', 'lines', 'file', 'project_path', 'insertions',\
                              'deletions', 'in_main_branch', 'files', 'author_date',\
                              'author_timezone', 'author_name', 'author_email',\
                              'committer_date', 'committer_timezone', 'committer_name',\
                              'committer_email', 'merge', 'branches']})

    # # wait for another repo before saving
    save_wait = 2
    repo_count = 0

    for repo in repos:
    # getting the repositroy
        repo_count+=1
        print("On the ", repo_count, 'th repo')

        start = dt.now()
        try:
            os.system('git clone "https://github.com/'+repo+'"')
            print("cloning along took: ", dt.now()-start, ' seconds')
        except FileNotFoundError:
            with open("../notFound.txt", "+w") as text_file:
                text_file.write("not found error repo: %s" % repo)
            continue

        # change dir to name part of repo slug
        try:
            os.chdir(repo.split('/')[1])
        except FileNotFoundError:
            os.chdir(repo.split('/')[1]+'.git')
        except FileNotFoundError:
            os.chdir(repo.split('/')[1].replace('.git',''))

        # using grep
        # start = dt.now()

        # checking file title with grep
        os.system("git ls-tree -r HEAD | grep -i -E 'code\s*_?-?of\s*_?-?conduct' > ../out"+str(num)+".txt")
        f = open("../out"+str(num)+".txt", "r")
        # print("saving to txt and opening it took: ", dt.now()-start, " seconds")

        pt = list()
        for line in f.readlines():
            # print(line)
            # print(type(line))
            res = line.replace('\t',' ').replace('\n','').split(' ')
            pt.append(' '.join(res[3:]))

        # checking file content with below command
        # "git grep -l "code of conduct""
        os.system('git grep -l -i -E "code\s*_?-?of\s*_?-?conduct"> ../out'+str(num)+'.txt')
        f = open("../out"+str(num)+".txt", "r")

        cont_res = f.readlines()
        for i in cont_res:
            pt.append(i.replace('\t', ' ').replace('\n',''))
        # print(paths)

        # eliminating duplicates in file paths
        paths = []
        [paths.append(x) for x in pt if x not in paths]

    # cont_res = cont
        # assumption for string matching:
        #   1. that the file path will end in: ".file_extension:"

        start = dt.now()
        for path in paths:
            print('current file path is: ', path)
            for r in Repository('.', filepath=path).traverse_commits():

                update_di = {'repository': repo, 'hash': r.hash, 'lines':r.lines, 'project_name':r.project_name,\
                              'msg':r.msg, 'project_path': r.project_path, 'insertions':r.insertions,\
                              'deletions': r.deletions, 'in_main_branch':r.in_main_branch, 'files':r.files, 'author_date':str(r.author_date),\
                              'author_timezone': r.author_timezone, 'author_name':r.author.name, 'author_email':r.author.email,\
                              'committer_date': str(r.committer_date), 'committer_timezone':r.committer_timezone,\
                              'committer_email': r.committer.email, 'committer_name':r.committer.name, 'merge':r.merge,\
                              'branches': str(r.branches).replace('{','').replace('}','')}

                files = list()

                try:
                    for i in range(len(r.modified_files)):
                        ifile = r.modified_files[i]

                        file_di = {'old_path': ifile.old_path, 'complexity':ifile.complexity,\
                                'new_path': ifile.new_path, 'filename': ifile.filename, \
                                'added_lines': ifile.added_lines, \
                                'deleted_lines': ifile.deleted_lines, 'diff_parsed': ifile.diff_parsed, \
                                'language_supported': ifile.language_supported, 'nloc': ifile.nloc, \
                                'token_count': ifile.token_count, 'change_type': ifile.change_type.name}
                        files.append(file_di)


                    # this makes sure that files length is one
                    emp = []
                    emp.append(files)
                except AttributeError:
                    emp = None
                update_di['file'] = emp
                # print('length is ', len(update_di['file']))

                for key, val in update_di.items():
                    if val is None:
                        update_di[key] = "None"

                # print(type(update_di))
                # for key, val in update_di.items():
                #     print('type of each dict val is: ', type(val))
                #     print('the key is ', key)

                try:
                    cur_df = pd.DataFrame(update_di)
                except ValueError:
                    continue

                # cur_df = pd.DataFrame.from_dict(update_di, orient='index')
                # cur_df = cur_df.transpose()
                # print(cur_df)

                update_df = pd.concat([update_df, cur_df])

        print("one repo _data_ field extraction and saving took: ", dt.now()-start, " seconds")

        os.chdir("..")
        os.system('rm -rf '+repo.split('/')[1])

        save_wait -= 1
        if not save_wait:
            save_wait = 2
            print('saving the last two repos ... ...')
            save_xlsx(update_df)
            update_df = pd.DataFrame({key: [] for key in
                                      ['repository', 'project_name', 'msg', 'hash', 'lines', 'file', 'project_path',
                                       'insertions', \
                                       'deletions', 'in_main_branch', 'files', 'author_date', \
                                       'author_timezone', 'author_name', 'author_email', \
                                       'committer_date', 'committer_timezone', 'committer_name', \
                                       'committer_email', 'merge', 'branches']})
        # clear paths in the out.txt file
        open('out'+str(num)+'.txt', 'w').close()
    # save_json({'_data_': js_li})
    print('all repos finished, saving .. ...')
    save_xlsx(update_df)


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

def combine():
    '''
    combining currently have _data_ on updates: ==============
    '''
    os.chdir('finished_repos')

    filepaths = [f for f in os.listdir(".") if f.endswith('.xlsx')]
    print(filepaths)

    df = pd.DataFrame()
    for f in filepaths:
        try:
            df = pd.concat([df, pd.read_excel(f)])
        except ValueError:
            print('error file is ', f)
            continue
    # df = pd.concat(map(pd.read_excel, filepaths))

    df.to_csv('../_data_/newest_attempt_on_CoC_updates.csv')


def analyze():
    att = pd.read_csv('_data_/newest_attempt_on_CoC_updates.csv')
    print('number of commits: ', len(att))

    no_dup = att.drop_duplicates('repository', keep='first')
    print('number of repos: ', len(no_dup))




if __name__ == "__main__":

    # SAMPLING DATA
    # ext = pd.read_csv('_data_/extracted_coc_issue_commits.csv')
    # li = [3, 300, 3000, 20000, 2500, 2600, 1900, 45, 260, 10000, 10567, 345, 30, 3590, 10496, 10294, 5329, 12053, 4000, 21400]
    #
    # sam = ext.iloc[li]
    # print(len(sam))
    # sam.to_csv('_data_/lang_filtered_sampled_extracted_coc_issue_commits.csv')
    #

    # DIVIDING DATA
    # repos = pd.read_csv('_data_/extracted_coc_issue_commits.csv')
    # # partition dataset into 50 parts, each is 515.64 == 516 repos
    # for i in (range(1,5,1)):
    #     start = 104*(i-1)
    #     end = 104 * i
    #     print(start)
    #     print(end)
    #     print()
    #     print()
    #     if end >416:
    #         repo = repos[start:]
    #     else:
    #         repo = repos[start:end]
    #     repo.to_csv('_data_/deep_partition/extracted_coc_issue_commits_1_'+str(i)+'.csv')

    pd.read_excel('finished_repos/first_6_parts_attempt_1.xlsx')

    extract()
    # combine()
    # analyze()





