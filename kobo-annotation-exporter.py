#!/usr/bin/python3
"""
Kobo e-reader annotation exportation script

Author: Dr. Mounir Mallek
Date: 14-01-2022
"""
from html.parser import HTMLParser
import os
from pathlib import Path
from sys import argv


ANNOT = {"quote": None, "comment": None}


class AnnotParser(HTMLParser):

    def __init__(self, *args):
        super().__init__(*args)

        # data
        self.title = None
        self.author = None
        self.annots = []

        # flag setup
        self.ftitle = False
        self.creator = False
        self.fragment = False
        self.content = False
        self.text = False

    def handle_starttag(self, tag, attrs):

        if tag == "dc:title":
            self.ftitle = True

        # avoid overwriting the book author by annotation author
        if tag == "dc:creator" and self.author is None:
            self.creator = True

        if tag == "annotation":
            self.annots.append(ANNOT.copy())

        if tag == "fragment":
            self.fragment = True

        if tag == "content":
            self.content = True

        if tag == "text":
            self.text = True

    def handle_endtag(self, tag):

        if tag == "fragment":
            self.fragment = False

        if tag == "content":
            self.content = False

        if tag == "text":
            self.text = False

    def handle_data(self, data):

        if self.ftitle:
            self.title = data
            self.ftitle = False

        if self.creator:
            self.author = data
            self.creator = False

        if self.content and self.text:
            self.annots[-1]["comment"] = data.replace("\n", " ")
            self.content = False
            self.text = False

        if self.fragment and self.text:
            self.annots[-1]["quote"] = data.replace("\n", " ")
            self.fragment = False
            self.text = False

    def to_markdown(self, path):
        """
        exports the annotation into a neat markdown file
        """

        fname = f"{self.author} - {self.title}.md"

        # log
        print(f"Exporting {fname}...")

        with open(os.path.join(path, fname), "w") as fp:

            # title of the note
            fp.write(f"# {self.author} - {self.title}\n\n")

            for i, annot in enumerate(self.annots):
                quote, comment = annot.values()

                fp.write(f"{comment}\n\n")
                fp.write(f"> {quote}\n\n")


if __name__ == "__main__":

    USER, cwd = os.environ["USER"], os.getcwd()

    try:
        path = argv[1]

    except IndexError:
        print("No path was provided.\nDefault KOBOeReader path will be used.")
        path = f"/media/{USER}/KOBOeReader/Digital Editions/Annotations"

    for annot_file in Path(path).rglob('*.annot'):

        # parse the file and export it into markdown
        with open(str(annot_file)) as fp:

            parser = AnnotParser()
            parser.feed(fp.read())
            parser.to_markdown(path=cwd)
