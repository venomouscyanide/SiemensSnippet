"""
Description : Crawl the web for UOIT webpages in BFS style starting from UOIT home page and save as a GEXF file
Author      : Paul Louis <paul.louis@ontariotechu.net>
Usage       : python3.9 web_crawler.py
"""

import pickle  # I pickle the bfs sequence list to interact with later (if needed)
import random
import time
from queue import SimpleQueue  # A queue to help in BFS traversal. A list works just as well
from typing import Set, List  # typing for readability of the code
from urllib.parse import urljoin, urlparse  # helps modify urls/parse urls
from urllib.request import urlopen  # helps make requests to get HTML data

import networkx as nx  # helps in creating a directed graph
from bs4 import BeautifulSoup  # helps parse webpages
from networkx import write_gexf  # write traversed graph as a GEXF file
from scrapy.linkextractors import IGNORED_EXTENSIONS  # common extensions to ignore
import math  # helps set the max numbers of nodes to be crawled to infinity (no limit)

MAX_URLs = math.inf  # set this to a smaller value for crawler less webpages


class UOITCrawler:
    def crawl(self, root: str) -> nx.DiGraph:
        """
        Crawl all UOIT/Ontariotechu webpages starting from the home page and save the BFS info graph formed as GEXF file
        :param root: Home page of UOIT
        :return: Directed graph formed after the traversal forming the info network
        """
        graph = nx.DiGraph()  # Directed graph showing the traversal
        queue = SimpleQueue()  # A Queue to help with the BFS style traversal
        seen = set()

        queue.put(root)
        bfs_seq = []

        seen.add(root)  # Mark the root as seen
        self._print_log(root, seen, bfs_seq)

        while self._continue_crawl(queue, seen):
            focus_node = queue.get()  # current focus node whose neighbors are to be explored
            bfs_seq.append(focus_node)

            self._print_log(focus_node, seen, bfs_seq)

            self._random_sleep()  # randomly sleep to avoid being seen as a crawler

            try:  # There are multiple errors which you can get, shows the exception so that it can be better handled
                with urlopen(focus_node) as website_html:
                    soup = BeautifulSoup(website_html, 'html.parser')  # parse the HTML doc

                    for link in soup.find_all('a'):  # find all <a> tags which contain the links
                        neigh_node = link.get('href')  # extract out the URLs from the <a> tags

                        if not neigh_node:  # empty link? move on
                            continue

                        if self._incorrect_extension(neigh_node):  # ignore PDFs, JPEGS etc.
                            continue

                        if neigh_node.startswith('/'):  # relative links need to be made absolute
                            neigh_node = urljoin(focus_node, neigh_node)

                        if self._uoit_url(neigh_node):  # a uoit webpage? update graph, add to queue and mark as seen
                            self._queue_helper(focus_node, neigh_node, queue, seen, graph)

                        if len(seen) % 5000 == 0:  # save the graph every 5000 nodes in case the code breaks
                            write_gexf(graph, f'interim_{len(seen)}_len_graph.gexf')

            except Exception as e:
                print(f"Failed: {focus_node} with exception: {e}")

        write_gexf(graph, f'final_{len(seen)}_len_graph.gexf')  # final graph containing ALL nodes

        print(f"Total number of nodes traversed: {len(bfs_seq)}")  # sanity check

        with open('bfs_seq.pkl', 'wb') as f:  # pickle it to interact with later
            pickle.dump(bfs_seq, f)

        return graph

    def _continue_crawl(self, queue: SimpleQueue, seen: Set[str]) -> bool:
        """
        Choose whether to exit the crawl
        The crawl exits either when:
                                    -> The queue is empty
                                    -> a maximum number of URLs have been traversed
        :param queue: Queue object that helps with the BFS traversal
        :param seen: Set of already traversed nodes
        :return: boolean indicating whether to exit or continue with the crawl execution
        """
        return not queue.empty() and len(seen) < MAX_URLs

    def _random_sleep(self) -> None:
        """
        Randomly sleep to not look like a bot to the server
        :return: None
        """
        sleep_time = random.randint(0, 3)  # choose to sleep for [0, 3] seconds
        print(f'Random sleep of {sleep_time} seconds')
        time.sleep(sleep_time)  # sleep for sleep_time seconds

    def _incorrect_extension(self, neigh_node: str) -> bool:
        """
        Ignore webpages that host a Picture/PDF or other artifacts/objects.
        :return: bool indicating whether to ignore the link
        """
        extension = urlparse(neigh_node).path.split('.')[-1].lower()  # get the extension of the website
        extensions_to_ignore = IGNORED_EXTENSIONS
        return extension in extensions_to_ignore

    def _uoit_url(self, neigh_node: str) -> bool:
        """
        Make sure the url is ontariotechu.ca or uoit.ca domains
        :param neigh_node: current node being explored from the root
        :return: bool indicating whether the link is a UOIT webpage
        """
        parsed_url = urlparse(neigh_node)  # get the netloc to only include uoit and ontariotechu links
        netloc = parsed_url.netloc
        # http makes sure it's a website
        return 'http' in parsed_url[0] and ('ontariotechu.ca' in netloc or 'uoit.ca' in netloc)

    def _print_log(self, url, seen: Set[str], bfs_seq: List[str]) -> None:
        """
        Helps print logs to reassure the user that the program is working
        :param url: Current node popped from the queue
        :param seen: Set of all seen nodes
        :param bfs_seq: List containing the nodes traversed in their order of traversal
        :return: None
        """
        print(f"Processing node: {url}, at total number of urls: {len(seen)} and bfs_seq len: {len(bfs_seq)}")

    def _queue_helper(self, focus_node: str, neigh_node: str, queue: SimpleQueue, seen: Set[str], graph: nx.DiGraph) \
            -> None:
        """
        Helper method to add a node to the queue, mark it as seen and add an edge to the final info network.
        It is to be noted that if the neighboring node is already seen, queue and seen are not updated.
        Regardless of whether the node has been seen or not, the graph will get updated.
        :param focus_node: Root node popped from the queue whose neighbors are to be traversed
        :param neigh_node: Neighboring node of the root node
        :param queue: SimpleQueue to help in BFS
        :param seen: Set to keep track of already visited nodes
        :param graph: Directed Graph holding the BFS traversal info
        :return: None
        """
        graph.add_edge(focus_node, neigh_node)
        if neigh_node in seen:  # already seen? don't add it to the queue and don't mark as seen. Simply return
            return
        queue.put(neigh_node)
        seen.add(neigh_node)


if __name__ == '__main__':
    root = 'https://ontariotechu.ca/'
    graph = UOITCrawler().crawl(root)
