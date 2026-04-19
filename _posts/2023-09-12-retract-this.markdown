---
title: "Retract this!"
layout: post
image: 
    feature: header_crossref_labs.png
doi: "https://doi.org/10.59348/9b1f4-29n44"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2023/09/12/retract-this"
---
Today's big news is that [Crossref has acquired the Retraction Watch database of expressions of concerns and retractions and has made it openly accessible to anyone who wants to use it](https://doi.org/10.13003/c23rw1d9). I'm waiting for full confirmation of the license or public domain dedication under which it will be released, but this is still a great commitment of Crossref to the POSI principles. The liberation of this database is good for science and scholarship in general. It means that Crossref now knows about approximately 50,000 retractions.

Access to the database, for now, is via the Crossref Labs API, which I write and maintain. The Crossref Labs API sits in between the user and the Live API to inject new experimental metadata fields. The API can also serve files, so you can get the CSV of the latest Retraction Watch data at https://api.labs.crossref.org/data/retractionwatch?mailto=[YOUR@EMAIL.HERE].

Meanwhile, the Labs API will show you retraction data in the cr-labs-updates entry if you visit a work that has data, e.g. https://api.labs.crossref.org/works/10.2147/CMAR.S324920?mailto=[YOUR@EMAIL.HERE].

The obvious question (and one that [was asked within an hour of our launch](https://twitter.com/gcabanac/status/1701594642142363877)) is: how can I retrieve a list of all retractions via the API? This is what we call a "filter" in the API and, for Reasons™, it is very difficult to do in the Labs API. The Reasons® that it's so difficult is because the Labs API gets its data by pulling from the Live API, which knows nothing about retractions, and then injecting the data. So pulling out just the entries that have retractions means building a separate index of all items with retractions, then fetching these, and paging through them with the user's requests. This gets to be HORRIBLY slow on the performance front with even not much load, and I don't recommend it. We tried several ways of implementing this but to no avail. So, for now, please download and parse the CSV if you want a full list of retractions. We'll continue to work on an API solution, but it's going to take us a bit longer.

In the meantime, publishers: please continue to deposit retractions. It's really important and we need to end the culture of _shame_ (at least for publishers) around declaring retractions. It is vital for the progress of science that we accurately mark papers that have been shown to be defective.

The other important thing to note about all this is that, with any luck, it will help to make Retraction Watch itself sustainable. As they say [in their announcement](https://retractionwatch.com/2023/09/12/the-retraction-watch-database-becomes-completely-open-and-rw-becomes-far-more-sustainable/): "That means we have achieved sustainability – the highest priority goal for any nonprofit – for the database side of our operation. And the acquisition fee provides important unrestricted reserves that allow for breathing room and the potential for growth." It's really great that Crossref can contribute towards this sustainability, in the spirit of also improving the metadata that we can offer.





