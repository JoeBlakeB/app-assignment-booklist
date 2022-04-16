#!/usr/bin/env python3

import hashlib
import json
import multiprocessing
import os
import random
import requests
import shutil
import time
import unittest

import database
import server

testData = [
    {"title": "Harry Potter and the Philosophers Stone"},
    {"title": "Nineteen Eighty-Four", "author": "George Orwell"}
]

bookDefaults = {
    "title": "", "author": "", "series": "", "genre": "", "isbn": "", "releaseDate": "",
    "publisher": "", "language": "", "files": [0], "hasCover": False, "lastModified": 0
}

imagesBaseURL = "https://cdn.discordapp.com/attachments/796434329831604288"
testImages = [
    imagesBaseURL + "/960619212798296144/gernotMinecraft.jpeg",  # jpeg
    imagesBaseURL + "/960619213486170153/replitMeme.png",        # png
    imagesBaseURL + "/960619213779767307/BrunoFunkoPop.png"      # png with transparency
]
testFiles = {
    imagesBaseURL + "/964247645709271070/GNULinux.txt": ["GNU+Linux.txt", "GNU_Linux.txt"],
    imagesBaseURL + "/964247645902217257/default-testpage.pdf": ["default-testpage.pdf", "default_testpage.pdf"],
    imagesBaseURL + "/964247646065807390/The_Fifth_Science_by_Exurb1a.epub": ["The Fifth Science - Exurb1a.epub", "The_Fifth_Science_Exurb1a.epub"]
}

testFileCache = {}

def getFile(url):
    """Get a file for testing from a URL, caches the file so it can be used on multiple tests."""
    if not url in testFileCache:
        r = requests.get(url)
        if 200 > r.status_code or r.status_code >= 300:
            raise requests.HTTPError(r.status_code)
        testFileCache[url] = r.content
    return testFileCache[url]


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
        bookData = db.bookGet(bookID)
        self.assertEqual(bookData, bookInDatabase)
        
        # Edit book
        bookInDatabase["language"] = "english"
        db.bookEdit(bookID, {"language": "english"})
        bookData = db.bookGet(bookID)
        bookInDatabase["lastModified"] = bookData["lastModified"]
        self.assertEqual(bookData, bookInDatabase)

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
    
    def testSafeFilename(self):
        """Test the safe filename function."""
        db = database.database()
        self.assertEqual(db.safeFilename("book.pdf"),         "book.pdf")
        self.assertEqual(db.safeFilename("book/book.pdf"),    "book_book.pdf")
        self.assertEqual(db.safeFilename("book file"),        "book_file")
        self.assertEqual(db.safeFilename("TEST%#//book.pdf"), "TEST_book.pdf")
        self.assertEqual(db.safeFilename(("bruh" * 100) + ".pdf"), ("bruh" * 11) + ".pdf")

    def testFiles(self):
        """Test adding and deleting files."""
        db = database.database(self.tempDataDir)
        db.data = {"bookNoFiles": {"files": [0]}}
        self.assertFalse(db.fileGet("bookNoFiles", "file.pdf")[0])
        self.assertFalse(db.fileGet("invalidBook", "file.pdf")[0])
        for fileUrl in testFiles.keys():
            bookID = fileUrl.split("/")[-2]
            db.data[bookID] = {"files": [0]}
            # Add
            db.fileAdd(bookID, testFiles[fileUrl][0], getFile(fileUrl))
            hashName = hashlib.md5(getFile(fileUrl)).hexdigest()
            hashName += ".1." + fileUrl.split(".")[-1]
            self.assertTrue(os.path.exists(db.bookFilePath(bookID, hashName)))
            # Get
            dbFile = db.fileGet(bookID, hashName)[0]
            self.assertEqual(hashName, dbFile["hashName"])
            self.assertEqual(dbFile["name"], testFiles[fileUrl][1])
            # Rename
            db.fileRename(bookID, hashName, fileUrl)
            newFilename = db.safeFilename(fileUrl)
            self.assertEqual(db.fileGet(bookID, hashName)
                             [0]["name"], newFilename)
            # Delete
            db.fileDelete(bookID, hashName)
            self.assertFalse(db.fileGet(bookID, hashName)[0])


