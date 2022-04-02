#!/usr/bin/env python3

import json
import multiprocessing
import os
import shutil
import unittest
import random
import requests

import database
import server


testData = [
    {"title": "Harry Potter and the Philosophers Stone"},
    {"title": "Nineteen Eighty-Four", "author": "George Orwell"}
]

bookDefaults = {
    "title": "", "author": "", "series": "", "isbn": "", "releaseDate": "",
    "publisher": "", "language": "", "files": [], "hasCover": False
}


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
        bookInDatabase = {**bookDefaults, **testData[0]}
        bookID = db.bookAdd(testData[0])
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
        bookIDs.append(db.bookAdd(testData[0]))
        bookIDs.append(db.bookAdd(testData[1]))
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
    baseUrl = f"http://{host}:{port}"

    @classmethod
    def setUpClass(self):
        """Start the server for the requests tests."""
        setUp(self)
        self.booklist = server.booklist
        server.db = database.database(self.tempDataDir)
        server.db.data = multiprocessing.Manager().dict()
        self.serverThread = multiprocessing.Process(
            target=lambda: self.booklist.run(host=self.host, port=self.port))
        self.serverThread.start()

    @classmethod
    def tearDownClass(self):
        """Stop the server."""
        self.serverThread.terminate()
        tearDown(self)

    def testIndex(self):
        """Test that the index is send without any errors."""
        r = requests.get(self.baseUrl)
        self.assertEqual(r.status_code, 200)

    def testStatic(self):
        """Check that files are sent from the static directory properly."""
        for path in (
            "images/favicon.ico",
            "scripts/main.js",
            "styles/layout.css"
        ):
            r = requests.get(f"{self.baseUrl}/static/{path}")
            self.assertEqual(r.status_code, 200)
            file = open("static/" + path, "rb")
            self.assertEqual(r.content, file.read())
            file.close()

    def testGetBook(self):
        """Tests getting books from the server"""
        bookID = server.db.bookAdd(testData[0])
        r1 = requests.get(f"{self.baseUrl}/api/get/{bookID}")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.headers['content-type'], "application/json")
        self.assertEqual(json.loads(r1.content), server.db.bookGet(bookID))
        r2 = requests.get(f"{self.baseUrl}/api/get/0")
        server.db.bookDelete(bookID)
        r3 = requests.get(f"{self.baseUrl}/api/get/{bookID}")
        self.assertEqual(r2.status_code, 404)
        self.assertEqual(r3.status_code, 404)
    
    def testAddBook(self):
        """Tests adding a book to the server"""
        for book in testData:
            r = requests.post(f"{self.baseUrl}/api/new", json=book)
            self.assertEqual(r.status_code, 200)
            bookID = json.loads(r.content)["bookID"]
            self.assertEqual(
                server.db.bookGet(bookID), 
                {**bookDefaults, **book})
        emptyBook = requests.post(f"{self.baseUrl}/api/new", json={})
        self.assertEqual(emptyBook.status_code, 422)
        invalidBook = requests.post(f"{self.baseUrl}/api/new", data=b"Harry Potter")
        self.assertEqual(invalidBook.status_code, 422)

    def testEditBook(self):
        """Tests editing a book on the server"""
        for book in testData:
            bookID = server.db.bookAdd(book)
            isbn = str(random.randint(0,999999999))
            r = requests.put(f"{self.baseUrl}/api/edit/{bookID}", json={"isbn": isbn})
            self.assertEqual(r.status_code, 200)
            self.assertEqual(json.loads(r.content), {"Success": True})
            self.assertEqual(
                server.db.bookGet(bookID), 
                {"isbn": isbn, **bookDefaults, **book})

    def testDeleteBook(self):
        """Tests deleting a book from the server"""
        for book in testData:
            bookID = server.db.bookAdd(book)
            r = requests.delete(f"{self.baseUrl}/api/delete/{bookID}")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(json.loads(r.content), {"Deleted": True})
            self.assertFalse(server.db.bookGet(bookID))

    def getBookIDList(self, response):
        """Used by both search tests to get a list of bookIDs from the response"""
        bookIDs = []
        for book in response["books"]:
            bookIDs.append(book["bookID"])
        return bookIDs.sort()

    def testSearchBook1(self):
        """Tests searching for books via the server without a query"""
        r = requests.get(f"{self.baseUrl}/api/search")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            self.getBookIDList(json.loads(r.content)),
            list(server.db.data.keys()).sort())

    def testSearchBook2(self):
        """Tests searching for books via the server with a query
        
        Only checks the IDs of the books and not any of the data
        Assumes database.bookSearch works correctly"""
        for book in testData:
            server.db.bookAdd(book)
        for query in ["harry potter", "orwell", "big chungus"]:
            r = requests.get(f"{self.baseUrl}/api/search?q={query}")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(
                self.getBookIDList(json.loads(r.content)),
                server.db.bookSearch(query).sort())


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
