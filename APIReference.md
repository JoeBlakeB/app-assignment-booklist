# APP Assignment Booklist API Reference

## Table of Contents  
- General GET Requests
  - [Interface Files](#booklist-interface)
  - [Book Cover](#book-cover)
  - [Book File](#book-file)
  - [Filetype Icon](#filetype-icon)
- Book Metadata
  - [Get](#get-book)
  - [New](#new-book)
  - [Edit](#edit-book)
  - [Delete](#delete-book)
  - [Search](#search-book)
- Book Files
  - [Upload Cover](#upload-cover)
  - [Delete Cover](#delete-cover)
  - [Upload File](#upload-file)
  - [Rename File](#rename-file)
  - [Delete File](#delete-file)
- Data Reference
  - [Book ID](#book-id---bookid)
  - [File Hash Name](#file-hash-name---hashname)
  - [Book JSON](#book-json)

# General GET Requests

## Booklist Interface

GET `/`

GET `/static/<path>`

Used by the end user for using the booklists interface.

## Book Cover

GET `/book/cover/<bookID>`

Full size (maximum 1200x1600) book cover image.

GET `/book/cover/<bookID>/preview`

Preview book cover image (60x80).

Response Status Codes:
- `200` - Book exists (jpeg)
- `404` - Book does not exist (png)

## Book File

GET `/book/file/<bookID>/<hashName>`

Download a file for a book. The filename will be set via the `Content-Disposition` header.

Response Status Codes:
- `200` - File exists
- `404` - File or book does not exist

## Filetype Icon

GET `/fileicon/<filetype>.svg`

Get an icon for a filetype from `/static/svg/filetype-*.svg`, if an icon is used for multiple filetypes, there will be a + between them in the filename (for example `filetype-png+jpg.svg`) and the file will be served for both filetypes (for example `/fileicon/png.svg`)

# Book Metadata

## Get Book

GET `/api/get/<bookID>`

Responds with a books full data, see [Book JSON](#book-json)

Response Status Codes:
- `200` - Book exists
- `404` - Book not found

## New Book

POST `/api/new` with a JSON containing [the books metadata as a JSON](#book-json), not all fields are required, however it must contain a title.

Responds with a JSON stating if adding the book was successful along with the new books ID:

```json
{
  "success": True,
  "bookID": bookID
}
```

Response Status Codes:
- `200` - Book added successfully
- `422` - Request JSON invalid

## Edit Book

PUT `/api/edit/<bookID>` with a JSON containing the books updated metadata [as a JSON](#book-json), no fields are required and it is prefered to only contain the fields which were updated.

Responds with a JSON which just states if the edit was successful:

```json
{
  "success": True
}
```

Response Status Codes:
- `200` - Book updated successfully
- `404` - Book not found
- `422` - Request JSON invalid

## Delete Book

DELETE `/api/delete/<bookID>`

Responds with a JSON which just states if the delete was successful:

```json
{
  "deleted": True
}
```

Response Status Codes:
- `200` - Book deleted successfully
- `404` - Book not found

## Search Books

GET `/api/search`

Get a list of books for a query, no query means all books will be sent. Arguments are optional and should be URL queries, for example `/api/search?q=Python&limit=100`

Arguments:

- `q` - the search query as a string, for example `q=Python` - default is no query
- `offset` - the amount of books to skip in the response, used for getting different pages of results if there are to many, for example `q=25` to get the second page - default is 0
- `limit` - the amount of books to be returned, for example `limit=50` - default is 25

The response is a list of books with only part of the metadata, along with some information about the search:

```json
{
  "books": [
    {
      "author": "Miguel Grinberg",
      "bookID": "6b44bea2-2434-4db5-8108-778137efaae7",
      "hasCover": true,
      "lastModified": 1653063610,
      "title": "Flask Web Development"
    }
  ],
  "first": 1, // The index of the first book in all results (starting at 1)
  "last": 1,  // The index of the last book in all results (starting at 1)
  "time": 1,  // The time in ms that the search took
  "total": 1  // The total number of books in results
}
```

# Book Files

## Upload Cover

PUT `/api/cover/<bookID>/upload` with the image as the request body.

The server will resize the image if it is over the maximum resolution of 1200x1600 and will generate a thumbnail with a resolution of 60x80, the file can then be accessed via [`/book/cover/<bookID>`](#book-cover)

Response Status Codes:
- `200` - Cover uploaded successfully
- `404` - Book not found
- `422` - Cover not uploaded successfully

## Delete Cover

DELETE `/api/cover/<bookID>/delete`

The file for the book covers image and the preview will be removed from the server.

Response Status Codes:
- `200` - Cover deleted successfully
- `404` - Book not found
- `422` - Delete unsuccessful

## Upload File

POST `/api/file/upload/<bookID>/<filename>` with the request body being the file.

The response will be a JSON stating if adding the upload was a success as well as the hashName of the file:

```json
{
  "hashName": "79317e272fc98ee957a1c1372a260848.4.jpeg",
  "success": true
}
```

The file can then be accessed via [`/book/file/<bookID>/<hashName>`](#book-file)

Response Status Codes:
- `200` - File uploaded successfully
- `404` - Book not found
- `413` - File too big
- `422` - File upload unsuccessful

## Rename File

POST `/api/file/rename/<bookID>` with a JSON of the files to be renamed, the hashname being the key and the new filename being the value:

```json
{
  "71bd3bdbe1b4aa2f4ee8af0bd26d5937.1.pdf": "Python_Guide.pdf"
}
```

If there are multiple files for the book, not all files are needed in the rename request, only the ones to be changed. If a filename is invalid, it will be automatically converted to a valid one. the get url for the file will stay the same as it uses the hashname instead of the filename.

Response Status Codes:
- `200` - File renamed successfully
- `404` - Book or file not found
- `422` - JSON invalid

## Delete File

DELETE `/api/file/delete/<bookID>/<hashName>`

The file will be removed from the server.

Response Status Codes:
- `200` - File deleted successfully
- `404` - Book or file not found

# Data Reference

## Book ID - `bookID`

The book ID is unique and used for identifying books. It is a UUID4, for example:

`b1f78c48-48b1-444d-a88c-b64b2cfa1a94`

## File Hash Name - `hashName`

A hashName is used for storing the file and accessing the file, it is three parts. First the files MD5 hash, then the number of the file which increases each time a file is uploaded to each book, meaning if a file is deleted and the same file is re uploaded it will be different, then at the end is the file extension. For example:

`71bd3bdbe1b4aa2f4ee8af0bd26d5937.1.png`

The files actual name is stored on the servers database and is shown on the interface and is set in the `Content-Disposition` header so that the filename is saved if a user downloads a file. The hashname is used so that a file can be renamed without needing to update the stored file or breaking any download links if any other users have the book open.

## Book JSON

A book as different data fields, not all are always filled but all will exist, here is an example of a books full JSON:

```json
{
  "author": "Miguel Grinberg",
  "description": "",
  "files": {
    "1": {
      "hashName": "508664dee8e911e3c91c5eb112ca1355.1.txt", // Cannot be changed
      "name": "Example_File.txt", // Actual filename, can be changed
      "size": 32, // Filesize in bytes
      "type": ".txt" 
    },
    "count": 1 // The total number of files the book has ever had
  },
  "genre": "web",
  "hasCover": true, // States whether the book has a cover image
  "isbn": "",
  "language": "",
  "lastModified": 1655809565, // Updated each time the book is modified
  "publisher": "O'Reilly",
  "releaseDate": "",
  "series": "",
  "title": "Flask Web Development"
}
```
