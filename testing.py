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
