## Code Snippet for Software Developer Interview at Siemens


This is a Python3 code for the first round of interviews with Siemens. This code crawls my university's websites starting from the home page (https://ontariotechu.ca/), in a BFS style and saves the graph of webpages discovered as a gefx file (https://gexf.net/). 


### Getting Started
- All dependencies can be installed with `pip install -r requirements.txt`.

- Following that, simply run `python3.9 crawler.py` to commence the crawling.

You might want to reduce the number of websites to be discovered by changing the `MAX_URLs` variable on line 21 of the `crawler.py` file. This is because UOIT contains millions of webpages resulting in the crawler running for days on end.



-- Paul Louis (last updated: 06/01/23.)

