import json
import os
import sys


class database:
    dataFilename = "data.json"
    
    fullFilePath = lambda self, filename : os.path.join(self.dataDir, filename)

    def load(self):
        """Load the database"""
        # Get data directory from argsv
        if "--data-dir" in sys.argv:
            self.dataDir = sys.argv[sys.argv.index("--data-dir") + 1]
        else:
            self.dataDir = "./data/"

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
            os.rename(filename, filename + ".bak")

        with open(filename, "w") as dataFile:
            dataFile.write(json.dumps(self.data, indent=4))
    
    def bookExists(self, bookID):
        """Returns a bool for if a book exists in the database"""
        return True