class requestsTestsBase(unittest.TestCase):
    host = "127.0.0.1"
    port = 8081
    baseUrl = f"http://{host}:{port}"

    @classmethod
    def setUpClass(self):
        """Start the server for the requests tests."""
        setUp(self)
        self.booklist = server.booklist
        server.db = database.database(self.tempDataDir)
        server.db.data = self.data
        self.serverThread = multiprocessing.Process(
            target=lambda: self.booklist.run(host=self.host, port=self.port))
        self.serverThread.start()

    @classmethod
    def tearDownClass(self):
        """Stop the server."""
        self.serverThread.terminate()
        tearDown(self)
    
    def get(self, url, status="2", **qwargs):
        """HTTP GET and check its status starts with the status arg"""
        r = requests.get(url, **qwargs)
        self.assertTrue(str(r.status_code).startswith(status))
        return r

    def post(self, url, status="2", **qwargs):
        """HTTP POST and check its status starts with the status arg"""
        r = requests.post(url, **qwargs)
        self.assertTrue(str(r.status_code).startswith(status))
        return r

    def put(self, url, status="2", **qwargs):
        """HTTP PUT and check its status starts with the status arg"""
        r = requests.put(url, **qwargs)
        self.assertTrue(str(r.status_code).startswith(status))
        return r

    def delete(self, url, status="2", **qwargs):
        """HTTP DELETE and check its status starts with the status arg"""
        r = requests.delete(url, **qwargs)
        self.assertTrue(str(r.status_code).startswith(status))
        return r


class requestsDataTests(requestsTestsBase):
    """Tests for the server using requests, 
    a multiprocessing manager is used for direct access to the servers data"""
    data = multiprocessing.Manager().dict()

    def testIndex(self):
        """Test that the index is send without any errors."""
        self.get(self.baseUrl)

    def testStatic(self):
        """Check that files are sent from the static directory properly."""
        for path in (
            "images/favicon.ico",
            "scripts/main.js",
            "styles/layout.css"
        ):
            r = self.get(f"{self.baseUrl}/static/{path}")
            file = open("static/" + path, "rb")
            self.assertEqual(r.content, file.read())
            file.close()

    def testGetBook(self):
        """Tests getting books from the server"""
        bookID = server.db.bookAdd(testData[0])
        r = self.get(f"{self.baseUrl}/api/get/{bookID}")
        self.assertEqual(r.headers["content-type"], "application/json")
        self.assertEqual(json.loads(r.content), server.db.bookGet(bookID))
        self.get(f"{self.baseUrl}/api/get/0", "404")
        server.db.bookDelete(bookID)
        self.get(f"{self.baseUrl}/api/get/{bookID}", "404")
    
    def testAddBook(self):
        """Tests adding a book to the server"""
        for book in testData:
            r = self.post(f"{self.baseUrl}/api/new", json=book)
            bookID = json.loads(r.content)["bookID"]
            bookData = server.db.bookGet(bookID)
            self.assertEqual(
                bookData,
                {**bookDefaults, **book, "lastModified": bookData["lastModified"]})
        self.post(f"{self.baseUrl}/api/new", "4", json={})
        self.post(f"{self.baseUrl}/api/new", "4", data=b"Harry Potter")

    def testEditBook(self):
        """Tests editing a book on the server"""
        for book in testData:
            bookID = server.db.bookAdd(book)
            isbn = str(random.randint(0,999999999))
            r = self.put(f"{self.baseUrl}/api/edit/{bookID}", json={"isbn": isbn})
            self.assertEqual(json.loads(r.content), {"success": True})
            bookData = server.db.bookGet(bookID)
            self.assertEqual(
                bookData, 
                {"isbn": isbn, **bookDefaults, **book, "lastModified": bookData["lastModified"]})

    def testDeleteBook(self):
        """Tests deleting a book from the server"""
        for book in testData:
            bookID = server.db.bookAdd(book)
            r = self.delete(f"{self.baseUrl}/api/delete/{bookID}")
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
        r = self.get(f"{self.baseUrl}/api/search")
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
            r = self.get(f"{self.baseUrl}/api/search?q={query}")
            self.assertEqual(
                self.getBookIDList(json.loads(r.content)),
                server.db.bookSearch(query).sort())


