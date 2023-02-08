# Download E-Books from Project Gutenberg in UTF-8 text format and save them as parquet files with metadata

Please **READ** the site's TOS before running this Notebook and follow these instructions: 
- The website will IP ban crawlers for going through each book's metadata page separately. Instead use `catalog()` to access the list of available E-books. For more information, visit: https://www.gutenberg.org/ebooks/feeds.html
- You can avoid running the crawler by mirroring the entire database of Project Gutenberg or use one of their FTPs instead, and then call the `parse()` function on each text
- For more on robot access see: https://www.gutenberg.org/policy/robot_access.html

How does it work?
- The crawler downloads the raw HTML code for each E-book based on **Text#** id (if available)
- The metadata and the body of text are not clearly separated so the parser will try to split them, then remove transcriber's notes and e-book related information from the body of text (text marked as copyrighted or malformed will be skipped)
- If there is text both the metadata and the cleared body of text are saved, the latter is then added to a filtered parquet file (will contain only the catalog information and body of text for the books that were successfully retrieved) 

Further **NOTICE** on copyright: 
- Some of the books are copyrighted! The crawler (parser) will ignore all books with an english copyright header by utilizing a regex expression, but make sure to check out the metadata for each book manually to ensure they are okay to use in your country! More information on copyright: https://www.gutenberg.org/help/copyright.html and https://www.gutenberg.org/policy/permission.html
- Project Gutenberg has the following requests when using books without metadata:
*Books obtianed from the Project Gutenberg site should have the following legal note next to them:
"This eBook is for the use of anyone anywhere in the United States and most other parts of the world at no cost and with almost" no restrictions whatsoever. You may copy it, give it away or re-use it under the terms of the Project Gutenberg License included with this eBook or online at www.gutenberg.org. If you are not located in the United States, you will have to check the laws of the country where you are located before using this eBook."*
