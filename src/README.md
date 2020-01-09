# Source Code

## Dependencies

`pandas`, `requests`, `lxml`, `tinycss2`.

## Scraping Image Links

In terminal, run

```bash
python3 main.py
```

You can see the status in `main.log`.

`main.py` will scrape all the Apple Store links and save them to [../output/apple_store_list.csv](../output/apple_store_list.csv), and then it will scrape images for each store and save the results to [../output/all_images.csv](../output/all_images.csv).

## Formatting Gallery

Instead of downloading images, markdown files are created and images are embedded inside. The main markdown file are located in [../output/gallery/README.md](../output/gallery/README.md). It has links to Apple Stores in each country and displays some flagship Apple Stores. Country-specific folders are located In the [gallery](../output/gallery) folder.

To generate this gallery, run

```
python3 format.py
```

Make sure it is run under the same working directory as running `main.py`.

## Testing

I use [Doctests](https://docs.python.org/3.8/library/doctest.html) in this project, so the tests are run when each python files are run. If you don't see anything from Doctests in the console, all the tests are passed.

Alternatively, you can the tests only by

```
python3 -m doctest -v main.py
python3 -m doctest -v format.py
```



