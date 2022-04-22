import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
import uuid

try:
    from PIL import Image, UnidentifiedImageError
except ModuleNotFoundError:
    Image = None
    UnidentifiedImageError = None
    print("Warning: Pillow is not installed, uploaded images will not be resized.")


class database:
    dataFilename = "data.json"
    bookFields = ("title", "author", "series", "isbn", "releaseDate", "publisher", "language", "genre")
    
    fullFilePath = lambda self, filename : os.path.join(self.dataDir, filename)
    bookFilePath = lambda self, bookID, filename="" : os.path.join(self.dataDir, "books", bookID, filename)

    def __init__(self, dataDir=None):
        """Set the data directory for the database"""
        if dataDir != None:
            self.dataDir = dataDir
        else:
            if "--data-dir" in sys.argv:
                self.dataDir = sys.argv[sys.argv.index("--data-dir") + 1]
            else:
                self.dataDir = os.path.join(os.path.dirname(__file__), "data")

    def load(self):
        """Load the database"""
        os.makedirs(self.dataDir, exist_ok=True)

        filename = self.fullFilePath(self.dataFilename)

        try:
            # Load database
            with open(filename, "r") as dataFile:
                self.data = json.loads(dataFile.read())
        except:
            try:
                # Cannot load database, try backup
                with open(filename + ".bak", "r") as dataFile:
                    self.data = json.loads(dataFile.read())
            except:
                # Cannot load backup either
                self.data = {}

    def save(self):
        """Save the database"""
        filename = self.fullFilePath(self.dataFilename)

        if os.path.exists(filename):
            try:
                os.remove(filename + ".bak")
            except: pass
            os.rename(filename, filename + ".bak")

        with open(filename, "w") as dataFile:
            dataFile.write(json.dumps(self.data, indent=4))

    def modified(self, bookID):
        """Update the lastModified variable
        
        lastModified used by client to make browser reload images"""
        self.data[bookID]["lastModified"] = int(time.time())

    def bookAdd(self, bookData):
        """Takes a dict with book data and returns the new book ID"""
        # If book doesnt have a title, dont add to database
        if not bookData.get("title"):
            return False
        
        # Generate book dict with all fields
        newBook = {"files": [0], "hasCover": False, "lastModified": 0}
        for field in self.bookFields:
            if field in bookData:
                newBook[field] = bookData[field]
            else:
                newBook[field] = ""

        # Generate book id and add to database
        bookID = None
        while bookID in self.data or bookID == None:
            bookID = str(uuid.uuid4())
        self.data[bookID] = newBook
        return bookID

    def bookEdit(self, bookID, newData):
        """Edit bookIDs data in the fields in of newData"""
        for field in self.bookFields:
            if field in newData:
                self.data[bookID][field] = newData[field]
        self.modified(bookID)

    def bookGet(self, bookID, search=False):
        """Returns the book data if it exists, or False if it doesnt
        
        search=True to limit data returned"""
        if bookID in self.data:
            book = self.data[bookID]
            if not search:
                return book
            else:
                return {
                    "title": book["title"],
                    "author": book["author"],
                    "hasCover": book["hasCover"],
                    "lastModified": book["lastModified"]
                }
        return False

    def bookDelete(self, bookID):
        """Delete a book and its files"""
        bookPath = self.bookFilePath(bookID)
        if os.path.exists(bookPath):
            shutil.rmtree(bookPath)
        del self.data[bookID]

    def bookSearch(self, query):
        """Returns a list of bookIDs for if the query is in the books data"""
        queryList = query.lower().split()
        results = []
        for bookID in list(self.data.keys())[::-1]:
            for word in queryList:
                if word in str(list(self.data[bookID].values())[2:]).lower():
                    results.append(bookID)
                    break

        return results

    def coverAdd(self, bookID, originalImage):
        """Take an images binary data and save it as the book covers images"""
        os.makedirs(self.bookFilePath(bookID), exist_ok=True)
        if Image:
            try:
                # Full size book cover (maximum of 1200x1600)
                fullCover = Image.open(io.BytesIO(originalImage)).convert("RGB")
                fullCover.thumbnail((1200, 1600), Image.Resampling.LANCZOS)
                fullCover.save(self.bookFilePath(bookID, "cover.jpg"), "JPEG", quality=95)
                # Book cover thumbnail (60x80)
                Image.open(io.BytesIO(originalImage)).convert("RGB").resize(
                    (60, 80), Image.Resampling.LANCZOS).save(
                    self.bookFilePath(bookID, "coverPreview.jpg"), "JPEG", quality=75)
            except UnidentifiedImageError:
                return False
        # If PIL is not installed, just save original image and have no thumbnail
        else:
            with open(self.bookFilePath(bookID, "cover.jpg"), "wb") as file:
                file.write(originalImage)
        self.data[bookID]["hasCover"] = True
        self.modified(bookID)
        return True

    def coverExists(self, bookID):
        """Returns a bool for if a book has a cover"""
        if bookID in self.data:
            return self.data[bookID]["hasCover"]
        return False

    def coverDelete(self, bookID):
        """Delete a books cover and cover preview, and update hasCover"""
        for fileName in ["cover.jpg", "coverPreview.jpg"]:
            try:
                os.remove(self.bookFilePath(bookID, fileName))
            except: pass
        self.data[bookID]["hasCover"] = os.path.exists(self.bookFilePath(bookID, "cover.jpg"))
        self.modified(bookID)
        return not self.data[bookID]["hasCover"]

    def safeFilename(self, filename):
        """Make a filename safe for the URL"""
        # Replace invalid characters
        filename = re.sub(r"[^\w\._]", "_", filename)
        while "__" in filename:
            filename = filename.replace("__", "_")
        # Shorten filename
        if len(filename) > 48:
            filetype = filename.split(".")[-1]
            if filetype != filename:
                filename = filename[:47 - len(filetype)] + "." + filetype
            else:
                filename = filename[:48]
        return filename

    def fileAdd(self, bookID, filename, data):
        """Save a file and store metadata in database"""
        # Exit if book does not exist
        if not bookID in self.data:
            return False
        # Store data
        filename = self.safeFilename(filename)
        hashName = hashlib.md5(data).hexdigest()
        fileType = filename.split(".")[-1]
        self.data[bookID]["files"][0] += 1
        hashName += "." + str(self.data[bookID]["files"][0]) + "." + fileType
        if "." in filename:
            fileType = "." + fileType
        os.makedirs(self.bookFilePath(bookID), exist_ok=True)
        with open(self.bookFilePath(bookID, hashName), "wb") as file:
            file.write(data)
        self.data[bookID]["files"].append({
            "name": filename,
            "hashName": hashName,
            "type": fileType,
            "size": len(data)
        })
        return hashName

    def fileGet(self, bookID, hashName):
        """Get full file from hash"""
        if bookID in self.data:
            for i in range(1, len(self.data[bookID]["files"])):
                if self.data[bookID]["files"][i]["hashName"] == hashName:
                    return self.data[bookID]["files"][i], i
        return False, None

    def fileRename(self, bookID, hashName, newFilename):
        """Change a files name in database"""
        file = self.fileGet(bookID, hashName)
        if file[0]:
            fileType = file[0]["type"]
            if not newFilename.endswith(fileType):
                newFilename += fileType
            newFilename = self.safeFilename(newFilename)
            self.data[bookID]["files"][file[1]]["name"] = newFilename
            return True
        return False

    def fileDelete(self, bookID, hashName):
        """Delete a file from filesystem and database"""
        file = self.fileGet(bookID, hashName)
        if file[0]:
            filename = self.bookFilePath(bookID, hashName)
            try:
                os.remove(filename)
            except: pass
            if not os.path.exists(filename):
                del self.data[bookID]["files"][file[1]]
                return True
        return False
