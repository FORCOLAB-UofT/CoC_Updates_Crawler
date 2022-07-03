from this import d
from pydriller import Repository
import os
import pandas as pd
import subprocess
# import os
import json
import subprocess
import time
import regex as re
import datetime as dt
import CoC_update_times.update_after_creation as updates
import CoC_update_times.label_commit_or_issue as label
import zipfile
import matplotlib.pyplot as plt

# import matplotlib as matplotlib



num = 7

def save_xlsx(update_df):

    try:
        cur_df = pd.read_excel('/data/Code_of_Conduct/repo_updates'+str(num)+'.xlsx')
        cont_df = pd.concat([cur_df, update_df], ignore_index = True)
        cont_df.to_excel('/data/Code_of_Conduct/repo_updates'+str(num)+'.xlsx')
    except FileNotFoundError:
        update_df.to_excel('/data/Code_of_Conduct/repo_updates'+str(num)+'.xlsx')
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
    start = dt.datetime.now()
    jstring = json.dumps(update_di, indent=4, sort_keys=True, default=str)

    # with open("../_data_/tensorflow_repo_updates.json", "w+") as fp:
    with open("_data_/repo_updates.json", "a") as fp:
        fp.write(jstring)
        fp.close()
    print("saving alone took: ", dt.datetime.now()-start, ' seconds')
       # update_df.to_csv('../_data_/GiHub_repo_with_coc_updates.csv')


