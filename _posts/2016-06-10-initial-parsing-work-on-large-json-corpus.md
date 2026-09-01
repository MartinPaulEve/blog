---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/06/10/initial-parsing-work-on-large-json-corpus
date: 2016-06-10
doi: https://doi.org/10.59348/7g3wf-b5f60
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Initial parsing work on large JSON corpus
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbe6bos2h"
categories:
- Programming
- Digital Humanities
---

Yesterday, I wrote of a challenge that I faced in <a href="https://www.martineve.com/2016/06/09/identifying-26gb-of-json-novel-data/">working out which texts in a corpus have decent OCR and, then, which texts they actually are</a>. This morning, I put together a small script that has a first go at this. I enclose this below for anybody who is interested.

The basic steps are:

1. Read input from CSV and build a list of titles and identifiers (stripping all punctuation from titles and limiting it to 5 words)
2. Sequentially read in the JSON files from disk, performing the same stripping transform above on the first ten elements in the dictionary.
3. See if the transformed title is in the transformed first ten elements of the JSON file.

This currently yields me about 15 good titles out of every 1,000 JSON files. That said, these JSON files are not all in English. And many of them have bad OCR.

In any case, I'll continue to refine this and expand the filters as safely as I can.

    # coding=UTF-8
    import csv
    import re
    import glob
    import json


    def load_csv():
        titles = {}

        # load the CSV file of titles
        with open('/home/martin/Mounts/THREETB/Corpus/book-list.csv', 'rb') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',', quotechar='"')

            # iterate over the CSV
            for row in csv_file:
                # extract a potential title and substitute out all punctuation
                titles[row[0]] = re.sub('[\.\?\(\)\]\[,;:\'!\*!“]', '', re.sub('\[.+?\]', '', row[7])).lower().replace('  ', ' ').strip()

                # remove any titles here that are either blank or less than three words long or less than 6 chars total
                if titles[row[0]] == '' or len(titles[row[0]].split(' ')) < 3 or len(titles[row[0]]) < 6:
                    del titles[row[0]]

                if row[0] in titles:
                    try:
                        # shorten title to first five words
                        titles[row[0]] = ' '.join(titles[row[0]].split(' ')[0:5])
                    except IndexError:
                        # title was short
                        pass

        return titles


    def parse_json(folder, titles):
        directory_to_parse = '/home/martin/Mounts/THREETB/Corpus/json/{0}'.format(folder)
        jsons = glob.glob('{0}/*.json'.format(directory_to_parse))
        ret = {}
        file_counter = 0

        for json_file in jsons:
            with open(json_file, 'rb') as json_file_handle:

                file_counter += 1
                if file_counter == 1000:
                    print "Processed 1,000 JSON files"
                    file_counter = 0

                loaded_json = json.load(json_file_handle)

                # check the first eight entries of the JSON
                try:
                    for x in range(0, 10):
                        subbed_text = re.sub('[\.\?\(\)\]\[,;:\'!\*!“]', '', re.sub('\[.+?\]', '', str(loaded_json[x]))).lower().replace('  ', ' ').strip()
                        should_break = False

                        for key, title in titles.iteritems():
                            if title in subbed_text:
                                print '[{0}] {1}: {2}'.format(key, title, json_file)
                                ret[key] = json_file
                                should_break = True

                                # remove the key to avoid duplicates
                                del titles[key]
                                break

                        if should_break:
                            break
                except IndexError:
                    # if we arrive here it's a short JSON
                    pass
                except:
                    pass

        return ret

    if __name__ == '__main__':
        titles = load_csv()

        for folder_name in range(0, 25):
            parse_json(str(folder_name).zfill(4), titles)