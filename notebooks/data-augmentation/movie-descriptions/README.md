## Dataset Summary

This dataset is created by scraping Letterbox
([popular](https://letterboxd.com/films/popular/) film titles) + Wikipedia (film
descriptions). This is because the descriptions in Letterbox are from The Movie
Database, whose terms prevent the use of their data:
https://www.themoviedb.org/terms-of-use.

The dataset format is:

```
INSTRUCTION: Write a description about the film {film}.
RESPONSE: In his second year of fighting crime, Batman uncovers corruption in Gotham City...
```

The notebook only contains the instructions to obtain the dataset, other steps
must be implemented. The process can take hours or days, so I recommend setting
a limit on the number of data to be obtained.
