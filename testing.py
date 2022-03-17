#!/usr/bin/env python3

import multiprocessing
import os
import shutil
import unittest
import requests


def setUp(self):
    if os.name == "posix":
        self.tempDataDir = "/tmp/AppAssignmentBooklistTest/"
    else:
        self.tempDataDir = "./AppAssignmentBooklistTest/"
    os.makedirs(self.tempDataDir, exist_ok=True)


def tearDown(self):
    shutil.rmtree(self.tempDataDir)


class databaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        setUp(self)

    @classmethod
    def tearDownClass(self):
        tearDown(self)

    def testFullFilePath(self):
        import database
        db = database.database("/test/directory")
        self.assertEqual(db.fullFilePath("testFile"), "/test/directory/testFile")
        self.assertEqual(db.fullFilePath("dir/test"), "/test/directory/dir/test")

    def testInit(self):
        import database
        database.sys.argv = ["--data-dir", "testDir1"]
        argv = database.database()
        param = database.database("testDir2")
        self.assertEqual(argv.dataDir, "testDir1")
        self.assertEqual(param.dataDir, "testDir2")

    def testSaveLoad(self):
        dbDataShouldBe = {}
        import database
        # Test loading and saving the database lots of times
        for i in range(16):
            db = database.database(self.tempDataDir + "testSaveLoad")
            db.load()
            self.assertEqual(db.data, dbDataShouldBe)
            db.data[str(i)] = i ** i
            dbDataShouldBe[str(i)] = i ** i
            db.save()
        # Test loading backup file
        os.remove(self.tempDataDir + "testSaveLoad/data.json")
        dbDataShouldBe.popitem()
        db = database.database(self.tempDataDir + "testSaveLoad")
        db.load()
        self.assertEqual(db.data, dbDataShouldBe)
        db.save()

    def testBookAddEditDelete(self):
        testBooks = [
            {"name": "Harry Potter and the Philosophers Stone", "author": "JK Rowling"},
            {"name": "test book 1"},
            {"name": "test book 2", "isbn": "9780141393049"}
        ]
        bookDefaults = {"name": "", "author": "", "series": "", "isbn": "", "releaseDate": "",
                        "publisher": "", "language": "", "files": [], "hasCover": False}
        import database
        db = database.database(self.tempDataDir + "testBookAddEditDelete")
        db.data = {}
        bookIDs = []
        # Add
        for book in testBooks:
            bookID = db.bookAdd(book)
            self.assertEqual(db.bookGet(bookID), {**bookDefaults, **book})
            bookIDs.append(bookID)
        for i in range(len(testBooks)):
            self.assertEqual(db.bookGet(bookIDs[i]), {**bookDefaults, **testBooks[i]})
        self.assertEqual(len(db.data), len(testBooks))
        # Edit
        bookDefaults["language"] = "english"
        for i in range(len(testBooks)):
            db.bookEdit(bookIDs[i], {"language": "english"})
            self.assertEqual(db.bookGet(bookIDs[i]), {**bookDefaults, **testBooks[i]})
        # Delete
        bookFilePath = self.tempDataDir + "testBookAddEditDelete/books/" + bookIDs[0]
        os.makedirs(bookFilePath)
        open(bookFilePath + "/testFile", "w").close()
        db.data[bookIDs[0]]["files"] = ["testFile"]
        for bookID in bookIDs:
            db.bookDelete(bookID)
            self.assertFalse(db.bookGet(bookID))
        self.assertEqual(db.data, {})
        self.assertFalse(os.path.exists(bookFilePath))

    # def testBookSearch(self):
    #     # TODO
    #     pass

    # def testFileAdd(self):
    #     # TODO
    #     pass

    # def testFileDelete(self):
    #     # TODO
    #     pass

    # def testCoverAdd(self):
    #     # TODO
    #     pass

    def testCoverExists(self):
        import database
        db = database.database()
        db.data = {
            "book1": {"hasCover": True},
            "book2": {"hasCover": False}
        }
        self.assertTrue(db.coverExists("book1"))
        self.assertFalse(db.coverExists("book2"))
        self.assertFalse(db.coverExists("book3"))

    # def testCoverDelete(self):
    #     # TODO
    #     pass

            

class requestsTests(unittest.TestCase):
    host = "127.0.0.1"
    port = 8080

    @classmethod
    def setUpClass(self):
        setUp(self)
        print("Starting server for requestsTests")
        import server
        self.server = server
        self.server.db = server.database(self.tempDataDir + "reqestsTest")
        self.server.db.load()
        self.serverThread = multiprocessing.Process(
            target=lambda: self.server.booklist.run(host=self.host, port=self.port))
        self.serverThread.start()

    @classmethod
    def tearDownClass(self):
        print("Stopping server for requestsTests")
        self.serverThread.terminate()
        self.server.db.save()
        tearDown(self)

    def testIndex(self):
        r = requests.get(f"http://{self.host}:{self.port}/")
        self.assertEqual(r.status_code, 200)

    def testStatic(self):
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
