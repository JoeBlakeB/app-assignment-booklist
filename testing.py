#!/usr/bin/env python3

import multiprocessing
import os
import shutil
import unittest
import requests

import database
import server


def setUp(self):
    """Create temporary directory for each set of tests."""
    if os.name == "posix":
        self.tempDataDir = "/tmp/AppAssignmentBooklistTest/"
    else:
        self.tempDataDir = "./AppAssignmentBooklistTest/"
    os.makedirs(self.tempDataDir, exist_ok=True)


def tearDown(self):
    """Remove temporary directory for each set of tests."""
    shutil.rmtree(self.tempDataDir)


class databaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        setUp(self)

    @classmethod
    def tearDownClass(self):
        tearDown(self)

    def testSaveLoad(self):
        """Test saving and loading the database."""
        dbDataShouldBe = {}
        for i in range(16):
            db = database.database(self.tempDataDir)
            db.load()
            self.assertEqual(db.data, dbDataShouldBe)
            db.data[str(i)] = {"test": i ** i}
            dbDataShouldBe[str(i)] = {"test": i ** i}
            db.save()
        os.remove(self.tempDataDir + "data.json")
        dbDataShouldBe.popitem()
        db = database.database(self.tempDataDir)
        db.load()
        self.assertEqual(db.data, dbDataShouldBe)
        db.save()

    def testBookAddEditDelete(self):
        """Test the database for adding, editing, and deleting books from the database."""
        db = database.database(self.tempDataDir)
        db.load()

        # Add book
        book = {"name": "Harry Potter and the Philosophers Stone"}
        bookInDatabase = {**book, "author": "", "series": "", "isbn": "", "releaseDate": "",
            "publisher": "", "language": "", "files": [], "hasCover": False}
        bookID = db.bookAdd(book)
        self.assertEqual(db.bookGet(bookID), bookInDatabase)
        
        # Edit book
        bookInDatabase["language"] = "english"
        db.bookEdit(bookID, {"language": "english"})
        self.assertEqual(db.bookGet(bookID), bookInDatabase)

        # Make file for testing delete
        bookFilePath = self.tempDataDir + "books/" + bookID
        os.makedirs(bookFilePath)
        open(bookFilePath + "/testFile", "w").close()

        # Delete book
        db.bookDelete(bookID)
        self.assertFalse(db.bookGet(bookID))
        self.assertFalse(os.path.exists(bookFilePath))

    def testSearch(self):
        """Test the book search.
        
        only makes sure relavant books are found and irrelevant books arent found
        does not test the order of books or how relevant the found books are"""
        db = database.database(self.tempDataDir)
        db.data = {}
        bookIDs = []
        bookIDs.append(db.bookAdd({"name": "Harry Potter and the Philosophers Stone"}))
        bookIDs.append(db.bookAdd({"name": "Nineteen Eighty-Four", "author": "George Orwell"}))
        self.assertEqual(db.bookSearch("harry potter"), [bookIDs[0]])
        self.assertEqual(db.bookSearch("orwell"), [bookIDs[1]])
        self.assertEqual(db.bookSearch("big chungus"), [])

    def testFiles(self):
        """Test adding and deleting files."""
        # TODO
        pass

    def testCovers(self):
        """Test adding and deleting book covers."""
        # TODO: make this test adding and deleting
        db = database.database()
        db.data = {
            "book1": {"hasCover": True},
            "book2": {"hasCover": False}
        }
        self.assertTrue(db.coverExists("book1"))
        self.assertFalse(db.coverExists("book2"))
        self.assertFalse(db.coverExists("book3"))


class requestsTests(unittest.TestCase):
    host = "127.0.0.1"
    port = 8080

    @classmethod
    def setUpClass(self):
        """Start the server for the requests tests."""
        setUp(self)
        self.server = server
        self.server.db = server.database(self.tempDataDir)
        self.server.db.load()
        self.serverThread = multiprocessing.Process(
            target=lambda: self.server.booklist.run(host=self.host, port=self.port))
        self.serverThread.start()

    @classmethod
    def tearDownClass(self):
        """Stop the server."""
        self.serverThread.terminate()
        self.server.db.save()
        tearDown(self)

    def testIndex(self):
        """Test that the index is send without any errors."""
        r = requests.get(f"http://{self.host}:{self.port}/")
        self.assertEqual(r.status_code, 200)

    def testStatic(self):
        """Check that files are sent from the static directory properly."""
        for path in (
            "images/favicon.ico",
            "scripts/main.js",
            "styles/layout.css"
        ):
            r = requests.get(f"http://{self.host}:{self.port}/static/{path}")
            self.assertEqual(r.status_code, 200)
            file = open("static/" + path, "rb")
            self.assertEqual(r.content, file.read())
            file.close()


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