def extract():
    
    repos = pd.read_csv('/autofs/fs1.ece/fs1.eecg.shuruizgrp/liming76/CoC_Updates_Crawler_new/_data_/extracted_coc_issue_commits_'+str(num)+'.csv')['repository']
    # repos = ['ming-afk/Octlearner']

    repo_df = pd.DataFrame({key: [] for key in ['repository', 'project_name', 'coc_location', 'msg', 'hash', 'lines', 'file', 'project_path', 'insertions',\
                              'deletions', 'in_main_branch', 'files', 'path', 'author_date',\
                              'author_timezone', 'author_name', 'author_email',\
                              'committer_date', 'committer_timezone', 'committer_name',\
                              'committer_email', 'merge', 'branches']})

    # # wait for another repo before saving
    save_wait = 1
    repo_count = 0

    for repo in repos:
    # getting the repositroy

        repo_count+=1
        print("On the ", repo_count, 'th repo')

        os.chdir('/data/Code_of_Conduct')

        start = dt.datetime.now()
        try:
            os.system('git clone "https://github.com/'+repo+'"')
            print("cloning along took: ", dt.datetime.now()-start, ' seconds')
        except FileNotFoundError:
            with open("notFound.txt", "+w") as text_file:
                text_file.write("not found error repo: %s" % repo)
            continue

        # change dir to name part of repo slug
        repo_path = ''
        try:
            repo_path = repo.split('/')[1]
            os.chdir(repo_path)
        except FileNotFoundError:
            try:
                repo_path = repo.split('/')[1]+'.git'
                os.chdir(repo_path)
            except FileNotFoundError:
                repo_path = repo.split('/')[1].replace('.git','')
                os.chdir(repo_path)
            raise


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

        # # if too many paths are there, just skip this repo as it will take too long
        # # the repos that are skipped will be collected when all others are crawled
        # if len(paths) > 15:
        #     continue

    # cont_res = cont
        # assumption for string matching:
        #   1. that the file path will end in: ".file_extension:"

        start = dt.datetime.now()

        for path in paths:
            # if (dt.datetime.now()-start) > dt.timedelta(hours=0.5):
            #     break
            print('current file path is: ', path)
            keyword_match = re.findall('code\s*_?-?of\s*_?-?conduct', path.lower())

            location = 'title'
            if not keyword_match:
                location = 'content'

                # if keyword in content, we assume only the lines containing the keyword are useful
                # and we only need commits on these specific lines
                target_commits = updates.find_target_commits(path)

            path_df = pd.DataFrame({key: [] for key in ['repository', 'project_name', 'coc_location', 'msg', 'hash', 'lines', 'file', 'project_path', 'insertions',\
                              'deletions', 'in_main_branch', 'files', 'path', 'author_date',\
                              'author_timezone', 'author_name', 'author_email',\
                              'committer_date', 'committer_timezone', 'committer_name',\
                              'committer_email', 'merge', 'branches']})

            for r in Repository('.', filepath=path).traverse_commits():
                #note that those files having CoC in both title and content will have been
                # marked as 'title', but that dn affect as we only wawnt to isolate those
                # only having CoC keywords in the content

                update_di = {'repository': repo, 'hash': r.hash, 'lines':r.lines, 'project_name':r.project_name,\
                              'msg':r.msg, 'project_path': r.project_path, 'path': path, 'insertions':r.insertions, 'coc_location':location, \
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
                                'deleted_lines': ifile.deleted_lines, 'diff':ifile.diff, 'diff_parsed': ifile.diff_parsed, \
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
                    print()
                    print('valerror!!!!')
                    print()
                    continue

                # cur_df = pd.DataFrame.from_dict(update_di, orient='index')
                # cur_df = cur_df.transpose()
                # print(cur_df)

                # append to dataframe once per commit
                path_df = pd.concat([path_df, cur_df])

            ## check here: filter out unneded paths
            if location == 'content':
                path_df = path_df[path_df['hash'].isin(target_commits)]

            repo_df = pd.concat([path_df, repo_df])

        print("one repo _data_ field extraction and saving took: ", dt.datetime.now()-start, " seconds")

        os.chdir("..") 
        os.system('rm -rf '+repo_path)

        save_wait -= 1
        if not save_wait:
            save_wait = 1
            print('saving the last two repos ... ...')
            save_xlsx(repo_df)
            repo_df = pd.DataFrame({key: [] for key in
                                      ['repository', 'project_name', 'msg', 'hash', 'lines', 'file', 'project_path',
                                       'insertions', 'coc_location', 'path', \
                                       'deletions', 'in_main_branch', 'files', 'author_date', \
                                       'author_timezone', 'author_name', 'author_email', \
                                       'committer_date', 'committer_timezone', 'committer_name', \
                                       'committer_email', 'merge', 'branches']})

        # clear paths in the out.txt file
        open("out"+str(num)+".txt", 'w').close()

        # *** one repo crawling ends *** #

    print('all repos finished, saving .. ...')
    save_xlsx(repo_df)


def combine():
    '''
    combining currently have _data_ on updates: ==============
    '''
    # decided to use datas in the backup folder
    os.chdir('/data/Code_of_Conduct/backup')

    df = pd.DataFrame()
    filebase= 'repo_updates'

    for f in range(1,51,1):
        path = filebase+str(f)+'.xlsx'
        print(path)
        try:
            cur_df = pd.read_excel(path)
            cur_df = cur_df[['repository', 'project_name', 'msg', 'hash', 'lines', 'file', 'project_path',
                                       'insertions', 'coc_location', 'path', \
                                       'deletions', 'in_main_branch', 'files', 'author_date', \
                                       'author_timezone', 'author_name', 'author_email', \
                                       'committer_date', 'committer_timezone', 'committer_name', \
                                       'committer_email', 'merge', 'branches' ]]
            df = pd.concat([df, cur_df])
        except ValueError:
            print('error file is ', f)
            continue

    # df = pd.concat(map(pd.read_excel, filepaths))

    df.to_csv('/data/Code_of_Conduct/repos_updates_June_29.csv')



def convert_datetime(string):
    string = string[:18]
    return dt.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


def plot_difference_distribution(df):
    '''
    takes a dataframe, then plot the OVERALL histogram distribution of difference in time between any two CoC commits
    on one repository, then sums the number for every repository  
    '''
    diff = list()
    for name, group in df.groupby('repository'):
        print('current repo is: ')
        print(name)

        times = list(group['author_date'])
        times.sort(reverse = True)
        for i in range(len(times) - 1):
            diff.append(convert_datetime(times[i])-convert_datetime(times[i+1]))

    plt.hist(dif, bins = 20)
    plt.show()



def plot_commits_count():


    '''
    giving a plot of the number of CoC updates versus the number of repositories


    At the same time, it gives a data table of the number of coc updates of all repositories
    '''

    df = pd.read_csv(
        '/data/Code_of_Conduct/repos_updates_June_29.csv'
    )


    # we count on distinct commits of all repos
    df = df.drop_duplicates('hash')

    # plotting based on whether the commit is on content or title

    # content_df = df[df['coc_location'] == 'content']
    # title_df = df[df['coc_location'] == 'title']

    # cont_result = content_df.groupby(['repository']).size()
    # title_result = title_df.groupby(['repository']).size()

    counter_df = pd.DataFrame({key:[] for key in list(['repository','count', 'link'])})
    
    for name, group in df.groupby('repository'):

        link = 'https://github.com/' + name

        count = len(group)
        diction = pd.DataFrame({'repository':[name], 'count':[count],'link':[link]})
        counter_df = pd.concat([counter_df, diction], ignore_index=True)

    counter_df = counter_df.sort_values('count')
    counter_df = counter_df.drop_duplicates('repository')
    counter_df.to_csv('_data_/repos_with_CoC_updates_count.csv')




    # result = df.groupby(['repository']).size().values

    
    # ma = max(list(result))
    # count = [0] * ma
    # for i in list(result):
    #     count[i-1] += 1
    #
    # # ax = plt.subplots()

    #
    # # plot the result

    # # sns.barplot(x=result.index, y=result.values)

    # # print('the indexes (hori) are: ', cont_result.index)
    # # print('the values (vert) are: ', cont_result.values)
    # #
    # # ma_cont = max(list(cont_result.values))
    # # count_cont = [0] * ma_cont
    # # for i in list(cont_result.values):
    # #     count_cont[i-1] += 1
    # #
    # # ma_title = max(list(title_result.values))
    # # count_title = [0] * ma_title
    # # for i in list(title_result.values):
    # #     count_title[i-1] += 1
    # #
    # # x_len = max([ma_title, ma_cont])
    # #
    # # if x_len == ma_title:
    # #     count_cont += [0] * (x_len - len(count_cont))
    # # elif x_len == ma_cont:
    # #     count_title += [0] * (x_len - len(count_title))
    #
    # print(count)
    #
    # plt.hist(count, bins=120)
    # # ax = sns.barplot(x=[str(i) for i in range(1, ma+1, 1)], y=count)

    # # sns.histplot(data=count, x='Number of CoC commits', bins=20)

    # # ax.set(xlabel='Number of CoC commits', ylabel='Number of Repositories')
    #
    # plt.show()


def get_earliest_latest_CoC_commits():

    def compare_date_string(date_strings):
        earliest = '4000-00-00 00:00:00+00:00'
        latest = '0000-00-00 00:00:00+00:00'

        for i in date_strings:
            if i <earliest:
                earliest = i
            if i > latest:
                latest = i
        return  earliest, latest

    df = pd.read_csv('/data/Code_of_Conduct/repos_updates_June_29.csv')

    res_df = pd.DataFrame({key:[] for key in ['repository', 'earliest_commit', 'latest_commit']})
    repo = list()
    earliest = list()
    latest = list()

    for name, group in df.groupby('repository'):
        e,l = compare_date_string(list(group['author_date']))
        earliest.append(e)
        latest.append(l)
        repo.append(name)
    
    res_df['repository'] = repo
    res_df['earliest_commit'] = earliest
    res_df['latest_commit'] = latest

    def get_commit_timespan(com1, com2):

        com1=  com1[:18]
        com2 = com2[:18]

        from datetime import datetime
        FMT = '%Y-%m-%d %H:%M:%S'

        return datetime.strptime(com1, FMT) - datetime.strptime(com2, FMT)

    res_df['commit_span'] = res_df.apply(lambda x: get_commit_timespan( x.latest_commit, x.earliest_commit), axis = 1)
    
    res_df = res_df.sort_values('commit_span')

    res_df.to_csv('_data_/age_of_CoC_update.csv')



def analyze():
    att = pd.read_csv('_data_/newest_attempt_on_CoC_updates.csv')
    print('number of commits: ', len(att))

    no_dup = att.drop_duplicates('repository', keep='first')
    print('number of repos: ', len(no_dup))


def divide():
    # DIVIDING DATA
    repos = pd.read_csv('_data_/extracted_coc_issue_commits.csv')
    print(len(repos))
    # partition dataset into 50 parts, each is 515.64 == 516 repos
    for i in (range(1,51,1)):
        start = 516*(i-1)
        end = 516 * i
        print(start)
        print(end)
        print()
        print()
        if end >25284:
            repo = repos[start:]
        else:
            repo = repos[start:end]
        repo.to_csv('new_data_/extracted_coc_issue_commits_'+str(i)+'.csv')


if __name__ == "__main__":

    # SAMPLING DATA
    # ext = pd.read_csv('_data_/extracted_coc_issue_commits.csv')
    # li = [3, 300, 3000, 20000, 2500, 2600, 1900, 45, 260, 10000, 10567, 345, 30, 3590, 10496, 10294, 5329, 12053, 4000, 21400]
    #
    # sam = ext.iloc[li]
    # print(len(sam))
    # sam.to_csv('_data_/lang_filtered_sampled_extracted_coc_issue_commits.csv')
    #

    # pd.read_excel('finished_repos/first_6_parts_attempt_1.xlsx')
    #
  
    # divide()
    # label.label_commit_or_issue()
    # extract()
    # combine()
    # analyze()
    df = pd.read_csv('_data_/CoC related file updates.csv', nrows=50)
    plot_difference_distribution(df)
    # get_earliest_latest_CoC_commits()

    # updates.filter_repo_without_updates()
    # print(len(pd.read_csv('_data_/CoC_text_updates_from_newest_attempts_file.csv').drop_duplicates('repository')))
    # updates.get_no_way_to_reckon_actual_coc_repos()

    # df = pd.read_csv('_data_/newest_attempt_on_CoC_updates.csv')
    #
    # updates.get_coc_path_commitSha_repoName(df)

    # getting the creation time
    # date_df = pd.read_csv('_data_/age_of_CoC_update.csv')
    # res_df = pd.read_csv('_data_/repos_with_CoC_updates_count.csv')
    
    # res_df = res_df['earliest_commit_x', 'repository', 'count', 'link']
    # all_ = pd.merge(res_dfs, date_df, how = ['outer','earliest_commit'], on='repository')
    # print(all_.columns)
    # all_ = all_[['repository', 'count', 'link', 'earliest_commit_x']]

