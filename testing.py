#!/usr/bin/env python3

import hashlib
import json
import multiprocessing
import os
import random
import requests
import shutil
import unittest

import database
import server

testData = [
    {"title": "Harry Potter and the Philosophers Stone"},
    {"title": "Nineteen Eighty-Four", "author": "George Orwell"}
]

bookDefaults = {
    "title": "", "author": "", "series": "", "genre": "", "isbn": "", "releaseDate": "",
    "publisher": "", "language": "", "files": [], "hasCover": False
}

imagesBaseURL = "https://cdn.discordapp.com/attachments/796434329831604288"
testImages = [
    imagesBaseURL + "/960619212798296144/gernotMinecraft.jpeg",  # jpeg
    imagesBaseURL + "/960619213486170153/replitMeme.png",        # png
    imagesBaseURL + "/960619213779767307/BrunoFunkoPop.png"      # png with transparency
]

testFiles = {}


def getFile(url):
    """Get a file for testing from a URL, caches the file so it can be used on multiple tests."""
    if not url in testFiles:
        r = requests.get(url)
        if 200 > r.status_code or r.status_code >= 300:
            raise requests.HTTPError(r.status_code)
        testFiles[url] = r.content
    return testFiles[url]


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

    def testBookCover(self):
        """Test adding and deleting book covers.
        
        only checks that the image files exist"""
        db = database.database(self.tempDataDir)
        db.data = {"bookNoCover": {"hasCover": False}}
        
        # Add images
        for i in range(len(testImages)):
            db.data[f"book{i}"] = {"hasCover": False}
            db.coverAdd(f"book{i}", getFile(testImages[i]))
            self.assertTrue(db.coverExists(f"book{i}"))
            self.assertTrue(os.path.exists(db.bookFilePath(f"book{i}", "cover.jpg")))
            self.assertTrue(os.path.exists(db.bookFilePath(f"book{i}", "coverPreview.jpg")))
            
        # Replace image on book1 with book2s image, check they are the same
        db.coverAdd("book0", getFile(testImages[1]))
        with open(db.bookFilePath("book0", "cover.jpg"), "rb") as book0:
            with open(db.bookFilePath("book1", "cover.jpg"), "rb") as book1:
                self.assertEqual(
                    hashlib.md5(book0.read()).hexdigest(),
                    hashlib.md5(book1.read()).hexdigest())
        self.assertTrue(db.coverExists("book0"))

        # Check other books dont have covers
        self.assertFalse(db.coverExists("bookNoCover"))
        self.assertFalse(db.coverExists("bookDoesntExist"))

        # Delete images
        for i in range(len(testImages)):
            db.coverDelete(f"book{i}")
            self.assertFalse(db.coverExists(f"book{i}"))
            self.assertFalse(os.path.exists(db.bookFilePath(f"book{i}", "cover.jpg")))
            self.assertFalse(os.path.exists(db.bookFilePath(f"book{i}", "coverPreview.jpg")))

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
        self.assertTrue(400 <= emptyBook.status_code <= 499)
        invalidBook = requests.post(f"{self.baseUrl}/api/new", data=b"Harry Potter")
        self.assertTrue(400 <= invalidBook.status_code <= 499)

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