class requestsFilesTests(requestsTestsBase):
    """Tests for the server using requests, 
    a dict is used for data and all access is done via the endpoints"""
    data = {}

    def newBook(self):
        r = self.post(f"{self.baseUrl}/api/new", json={"title": str(time.time())})
        return json.loads(r.content)["bookID"]

    def testBookCover(self):
        """Test adding, getting, and deleting book covers from the server."""
        coverExists = lambda bookID : 200 == requests.get(f"{self.baseUrl}/book/cover/{bookID}").status_code
        bookIDs = []
        # Add images
        for i in range(len(testImages)):
            bookID = self.newBook()
            bookIDs.append(bookID)
            self.put(f"{self.baseUrl}/api/cover/{bookID}/upload", data=getFile(testImages[i]))
            self.assertTrue(coverExists(bookID))
            self.assertTrue(os.path.exists(server.db.bookFilePath(bookID, "cover.jpg")))
            self.assertTrue(os.path.exists(server.db.bookFilePath(bookID, "coverPreview.jpg")))

        # Replace image on book0 with book1s image, check they are the same
        self.put(f"{self.baseUrl}/api/cover/{bookIDs[0]}/upload", data=getFile(testImages[1]))
        with open(server.db.bookFilePath(bookIDs[0], "cover.jpg"), "rb") as book0:
            with open(server.db.bookFilePath(bookIDs[1], "cover.jpg"), "rb") as book1:
                self.assertEqual(
                    hashlib.md5(book0.read()).hexdigest(),
                    hashlib.md5(book1.read()).hexdigest())
        self.assertTrue(coverExists(bookIDs[0]))

        # Check other books dont have covers
        bookNoCover = self.newBook()
        self.assertFalse(coverExists(bookNoCover))
        self.assertFalse(coverExists("bookDoesntExist"))

        for i in range(len(testImages)):
            # Delete images
            self.delete(f"{self.baseUrl}/api/cover/{bookIDs[i]}/delete")
            self.assertFalse(coverExists(bookIDs[i]))
            self.assertFalse(os.path.exists(server.db.bookFilePath(bookIDs[i], "cover.jpg")))
            self.assertFalse(os.path.exists(server.db.bookFilePath(bookIDs[i], "coverPreview.jpg")))
        
        # Test bad requests
        self.put(f"{self.baseUrl}/api/cover/{bookNoCover}/upload", "4", data=b"")
        self.put(f"{self.baseUrl}/api/cover/invalidbook/upload", "4", data=getFile(testImages[1]))
        self.delete(f"{self.baseUrl}/api/cover/invalidbook/delete", "4")
    
    def testFileUpload(self):
        """Test uploading, renaming, getting, and deleting files from the server"""
        bookIDNoFiles = self.newBook()
        self.get(f"{self.baseUrl}/book/file/{bookIDNoFiles}/test", "404")
        self.get(f"{self.baseUrl}/book/file/bookDoesntExist/test", "404")

        for fileUrl in testFiles.keys():
            bookID = self.newBook()
            # Add
            r = self.post(f"{self.baseUrl}/api/file/upload/{bookID}/{testFiles[fileUrl][0]}",
                          data=getFile(fileUrl))
            hashName = json.loads(r.content)["hashName"]
            
            # Get
            book = self.get(f"{self.baseUrl}/book/file/{bookID}/{hashName}")
            self.assertEqual(book.headers["content-disposition"],
                "inline; filename=" + testFiles[fileUrl][1])
            self.assertEqual(
                hashlib.md5(getFile(fileUrl)).hexdigest(),
                hashlib.md5(book.content).hexdigest())

            # Rename
            self.post(f"{self.baseUrl}/api/file/rename/{bookID}", 
                      json={hashName: fileUrl})
            book = self.get(f"{self.baseUrl}/book/file/{bookID}/{hashName}")
            self.assertEqual(book.headers["content-disposition"], 
                "inline; filename=" + server.db.safeFilename(fileUrl))

            # Delete
            r = self.delete(f"{self.baseUrl}/api/file/delete/{bookID}/{hashName}")
            self.assertEqual(json.loads(r.content), {"Deleted": True})

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
